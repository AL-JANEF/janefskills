#!/usr/bin/env python3
"""JANEF Forge developer CLI: validate, list, find, explain, context, doctor, sync, check.

Standard library only. Every command is deterministic.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import CONTRACT_PATH, ENTRY_SKILL, PRODUCT, VERSION, registry as registry_mod  # noqa: E402
from core import context as context_mod  # noqa: E402
from core.composition import check_composition  # noqa: E402
from core.routing import route  # noqa: E402
from core.verification import requirements  # noqa: E402

CONTRACT_BEGIN = "<!-- FORGE_CONTRACT_BEGIN -->"
CONTRACT_END = "<!-- FORGE_CONTRACT_END -->"
SYNCED_FILES = (
    ROOT / "skills" / "core" / "forge" / "SKILL.md",
    ROOT / "adapters" / "claude-code" / "CLAUDE.md.fragment",
    ROOT / "adapters" / "codex" / "AGENTS.md.fragment",
)
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def _load():
    return registry_mod.load()


def _render_contract_block(contract: str) -> str:
    return f"{CONTRACT_BEGIN}\n{contract.strip()}\n{CONTRACT_END}"


def sync_contract(write: bool) -> list[str]:
    """Embed core/protocol/contract.md into every synced file; return files out of sync."""
    contract = CONTRACT_PATH.read_text(encoding="utf-8")
    block = _render_contract_block(contract)
    pattern = re.compile(re.escape(CONTRACT_BEGIN) + r".*?" + re.escape(CONTRACT_END), re.S)
    stale: list[str] = []
    for path in SYNCED_FILES:
        text = path.read_text(encoding="utf-8")
        if not pattern.search(text):
            stale.append(f"{path.relative_to(ROOT)}: missing contract markers")
            continue
        updated = pattern.sub(lambda _m: block, text)
        if updated != text:
            stale.append(str(path.relative_to(ROOT)))
            if write:
                path.write_text(updated, encoding="utf-8")
    return stale


def validate_links() -> list[str]:
    errors: list[str] = []
    for document in ROOT.rglob("*.md"):
        if any(part in {".git", "dist", "node_modules", ".serena"} for part in document.parts):
            continue
        text = document.read_text(encoding="utf-8")
        for raw in MARKDOWN_LINK.findall(text):
            target = raw.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            resolved = (document.parent / target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(f"link escapes repository: {document.relative_to(ROOT)} -> {raw}")
                continue
            if not resolved.exists():
                errors.append(f"broken link: {document.relative_to(ROOT)} -> {raw}")
    return errors


def validate_packaging(reg) -> list[str]:
    errors: list[str] = []
    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    market_path = ROOT / ".claude-plugin" / "marketplace.json"
    try:
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        market = json.loads(market_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"plugin metadata unreadable: {exc}"]
    expected = [f"./{cap.path.relative_to(ROOT).as_posix()}" for cap in reg.ordered()]
    if plugin.get("name") != "janef-forge":
        errors.append("plugin.json name must be janef-forge")
    if plugin.get("skills") != expected:
        errors.append("plugin.json skills must list every registry capability in registry order")
    if plugin.get("version") != VERSION:
        errors.append(f"plugin.json version must be {VERSION}")
    entries = market.get("plugins") or []
    if market.get("name") != "janef-forge":
        errors.append("marketplace.json name must be janef-forge")
    if (
        len(entries) != 1
        or entries[0].get("name") != "janef-forge"
        or entries[0].get("version") != VERSION
        or market.get("version") != VERSION
    ):
        errors.append(f"marketplace.json must declare one janef-forge plugin at version {VERSION}")
    for cap in reg.capabilities.values():
        if cap.manifest["version"] != VERSION:
            errors.append(f"{cap.id}: manifest version must be {VERSION}")
    return errors


def validate_budgets(reg) -> list[str]:
    errors: list[str] = []
    budgets = reg.budgets
    contract = context_mod.estimate_text(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract > budgets["core_contract_max_tokens"]:
        errors.append(f"core contract {contract} tokens exceeds budget {budgets['core_contract_max_tokens']}")
    entry = context_mod.skill_body_tokens(reg, ENTRY_SKILL)
    if entry > budgets["entry_skill_max_tokens"]:
        errors.append(f"entry skill {entry} tokens exceeds budget {budgets['entry_skill_max_tokens']}")
    metadata = context_mod.metadata_tokens(reg)
    if metadata > budgets["always_loaded_metadata_max_tokens"]:
        errors.append(f"always-loaded metadata {metadata} tokens exceeds budget {budgets['always_loaded_metadata_max_tokens']}")
    for cap in reg.selectable():
        body = context_mod.skill_body_tokens(reg, cap.id)
        if body > budgets["skill_body_max_tokens"]:
            errors.append(f"{cap.id}: SKILL.md {body} tokens exceeds budget {budgets['skill_body_max_tokens']}")
    return errors


def cmd_validate(args) -> int:
    reg = _load()
    errors = list(reg.errors)
    errors.extend(validate_packaging(reg))
    errors.extend(validate_budgets(reg))
    errors.extend(validate_links())
    stale = sync_contract(write=False)
    errors.extend(f"contract out of sync: {item} (run: forge sync)" for item in stale)
    if errors:
        print(f"{PRODUCT} validate: FAIL ({len(errors)})")
        for error in errors:
            print(f"- {error}")
        return 1
    selectable = len(reg.selectable())
    print(f"{PRODUCT} validate: PASS")
    print(f"{len(reg.capabilities)} manifests ({selectable} selectable, 1 entry, "
          f"{len(reg.capabilities) - selectable - 1} deprecated), {len(reg.profiles)} profiles, "
          f"{len(reg.aliases)} aliases, packaging, budgets, links, contract sync verified.")
    return 0


def cmd_list(args) -> int:
    reg = _load()
    if args.json:
        payload = [
            {k: cap.manifest[k] for k in ("id", "name", "domain", "risk_level", "context_cost", "status", "requires", "conflicts_with")}
            for cap in reg.ordered()
        ]
        print(json.dumps(payload, indent=2))
        return 0
    print(f"{PRODUCT} {VERSION} capabilities")
    for cap in reg.ordered():
        flags = "" if cap.status == "stable" else f" [{cap.status}]"
        req = f"  requires: {', '.join(cap.manifest['requires'])}" if cap.manifest["requires"] else ""
        print(f"  {cap.domain:<12} {cap.id:<26} risk={cap.risk_level:<8} cost={cap.manifest['context_cost']:<6}{flags}{req}")
    print(f"profiles: {', '.join(sorted(reg.profiles))}")
    print(f"aliases:  {', '.join(f'{a}->{t}' for a, t in sorted(reg.aliases.items()))}")
    return 0


def cmd_find(args) -> int:
    reg = _load()
    result = route(" ".join(args.task), reg, args.profile)
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0
    if not result.applicable:
        print("not applicable: no software-engineering capability selected")
        return 0
    for cap_id in result.selected:
        via = f"  (required by {', '.join(result.required_by[cap_id])})" if cap_id in result.required_by else ""
        print(f"{cap_id}{via}")
    return 0


def cmd_explain(args) -> int:
    reg = _load()
    result = route(" ".join(args.task), reg, args.profile)
    if args.json:
        payload = result.to_dict()
        payload["verification"] = requirements(result.risk_level, reg.profiles[result.profile]["verification_floor"])
        payload["context"] = context_mod.report(reg, result.selected).to_dict()
        print(json.dumps(payload, indent=2))
        return 0
    print(f"task:     {result.prompt}")
    print(f"applies:  {'yes' if result.applicable else 'no'}")
    if not result.applicable:
        for line in result.explanation:
            print(f"  {line}")
        return 0
    profile = result.profile if result.profile == result.requested_profile else f"{result.requested_profile} -> {result.profile}"
    print(f"profile:  {profile}")
    print(f"risk:     {result.risk_level}  ({', '.join(result.risk_signals) or 'no signals'})")
    print("selected:")
    for cap_id in result.selected:
        reason = f"required by {', '.join(result.required_by[cap_id])}" if cap_id in result.required_by else f"score {result.scores.get(cap_id, 0)}"
        print(f"  - {cap_id:<26} {reason}")
    if result.rejected:
        print("rejected:")
        for item in result.rejected:
            print(f"  - {item['id']:<26} {item['reason']}")
    verification = requirements(result.risk_level, reg.profiles[result.profile]["verification_floor"])
    print(f"verification tier: {verification['level'][0]}")
    for item in verification["required"]:
        print(f"  - {item}")
    ctx = context_mod.report(reg, result.selected)
    print(f"context:  {ctx.total_estimated_tokens} est. tokens (core {ctx.core_tokens} + skills {ctx.selected_skill_tokens}); "
          f"+{ctx.selected_reference_tokens} references on demand; skipped {len(ctx.skipped)} capabilities ({ctx.skipped_tokens} tokens)")
    print("trace:")
    for line in result.explanation:
        print(f"  {line}")
    return 0


def cmd_context(args) -> int:
    reg = _load()
    if args.skills:
        selected = [reg.resolve(s) for s in args.skills]
        problems = check_composition(reg, selected)
        if problems:
            for problem in problems:
                print(f"ERROR: {problem}", file=sys.stderr)
            return 1
    else:
        result = route(" ".join(args.task), reg, args.profile)
        selected = result.selected
    rep = context_mod.report(reg, selected)
    if args.json:
        print(json.dumps(rep.to_dict(), indent=2))
        return 0
    print(f"method:                    {rep.method}")
    print(f"core (entry skill):        {rep.core_tokens}  (contract alone: {rep.contract_tokens})")
    print(f"always-loaded metadata:    {rep.metadata_tokens}")
    print(f"selected skills:           {rep.selected_skill_tokens}  {rep.selected}")
    for cap_id, sizes in rep.per_skill.items():
        print(f"  - {cap_id:<26} skill {sizes['skill']:>5}  references {sizes['references']:>5}")
    print(f"selected references:       {rep.selected_reference_tokens}  (on demand)")
    print(f"total estimated:           {rep.total_estimated_tokens}  (with references: {rep.total_with_references_tokens})")
    print(f"eager full load:           {rep.eager_total_tokens}  -> estimated savings {rep.estimated_savings:.1%}")
    print(f"skipped capabilities:      {len(rep.skipped)} ({rep.skipped_tokens} tokens)")
    print("note: estimated structural context cost, not measured provider billing")
    return 0


def cmd_doctor(args) -> int:
    import shutil
    from scripts.install import doctor as install_doctor  # local import keeps CLI startup cheap

    reg = _load()
    failures = 0
    print(f"{PRODUCT} {VERSION} doctor")
    status = "OK" if not reg.errors else "FAIL"
    failures += bool(reg.errors)
    print(f"[{status}] registry: {len(reg.capabilities)} capabilities, {len(reg.profiles)} profiles")
    for error in reg.errors:
        print(f"       - {error}")
    stale = sync_contract(write=False)
    print(f"[{'OK' if not stale else 'FAIL'}] contract sync")
    failures += bool(stale)
    for tool in ("git", "python3", "claude", "codex", "rg", "semgrep", "gitleaks", "skillspector", "shellcheck", "actionlint"):
        found = shutil.which(tool)
        print(f"[{'OK' if found else 'OPTIONAL'}] {tool}: {found or '-'}")
    failures += install_doctor(args.target, reg, verbose=True)
    return 1 if failures else 0


def cmd_sync(args) -> int:
    stale = sync_contract(write=True)
    if stale:
        print("updated: " + ", ".join(stale))
    else:
        print("contract already in sync")
    return 0


def cmd_check(args) -> int:
    reg = _load()
    problems = check_composition(reg, args.skills)
    if problems:
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("composition ok: " + ", ".join(reg.resolve(s) for s in args.skills))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forge", description=f"{PRODUCT} {VERSION} developer tooling")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate", help="validate manifests, registry, packaging, budgets, links").set_defaults(func=cmd_validate)
    p = sub.add_parser("list", help="list capabilities, profiles, aliases"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_list)
    for name, func, help_text in (("find", cmd_find, "select capabilities for a task"), ("explain", cmd_explain, "explain the deterministic selection")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("task", nargs="+")
        p.add_argument("--profile", choices=("lean", "standard", "high-assurance"))
        p.add_argument("--json", action="store_true")
        p.set_defaults(func=func)
    p = sub.add_parser("context", help="estimated structural context cost for a task or explicit skill set")
    p.add_argument("task", nargs="*")
    p.add_argument("--skills", nargs="+", metavar="ID")
    p.add_argument("--profile", choices=("lean", "standard", "high-assurance"))
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_context)
    p = sub.add_parser("doctor", help="repository and installation integrity check")
    p.add_argument("--target", choices=("claude", "codex", "both"), default="both")
    p.set_defaults(func=cmd_doctor)
    sub.add_parser("sync", help="embed core/protocol/contract.md into the entry skill and adapters").set_defaults(func=cmd_sync)
    p = sub.add_parser("check", help="validate an explicit composition of skill ids"); p.add_argument("skills", nargs="+"); p.set_defaults(func=cmd_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "context" and not args.task and not args.skills:
        print("ERROR: provide a task or --skills", file=sys.stderr)
        return 2
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
