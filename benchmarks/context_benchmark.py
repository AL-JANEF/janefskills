#!/usr/bin/env python3
"""Estimated structural context cost across the routing corpus, with regression gates.

Character-based estimate (ceil(chars/4)). Not a provider billing measurement.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import CONTRACT_PATH, ENTRY_SKILL, registry as registry_mod  # noqa: E402
from core import context as context_mod  # noqa: E402
from core.routing import route  # noqa: E402

CORPUS = ROOT / "evals" / "routing_corpus.json"


def build_report(reg) -> dict:
    cases = json.loads(CORPUS.read_text(encoding="utf-8"))["cases"]
    routes = []
    per_profile: dict[str, list[int]] = {"lean": [], "standard": [], "high-assurance": []}
    for case in cases:
        result = route(case["prompt"], reg, case.get("profile"))
        if not result.applicable:
            continue
        rep = context_mod.report(reg, result.selected)
        per_profile[result.profile].append(rep.total_estimated_tokens)
        routes.append({
            "id": case["id"], "profile": result.profile, "selected": result.selected,
            "estimated_tokens": rep.total_estimated_tokens,
            "with_references": rep.total_with_references_tokens,
            "estimated_savings": rep.estimated_savings,
        })
    # worst case per profile: the largest routed selection observed
    return {
        "method": context_mod.METHOD,
        "contract_tokens": context_mod.estimate_text(CONTRACT_PATH.read_text(encoding="utf-8")),
        "core_tokens": context_mod.skill_body_tokens(reg, ENTRY_SKILL),
        "always_loaded_metadata_tokens": context_mod.metadata_tokens(reg),
        "eager_total_tokens": context_mod.eager_total(reg),
        "median_route_tokens": statistics.median(r["estimated_tokens"] for r in routes),
        "median_route_savings": round(statistics.median(r["estimated_savings"] for r in routes), 4),
        "max_route_tokens_by_profile": {k: (max(v) if v else 0) for k, v in per_profile.items()},
        "routes": routes,
        "budgets": reg.budgets,
        "note": "estimated structural context cost; not measured provider billing",
    }


def check_report(report: dict) -> list[str]:
    budgets = report["budgets"]
    errors = []
    if report["contract_tokens"] > budgets["core_contract_max_tokens"]:
        errors.append(f"contract {report['contract_tokens']} > {budgets['core_contract_max_tokens']}")
    if report["core_tokens"] > budgets["entry_skill_max_tokens"]:
        errors.append(f"entry skill {report['core_tokens']} > {budgets['entry_skill_max_tokens']}")
    if report["always_loaded_metadata_tokens"] > budgets["always_loaded_metadata_max_tokens"]:
        errors.append(f"metadata {report['always_loaded_metadata_tokens']} > {budgets['always_loaded_metadata_max_tokens']}")
    if report["median_route_savings"] < budgets["minimum_median_route_savings"]:
        errors.append(f"median route savings {report['median_route_savings']:.1%} < {budgets['minimum_median_route_savings']:.1%}")
    for profile, worst in report["max_route_tokens_by_profile"].items():
        limit = budgets["profile_selected_max_tokens"][profile]
        if worst > limit:
            errors.append(f"profile {profile}: worst routed selection {worst} > {limit}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    reg = registry_mod.load()
    if reg.errors:
        print("registry errors:", *reg.errors, sep="\n- ", file=sys.stderr)
        return 1
    report = build_report(reg)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("JANEF Forge context benchmark (estimated structural cost)")
        print(f"  method:                  {report['method']}")
        print(f"  contract:                {report['contract_tokens']}")
        print(f"  core (entry skill):      {report['core_tokens']}")
        print(f"  always-loaded metadata:  {report['always_loaded_metadata_tokens']}")
        print(f"  eager full load:         {report['eager_total_tokens']}")
        print(f"  median routed selection: {report['median_route_tokens']}  (savings {report['median_route_savings']:.1%})")
        for profile, worst in report["max_route_tokens_by_profile"].items():
            print(f"  worst {profile:<15} {worst}  (budget {report['budgets']['profile_selected_max_tokens'][profile]})")
    if args.check:
        errors = check_report(report)
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("context regression gates: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
