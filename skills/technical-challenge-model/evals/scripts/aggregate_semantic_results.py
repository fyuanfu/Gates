#!/usr/bin/env python3
"""Aggregate semantic evaluation runs, expert adjudication, and stability metrics."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

VALID_LABELS = {"valid", "invalid", "duplicate", "unverifiable"}
VALID_FAILURE_CLASSES = {
    "A_ANCHOR",
    "B_DECISION_EXTRACTION",
    "C_PRECONDITION",
    "D_COUNTEREXAMPLE",
    "E_EVIDENCE",
    "F_ADJUDICATION",
    "G_SCOPE",
}


def _key(run: dict, finding_id: str) -> str:
    return f"{run['case_id']}/{run['run_id']}/{finding_id}"


def _normalize_adjudication(value):
    if isinstance(value, str):
        return {"label": value, "scope_expansion": False, "failure_class": None}
    if isinstance(value, dict):
        return {
            "label": value.get("label"),
            "scope_expansion": bool(value.get("scope_expansion", False)),
            "failure_class": value.get("failure_class"),
        }
    return {"label": None, "scope_expansion": False, "failure_class": None}


def _case_stability(runs: list[dict]) -> tuple[dict[str, float], float | None]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for run in runs:
        grouped[run["case_id"]].append(run.get("outcome_signature", ""))
    result = {}
    for case_id, signatures in grouped.items():
        counts = Counter(signatures)
        result[case_id] = max(counts.values()) / len(signatures)
    overall = None if not result else sum(result.values()) / len(result)
    return result, overall


def aggregate_semantic(runs: list[dict], adjudications: dict[str, object]) -> dict:
    required_total = sum(run["score"].get("required_total", 0) for run in runs)
    required_detected = sum(run["score"].get("required_detected", 0) for run in runs)

    unresolved: set[str] = set()
    known_valid = required_detected
    extra_valid = 0
    invalid = 0
    scope_expansion_count = 0
    failure_classes: Counter[str] = Counter()
    clean_runs_with_invalid: set[tuple[str, str]] = set()
    clean_ground_truth_disputes: set[str] = set()

    for run in runs:
        for finding_id in run["score"].get("needs_expert_adjudication", []):
            key = _key(run, finding_id)
            item = _normalize_adjudication(adjudications.get(key))
            label = item["label"]
            if label not in VALID_LABELS or label == "unverifiable":
                unresolved.add(key)
                continue
            if item["scope_expansion"]:
                scope_expansion_count += 1
            failure_class = item["failure_class"]
            if failure_class:
                if failure_class not in VALID_FAILURE_CLASSES:
                    unresolved.add(key)
                    continue
                failure_classes[failure_class] += 1
            if label == "valid":
                extra_valid += 1
                if run.get("clean_case"):
                    clean_ground_truth_disputes.add(key)
            elif label == "invalid":
                invalid += 1
                if run.get("clean_case"):
                    clean_runs_with_invalid.add((run["case_id"], run["run_id"]))

    finding_precision = None
    clean_fp_rate = None
    if not unresolved:
        denominator = known_valid + extra_valid + invalid
        finding_precision = 1.0 if denominator == 0 else (known_valid + extra_valid) / denominator
        clean_runs = [run for run in runs if run.get("clean_case")]
        clean_fp_rate = None if not clean_runs else len(clean_runs_with_invalid) / len(clean_runs)

    case_stability, inter_run_stability = _case_stability(runs)

    return {
        "critical_defect_recall": None if required_total == 0 else required_detected / required_total,
        "finding_precision": finding_precision,
        "clean_case_false_positive_rate": clean_fp_rate,
        "inter_run_stability": inter_run_stability,
        "case_stability": case_stability,
        "scope_expansion_finding_count": scope_expansion_count,
        "failure_class_counts": dict(sorted(failure_classes.items())),
        "clean_case_ground_truth_disputes": sorted(clean_ground_truth_disputes),
        "unresolved_adjudications": sorted(unresolved),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path, help="JSON array of semantic run records")
    parser.add_argument("--adjudications", type=Path)
    args = parser.parse_args(argv)
    try:
        runs = json.loads(args.runs.read_text(encoding="utf-8"))
        adjudications = {}
        if args.adjudications:
            adjudications = json.loads(args.adjudications.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(str(exc))
        return 2
    result = aggregate_semantic(runs, adjudications)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["unresolved_adjudications"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
