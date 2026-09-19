#!/usr/bin/env python3
"""Install, upgrade, uninstall, and check JANEF Forge for Claude Code and Codex.

Safety contract:
- never overwrites silently: an existing destination is refused unless --force
  (any content, backed up) or --upgrade (only Forge-managed, unmodified content, backed up);
- managed files are recorded in a per-skill marker with SHA-256 hashes, so
  ``doctor`` detects drift and ``uninstall`` removes only what Forge installed;
- idempotent: identical content already installed is reported as unchanged;
- destinations must be absolute, not the filesystem root, not a symlink, and not
  inside the source tree; skill directories are staged in a temp dir and moved into
  place; failures roll back to the previous state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import PRODUCT, VERSION, registry as registry_mod  # noqa: E402
from core.registry import Registry  # noqa: E402

MARKER = ".janef-forge.json"
POLICY_BEGIN = "<!-- JANEF_FORGE_BEGIN -->"
POLICY_END = "<!-- JANEF_FORGE_END -->"
LEGACY_POLICY = re.compile(r"(?ms)^<!-- AGENT_ENGINEERING_STACK_BEGIN -->.*?^<!-- AGENT_ENGINEERING_STACK_END -->\s*")
HOSTS = ("claude", "codex")
SKILL_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class InstallError(RuntimeError):
    """Raised when an operation cannot complete safely."""


def default_root(target: str) -> Path:
    home = Path.home()
    if target == "claude":
        return Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude")) / "skills"
    if target == "codex":
        return Path(os.environ.get("CODEX_HOME", home / ".codex")) / "skills"
    raise InstallError(f"unsupported target: {target}")


def policy_file(target: str) -> Path:
    home = Path.home()
    if target == "claude":
        return Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude")) / "CLAUDE.md"
    return Path(os.environ.get("CODEX_HOME", home / ".codex")) / "AGENTS.md"


def resolve_targets(target: str, destination: Path | None) -> tuple[tuple[str, Path], ...]:
    if destination is not None:
        if not destination.is_absolute():
            raise InstallError("--dest must be an absolute path")
        if target == "both":
            raise InstallError("--dest cannot be combined with --target both")
    names = HOSTS if target == "both" else (target,)
    result = []
    for name in names:
        root = (destination or default_root(name)).expanduser()
        check_destination_root(root)
        result.append((name, root))
    return tuple(result)


def check_destination_root(root: Path) -> None:
    if root.is_symlink():
        raise InstallError(f"refusing symlinked destination: {root}")
    resolved = root.resolve()
    if resolved == Path(resolved.anchor) or resolved == Path.home().resolve():
        raise InstallError(f"refusing unsafe destination: {root}")
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        return
    raise InstallError(f"destination is inside the source tree: {root}")


def choose_skills(reg: Registry, requested: list[str]) -> list[str]:
    if not requested:
        return [cap.id for cap in reg.ordered() if cap.status != "deprecated"] + [
            cap.id for cap in reg.ordered() if cap.status == "deprecated"
        ]
    selected: list[str] = []
    for name in requested:
        resolved = reg.resolve(name)
        if resolved not in reg.capabilities:
            raise InstallError(f"unknown skill: {name}")
        if resolved != name:
            print(f"note: {name} is a compatibility alias for {resolved}")
        if resolved not in selected:
            selected.append(resolved)
    # requires closure so an installed skill never references a missing dependency
    return registry_mod.closure(reg, selected)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_tree(directory: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise InstallError(f"symlink not allowed in installed content: {path}")
        if path.is_file() and path.name != MARKER:
            hashes[path.relative_to(directory).as_posix()] = sha256_file(path)
    return hashes


def render_openai_yaml(reg: Registry, cap_id: str) -> str:
    interface = json.loads((ROOT / "adapters" / "codex" / "interface.json").read_text(encoding="utf-8"))
    cap = reg.capabilities[cap_id]
    short = cap.manifest["description"].split(". ")[0].split(": ")[0]
    limit = int(interface["short_description_max"])
    if len(short) > limit:
        short = short[: limit - 3].rstrip() + "..."
    display = interface["display_name_template"].format(name=cap.manifest["name"])
    prompt = interface["default_prompt_template"].replace("{id}", cap_id)
    return (
        "interface:\n"
        f"  display_name: {json.dumps(display)}\n"
        f"  short_description: {json.dumps(short)}\n"
        f"  brand_color: {json.dumps(interface['brand_color'])}\n"
        f"  default_prompt: {json.dumps(prompt)}\n"
    )


def stage_skill(reg: Registry, cap_id: str, target: str, stage_root: Path) -> Path:
    source = reg.capabilities[cap_id].path
    staged = stage_root / target / cap_id
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, staged, symlinks=True, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"))
    for path in staged.rglob("*"):
        if path.is_symlink():
            raise InstallError(f"source contains a symlink: {source / path.relative_to(staged)}")
    if target == "codex":
        (staged / "agents").mkdir()
        (staged / "agents" / "openai.yaml").write_text(render_openai_yaml(reg, cap_id), encoding="utf-8")
    marker = {
        "product": PRODUCT,
        "version": VERSION,
        "capability": cap_id,
        "target": target,
        "installed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": hash_tree(staged),
    }
    (staged / MARKER).write_text(json.dumps(marker, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return staged


def read_marker(directory: Path) -> dict | None:
    path = directory / MARKER
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) and payload.get("product") == PRODUCT else None


def classify_existing(directory: Path) -> str:
    """'absent' | 'unmanaged' | 'managed-clean' | 'managed-modified'."""
    if not directory.exists() and not directory.is_symlink():
        return "absent"
    marker = read_marker(directory)
    if marker is None or directory.is_symlink():
        return "unmanaged"
    try:
        current = hash_tree(directory)
    except InstallError:
        return "managed-modified"
    return "managed-clean" if current == marker.get("files") else "managed-modified"


def backup_path(destination: Path, stamp: str) -> Path:
    candidate = destination.with_name(f"{destination.name}.backup.{stamp}")
    counter = 1
    while candidate.exists():
        candidate = destination.with_name(f"{destination.name}.backup.{stamp}.{counter}")
        counter += 1
    return candidate


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def install(reg: Registry, targets: tuple[tuple[str, Path], ...], skills: list[str], *,
            force: bool, upgrade: bool, dry_run: bool) -> list[dict]:
    """Return one record per (target, skill): action, destination, backup."""
    for cap_id in skills:
        if not SKILL_ID.fullmatch(cap_id):
            raise InstallError(f"invalid skill id: {cap_id}")
    plans = []
    with tempfile.TemporaryDirectory(prefix="janef-forge-install-") as temp_dir:
        stage_root = Path(temp_dir)
        for target, root in targets:
            for cap_id in skills:
                staged = stage_skill(reg, cap_id, target, stage_root)
                destination = root / cap_id
                state = classify_existing(destination)
                staged_hashes = json.loads((staged / MARKER).read_text(encoding="utf-8"))["files"]
                if state == "managed-clean" and read_marker(destination).get("files") == staged_hashes \
                        and read_marker(destination).get("version") == VERSION:
                    action = "unchanged"
                elif state == "absent":
                    action = "install"
                elif state == "managed-clean" and (upgrade or force):
                    action = "upgrade"
                elif force:
                    action = "replace"
                else:
                    hint = "--upgrade" if state == "managed-clean" else "--force (the existing content is not Forge-managed or was modified)"
                    raise InstallError(f"existing installation at {destination} ({state}); use {hint} to back it up and replace it")
                plans.append({"target": target, "skill": cap_id, "destination": destination, "action": action, "staged": staged})

        if dry_run:
            for plan in plans:
                print(f"DRY RUN [{plan['target']}] {plan['action']}: {plan['destination']}")
            return [{**p, "backup": None, "staged": None} for p in plans]

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        completed: list[dict] = []
        try:
            for plan in plans:
                if plan["action"] == "unchanged":
                    completed.append({**plan, "backup": None})
                    continue
                destination: Path = plan["destination"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                backup = None
                if destination.exists() or destination.is_symlink():
                    backup = backup_path(destination, stamp)
                    shutil.move(str(destination), str(backup))
                record = {**plan, "backup": backup}
                completed.append(record)
                shutil.move(str(plan["staged"]), str(destination))
                if classify_existing(destination) != "managed-clean":
                    raise InstallError(f"post-install verification failed: {destination}")
        except Exception as exc:
            for record in reversed(completed):
                if record["action"] == "unchanged":
                    continue
                remove_path(record["destination"])
                if record["backup"] is not None and record["backup"].exists():
                    shutil.move(str(record["backup"]), str(record["destination"]))
            raise InstallError(f"installation failed and was rolled back: {exc}") from exc
    return [{k: v for k, v in r.items() if k != "staged"} for r in completed]


def uninstall(reg: Registry, targets: tuple[tuple[str, Path], ...], skills: list[str], *,
              force: bool, dry_run: bool) -> list[dict]:
    records: list[dict] = []
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for target, root in targets:
        for cap_id in skills:
            destination = root / cap_id
            state = classify_existing(destination)
            if state == "absent":
                records.append({"target": target, "skill": cap_id, "destination": destination, "action": "absent", "backup": None})
                continue
            if state == "unmanaged":
                raise InstallError(f"refusing to remove {destination}: not installed by {PRODUCT}")
            if state == "managed-modified" and not force:
                raise InstallError(f"refusing to remove {destination}: managed files were modified (use --force to back up and remove)")
            action = "remove" if state == "managed-clean" else "backup-and-remove"
            if dry_run:
                print(f"DRY RUN [{target}] {action}: {destination}")
                records.append({"target": target, "skill": cap_id, "destination": destination, "action": action, "backup": None})
                continue
            backup = None
            if action == "backup-and-remove":
                backup = backup_path(destination, stamp)
                shutil.copytree(destination, backup)
            remove_path(destination)
            records.append({"target": target, "skill": cap_id, "destination": destination, "action": action, "backup": backup})
    return records


def doctor(target: str, reg: Registry, *, destination: Path | None = None, verbose: bool = True) -> int:
    """Report installation state per host; return the number of problems."""
    problems = 0
    names = HOSTS if target == "both" else (target,)
    for name in names:
        root = (destination or default_root(name)).expanduser()
        if verbose:
            print(f"[{name}] skills root: {root}")
        if not root.is_dir():
            if verbose:
                print(f"       not installed")
            continue
        for cap in reg.ordered():
            path = root / cap.id
            state = classify_existing(path)
            if state == "absent":
                continue
            marker = read_marker(path) or {}
            version = marker.get("version", "?")
            note = ""
            if state == "unmanaged":
                note = "present but not Forge-managed (legacy or user-owned)"
                problems += 1
            elif state == "managed-modified":
                note = f"v{version}, managed files modified locally"
                problems += 1
            elif version != VERSION:
                note = f"v{version} installed, {VERSION} available (run install --upgrade)"
                problems += 1
            else:
                note = f"v{version} ok"
            if verbose:
                print(f"       {'WARN' if note and 'ok' not in note else 'OK  '} {cap.id:<26} {note}")
        for legacy in ("janef", "engineering-standard", "engineering-router", "lean-code-engineer", "security-engineering"):
            path = root / legacy
            if path.exists() and legacy not in reg.capabilities:
                problems += 1
                if verbose:
                    print(f"       WARN {legacy:<26} legacy skill directory; see docs/migration-v2.md")
    return problems


def merge_policy(target: str, remove: bool, dry_run: bool) -> Path:
    fragment_name = "CLAUDE.md.fragment" if target == "claude" else "AGENTS.md.fragment"
    adapter_dir = "claude-code" if target == "claude" else "codex"
    fragment = (ROOT / "adapters" / adapter_dir / fragment_name).read_text(encoding="utf-8").strip()
    path = policy_file(target)
    if path.is_symlink():
        raise InstallError(f"refusing symlinked policy file: {path}")
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    block = re.compile(re.escape(POLICY_BEGIN) + r".*?" + re.escape(POLICY_END) + r"\s*", re.S)
    stripped = block.sub("", existing)
    stripped = LEGACY_POLICY.sub("", stripped).rstrip()
    updated = stripped if remove else (stripped + ("\n\n" if stripped else "") + fragment)
    updated = updated.rstrip() + "\n" if updated.strip() else ""
    if updated == existing:
        print(f"policy unchanged: {path}")
        return path
    if dry_run:
        print(f"DRY RUN {'remove' if remove else 'merge'} policy block: {path}")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    if existing:
        backup = backup_path(path, datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
        shutil.copy2(path, backup)
        print(f"backup: {backup}")
    path.write_text(updated, encoding="utf-8")
    print(f"{'removed' if remove else 'merged'} policy block: {path}")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"Install {PRODUCT} {VERSION} for Claude Code, Codex, or both.")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--target", choices=("claude", "codex", "both"), default="claude")
        p.add_argument("--dest", type=Path, help="custom absolute skills directory (single target only)")
        p.add_argument("--only", nargs="+", metavar="SKILL", default=[], help="limit to these skills (aliases accepted)")
        p.add_argument("--dry-run", action="store_true")

    p = sub.add_parser("install", help="install or upgrade skills"); common(p)
    p.add_argument("--upgrade", action="store_true", help="replace Forge-managed, unmodified skills (backed up)")
    p.add_argument("--force", action="store_true", help="replace any existing skill directory (backed up)")
    p = sub.add_parser("uninstall", help="remove skills installed by Forge"); common(p)
    p.add_argument("--force", action="store_true", help="also remove managed skills that were modified (backed up)")
    p = sub.add_parser("doctor", help="report installation state")
    p.add_argument("--target", choices=("claude", "codex", "both"), default="both")
    p.add_argument("--dest", type=Path)
    p = sub.add_parser("policy", help="merge or remove the compact policy block in CLAUDE.md / AGENTS.md")
    p.add_argument("--target", choices=("claude", "codex", "both"), default="claude")
    p.add_argument("--remove", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        reg = registry_mod.load()
        if reg.errors:
            raise InstallError("repository failed validation; run scripts/forge.py validate")
        if args.command == "doctor":
            return 1 if doctor(args.target, reg, destination=args.dest) else 0
        if args.command == "policy":
            for name in (HOSTS if args.target == "both" else (args.target,)):
                merge_policy(name, args.remove, args.dry_run)
            return 0
        targets = resolve_targets(args.target, args.dest)
        skills = choose_skills(reg, args.only)
        if args.command == "install":
            records = install(reg, targets, skills, force=args.force, upgrade=args.upgrade, dry_run=args.dry_run)
        else:
            records = uninstall(reg, targets, skills, force=args.force, dry_run=args.dry_run)
    except InstallError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if not args.dry_run:
        for record in records:
            print(f"{record['action']:<18}[{record['target']}] {record['destination']}")
            if record.get("backup"):
                print(f"{'':<18}backup: {record['backup']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
