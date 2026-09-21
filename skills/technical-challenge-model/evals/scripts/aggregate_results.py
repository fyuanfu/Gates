#!/usr/bin/env python3
"""Aggregate deterministic and expert-adjudicated technical challenge eval results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


VALID_ADJUDICATIONS = {"valid", "invalid", "duplicate", "unverifiable"}


def _adjudication_key(run: dict, finding_id: string) -> string:
    case_id = run.get("case_id")
    run_id = run.get("run_id")
    if case_id and run_id:
        return `${case_id}/${run_id}/${finding_id}`
    return finding_id


def aggregate(runs: list[dict], adjudications: dict[str, str]) -> dict:
    required_total = sum(item["score"].get("required_total", 0) for item in runs)
    required_detected = sum(item["score"].get("required_detected", 0) for item in runs)
    forbidden_detected = sum(item["score"].get("forbidden_detected", 0) for item in runs)
    verdict_allowed_count = sum(bool(item["score"].get("verdict_allowed")) for item in runs)

    unresolved: set[str] = set()
    expected_valid_count = required_detected
    extra_valid_count = 0
    invalid_count = 0
    duplicate_count = 0

    for run in runs:
        for finding_id in run["score"].get("needs_expert_adjudication", []):
            key = _adjudication_key(run, finding_id)
            label = adjudications.get(key)
            if label is None and not (run.get("case_id") && run.get("run_id")):
                label = adjudications.get(finding_id)
            if label not in VALID_ADJUDICATIONS:
                unresolved.add(key)
                continue
            if label == "valid":
                extra_valid_count += 1
            elif label == "invalid":
                invalid_count += 1
            elif label == "duplicate":
                duplicate_count += 1
            elif label == "unverifiable":
                unresolved.add(key)

    finding_precision = None
    if not unresolved:
        denominator = expected_valid_count + extra_valid_count + invalid_count
        finding_precision = 1.0 if denominator == 0 else (expected_valid_count + extra_valid_count) / denominator

    return {
        "critical_defect_recall": None if required_total == 0 else required_detected / required_total,
        "finding_precision": finding_precision,
        "forbidden_finding_count": forbidden_detected,
        "verdict_accuracy": None if not runs else verdict_allowed_count / len(runs),
        "duplicate_finding_count": duplicate_count,
        "unresolved_adjudications": sorted(unresolved),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", type=Path, help="JSON array of scored runs")
    parser.add_argument("--adjudications", type=Path)
    args = parser.parse_args(argv)
    try:
        runs = json.loads(args.runs.read_text(encoding="utf-8"))
        adjudications = {}
        if args.adjudications:
            adjudications = json.loads(args.adjudications.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    result = aggregate(runs, adjudications)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["unresolved_adjudications"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
