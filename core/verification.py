"""Risk-based verification model shared by the router explanation, profiles, and docs."""

from __future__ import annotations

from core.registry import RISK_ORDER

VERIFICATION_MODEL: dict[str, dict[str, list[str]]] = {
    "low": {
        "required": [
            "static or structural check on edited files (lint/type/syntax as applicable)",
            "one focused test or manual observation of the changed behavior",
            "final diff inspected",
        ],
        "evidence": ["command run and its result"],
    },
    "medium": {
        "required": [
            "everything in low",
            "focused tests covering the changed behavior and one failure or boundary case",
            "neighboring tests across the affected boundary",
            "repository gates that the change can affect (build, lint, type check)",
        ],
        "evidence": ["test output with counts", "gate results"],
    },
    "high": {
        "required": [
            "everything in medium",
            "integration or contract test across the security or data boundary",
            "one denied/unauthorized path and one malformed or adversarial input tested",
            "security scan of the changed surface when tooling is available (report NOT RUN otherwise)",
            "independent defect-first review of the diff",
        ],
        "evidence": ["denied-path test output", "scanner output or explicit NOT RUN", "review findings"],
    },
    "critical": {
        "required": [
            "everything in high",
            "real database or environment verification for schema, RLS, or privilege changes",
            "mutation check: weakening the enforcing control makes a required test fail",
            "rollback or recovery path verified",
            "explicit user authorization recorded for destructive or production-impacting steps",
        ],
        "evidence": ["mutation-test result", "rollback evidence", "authorization reference"],
    },
}


def requirements(risk_level: str, floor: str = "low") -> dict[str, list[str]]:
    """Return the verification tier for the higher of ``risk_level`` and the profile floor."""
    level = risk_level if RISK_ORDER[risk_level] >= RISK_ORDER[floor] else floor
    return {"level": [level], **VERIFICATION_MODEL[level]}
