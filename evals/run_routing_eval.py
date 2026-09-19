#!/usr/bin/env python3
"""Routing evaluation: deterministic selection quality over evals/routing_corpus.json.

Reports cases and checks accurately: one case = one prompt; each case contributes
several checks (selection, applicability, risk, dependencies, conflicts, profile).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import registry as registry_mod  # noqa: E402
from core.composition import check_composition  # noqa: E402
from core.routing import route  # noqa: E402

CORPUS = ROOT / "evals" / "routing_corpus.json"


def evaluate(reg, cases: list[dict]) -> dict:
    per_case = []
    totals = Counter()
    fp = fn = 0
    expected_total = 0
    for case in cases:
        result = route(case["prompt"], reg, case.get("profile"))
        auto = [s for s in result.selected if any(x.startswith("profile:") for x in result.required_by.get(s, []))]
        routed = [s for s in result.selected if s not in auto] if result.applicable else []
        expected = set(case["expected"])
        got = set(routed)
        checks = {
            "applicability": result.applicable == case.get("applicable", True),
            "exact_selection": got == expected,
            "risk": result.risk_level == case["risk"],
            "dependencies": not [p for p in check_composition(reg, result.selected) if "requires" in p],
            "conflicts": not [p for p in check_composition(reg, result.selected) if "conflicts" in p],
        }
        if "expected_profile" in case:
            checks["profile"] = result.profile == case["expected_profile"]
        if "expected_auto" in case:
            checks["auto_include"] = sorted(auto) == sorted(case["expected_auto"])
        fp += len(got - expected)
        fn += len(expected - got)
        expected_total += len(expected)
        for name, ok in checks.items():
            totals[f"{name}_pass" if ok else f"{name}_fail"] += 1
        per_case.append({
            "id": case["id"], "category": case["category"], "prompt": case["prompt"],
            "expected": sorted(expected), "routed": sorted(got), "auto_included": sorted(auto),
            "unnecessary": sorted(got - expected), "missing": sorted(expected - got),
            "risk": result.risk_level, "expected_risk": case["risk"], "profile": result.profile,
            "checks": checks, "passed": all(checks.values()),
        })
    n = len(cases)
    negatives = [c for c in per_case if c["category"] in {"negative"}]
    metrics = {
        "cases": n,
        "checks": sum(totals.values()),
        "checks_failed": sum(v for k, v in totals.items() if k.endswith("_fail")),
        "exact_match_rate": round(totals["exact_selection_pass"] / n, 4),
        "applicability_accuracy": round(totals["applicability_pass"] / n, 4),
        "risk_accuracy": round(totals["risk_pass"] / n, 4),
        "false_positive_rate": round(fp / max(1, expected_total + fp), 4),
        "false_negative_rate": round(fn / max(1, expected_total), 4),
        "unnecessary_activations": fp,
        "missed_activations": fn,
        "dependency_correctness": round(totals["dependencies_pass"] / n, 4),
        "conflict_correctness": round(totals["conflicts_pass"] / n, 4),
        "negative_case_accuracy": round(sum(c["checks"]["applicability"] and not c["routed"] for c in negatives) / max(1, len(negatives)), 4),
        "by_category": {},
    }
    for category in sorted({c["category"] for c in per_case}):
        subset = [c for c in per_case if c["category"] == category]
        metrics["by_category"][category] = {"cases": len(subset), "passed": sum(c["passed"] for c in subset)}
    return {"metrics": metrics, "cases": per_case}


def check_thresholds(metrics: dict, thresholds: dict) -> list[str]:
    errors = []
    if metrics["exact_match_rate"] < thresholds["min_exact_match_rate"]:
        errors.append(f"exact match rate {metrics['exact_match_rate']:.1%} < {thresholds['min_exact_match_rate']:.1%}")
    if metrics["false_positive_rate"] > thresholds["max_false_positive_rate"]:
        errors.append(f"false positive rate {metrics['false_positive_rate']:.1%} > {thresholds['max_false_positive_rate']:.1%}")
    if metrics["false_negative_rate"] > thresholds["max_false_negative_rate"]:
        errors.append(f"false negative rate {metrics['false_negative_rate']:.1%} > {thresholds['max_false_negative_rate']:.1%}")
    if metrics["risk_accuracy"] < thresholds["min_risk_accuracy"]:
        errors.append(f"risk accuracy {metrics['risk_accuracy']:.1%} < {thresholds['min_risk_accuracy']:.1%}")
    if metrics["negative_case_accuracy"] < thresholds["min_negative_case_accuracy"]:
        errors.append(f"negative case accuracy {metrics['negative_case_accuracy']:.1%} < {thresholds['min_negative_case_accuracy']:.1%}")
    if metrics["dependency_correctness"] < 1.0 or metrics["conflict_correctness"] < 1.0:
        errors.append("dependency or conflict correctness below 100%")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true", help="enforce thresholds from config/budgets.json")
    parser.add_argument("--verbose", action="store_true", help="print every failing case")
    args = parser.parse_args(argv)
    reg = registry_mod.load()
    if reg.errors:
        print("registry errors:", *reg.errors, sep="\n- ", file=sys.stderr)
        return 1
    cases = json.loads(CORPUS.read_text(encoding="utf-8"))["cases"]
    report = evaluate(reg, cases)
    metrics = report["metrics"]
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"routing eval: {metrics['cases']} cases, {metrics['checks']} checks, {metrics['checks_failed']} failed")
        for key in ("exact_match_rate", "applicability_accuracy", "risk_accuracy", "false_positive_rate", "false_negative_rate",
                    "unnecessary_activations", "missed_activations", "dependency_correctness", "conflict_correctness", "negative_case_accuracy"):
            print(f"  {key:<26} {metrics[key]}")
        for category, stats in metrics["by_category"].items():
            print(f"  {category:<14} {stats['passed']}/{stats['cases']} cases passed")
        if args.verbose:
            for case in report["cases"]:
                if not case["passed"]:
                    print(f"  FAIL {case['id']}: routed={case['routed']} expected={case['expected']} risk={case['risk']}/{case['expected_risk']}")
    if args.check:
        errors = check_thresholds(metrics, reg.budgets["routing_eval_thresholds"])
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("routing eval thresholds: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
