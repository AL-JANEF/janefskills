from __future__ import annotations

import json
import unittest

from tests.helpers import ROOT, TempRepo, registry_mod
from core.composition import check_composition, compose
from core.routing import normalize, route
from core.verification import requirements


class RoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reg = registry_mod.load()
        cls.cases = json.loads((ROOT / "evals" / "routing_corpus.json").read_text(encoding="utf-8"))["cases"]

    def routed(self, prompt: str, profile: str | None = None):
        result = route(prompt, self.reg, profile)
        auto = [s for s in result.selected if any(x.startswith("profile:") for x in result.required_by.get(s, []))]
        return result, [s for s in result.selected if s not in auto]

    def test_normalize_handles_punctuation_hyphens_and_dotfiles(self) -> None:
        self.assertEqual(normalize("Force-push to main."), "force push to main")
        self.assertIn(".env", normalize("print the .env file."))
        self.assertEqual(normalize("CI/CD, n+1!"), "ci/cd n+1")

    def test_routing_is_deterministic(self) -> None:
        first = route("Add a tenant-scoped API endpoint that exports billing history.", self.reg).to_dict()
        second = route("Add a tenant-scoped API endpoint that exports billing history.", self.reg).to_dict()
        self.assertEqual(first, second)

    def test_corpus_exact_selection(self) -> None:
        for case in self.cases:
            with self.subTest(case=case["id"]):
                result, routed = self.routed(case["prompt"], case.get("profile"))
                self.assertEqual(result.applicable, case.get("applicable", True))
                self.assertEqual(sorted(routed) if result.applicable else [], sorted(case["expected"]))
                self.assertEqual(result.risk_level, case["risk"])

    def test_negative_prompts_select_nothing(self) -> None:
        for prompt in ("Write a marketing email for the launch.", "Plan a birthday party.", "Write a poem about rain."):
            with self.subTest(prompt=prompt):
                result = route(prompt, self.reg)
                self.assertFalse(result.applicable)
                self.assertEqual(result.selected, [])

    def test_requires_are_pulled_in_and_attributed(self) -> None:
        result, _ = self.routed("Build the landing page hero section with our design tokens.")
        self.assertIn("accessibility-quality", result.selected)
        self.assertEqual(result.required_by["accessibility-quality"], ["frontend-design-quality"])
        result, _ = self.routed("Run a full security pass on this repository before launch.")
        self.assertIn("vuln-audit", result.selected)
        self.assertIn("variant-hunt", result.selected)

    def test_high_risk_escalates_standard_to_high_assurance_with_auto_includes(self) -> None:
        result = route("Add an index on orders.customer_id.", self.reg)
        self.assertEqual(result.requested_profile, "standard")
        self.assertEqual(result.profile, "high-assurance")
        self.assertIn("testing-verification", result.selected)
        self.assertIn("review-defect-first", result.selected)

    def test_lean_profile_caps_selection_and_never_escalates(self) -> None:
        result = route("Fix and verify a security auth regression in a large repo, then delegate it.", self.reg, "lean")
        self.assertEqual(result.profile, "lean")
        routed = [s for s in result.selected if not any(x.startswith("profile:") for x in result.required_by.get(s, []))]
        self.assertLessEqual(len(routed), 2)
        self.assertIn("testing-verification", result.selected)  # high risk still adds verification

    def test_critical_risk_in_high_assurance_adds_variant_hunt(self) -> None:
        result = route("Enable row level security on the tenants table and add policies for every role.", self.reg)
        self.assertEqual(result.risk_level, "critical")
        self.assertIn("variant-hunt", result.selected)

    def test_unknown_profile_rejected(self) -> None:
        with self.assertRaises(ValueError):
            route("Fix a bug", self.reg, "turbo")

    def test_verification_tiers_respect_profile_floor(self) -> None:
        self.assertEqual(requirements("low", "high")["level"], ["high"])
        self.assertEqual(requirements("critical", "low")["level"], ["critical"])
        self.assertIn("mutation check", " ".join(requirements("critical")["required"]))


class CompositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = TempRepo()
        self.addCleanup(self.repo.cleanup)
        self.reg = registry_mod.load()

    def test_tenant_api_composition_is_valid(self) -> None:
        ids = ["api-contracts", "database-integrity", "auth-hardening", "testing-verification"]
        self.assertEqual(check_composition(self.reg, ids), [])

    def test_ui_composition_does_not_pull_database_or_security(self) -> None:
        result = route("Redesign the settings page: new layout with our design system, clearer navigation, and full keyboard support.", self.reg)
        self.assertEqual(set(result.selected), {"frontend-design-quality", "ui-ux-quality", "accessibility-quality"})

    def test_missing_dependency_reported(self) -> None:
        problems = check_composition(self.reg, ["frontend-design-quality"])
        self.assertTrue(any("requires accessibility-quality" in p for p in problems))

    def test_legacy_alias_resolves_to_replacement(self) -> None:
        self.assertEqual(self.reg.resolve("janef"), "forge")
        self.assertEqual(self.reg.resolve("engineering-standard"), "implementation-quality")
        self.assertEqual(check_composition(self.reg, ["janef", "engineering-standard"]), [])

    def test_conflict_resolution_drops_weaker_side(self) -> None:
        self.repo.edit("git-discipline", conflicts_with=["documentation-integrity"])
        self.repo.edit("documentation-integrity", conflicts_with=["git-discipline"])
        reg = self.repo.load()
        self.assertEqual(reg.errors, [])
        comp = compose(reg, ["documentation-integrity", "git-discipline"], {"documentation-integrity": 4, "git-discipline": 1}, reg.profiles["standard"], "low")
        self.assertEqual(comp.selected, ["documentation-integrity"])
        self.assertEqual(comp.rejected[0]["id"], "git-discipline")
        self.assertTrue(check_composition(reg, ["git-discipline", "documentation-integrity"]))

    def test_profile_cap_rejects_overflow_but_keeps_requires(self) -> None:
        comp = compose(self.reg, ["frontend-design-quality", "ui-ux-quality", "api-contracts"], {}, self.reg.profiles["lean"], "low")
        self.assertEqual(comp.selected, ["frontend-design-quality", "accessibility-quality", "ui-ux-quality"])
        self.assertEqual(comp.rejected[0]["id"], "api-contracts")


if __name__ == "__main__":
    unittest.main()
