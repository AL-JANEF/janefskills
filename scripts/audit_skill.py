#!/usr/bin/env python3
"""Conservative static triage for external skill, plugin, hook, or MCP package directories.

This is not a sandbox and not proof of safety. It never executes candidate code; it
reads text files and reports risky patterns for human review. Exit code 2 means a
finding at or above ``--fail-on`` was found. Non-text files are listed for review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TEXT_EXTS = {".md", ".txt", ".sh", ".bash", ".zsh", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx",
             ".json", ".yaml", ".yml", ".toml", ".ps1", ".rb", ".go", ".rs"}
TEXT_NAMES = {"SKILL.md", "Dockerfile", "Makefile", "AGENTS.md", "CLAUDE.md"}
MAX_FILE_BYTES = 2_000_000
PATTERNS = [
    ("high", "credential-path", re.compile(r"(?i)(~?/\.ssh\b|\.aws/credentials|\.config/gcloud|keychain|security\s+find-generic-password|\.npmrc|\.pypirc|\.netrc)")),
    ("high", "secret-access", re.compile(r"(?i)(process\.env\[[^\]]*(key|token|secret|password)|os\.environ[^\n]*(key|token|secret|password)|cat\s+[^\n]*(\.env\b|credentials))")),
    ("high", "destructive-shell", re.compile(r"(?i)(rm\s+-[a-z]*r[a-z]*f?\s+[/~$]|rm\s+-[a-z]*f[a-z]*r?\s+[/~$]|git\s+reset\s+--hard|git\s+clean\s+-[a-z]*f|git\s+push\s+[^\n]*--force|\bmkfs\b|\bdd\s+if=|chmod\s+-R\s+777)")),
    ("high", "dynamic-exec", re.compile(r"(?i)(\beval\s*\(|\bexec\s*\(|child_process|subprocess\.(Popen|run|call|check_output)|os\.system\s*\(|os\.popen\s*\(|Invoke-Expression)")),
    ("high", "unsafe-deserialization", re.compile(r"(?i)(pickle\.loads?\(|yaml\.load\((?![^\n]*SafeLoader)|yaml\.(unsafe_load|full_load)\(|marshal\.loads?\(|shelve\.open\()")),
    ("high", "remote-pipe-to-shell", re.compile(r"(?i)((curl|wget)[^\n|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b|iex\s*\(.*DownloadString)")),
    ("medium", "network-command", re.compile(r"(?i)(\bcurl\b|\bwget\b|requests\.(get|post|put|delete|request)\(|\bfetch\s*\(|https?\.request\s*\(|urllib\.request|socket\.connect)")),
    ("medium", "package-install-hook", re.compile(r"(?i)(\"(pre|post)install\"\s*:|\"prepare\"\s*:|npm\s+(install|i)\b|pip\s+install\b|brew\s+install\b|uv\s+tool\s+install\b|npx\s+[a-z@])")),
    ("medium", "agent-config-mutation", re.compile(r"(?i)(AGENTS\.md|CLAUDE\.md|settings(\.local)?\.json|config\.toml|\.mcp\.json).{0,80}(overwrite|replace|delete|write|append|modify)")),
    ("medium", "prompt-override", re.compile(r"(?i)(ignore\s+(all\s+)?(previous|prior)\s+instructions|reveal\s+(the\s+)?(system|developer)\s+prompt|disable\s+(safety|security|guardrails?)|bypass\s+(approval|permission|the\s+gate)|do\s+not\s+tell\s+the\s+user)")),
    ("medium", "hidden-content", re.compile(r"(?i)(<!--[^\n]*(instruction|ignore|secret|do not show)[^\n]*-->|​|⁠|display:\s*none)")),
    ("low", "encoded-content", re.compile(r"(?i)(base64\s+(-d|--decode)|atob\s*\(|fromBase64|binascii\.unhexlify|\\x[0-9a-f]{2}\\x[0-9a-f]{2}\\x[0-9a-f]{2})")),
]
RANK = {"low": 1, "medium": 2, "high": 3}


def scan(root: Path) -> tuple[list[dict], list[str], list[str]]:
    findings: list[dict] = []
    non_text: list[str] = []
    symlinks: list[str] = []
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if ".git" in path.parts:
            continue
        if path.is_symlink():
            symlinks.append(rel)
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_EXTS and path.name not in TEXT_NAMES:
            non_text.append(rel)
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            findings.append({"severity": "medium", "kind": "oversized-text-file", "file": rel, "line": 0, "excerpt": f"{path.stat().st_size} bytes"})
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for severity, kind, regex in PATTERNS:
                if regex.search(line):
                    findings.append({"severity": severity, "kind": kind, "file": rel, "line": lineno, "excerpt": line.strip()[:240]})
    return findings, non_text, symlinks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on", choices=("low", "medium", "high"), default="high")
    parser.add_argument("--allowlist", type=Path, help="JSON file of reviewed, accepted findings: [{file, kind, reason}]")
    args = parser.parse_args(argv)
    root = args.path.expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 1
    findings, non_text, symlinks = scan(root)
    accepted: list[dict] = []
    if args.allowlist:
        entries = json.loads(args.allowlist.read_text(encoding="utf-8"))["accepted"]
        for entry in entries:
            if not entry.get("reason"):
                print(f"ERROR: allowlist entry without reason: {entry}", file=sys.stderr)
                return 1
        keep = []
        for finding in findings:
            match = next((e for e in entries if e["file"] == finding["file"] and e["kind"] == finding["kind"]), None)
            (accepted if match else keep).append(finding)
        findings = keep
    for link in symlinks:
        findings.append({"severity": "medium", "kind": "symlink", "file": link, "line": 0, "excerpt": "symbolic link in candidate"})
    max_rank = max((RANK[f["severity"]] for f in findings), default=0)
    payload = {
        "path": str(root),
        "findings": findings,
        "non_text_files": non_text,
        "accepted": accepted,
        "result": "review" if findings or non_text else "clean-static-triage",
        "note": "static triage only; not proof of safety",
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for finding in findings:
            print(f'{finding["severity"].upper():6} {finding["kind"]:24} {finding["file"]}:{finding["line"]}  {finding["excerpt"]}')
        for item in non_text:
            print(f"REVIEW non-text-file          {item}")
        print(f"Findings: {len(findings)}; accepted by allowlist: {len(accepted)}; non-text files: {len(non_text)}; result: {payload['result']}")
    return 2 if max_rank >= RANK[args.fail_on] else 0


if __name__ == "__main__":
    raise SystemExit(main())
