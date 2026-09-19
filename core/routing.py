"""Deterministic task router: classify, estimate risk, select the minimum sufficient skills."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from typing import Any

from core import CONFIG_DIR, ENTRY_SKILL
from core.composition import compose
from core.registry import RISK_ORDER, Registry

DEFAULT_PROFILE = "standard"
RISK_LEVELS = ("low", "medium", "high", "critical")


@dataclass
class RouteResult:
    prompt: str
    applicable: bool
    requested_profile: str
    profile: str
    risk_level: str
    risk_signals: list[str]
    selected: list[str]
    scores: dict[str, int]
    required_by: dict[str, list[str]]
    rejected: list[dict[str, str]]
    explanation: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "applicable": self.applicable,
            "requested_profile": self.requested_profile,
            "profile": self.profile,
            "risk_level": self.risk_level,
            "risk_signals": self.risk_signals,
            "selected": self.selected,
            "scores": self.scores,
            "required_by": self.required_by,
            "rejected": self.rejected,
            "explanation": self.explanation,
        }


def load_routing_config() -> dict[str, Any]:
    return json.loads((CONFIG_DIR / "routing.json").read_text(encoding="utf-8"))


TOKEN = re.compile(r"\.?[a-z0-9_+]+(?:[./][a-z0-9_+]+)*")


def normalize(text: str) -> str:
    """Lowercase, treat hyphens as spaces, strip trailing punctuation from tokens."""
    return " ".join(TOKEN.findall(text.lower().replace("-", " ")))


def phrase_weight(phrase: str) -> int:
    words = len(phrase.split())
    return 2 * words - 1


def match_phrases(padded: str, phrases: list[str]) -> list[str]:
    hits = []
    for phrase in phrases:
        needle = normalize(phrase)
        if needle and f" {needle} " in padded:
            hits.append(phrase)
    return hits


def estimate_risk(padded: str, config: dict[str, Any], skill_levels: list[str]) -> tuple[str, list[str]]:
    level = "low"
    signals: list[str] = []
    for candidate in ("critical", "high", "medium"):
        hits = match_phrases(padded, config["risk_signals"].get(candidate, []))
        if hits:
            signals.extend(f"{candidate}:{hit}" for hit in hits)
            if RISK_ORDER[candidate] > RISK_ORDER[level]:
                level = candidate
    for skill_level in skill_levels:
        if RISK_ORDER[skill_level] >= RISK_ORDER["high"] and RISK_ORDER[skill_level] > RISK_ORDER[level]:
            level = skill_level
            signals.append(f"{skill_level}:capability-risk")
    return level, sorted(set(signals))


def route(prompt: str, registry: Registry, profile: str | None = None,
          config: dict[str, Any] | None = None) -> RouteResult:
    cfg = config or load_routing_config()
    requested = profile or DEFAULT_PROFILE
    if requested not in registry.profiles:
        raise ValueError(f"unknown profile: {requested}")
    padded = f" {normalize(prompt)} {normalize(prompt.replace(chr(46), chr(32)))} "
    explanation: list[str] = []

    entry = registry.capabilities[ENTRY_SKILL].manifest
    activation_hits = match_phrases(padded, entry["triggers"])
    negative_hits = match_phrases(padded, entry["negative_triggers"])
    activation_score = sum(phrase_weight(hit) for hit in activation_hits)
    negative_score = sum(phrase_weight(hit) for hit in negative_hits)

    scores: dict[str, int] = {}
    matched: dict[str, list[str]] = {}
    for cap in registry.selectable():
        positive = match_phrases(padded, cap.manifest["triggers"])
        negative = match_phrases(padded, cap.manifest["negative_triggers"])
        score = sum(phrase_weight(hit) for hit in positive) - sum(cfg.get("negative_weight", 3) * phrase_weight(hit) for hit in negative)
        if positive:
            matched[cap.id] = positive
        if score > 0:
            scores[cap.id] = score

    top = max(scores.values(), default=0)
    applicable = (activation_score > 0 or top >= 3) and not (negative_score >= activation_score and top < 3)
    if not applicable:
        explanation.append(
            f"not a software-engineering task: activation={activation_score} negative={negative_score} "
            f"(hits: {negative_hits or activation_hits or 'none'})"
        )
        return RouteResult(prompt, False, requested, requested, "low", [], [], scores, {}, [], explanation)

    fallback = cfg.get("fallback_capability")
    if not scores and fallback in registry.capabilities and match_phrases(padded, cfg.get("fallback_verbs", [])):
        scores[fallback] = 1
        matched[fallback] = ["fallback: code-change verb"]
        top = 1
    ranked = sorted(scores.items(), key=lambda item: (-item[1], -registry.capabilities[item[0]].priority, item[0]))
    cutoff = max(cfg["min_score"], math.ceil(top * cfg["relative_cutoff"]))
    candidates = [cap_id for cap_id, score in ranked if score >= cutoff]
    rejected: list[dict[str, str]] = [
        {"id": cap_id, "reason": f"score {score} below cutoff {cutoff}"}
        for cap_id, score in ranked if score < cutoff
    ]
    for cap_id in candidates:
        explanation.append(f"{cap_id}: score {scores[cap_id]} via {matched[cap_id]}")

    skill_levels = [registry.capabilities[c].risk_level for c in candidates]
    risk_level, risk_signals = estimate_risk(padded, cfg, skill_levels)
    final_profile = requested
    profile_data = registry.profiles[requested]
    if profile_data["auto_escalate"] and RISK_ORDER[risk_level] >= RISK_ORDER["high"] and requested != "high-assurance":
        final_profile = "high-assurance"
        explanation.append(f"profile escalated {requested} -> high-assurance (risk {risk_level})")
        profile_data = registry.profiles[final_profile]

    composition = compose(registry, candidates, scores, profile_data, risk_level)
    rejected.extend(composition.rejected)
    explanation.extend(composition.explanation)
    explanation.append(f"risk {risk_level}; signals {risk_signals or 'none'}")
    return RouteResult(
        prompt, True, requested, final_profile, risk_level, risk_signals,
        composition.selected, scores, composition.required_by, rejected, explanation,
    )
