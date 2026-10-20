#!/usr/bin/env python3
"""Record one semantic Skill run after the review agent has produced report.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from score_case import score_case


def _outcome_signature(report: dict) -> str:
    finding_types = sorted(item.get("type", "") for item in report.get("findings", []))
    return (
        f"{report.get('verdict')}|findings={','.join(finding_types)}"
        f"|rg={len(report.get('requirement_gaps', []))}"
        f"|eg={len(report.get('evidence_gaps', []))}"
        f"|od={len(report.get('open_decisions', []))}"
    )


def build_record(report: dict, case: dict, run_id: str, baseline_sha: str) -> dict:
    expected = case.get("expected") or {}
    metadata = case.get("metadata") or {}
    return {
        "case_id": case["case_id"],
        "run_id": run_id,
        "baseline_sha": baseline_sha,
        "design_stage": metadata.get("design_stage"),
        "expected_output_class": metadata.get("expected_output"),
        "clean_case": metadata.get("expected_output") == "pass",
        "verdict": report.get("verdict"),
        "finding_ids": [item.get("id") for item in report.get("findings", [])],
        "finding_types": [item.get("type") for item in report.get("findings", [])],
        "gap_counts": {
            "requirement": len(report.get("requirement_gaps", [])),
            "evidence": len(report.get("evidence_gaps", [])),
            "open_decision": len(report.get("open_decisions", [])),
        },
        "outcome_signature": _outcome_signature(report),
        "score": score_case(report, expected),
    }


def _find_case(path: Path, case_id: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    for case in payload.get("cases", []):
        if case.get("case_id") == case_id:
            return case
    raise ValueError(f"unknown case_id: {case_id}")


def load_case_for_scoring(catalog: Path, case_id: str, oracle: Path | None = None) -> dict:
    case = dict(_find_case(catalog, case_id))
    if oracle is not None:
        oracle_case = _find_case(oracle, case_id)
        if "expected" not in oracle_case:
            raise ValueError(f"{case_id}: oracle missing expected")
        case["expected"] = oracle_case["expected"]
    if "expected" not in case:
        raise ValueError(f"{case_id}: expected answer not available for evaluator")
    return case


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("catalog", type=Path)
    parser.add_argument("case_id")
    parser.add_argument("run_id")
    parser.add_argument("output", type=Path)
    parser.add_argument("--baseline-sha", required=True)
    parser.add_argument("--oracle", type=Path, help="Evaluator-only oracle catalog for sealed holdout scoring")
    args = parser.parse_args(argv)
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        case = load_case_for_scoring(args.catalog, args.case_id, args.oracle)
        record = build_record(report, case, args.run_id, args.baseline_sha)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "
", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(str(exc))
        return 2
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
