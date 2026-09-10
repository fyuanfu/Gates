#!/usr/bin/env python3
"""Run deterministic contract, verdict, renderer, and negative-path tests."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from adjudicate_review import adjudicate, atomic_write
from render_review import render
from validate_review import ContractError, load_and_validate, validate_cross_fields


SKILL_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = SKILL_ROOT / "fixtures"
BASE_PATH = FIXTURES / "pass" / "T01_review_passed.json"
CASES_PATH = FIXTURES / "expected" / "cases.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def merge_patch(target, patch):
    """Apply the object subset of JSON Merge Patch used by the fixtures."""
    if not isinstance(patch, dict):
        return copy.deepcopy(patch)
    result = copy.deepcopy(target) if isinstance(target, dict) else {}
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_patch(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_case(case: dict) -> dict:
    path = FIXTURES / case["file"]
    if path == BASE_PATH:
        return read_json(path)
    return merge_patch(read_json(BASE_PATH), read_json(path))


class ContractFixtures(unittest.TestCase):
    def test_all_declared_fixtures(self):
        cases = read_json(CASES_PATH)["cases"]
        self.assertEqual(11, len(cases))
        self.assertEqual(11, len({case["id"] for case in cases}))
        for case in cases:
            with self.subTest(case=case["id"]), tempfile.TemporaryDirectory() as temporary:
                review_path = Path(temporary) / "review.json"
                atomic_write(review_path, load_case(case))
                if "expected_error" in case:
                    with self.assertRaisesRegex(ContractError, case["expected_error"]):
                        load_and_validate(review_path, check_verdict=False)
                    continue
                review = load_and_validate(review_path, check_verdict=False)
                adjudicate(review)
                atomic_write(review_path, review)
                final = load_and_validate(review_path, check_verdict=True)
                self.assertEqual(case["expected_verdict"], final["verdict"])
                markdown = render(final)
                self.assertIn(case["markdown_contains"], markdown)
                headings = [
                    "## Verdict",
                    "## Summary",
                    "## Blocking Findings",
                    "## Non-blocking Findings",
                    "## Open Questions",
                    "## Observations",
                    "## Coverage",
                    "## Execution Issues",
                ]
                positions = [markdown.index(heading) for heading in headings]
                self.assertEqual(positions, sorted(positions))

    def test_negative_contract_paths(self):
        mutations = {
            "invalid enum": lambda item: item.update(verdict="PASS"),
            "dangling requirement": lambda item: item["review_slices"][0]["requirement_ids"].append("R-999-9999"),
            "wrong coverage": lambda item: item["coverage"]["artifacts"].update(total=7),
            "unknown field": lambda item: item.update(extra="not allowed"),
            "duplicate ID": lambda item: item["requirements"].append(copy.deepcopy(item["requirements"][0])),
        }
        for name, mutate in mutations.items():
            with self.subTest(case=name):
                review = read_json(BASE_PATH)
                mutate(review)
                with tempfile.TemporaryDirectory() as temporary:
                    path = Path(temporary) / "review.json"
                    atomic_write(path, review)
                    with self.assertRaises(ContractError):
                        load_and_validate(path, check_verdict=True)

    def test_verdict_precedence(self):
        review = load_case(read_json(CASES_PATH)["cases"][1])
        review["review_status"] = "INCOMPLETE"
        review["execution_issues"] = [{"id": "E-0001", "code": "CRITICAL_EVIDENCE_UNAVAILABLE", "message": "A required source is unavailable.", "blocking": True, "artifact_ids": ["A-001"], "requirement_ids": ["R-001-0001"]}]
        adjudicate(review)
        self.assertEqual("review_incomplete", review["verdict"])
        self.assertIn("E-0001", review["verdict_reasons"][0])

    def test_risk_pattern_contract(self):
        value = read_json(SKILL_ROOT / "references" / "risk-patterns.json")
        self.assertEqual("1.0.0", value["schema_version"])
        self.assertGreaterEqual(len(value["patterns"]), 8)
        required = {"id", "name", "applicable_slice_types", "trigger_signals", "failure_mechanism", "user_or_business_impact", "challenge_question", "tags"}
        self.assertEqual(len(value["patterns"]), len({item["id"] for item in value["patterns"]}))
        for pattern in value["patterns"]:
            self.assertEqual(required, set(pattern))

    def test_schema_declares_draft_and_closes_root(self):
        schema = read_json(SKILL_ROOT / "references" / "review.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertIs(False, schema["additionalProperties"])
        self.assertEqual("1.0.0", schema["properties"]["schema_version"]["const"])

    def test_pre_adjudication_allows_stale_verdict_only(self):
        review = load_case(read_json(CASES_PATH)["cases"][1])
        validate_cross_fields(review, check_verdict=False)
        with self.assertRaises(ContractError):
            validate_cross_fields(review, check_verdict=True)

    def test_no_requirement_input_is_machine_readable_and_incomplete(self):
        review = read_json(BASE_PATH)
        review.update(
            review_status="INCOMPLETE",
            artifacts=[],
            requirements=[],
            review_slices=[],
            execution_issues=[{"id": "E-0001", "code": "NO_REQUIREMENT_INPUT", "message": "No requirement artifact was supplied.", "blocking": True, "artifact_ids": [], "requirement_ids": []}],
            coverage={"artifacts": {"total": 0, "parsed": 0, "failed": 0}, "requirements": {"total": 0, "assigned": 0, "standalone": 0, "excluded": 0, "unassigned": 0}, "review_slices": {"total": 0, "integrity_valid": 0, "fast_scan_done": 0, "minimal_challenge_done": 0, "deep_challenge_done": 0, "deep_challenge_not_required": 0}, "critical_decision_guard_done": False, "completion_guard_done": True},
            metrics={"raw_candidate_count": 0, "qualified_candidate_count": 0, "confirmed_candidate_count": 0, "rejected_candidate_count": 0, "dropped_candidate_count": 0, "deep_challenge_trigger_count": 0, "review_slice_count": 0},
        )
        adjudicate(review)
        self.assertEqual("review_incomplete", review["verdict"])
        validate_cross_fields(review, check_verdict=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
