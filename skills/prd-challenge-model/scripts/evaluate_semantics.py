#!/usr/bin/env python3
"""Evaluate a canonical review against compact semantic expectations."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from validate_review import ContractError, load_and_validate


SEVERITY_RANK = {"P3": 1, "P2": 2, "P1": 3, "P0": 4}


def load_expected(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    required = {"case_id", "expected_verdict", "must_find", "must_not_find"}
    missing = required - set(value)
    if missing:
        raise ValueError(f"expectation is missing fields: {sorted(missing)}")
    return value


def source_ids(review: dict, finding: dict) -> set[str]:
    requirements = {item["id"]: item for item in review["requirements"]}
    return {
        requirements[item]["source_requirement_id"]
        for item in finding["requirement_ids"]
        if item in requirements and requirements[item]["source_requirement_id"] is not None
    }


def finding_text(finding: dict) -> str:
    return "\n".join(
        [finding["title"], finding["problem"], finding["impact"], finding["required_decision"]]
    )


def matches(review: dict, finding: dict, expectation: dict) -> bool:
    expected_source = expectation.get("source_requirement_id")
    if expected_source is not None and expected_source not in source_ids(review, finding):
        return False
    if expectation.get("defect_type") not in (None, finding["defect_type"]):
        return False
    consequence = expectation.get("consequence_type")
    if consequence and consequence not in finding["consequence_types"]:
        return False
    minimum = expectation.get("minimum_severity")
    if minimum and SEVERITY_RANK[finding["severity"]] < SEVERITY_RANK[minimum]:
        return False
    pattern = expectation.get("text_pattern")
    return pattern is None or re.search(pattern, finding_text(finding), re.IGNORECASE) is not None


def evaluate(review: dict, expected: dict) -> list[str]:
    errors: list[str] = []
    if review["verdict"] != expected["expected_verdict"]:
        errors.append(
            f"verdict: expected {expected['expected_verdict']}, got {review['verdict']}"
        )
    for index, expectation in enumerate(expected["must_find"], start=1):
        if not any(matches(review, finding, expectation) for finding in review["findings"]):
            errors.append(f"must_find[{index}] was not satisfied: {expectation}")
    for index, expectation in enumerate(expected["must_not_find"], start=1):
        found = [finding["id"] for finding in review["findings"] if matches(review, finding, expectation)]
        if found:
            errors.append(f"must_not_find[{index}] matched {found}: {expectation}")
    maximum = expected.get("maximum_finding_count")
    if maximum is not None and len(review["findings"]) > maximum:
        errors.append(f"finding count: maximum {maximum}, got {len(review['findings'])}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("review_json", type=Path)
    parser.add_argument("expected_json", type=Path)
    args = parser.parse_args()
    try:
        review = load_and_validate(args.review_json, check_verdict=True)
        expected = load_expected(args.expected_json)
        errors = evaluate(review, expected)
    except (OSError, json.JSONDecodeError, ValueError, ContractError) as error:
        print(f"SEMANTIC EVAL ERROR: {error}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {expected['case_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
