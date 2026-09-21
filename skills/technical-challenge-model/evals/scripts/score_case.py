#!/usr/bin/env python3
"""Score structured technical challenge output against deterministic case expectations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def score_case(report: dict, expected: dict) -> dict:
    findings = report.get("findings", [])
    finding_types = [item.get("type") for item in findings]
    required = expected.get("must_detect", [])
    forbidden = expected.get("must_not_detect", [])

    required_detected = sum(1 for item in required if item.get("type") in finding_types)
    forbidden_detected = sum(1 for item in forbidden if item in finding_types)
    expected_types = {item.get("type") for item in required}
    unexpected_ids = [item.get("id", f"finding-{index}") for index, item in enumerate(findings, start=1) if item.get("type") not in expected_types and item.get("type") not in forbidden]

    return {
        "required_total": len(required),
        "required_detected": required_detected,
        "forbidden_detected": forbidden_detected,
        "verdict_allowed": report.get("verdict") in expected.get("allowed_verdicts", []),
        "requirement_gap_count_match": len(report.get("requirement_gaps", [])) == expected.get("expected_requirement_gap_count", 0),
        "evidence_gap_count_match": len(report.get("evidence_gaps", [])) == expected.get("expected_evidence_gap_count", 0),
        "open_decision_count_match": len(report.get("open_decisions", [])) == expected.get("expected_open_decision_count", 0),
        "needs_expert_adjudication": unexpected_ids,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("expected", type=Path)
    args = parser.parse_args(argv)
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        expected = json.loads(args.expected.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    result = score_case(report, expected)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    hard_fail = (
        result["required_detected"] != result["required_total"]
        or result["forbidden_detected"] > 0
        or not result["verdict_allowed"]
        or not result["requirement_gap_count_match"]
        or not result["evidence_gap_count_match"]
        or not result["open_decision_count_match"]
    )
    return 1 if hard_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
