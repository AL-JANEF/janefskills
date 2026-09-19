from __future__ import annotations

import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

from tests.helpers import ROOT, registry_mod
from core import CONTRACT_PATH, ENTRY_SKILL
from core import context as context_mod

PY = sys.executable


def run(*argv: str, env: dict | None = None) -> subprocess.CompletedProcess:
    import os
    return subprocess.run([PY, *argv], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          env={**os.environ, "PYTHONUTF8": "1", **(env or {})})


class ForgeCliTests(unittest.TestCase):
    def test_validate_passes(self) -> None:
        proc = run("scripts/forge.py", "validate")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS", proc.stdout)

    def test_list_json_contains_every_capability(self) -> None:
        proc = run("scripts/forge.py", "list", "--json")
        rows = json.loads(proc.stdout)
        self.assertEqual({r["id"] for r in rows}, set(registry_mod.load().capabilities))

    def test_find_and_explain_agree_and_are_deterministic(self) -> None:
        task = "Add a database migration that introduces a unique constraint on users.email."
        find = run("scripts/forge.py", "find", task, "--json")
        explain = run("scripts/forge.py", "explain", task, "--json")
        self.assertEqual(json.loads(find.stdout)["selected"], json.loads(explain.stdout)["selected"])
        self.assertEqual(run("scripts/forge.py", "find", task, "--json").stdout, find.stdout)
        payload = json.loads(explain.stdout)
        self.assertIn("verification", payload)
        self.assertIn("context", payload)
        self.assertEqual(payload["profile"], "high-assurance")

    def test_find_negative_task_reports_not_applicable(self) -> None:
        proc = run("scripts/forge.py", "find", "Write a poem about autumn.")
        self.assertIn("not applicable", proc.stdout)

    def test_context_reports_components_and_skipped(self) -> None:
        proc = run("scripts/forge.py", "context", "--skills", "api-contracts", "auth-hardening", "--json")
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["selected"], ["api-contracts", "auth-hardening"])
        self.assertGreater(payload["skipped_tokens"], 0)
        self.assertEqual(payload["total_estimated_tokens"], payload["core_tokens"] + payload["selected_skill_tokens"])
        self.assertIn("not measured provider billing", " ".join(payload["notes"]))

    def test_context_rejects_invalid_composition(self) -> None:
        proc = run("scripts/forge.py", "context", "--skills", "frontend-design-quality")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("requires accessibility-quality", proc.stderr)

    def test_check_composition_command(self) -> None:
        self.assertEqual(run("scripts/forge.py", "check", "api-contracts", "database-integrity").returncode, 0)
        self.assertNotEqual(run("scripts/forge.py", "check", "frontend-design-quality").returncode, 0)

    def test_sync_detects_drift(self) -> None:
        skill = ROOT / "skills" / "core" / "forge" / "SKILL.md"
        original = skill.read_text(encoding="utf-8")
        try:
            skill.write_text(original.replace("<!-- FORGE_CONTRACT_END -->", "drift\n<!-- FORGE_CONTRACT_END -->"), encoding="utf-8")
            proc = run("scripts/forge.py", "validate")
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("contract out of sync", proc.stdout)
            run("scripts/forge.py", "sync")
            self.assertEqual(skill.read_text(encoding="utf-8"), original)
        finally:
            skill.write_text(original, encoding="utf-8")


class ContextBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reg = registry_mod.load()

    def test_core_and_metadata_within_budgets(self) -> None:
        budgets = self.reg.budgets
        self.assertLessEqual(context_mod.estimate_text(CONTRACT_PATH.read_text()), budgets["core_contract_max_tokens"])
        self.assertLessEqual(context_mod.skill_body_tokens(self.reg, ENTRY_SKILL), budgets["entry_skill_max_tokens"])
        self.assertLessEqual(context_mod.metadata_tokens(self.reg), budgets["always_loaded_metadata_max_tokens"])

    def test_every_route_is_smaller_than_eager_load(self) -> None:
        eager = context_mod.eager_total(self.reg)
        for ids in (["documentation-integrity"], ["api-contracts", "database-integrity", "auth-hardening", "testing-verification"]):
            rep = context_mod.report(self.reg, ids)
            self.assertLess(rep.total_with_references_tokens, eager)
            self.assertGreater(rep.estimated_savings, 0.5)

    def test_benchmark_gates_pass(self) -> None:
        proc = run("benchmarks/context_benchmark.py", "--check")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class ProfileTests(unittest.TestCase):
    def test_profiles_are_ordered_by_strictness(self) -> None:
        reg = registry_mod.load()
        lean, std, high = reg.profiles["lean"], reg.profiles["standard"], reg.profiles["high-assurance"]
        self.assertLess(lean["max_skills"], std["max_skills"])
        self.assertLessEqual(std["max_skills"], high["max_skills"])
        self.assertEqual(lean["delegation"], "single-agent")
        self.assertEqual(high["independent_review"], "always")
        self.assertTrue(std["auto_escalate"])
        self.assertFalse(lean["auto_escalate"])
        self.assertIn("testing-verification", lean["auto_include"]["high"])


class EvalRunnerTests(unittest.TestCase):
    def test_eval_reports_cases_and_checks_separately(self) -> None:
        proc = run("evals/run_routing_eval.py", "--json")
        report = json.loads(proc.stdout)
        metrics = report["metrics"]
        self.assertEqual(metrics["cases"], len(report["cases"]))
        self.assertGreater(metrics["checks"], metrics["cases"])
        self.assertGreaterEqual(metrics["cases"], 100)
        self.assertEqual(set(metrics["by_category"]), {"obvious", "single", "multi-domain", "ambiguous", "negative", "adversarial", "high-risk", "profile"})

    def test_eval_thresholds_pass(self) -> None:
        self.assertEqual(run("evals/run_routing_eval.py", "--check").returncode, 0)


class AuditSkillTests(unittest.TestCase):
    def test_risky_fixture_fails_and_safe_fixture_passes(self) -> None:
        self.assertEqual(run("scripts/audit_skill.py", str(ROOT / "tests/fixtures/risky-skill"), "--fail-on", "high").returncode, 2)
        self.assertEqual(run("scripts/audit_skill.py", str(ROOT / "tests/fixtures/safe-skill"), "--fail-on", "high").returncode, 0)

    def test_allowlist_requires_reason_and_only_accepts_named_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            allow = Path(tmp) / "allow.json"
            allow.write_text(json.dumps({"accepted": [{"file": "SKILL.md", "kind": "credential-path"}]}))
            self.assertEqual(run("scripts/audit_skill.py", str(ROOT / "tests/fixtures/risky-skill"), "--allowlist", str(allow)).returncode, 1)
            allow.write_text(json.dumps({"accepted": [{"file": "SKILL.md", "kind": "credential-path", "reason": "test"}]}))
            proc = run("scripts/audit_skill.py", str(ROOT / "tests/fixtures/risky-skill"), "--allowlist", str(allow), "--json")
            payload = json.loads(proc.stdout)
            self.assertEqual(len(payload["accepted"]), 1)
            self.assertTrue(any(f["kind"] == "remote-pipe-to-shell" for f in payload["findings"]))

    def test_own_skills_pass_with_reviewed_allowlist(self) -> None:
        proc = run("scripts/audit_skill.py", "skills", "--fail-on", "medium", "--allowlist", "config/audit-allowlist.json")
        self.assertEqual(proc.returncode, 0, proc.stdout)


class PackageTests(unittest.TestCase):
    def test_release_archives_are_reproducible_and_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a", Path(tmp) / "b"
            env = {"SOURCE_DATE_EPOCH": "1700000000"}
            self.assertEqual(run("scripts/package_release.py", "--out", str(a), env=env).returncode, 0)
            self.assertEqual(run("scripts/package_release.py", "--out", str(b), env=env).returncode, 0)
            self.assertEqual((a / "SHA256SUMS").read_bytes(), (b / "SHA256SUMS").read_bytes())
            with tarfile.open(a / "janef-forge-2.0.0.tar.gz") as tar:
                names = set(tar.getnames())
            with zipfile.ZipFile(a / "janef-forge-2.0.0.zip") as archive:
                zip_names = set(archive.namelist())
            self.assertEqual(names, zip_names)
            self.assertIn("janef-forge-2.0.0/skills/core/forge/SKILL.md", names)
            self.assertIn("janef-forge-2.0.0/NOTICE.md", names)
            self.assertFalse(any("__pycache__" in n or ".git/" in n for n in names))
            evidence = json.loads((a / "release-evidence.json").read_text())
            self.assertEqual(evidence["version"], "2.0.0")
            self.assertFalse(evidence["published"])


if __name__ == "__main__":
    unittest.main()
