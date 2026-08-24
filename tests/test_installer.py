from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.install import InstallError, install, load_skill_names


ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def test_installs_every_skill_without_modifying_sources(self) -> None:
        skills = load_skill_names(ROOT)
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "skills"
            completed = install(
                ROOT,
                (("claude", destination),),
                skills,
                force=False,
                dry_run=False,
            )

            self.assertEqual(len(completed), len(skills))
            for skill in skills:
                self.assertTrue((destination / skill / "SKILL.md").is_file())
                self.assertEqual(
                    (destination / skill / "SKILL.md").read_bytes(),
                    (ROOT / skill / "SKILL.md").read_bytes(),
                )

    def test_refuses_overwrite_then_preserves_backup_on_force(self) -> None:
        skill = ("janef",)
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "skills"
            targets = (("codex", destination),)
            install(ROOT, targets, skill, force=False, dry_run=False)
            marker = destination / "janef" / "local-note.txt"
            marker.write_text("preserve me", encoding="utf-8")

            with self.assertRaises(InstallError):
                install(ROOT, targets, skill, force=False, dry_run=False)

            completed = install(ROOT, targets, skill, force=True, dry_run=False)
            backup = completed[0][2]
            self.assertIsNotNone(backup)
            assert backup is not None
            self.assertEqual(
                (backup / "local-note.txt").read_text(encoding="utf-8"),
                "preserve me",
            )
            self.assertFalse((destination / "janef" / "local-note.txt").exists())

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "skills"
            result = install(
                ROOT,
                (("claude", destination),),
                ("janef",),
                force=False,
                dry_run=True,
            )
            self.assertEqual(result, [])
            self.assertFalse(destination.exists())

    def test_restores_existing_skill_when_replacement_fails(self) -> None:
        skill = ("janef",)
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "skills"
            targets = (("claude", destination),)
            install(ROOT, targets, skill, force=False, dry_run=False)
            marker = destination / "janef" / "local-note.txt"
            marker.write_text("original install", encoding="utf-8")

            real_move = shutil.move

            def fail_staged_move(source: str, target: str) -> str:
                if "janefskills-install-" in source:
                    raise OSError("simulated replacement failure")
                return real_move(source, target)

            with mock.patch("scripts.install.shutil.move", side_effect=fail_staged_move):
                with self.assertRaises(InstallError):
                    install(ROOT, targets, skill, force=True, dry_run=False)

            self.assertEqual(marker.read_text(encoding="utf-8"), "original install")
            self.assertEqual(list(destination.glob("janef.backup.*")), [])


if __name__ == "__main__":
    unittest.main()
