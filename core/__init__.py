"""JANEF Forge core: capability registry, routing, composition, context accounting.

Standard library only. Import via ``sys.path`` insertion of the repository root.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
PROFILES_DIR = ROOT / "profiles"
SCHEMAS_DIR = ROOT / "schemas"
CONTRACT_PATH = ROOT / "core" / "protocol" / "contract.md"
CONFIG_DIR = ROOT / "config"
PRODUCT = "JANEF Forge"
VERSION = "2.0.0"
ENTRY_SKILL = "forge"
