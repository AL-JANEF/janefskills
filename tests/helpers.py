"""Shared fixtures for JANEF Forge tests: temporary registries built from the real one."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import registry as registry_mod  # noqa: E402


class TempRepo:
    """Copy skills/, profiles/, config/ into a temp dir so tests can mutate manifests safely."""

    def __init__(self) -> None:
        self.dir = Path(tempfile.mkdtemp(prefix="forge-test-"))
        for name in ("skills", "profiles", "config"):
            shutil.copytree(ROOT / name, self.dir / name)

    def manifest(self, cap_id: str) -> Path:
        return next(self.dir.glob(f"skills/*/{cap_id}/capability.json"))

    def edit(self, cap_id: str, **changes) -> None:
        path = self.manifest(cap_id)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload.update(changes)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self):
        return registry_mod.load(self.dir / "skills", self.dir / "profiles", self.dir / "config")

    def cleanup(self) -> None:
        shutil.rmtree(self.dir, ignore_errors=True)
