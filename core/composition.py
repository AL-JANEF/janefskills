"""Explicit composition model: caps, required dependencies, auto-includes, conflict rejection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.registry import RISK_ORDER, Registry, closure


@dataclass
class Composition:
    selected: list[str]
    required_by: dict[str, list[str]]
    rejected: list[dict[str, str]] = field(default_factory=list)
    explanation: list[str] = field(default_factory=list)


def compose(registry: Registry, candidates: list[str], scores: dict[str, int],
            profile: dict[str, Any], risk_level: str) -> Composition:
    """Build the final ordered selection from ranked candidates under a profile."""
    rejected: list[dict[str, str]] = []
    explanation: list[str] = []
    cap = int(profile["max_skills"])
    seeds = candidates[:cap]
    for dropped in candidates[cap:]:
        rejected.append({"id": dropped, "reason": f"over profile cap of {cap} skills"})

    required_by: dict[str, list[str]] = {}
    selected: list[str] = []
    for seed in seeds:
        for member in closure(registry, [seed]):
            if member not in selected:
                selected.append(member)
            if member != seed:
                required_by.setdefault(member, []).append(seed)

    for level in ("low", "medium", "high", "critical"):
        if RISK_ORDER[level] > RISK_ORDER[risk_level]:
            break
        for auto in profile.get("auto_include", {}).get(level, []):
            for member in closure(registry, [auto]):
                if member not in selected:
                    selected.append(member)
                    explanation.append(f"{member}: auto-included by profile {profile['id']} at risk {level}")
                if member != auto:
                    required_by.setdefault(member, []).append(auto)
                elif member not in required_by and member not in seeds:
                    required_by.setdefault(member, []).append(f"profile:{profile['id']}")

    selected = _resolve_conflicts(registry, selected, scores, required_by, rejected)
    required_by = {k: sorted(set(v)) for k, v in required_by.items() if k in selected}
    return Composition(selected, required_by, rejected, explanation)


def _resolve_conflicts(registry: Registry, selected: list[str], scores: dict[str, int],
                       required_by: dict[str, list[str]], rejected: list[dict[str, str]]) -> list[str]:
    def strength(cap_id: str) -> tuple[int, int]:
        return (scores.get(cap_id, 0) + 100 * len(required_by.get(cap_id, [])), -selected.index(cap_id))

    kept = list(selected)
    changed = True
    while changed:
        changed = False
        for cap_id in list(kept):
            for other in registry.capabilities[cap_id].manifest.get("conflicts_with", []):
                if other in kept:
                    loser = cap_id if strength(cap_id) < strength(other) else other
                    winner = other if loser == cap_id else cap_id
                    kept.remove(loser)
                    rejected.append({"id": loser, "reason": f"conflicts with selected {winner}"})
                    changed = True
                    break
            if changed:
                break
    return kept


def check_composition(registry: Registry, ids: list[str]) -> list[str]:
    """Validate an explicit set: unknown ids, missing requires, conflicts. Returns problems."""
    problems: list[str] = []
    resolved = [registry.resolve(i) for i in ids]
    for cap_id in resolved:
        if cap_id not in registry.capabilities:
            problems.append(f"unknown capability: {cap_id}")
    known = [c for c in resolved if c in registry.capabilities]
    for cap_id in known:
        manifest = registry.capabilities[cap_id].manifest
        for need in manifest.get("requires", []):
            if need not in known:
                problems.append(f"{cap_id} requires {need}, which is not included")
        for other in manifest.get("conflicts_with", []):
            if other in known and cap_id < other:
                problems.append(f"{cap_id} conflicts with {other}")
        if registry.capabilities[cap_id].status == "deprecated":
            problems.append(f"{cap_id} is deprecated; use {manifest.get('replaced_by')}")
    return problems
