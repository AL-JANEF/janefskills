from __future__ import annotations

import json
import unittest

from tests.helpers import ROOT, TempRepo, registry_mod
from core.schema import SchemaError, load_schema, validate


class SchemaTests(unittest.TestCase):
    def test_all_schemas_use_only_supported_keywords(self) -> None:
        for path in (ROOT / "schemas").glob("*.json"):
            load_schema(path)

    def test_unsupported_keyword_is_rejected(self) -> None:
        with self.assertRaises(SchemaError):
            from core.schema import _assert_supported
            _assert_supported({"type": "object", "oneOf": []}, "x")

    def test_validator_catches_type_enum_pattern_and_extra_property(self) -> None:
        schema = load_schema(ROOT / "schemas" / "capability.schema.json")
        manifest = json.loads((ROOT / "skills" / "security" / "vuln-audit" / "capability.json").read_text())
        self.assertEqual(validate(manifest, schema), [])
        broken = {**manifest, "risk_level": "extreme", "id": "Bad_ID", "extra": 1}
        errors = validate(broken, schema)
        self.assertTrue(any("risk_level" in e for e in errors))
        self.assertTrue(any("does not match" in e for e in errors))
        self.assertTrue(any("unexpected property 'extra'" in e for e in errors))


class RegistryIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = TempRepo()
        self.addCleanup(self.repo.cleanup)

    def test_real_registry_is_clean(self) -> None:
        reg = registry_mod.load()
        self.assertEqual(reg.errors, [])
        self.assertIn("forge", reg.capabilities)
        self.assertEqual(set(reg.profiles), {"lean", "standard", "high-assurance"})

    def test_duplicate_id_detected(self) -> None:
        self.repo.edit("git-discipline", id="documentation-integrity")
        errors = self.repo.load().errors
        self.assertTrue(any("must equal directory name" in e for e in errors))

    def test_broken_dependency_detected(self) -> None:
        self.repo.edit("api-contracts", requires=["does-not-exist"])
        self.assertTrue(any("unknown capability 'does-not-exist'" in e for e in self.repo.load().errors))

    def test_requires_cycle_detected(self) -> None:
        self.repo.edit("api-contracts", requires=["database-integrity"])
        self.repo.edit("database-integrity", requires=["api-contracts"])
        self.assertTrue(any("requires cycle" in e for e in self.repo.load().errors))

    def test_conflict_must_be_symmetric_and_not_required(self) -> None:
        self.repo.edit("api-contracts", conflicts_with=["database-integrity"])
        errors = self.repo.load().errors
        self.assertTrue(any("both sides" in e for e in errors))
        self.repo.edit("api-contracts", requires=["database-integrity"], conflicts_with=["database-integrity"])
        self.repo.edit("database-integrity", conflicts_with=["api-contracts"])
        self.assertTrue(any("requires and conflicts" in e for e in self.repo.load().errors))

    def test_duplicate_responsibility_ownership_detected(self) -> None:
        self.repo.edit("git-discipline", responsibilities=["history-integrity", "test-selection"])
        self.assertTrue(any("owned by more than one" in e for e in self.repo.load().errors))

    def test_duplicate_trigger_detected(self) -> None:
        self.repo.edit("git-discipline", triggers=["git", "unit test"])
        self.assertTrue(any("trigger 'unit test'" in e for e in self.repo.load().errors))

    def test_malformed_manifest_reported_not_raised(self) -> None:
        self.repo.manifest("git-discipline").write_text("{not json", encoding="utf-8")
        errors = self.repo.load().errors
        self.assertTrue(any("invalid JSON" in e for e in errors))

    def test_description_drift_between_manifest_and_skill_detected(self) -> None:
        self.repo.edit("git-discipline", description="A different description that is long enough to pass the schema check.")
        self.assertTrue(any("frontmatter description" in e for e in self.repo.load().errors))

    def test_deprecated_requires_replaced_by(self) -> None:
        self.repo.edit("git-discipline", status="deprecated")
        self.assertTrue(any("replaced_by" in e for e in self.repo.load().errors))

    def test_alias_collision_and_unknown_target(self) -> None:
        aliases = self.repo.dir / "config" / "aliases.json"
        payload = json.loads(aliases.read_text())
        payload["aliases"]["git-discipline"] = "forge"
        payload["aliases"]["ghost"] = "nope"
        aliases.write_text(json.dumps(payload))
        errors = self.repo.load().errors
        self.assertTrue(any("collides" in e for e in errors))
        self.assertTrue(any("unknown capability 'nope'" in e for e in errors))

    def test_undeclared_reference_file_detected(self) -> None:
        refs = self.repo.dir / "skills" / "engineering" / "git-discipline" / "references"
        refs.mkdir()
        (refs / "extra.md").write_text("# extra\n")
        self.assertTrue(any("not declared" in e for e in self.repo.load().errors))


if __name__ == "__main__":
    unittest.main()
