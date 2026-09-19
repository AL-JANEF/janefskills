"""Deterministic capability registry: discovery, schema validation, graph integrity."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from core import CONFIG_DIR, ENTRY_SKILL, PROFILES_DIR, SCHEMAS_DIR, SKILLS_DIR
from core.schema import load_schema, validate

MANIFEST_NAME = "capability.json"
SKILL_FILE = "SKILL.md"
MAX_SKILL_LINES = 500
RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class RegistryError(ValueError):
    """Raised when the registry cannot be loaded at all (malformed files)."""


@dataclass(frozen=True)
class Capability:
    id: str
    path: Path
    manifest: dict[str, Any]
    frontmatter: dict[str, str]
    body: str

    @property
    def domain(self) -> str:
        return self.manifest["domain"]

    @property
    def status(self) -> str:
        return self.manifest["status"]

    @property
    def risk_level(self) -> str:
        return self.manifest["risk_level"]

    @property
    def priority(self) -> int:
        return int(self.manifest.get("priority", 50))

    @property
    def is_selectable(self) -> bool:
        return self.status != "deprecated" and self.domain in {"engineering", "security"}

    def reference_paths(self) -> list[Path]:
        return [self.path / ref for ref in self.manifest.get("references", [])]


@dataclass
class Registry:
    capabilities: dict[str, Capability]
    profiles: dict[str, dict[str, Any]]
    aliases: dict[str, str]
    budgets: dict[str, Any]
    errors: list[str] = field(default_factory=list)

    def get(self, capability_id: str) -> Capability:
        resolved = self.aliases.get(capability_id, capability_id)
        try:
            return self.capabilities[resolved]
        except KeyError as exc:
            raise KeyError(f"unknown capability: {capability_id}") from exc

    def resolve(self, name: str) -> str:
        return self.aliases.get(name, name)

    def selectable(self) -> list[Capability]:
        return sorted(
            (cap for cap in self.capabilities.values() if cap.is_selectable),
            key=lambda cap: cap.id,
        )

    def ordered(self) -> list[Capability]:
        domain_rank = {"core": 0, "engineering": 1, "security": 2, "compat": 3}
        return sorted(
            self.capabilities.values(),
            key=lambda cap: (domain_rank.get(cap.domain, 9), cap.id),
        )


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse the YAML-ish frontmatter used by SKILL.md (scalars and folded blocks)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise RegistryError("missing frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise RegistryError("unterminated frontmatter") from exc
    result: dict[str, str] = {}
    index = 1
    while index < end:
        match = re.match(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$", lines[index])
        if not match:
            index += 1
            continue
        key, value = match.group(1), (match.group(2) or "").strip()
        if value in {">", ">-", "|", "|-"}:
            block: list[str] = []
            index += 1
            while index < end and (not lines[index] or lines[index][0].isspace()):
                block.append(lines[index].strip())
                index += 1
            result[key] = " ".join(part for part in block if part)
            continue
        result[key] = value.strip("\"'")
        index += 1
    body = "\n".join(lines[end + 1:])
    return result, body


def _load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path}")
        return None
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON: {path}: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"JSON root must be an object: {path}")
        return None
    return payload


def discover(skills_dir: Path = SKILLS_DIR) -> list[Path]:
    return sorted(p.parent for p in skills_dir.glob(f"*/*/{MANIFEST_NAME}"))


def load(skills_dir: Path = SKILLS_DIR, profiles_dir: Path = PROFILES_DIR,
         config_dir: Path = CONFIG_DIR) -> Registry:
    """Load everything and collect integrity errors without raising on the first one."""
    errors: list[str] = []
    schema = load_schema(SCHEMAS_DIR / "capability.schema.json")
    profile_schema = load_schema(SCHEMAS_DIR / "profile.schema.json")
    budgets_schema = load_schema(SCHEMAS_DIR / "budgets.schema.json")

    capabilities: dict[str, Capability] = {}
    for directory in discover(skills_dir):
        rel = directory.relative_to(skills_dir.parent)
        manifest = _load_json(directory / MANIFEST_NAME, errors)
        if manifest is None:
            continue
        for violation in validate(manifest, schema):
            errors.append(f"{rel}/{MANIFEST_NAME}: {violation}")
        cap_id = manifest.get("id")
        if not isinstance(cap_id, str):
            continue
        if cap_id != directory.name:
            errors.append(f"{rel}: manifest id {cap_id!r} must equal directory name")
        if cap_id in capabilities:
            errors.append(f"duplicate capability id: {cap_id}")
            continue
        expected_domain = directory.parent.name
        if manifest.get("domain") != expected_domain and not (
            expected_domain == "compat" and manifest.get("domain") in {"core", "compat"}
        ):
            errors.append(f"{rel}: domain {manifest.get('domain')!r} does not match directory {expected_domain!r}")
        skill_file = directory / SKILL_FILE
        try:
            text = skill_file.read_text(encoding="utf-8")
            frontmatter, body = parse_frontmatter(text)
        except (OSError, RegistryError) as exc:
            errors.append(f"{rel}/{SKILL_FILE}: {exc}")
            frontmatter, body, text = {}, "", ""
        capabilities[cap_id] = Capability(cap_id, directory, manifest, frontmatter, body)
        _check_skill_file(cap_id, rel, manifest, frontmatter, text, directory, errors)

    aliases_payload = _load_json(config_dir / "aliases.json", errors) or {}
    aliases = {k: v for k, v in aliases_payload.get("aliases", {}).items() if isinstance(v, str)}
    budgets = _load_json(config_dir / "budgets.json", errors) or {}
    for violation in validate(budgets, budgets_schema):
        errors.append(f"config/budgets.json: {violation}")

    profiles: dict[str, dict[str, Any]] = {}
    for path in sorted(profiles_dir.glob("*/profile.json")):
        payload = _load_json(path, errors)
        if payload is None:
            continue
        for violation in validate(payload, profile_schema):
            errors.append(f"{path.relative_to(profiles_dir.parent)}: {violation}")
        if payload.get("id") != path.parent.name:
            errors.append(f"{path}: profile id must equal directory name")
        if not (path.parent / "PROFILE.md").is_file():
            errors.append(f"{path.parent}: missing PROFILE.md")
        profiles[path.parent.name] = payload

    registry = Registry(capabilities, profiles, aliases, budgets, errors)
    errors.extend(check_graph(registry))
    return registry


def _check_skill_file(cap_id: str, rel: Path, manifest: dict[str, Any], frontmatter: dict[str, str],
                      text: str, directory: Path, errors: list[str]) -> None:
    if not text:
        return
    if frontmatter.get("name") != cap_id:
        errors.append(f"{rel}/{SKILL_FILE}: frontmatter name must be {cap_id!r}")
    if frontmatter.get("license") != "MIT":
        errors.append(f"{rel}/{SKILL_FILE}: frontmatter must declare license: MIT")
    if frontmatter.get("description", "") != manifest.get("description"):
        errors.append(f"{rel}/{SKILL_FILE}: frontmatter description must equal the manifest description")
    if len(text.splitlines()) > MAX_SKILL_LINES:
        errors.append(f"{rel}/{SKILL_FILE}: exceeds {MAX_SKILL_LINES} lines")
    declared = set(manifest.get("references", []))
    actual = {f"references/{p.name}" for p in (directory / "references").glob("*.md")}
    for missing in sorted(declared - actual):
        errors.append(f"{rel}: declared reference does not exist: {missing}")
    for undeclared in sorted(actual - declared):
        errors.append(f"{rel}: reference file not declared in manifest: {undeclared}")
    for reference in sorted(declared & actual):
        if reference not in text:
            errors.append(f"{rel}/{SKILL_FILE}: does not link declared reference {reference}")
    for stray in directory.iterdir():
        if stray.name not in {SKILL_FILE, MANIFEST_NAME, "references"} and not stray.name.startswith("."):
            errors.append(f"{rel}: unexpected entry in skill directory: {stray.name}")


def check_graph(registry: Registry) -> list[str]:
    """Dependency, conflict, ownership, alias, and profile integrity."""
    errors: list[str] = []
    caps = registry.capabilities
    ids = set(caps)

    for cap in caps.values():
        for key in ("requires", "optional_with", "conflicts_with"):
            for target in cap.manifest.get(key, []):
                if target == cap.id:
                    errors.append(f"{cap.id}: {key} references itself")
                elif target not in ids:
                    errors.append(f"{cap.id}: {key} references unknown capability {target!r}")
        for target in cap.manifest.get("requires", []):
            if target in cap.manifest.get("conflicts_with", []):
                errors.append(f"{cap.id}: requires and conflicts with {target!r}")
            if target in caps and caps[target].status == "deprecated":
                errors.append(f"{cap.id}: requires deprecated capability {target!r}")
        if cap.status == "deprecated":
            replaced = cap.manifest.get("replaced_by")
            if not replaced or replaced not in ids:
                errors.append(f"{cap.id}: deprecated capability must name an existing replaced_by")
        elif "replaced_by" in cap.manifest:
            errors.append(f"{cap.id}: only deprecated capabilities may set replaced_by")

    for cap in caps.values():
        for other in cap.manifest.get("conflicts_with", []):
            if other in caps and cap.id not in caps[other].manifest.get("conflicts_with", []):
                errors.append(f"conflict must be declared on both sides: {cap.id} <-> {other}")

    errors.extend(_check_cycles(caps))

    owners: dict[str, list[str]] = {}
    for cap in caps.values():
        if cap.status == "deprecated":
            continue
        for tag in cap.manifest.get("responsibilities", []):
            owners.setdefault(tag, []).append(cap.id)
    for tag, holders in sorted(owners.items()):
        if len(holders) > 1:
            errors.append(f"responsibility {tag!r} owned by more than one capability: {sorted(holders)}")

    trigger_owners: dict[str, list[str]] = {}
    for cap in caps.values():
        if not cap.is_selectable:
            continue
        for trigger in cap.manifest.get("triggers", []):
            trigger_owners.setdefault(_normalize_phrase(trigger), []).append(cap.id)
    for trigger, holders in sorted(trigger_owners.items()):
        if len(holders) > 1:
            errors.append(f"trigger {trigger!r} declared by more than one capability: {sorted(holders)}")

    for alias, target in sorted(registry.aliases.items()):
        if alias in ids and caps[alias].status != "deprecated":
            errors.append(f"alias {alias!r} collides with a live capability id")
        if target not in ids:
            errors.append(f"alias {alias!r} points to unknown capability {target!r}")

    if ENTRY_SKILL not in ids:
        errors.append(f"entry capability {ENTRY_SKILL!r} is missing")

    for profile_id, profile in registry.profiles.items():
        for level, included in profile.get("auto_include", {}).items():
            for target in included:
                if target not in ids:
                    errors.append(f"profile {profile_id}: auto_include[{level}] references unknown {target!r}")
    for required in ("lean", "standard", "high-assurance"):
        if required not in registry.profiles:
            errors.append(f"missing profile: {required}")
    return errors


def _check_cycles(caps: dict[str, Capability]) -> list[str]:
    errors: list[str] = []
    state: dict[str, int] = {}

    def visit(node: str, stack: list[str]) -> None:
        state[node] = 1
        for nxt in caps[node].manifest.get("requires", []):
            if nxt not in caps:
                continue
            if state.get(nxt) == 1:
                cycle = " -> ".join(stack[stack.index(nxt):] + [nxt]) if nxt in stack else f"{node} -> {nxt}"
                errors.append(f"requires cycle: {cycle}")
            elif state.get(nxt) is None:
                visit(nxt, stack + [nxt])
        state[node] = 2

    for cap_id in sorted(caps):
        if state.get(cap_id) is None:
            visit(cap_id, [cap_id])
    return errors


def _normalize_phrase(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9_+.-]+", value.lower()))


def closure(registry: Registry, ids: Iterable[str]) -> list[str]:
    """Transitive ``requires`` closure in deterministic order (seeds first)."""
    result: list[str] = []
    queue = list(ids)
    while queue:
        current = queue.pop(0)
        if current in result:
            continue
        result.append(current)
        if current in registry.capabilities:
            queue.extend(registry.capabilities[current].manifest.get("requires", []))
    return result
