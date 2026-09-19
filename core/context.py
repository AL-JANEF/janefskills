"""Estimated structural context cost. Character-based; never a provider billing claim."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core import CONTRACT_PATH, ENTRY_SKILL
from core.registry import Registry

METHOD = "ceil(UTF-8 characters / 4)"


def estimate_text(text: str) -> int:
    return math.ceil(len(text) / 4)


def estimate_paths(paths: list[Path]) -> int:
    return sum(estimate_text(p.read_text(encoding="utf-8")) for p in paths)


@dataclass
class ContextReport:
    method: str
    core_tokens: int
    contract_tokens: int
    metadata_tokens: int
    selected: list[str]
    selected_skill_tokens: int
    selected_reference_tokens: int
    per_skill: dict[str, dict[str, int]]
    skipped: list[str]
    skipped_tokens: int
    eager_total_tokens: int
    total_estimated_tokens: int = 0
    total_with_references_tokens: int = 0
    estimated_savings: float = 0.0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def skill_body_tokens(registry: Registry, cap_id: str) -> int:
    return estimate_text((registry.capabilities[cap_id].path / "SKILL.md").read_text(encoding="utf-8"))


def reference_tokens(registry: Registry, cap_id: str) -> int:
    return estimate_paths(registry.capabilities[cap_id].reference_paths())


def metadata_tokens(registry: Registry) -> int:
    """Always-loaded surface: what a host lists for every capability (name + description)."""
    return sum(
        estimate_text(f"{cap.id}: {cap.manifest['description']}")
        for cap in registry.capabilities.values()
    )


def eager_total(registry: Registry) -> int:
    total = skill_body_tokens(registry, ENTRY_SKILL)
    for cap in registry.selectable():
        total += skill_body_tokens(registry, cap.id) + reference_tokens(registry, cap.id)
    return total


def report(registry: Registry, selected: list[str]) -> ContextReport:
    core = skill_body_tokens(registry, ENTRY_SKILL)
    contract = estimate_text(CONTRACT_PATH.read_text(encoding="utf-8"))
    per_skill: dict[str, dict[str, int]] = {}
    skill_total = 0
    ref_total = 0
    for cap_id in selected:
        body = skill_body_tokens(registry, cap_id)
        refs = reference_tokens(registry, cap_id)
        per_skill[cap_id] = {"skill": body, "references": refs}
        skill_total += body
        ref_total += refs
    skipped = [cap.id for cap in registry.selectable() if cap.id not in selected]
    skipped_tokens = sum(skill_body_tokens(registry, c) + reference_tokens(registry, c) for c in skipped)
    eager = eager_total(registry)
    result = ContextReport(
        METHOD, core, contract, metadata_tokens(registry), list(selected), skill_total, ref_total,
        per_skill, skipped, skipped_tokens, eager,
    )
    result.total_estimated_tokens = core + skill_total
    result.total_with_references_tokens = core + skill_total + ref_total
    result.estimated_savings = round(1 - (result.total_with_references_tokens / eager), 4) if eager else 0.0
    result.notes = [
        "estimated structural context cost; not measured provider billing",
        "references are loaded on demand; total_with_references is the ceiling for the selection",
        "metadata_tokens is the always-loaded listing surface across all capabilities",
    ]
    return result
