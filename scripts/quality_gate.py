#!/usr/bin/env python3
"""The one canonical quality command. Runs every deterministic check required before release.

Each step records: name, status (PASS / FAIL / SKIPPED), and evidence. SKIPPED is only
used for optional external tools that are not installed; it is always reported, never
hidden. Exit code is non-zero if any required step fails.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PY = sys.executable
SECRET_SHAPES = re.compile(
    r"(-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|"
    r"sk-[A-Za-z0-9]{32,}|xox[baprs]-[A-Za-z0-9-]{20,}|AIza[0-9A-Za-z_-]{35})"
)


class Gate:
    def __init__(self, verbose: bool) -> None:
        self.steps: list[dict] = []
        self.verbose = verbose

    def run(self, name: str, argv: list[str], *, cwd: Path = ROOT, required: bool = True, env: dict | None = None) -> bool:
        start = time.time()
        proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              env={**os.environ, "PYTHONUTF8": "1", **(env or {})})
        ok = proc.returncode == 0
        output = (proc.stdout + proc.stderr).strip()
        self.record(name, "PASS" if ok else "FAIL", output, required, time.time() - start, argv)
        return ok

    def record(self, name: str, status: str, evidence: str, required: bool = True, seconds: float = 0.0, argv: list[str] | None = None) -> None:
        self.steps.append({"name": name, "status": status, "required": required, "seconds": round(seconds, 2),
                           "command": " ".join(argv) if argv else None, "evidence": evidence[-4000:]})
        marker = {"PASS": "ok  ", "FAIL": "FAIL", "SKIPPED": "skip"}[status]
        print(f"[{marker}] {name}")
        if self.verbose or status == "FAIL":
            for line in evidence.splitlines()[-25:]:
                print(f"       {line}")

    def skip(self, name: str, reason: str) -> None:
        self.record(name, "SKIPPED", reason, required=False)

    @property
    def failed(self) -> list[dict]:
        return [s for s in self.steps if s["status"] == "FAIL" and s["required"]]


def check_secret_shapes() -> tuple[bool, str]:
    hits = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", "dist", "__pycache__", ".serena"} for part in path.parts):
            continue
        if path.suffix.lower() not in {".md", ".py", ".json", ".yaml", ".yml", ".sh", ".txt", ".fragment", ".svg", ".toml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in SECRET_SHAPES.finditer(text):
            hits.append(f"{path.relative_to(ROOT)}: {match.group(0)[:12]}…")
    return not hits, "\n".join(hits) or "no secret-shaped strings"


def check_no_symlinks() -> tuple[bool, str]:
    links = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_symlink() and ".git" not in p.parts]
    return not links, "\n".join(links) or "no symlinks"


def check_install_smoke(gate: Gate) -> None:
    with tempfile.TemporaryDirectory(prefix="forge-gate-") as tmp:
        dest = Path(tmp) / "skills"
        ok = gate.run("install smoke: dry-run", [PY, "scripts/install.py", "install", "--target", "codex", "--dest", str(dest), "--dry-run"])
        ok = gate.run("install smoke: install codex", [PY, "scripts/install.py", "install", "--target", "codex", "--dest", str(dest)]) and ok
        ok = gate.run("install smoke: idempotent reinstall", [PY, "scripts/install.py", "install", "--target", "codex", "--dest", str(dest)]) and ok
        (dest / "forge" / "SKILL.md").write_text("locally edited", encoding="utf-8")
        refused = subprocess.run([PY, "scripts/install.py", "install", "--target", "codex", "--dest", str(dest), "--only", "forge"],
                                 cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env={**os.environ, "PYTHONUTF8": "1"})
        gate.record("install smoke: modified install refused without --force", "PASS" if refused.returncode != 0 else "FAIL", refused.stdout + refused.stderr)
        forced = subprocess.run([PY, "scripts/install.py", "install", "--target", "codex", "--dest", str(dest), "--only", "forge", "--force"],
                                cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env={**os.environ, "PYTHONUTF8": "1"})
        gate.record("install smoke: forced replace backs up", "PASS" if forced.returncode == 0 and "backup" in forced.stdout else "FAIL", forced.stdout + forced.stderr)
        gate.run("install smoke: doctor", [PY, "scripts/install.py", "doctor", "--target", "codex", "--dest", str(dest)])
        gate.run("install smoke: uninstall", [PY, "scripts/install.py", "uninstall", "--target", "codex", "--dest", str(dest)])
        leftovers = [p.name for p in dest.iterdir() if not p.name.endswith(tuple(f".backup.{c}" for c in "0123456789")) and ".backup." not in p.name] if dest.exists() else []
        gate.record("install smoke: clean uninstall leaves only backups", "PASS" if not leftovers else "FAIL", "\n".join(leftovers) or "clean")


def check_package(gate: Gate) -> None:
    with tempfile.TemporaryDirectory(prefix="forge-pkg-") as tmp:
        out_a, out_b = Path(tmp) / "a", Path(tmp) / "b"
        env = {"SOURCE_DATE_EPOCH": "1700000000"}
        ok = gate.run("package: build", [PY, "scripts/package_release.py", "--out", str(out_a)], env=env)
        ok = gate.run("package: rebuild", [PY, "scripts/package_release.py", "--out", str(out_b)], env=env) and ok
        if ok:
            same = (out_a / "SHA256SUMS").read_bytes() == (out_b / "SHA256SUMS").read_bytes()
            gate.record("package: reproducible (identical SHA256SUMS)", "PASS" if same else "FAIL",
                        (out_a / "SHA256SUMS").read_text() + (out_b / "SHA256SUMS").read_text())
            import tarfile
            with tarfile.open(out_a / f"janef-forge-2.0.0.tar.gz") as tar:
                names = tar.getnames()
            required = {"janef-forge-2.0.0/skills/core/forge/SKILL.md", "janef-forge-2.0.0/LICENSE", "janef-forge-2.0.0/NOTICE.md",
                        "janef-forge-2.0.0/.claude-plugin/plugin.json", "janef-forge-2.0.0/scripts/install.py"}
            missing = sorted(required - set(names))
            gate.record("package: integrity (required files present, no junk)", "PASS" if not missing and not any("__pycache__" in n for n in names) else "FAIL",
                        f"{len(names)} entries; missing={missing}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="write the full evidence report to this path")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--fast", action="store_true", help="skip package and install smoke tests")
    args = parser.parse_args(argv)
    gate = Gate(args.verbose)
    print(f"JANEF Forge quality gate (python {sys.version.split()[0]}, {sys.platform})")

    gate.run("validate: registry, schemas, packaging, budgets, links, contract sync", [PY, "scripts/forge.py", "validate"])
    gate.run("unit tests", [PY, "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-p", "test_*.py"])
    gate.run("routing evals (thresholds)", [PY, "evals/run_routing_eval.py", "--check"])
    gate.run("context regression gates", [PY, "benchmarks/context_benchmark.py", "--check"])
    gate.run("static self-scan of skill content (allowlisted)", [PY, "scripts/audit_skill.py", "skills", "--fail-on", "medium", "--allowlist", "config/audit-allowlist.json"])
    gate.run("static scan of adapters", [PY, "scripts/audit_skill.py", "adapters", "--fail-on", "medium"])
    gate.run("static scan of profiles", [PY, "scripts/audit_skill.py", "profiles", "--fail-on", "medium"])
    ok, evidence = check_secret_shapes()
    gate.record("secret-shaped strings", "PASS" if ok else "FAIL", evidence)
    ok, evidence = check_no_symlinks()
    gate.record("no symlinks in tree", "PASS" if ok else "FAIL", evidence)
    gate.run("python bytecode compile", [PY, "-m", "compileall", "-q", "core", "scripts", "tests", "evals", "benchmarks"])
    if not args.fast:
        check_install_smoke(gate)
        check_package(gate)

    for tool, argv_ in (("gitleaks", ["gitleaks", "dir", ".", "--no-banner", "--redact"]),
                        ("actionlint", ["actionlint"]),
                        ("claude", ["claude", "plugin", "validate", "."])):
        if shutil.which(tool):
            gate.run(f"optional: {tool}", argv_, required=False)
        else:
            gate.skip(f"optional: {tool}", f"{tool} not installed")

    failed = gate.failed
    optional_failed = [s for s in gate.steps if s["status"] == "FAIL" and not s["required"]]
    summary = {
        "steps": len(gate.steps),
        "passed": sum(s["status"] == "PASS" for s in gate.steps),
        "failed": len(failed),
        "optional_failed": len(optional_failed),
        "skipped": sum(s["status"] == "SKIPPED" for s in gate.steps),
        "result": "FAIL" if failed else "PASS",
        "python": sys.version.split()[0],
        "platform": sys.platform,
    }
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps({"summary": summary, "steps": gate.steps}, indent=2) + "\n", encoding="utf-8")
    print(f"quality gate: {summary['result']}  ({summary['passed']} passed, {summary['failed']} failed, "
          f"{summary['optional_failed']} optional failed, {summary['skipped']} skipped)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
