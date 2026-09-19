from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.helpers import ROOT, registry_mod
from scripts import install as installer
from scripts.install import InstallError, MARKER


class InstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reg = registry_mod.load()
        cls.all_skills = installer.choose_skills(cls.reg, [])

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="forge-install-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.dest = self.tmp / "skills"
        self.targets = (("claude", self.dest),)

    def test_installs_every_capability_with_markers_and_identical_content(self) -> None:
        records = installer.install(self.reg, self.targets, self.all_skills, force=False, upgrade=False, dry_run=False)
        self.assertEqual(len(records), len(self.reg.capabilities))
        for cap in self.reg.capabilities.values():
            installed = self.dest / cap.id
            self.assertEqual((installed / "SKILL.md").read_bytes(), (cap.path / "SKILL.md").read_bytes())
            marker = json.loads((installed / MARKER).read_text())
            self.assertEqual(marker["version"], "2.0.0")
            self.assertFalse((installed / "agents").exists())

    def test_codex_target_renders_openai_yaml_without_touching_source(self) -> None:
        installer.install(self.reg, (("codex", self.dest),), ["auth-hardening"], force=False, upgrade=False, dry_run=False)
        rendered = (self.dest / "auth-hardening" / "agents" / "openai.yaml").read_text()
        self.assertIn("$auth-hardening", rendered)
        self.assertIn("display_name", rendered)
        self.assertFalse((ROOT / "skills" / "security" / "auth-hardening" / "agents").exists())

    def test_dry_run_writes_nothing(self) -> None:
        installer.install(self.reg, self.targets, ["forge"], force=False, upgrade=False, dry_run=True)
        self.assertFalse(self.dest.exists())

    def test_reinstall_is_idempotent(self) -> None:
        installer.install(self.reg, self.targets, ["forge"], force=False, upgrade=False, dry_run=False)
        records = installer.install(self.reg, self.targets, ["forge"], force=False, upgrade=False, dry_run=False)
        self.assertEqual(records[0]["action"], "unchanged")
        self.assertEqual(list(self.dest.glob("forge.backup.*")), [])

    def test_refuses_to_overwrite_unmanaged_directory_without_force(self) -> None:
        (self.dest / "forge").mkdir(parents=True)
        (self.dest / "forge" / "SKILL.md").write_text("user content")
        with self.assertRaises(InstallError):
            installer.install(self.reg, self.targets, ["forge"], force=False, upgrade=False, dry_run=False)
        with self.assertRaises(InstallError):
            installer.install(self.reg, self.targets, ["forge"], force=False, upgrade=True, dry_run=False)
        self.assertEqual((self.dest / "forge" / "SKILL.md").read_text(), "user content")
        records = installer.install(self.reg, self.targets, ["forge"], force=True, upgrade=False, dry_run=False)
        self.assertEqual(records[0]["action"], "replace")
        self.assertEqual((records[0]["backup"] / "SKILL.md").read_text(), "user content")

    def test_upgrade_replaces_clean_managed_but_refuses_modified(self) -> None:
        installer.install(self.reg, self.targets, ["forge"], force=False, upgrade=False, dry_run=False)
        marker_path = self.dest / "forge" / MARKER
        marker = json.loads(marker_path.read_text())
        marker["version"] = "1.9.0"
        marker_path.write_text(json.dumps(marker))
        records = installer.install(self.reg, self.targets, ["forge"], force=False, upgrade=True, dry_run=False)
        self.assertEqual(records[0]["action"], "upgrade")
        self.assertIsNotNone(records[0]["backup"])
        (self.dest / "forge" / "SKILL.md").write_text("edited locally")
        with self.assertRaises(InstallError):
            installer.install(self.reg, self.targets, ["forge"], force=False, upgrade=True, dry_run=False)

    def test_rollback_restores_previous_install_on_failure(self) -> None:
        installer.install(self.reg, self.targets, ["forge"], force=False, upgrade=False, dry_run=False)
        marker = self.dest / "forge" / "local-note.txt"
        marker.write_text("original")
        real_move = shutil.move

        def fail_staged_move(source, target):
            if "janef-forge-install-" in str(source):
                raise OSError("simulated failure")
            return real_move(source, target)

        with mock.patch("scripts.install.shutil.move", side_effect=fail_staged_move):
            with self.assertRaises(InstallError):
                installer.install(self.reg, self.targets, ["forge"], force=True, upgrade=False, dry_run=False)
        self.assertEqual(marker.read_text(), "original")
        self.assertEqual(list(self.dest.glob("forge.backup.*")), [])

    def test_uninstall_removes_only_managed_content(self) -> None:
        installer.install(self.reg, self.targets, ["forge", "git-discipline"], force=False, upgrade=False, dry_run=False)
        (self.dest / "user-skill").mkdir()
        (self.dest / "user-skill" / "SKILL.md").write_text("mine")
        records = installer.uninstall(self.reg, self.targets, ["forge", "git-discipline"], force=False, dry_run=False)
        self.assertEqual({r["action"] for r in records}, {"remove"})
        self.assertTrue((self.dest / "user-skill" / "SKILL.md").exists())
        self.assertFalse((self.dest / "forge").exists())

    def test_uninstall_refuses_modified_managed_without_force_and_backs_up_with_force(self) -> None:
        installer.install(self.reg, self.targets, ["forge"], force=False, upgrade=False, dry_run=False)
        (self.dest / "forge" / "SKILL.md").write_text("edited")
        with self.assertRaises(InstallError):
            installer.uninstall(self.reg, self.targets, ["forge"], force=False, dry_run=False)
        records = installer.uninstall(self.reg, self.targets, ["forge"], force=True, dry_run=False)
        self.assertEqual(records[0]["action"], "backup-and-remove")
        self.assertEqual((records[0]["backup"] / "SKILL.md").read_text(), "edited")

    def test_uninstall_refuses_unmanaged_directory(self) -> None:
        (self.dest / "forge").mkdir(parents=True)
        (self.dest / "forge" / "SKILL.md").write_text("not ours")
        with self.assertRaises(InstallError):
            installer.uninstall(self.reg, self.targets, ["forge"], force=True, dry_run=False)

    def test_aliases_resolve_and_requires_closure_is_installed(self) -> None:
        skills = installer.choose_skills(self.reg, ["engineering-standard", "frontend-design-quality"])
        self.assertEqual(skills, ["implementation-quality", "frontend-design-quality", "accessibility-quality"])
        with self.assertRaises(InstallError):
            installer.choose_skills(self.reg, ["nonexistent"])

    def test_unsafe_destinations_rejected(self) -> None:
        with self.assertRaises(InstallError):
            installer.resolve_targets("claude", Path("relative/path"))
        with self.assertRaises(InstallError):
            installer.resolve_targets("claude", Path(Path.cwd().anchor))
        with self.assertRaises(InstallError):
            installer.resolve_targets("claude", ROOT / "skills")
        with self.assertRaises(InstallError):
            installer.resolve_targets("both", self.dest)

    @unittest.skipIf(sys.platform.startswith("win"), "symlink creation needs privileges on Windows")
    def test_symlinked_destination_rejected(self) -> None:
        real = self.tmp / "real"
        real.mkdir()
        link = self.tmp / "link"
        os.symlink(real, link)
        with self.assertRaises(InstallError):
            installer.resolve_targets("claude", link)

    def test_doctor_reports_drift_and_legacy(self) -> None:
        installer.install(self.reg, self.targets, ["forge"], force=False, upgrade=False, dry_run=False)
        self.assertEqual(installer.doctor("claude", self.reg, destination=self.dest, verbose=False), 0)
        (self.dest / "forge" / "SKILL.md").write_text("edited")
        (self.dest / "engineering-standard").mkdir()
        self.assertEqual(installer.doctor("claude", self.reg, destination=self.dest, verbose=False), 2)

    def test_policy_merge_is_idempotent_reversible_and_replaces_legacy_block(self) -> None:
        home = self.tmp / "home"
        home.mkdir()
        policy = home / "CLAUDE.md"
        policy.write_text("# mine\n\n<!-- AGENT_ENGINEERING_STACK_BEGIN -->\nold\n<!-- AGENT_ENGINEERING_STACK_END -->\n")
        with mock.patch.dict(os.environ, {"CLAUDE_CONFIG_DIR": str(home)}):
            installer.merge_policy("claude", remove=False, dry_run=False)
            text = policy.read_text()
            self.assertIn("JANEF_FORGE_BEGIN", text)
            self.assertNotIn("AGENT_ENGINEERING_STACK", text)
            self.assertTrue(text.startswith("# mine"))
            installer.merge_policy("claude", remove=False, dry_run=False)
            self.assertEqual(text, policy.read_text())
            installer.merge_policy("claude", remove=True, dry_run=False)
            self.assertEqual(policy.read_text().strip(), "# mine")


if __name__ == "__main__":
    unittest.main()
