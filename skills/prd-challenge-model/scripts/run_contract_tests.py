#!/usr/bin/env python3
"""Run deterministic contract, verdict, renderer, and negative-path tests."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from adjudicate_review import adjudicate, atomic_write
from evaluate_semantics import evaluate, load_expected
from render_review import render
from validate_review import (
    ContractError,
    derive_traceability_gaps,
    expected_input_fingerprint,
    load_and_validate,
    validate_cross_fields,
)


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
                    "## Behavior Coverage",
                    "## Verification Readiness",
                    "## Traceability Gaps",
                    "## Observations",
                    "## Coverage",
                    "## Execution Issues",
                ]
                positions = [markdown.index(heading) for heading in headings]
                self.assertEqual(positions, sorted(positions))

    def test_negative_contract_paths(self):
        mutations = {
            "invalid enum": lambda item: item.update(verdict="PASS"),
            "dangling requirement": lambda item: item["review_slices"][0]["requirement_bindings"].append({"requirement_id": "R-999-9999", "roles": ["DEFINES_BEHAVIOR"]}),
            "wrong coverage": lambda item: item["coverage"]["artifacts"].update(total=7),
            "unknown field": lambda item: item.update(extra="not allowed"),
            "duplicate ID": lambda item: item["requirements"].append(copy.deepcopy(item["requirements"][0])),
            "incomplete Verification": lambda item: item["review_slices"][0]["verification"].update(decision_rule=None),
            "missing Coverage dimension": lambda item: item["review_slices"][0]["behavior_coverage"].pop(),
            "invalid input fingerprint": lambda item: item["review_context"].update(input_fingerprint="0" * 64),
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

    def test_typed_link_target_and_traceability_exemption(self):
        review = read_json(BASE_PATH)
        review["review_slices"][0]["traceability_exemption"] = {
            "reason": "Behavior must not bypass traceability.",
            "requirement_ids": ["R-001-0001"],
        }
        with self.assertRaisesRegex(ContractError, "BEHAVIOR Slice cannot bypass"):
            validate_cross_fields(review)

        review = read_json(BASE_PATH)
        review["requirements"].append(
            {
                "id": "R-001-0002",
                "artifact_id": "A-001",
                "source_requirement_id": "RULE-01",
                "section": "Rules",
                "source_order": 2,
                "type": "BUSINESS_RULE",
                "title": "A rule",
                "text": "This rule applies globally.",
                "coverage_status": "ASSIGNED_TO_SLICE",
                "exclusion_reason": None,
            }
        )
        support = copy.deepcopy(review["review_slices"][0])
        support.update(
            id="S-RULE-001",
            type="BUSINESS_RULE",
            requirement_bindings=[{"requirement_id": "R-001-0002", "roles": ["DEFINES_RULE"]}],
            behavior_coverage=None,
            traceability_exemption={"reason": "Explicit global rule.", "requirement_ids": ["R-001-0002"]},
        )
        review["review_slices"].append(support)
        review["review_slices"][0]["cross_slice_links"] = [
            {"slice_id": "S-RULE-001", "relation": "SUBJECT_TO_NFR"}
        ]
        with self.assertRaisesRegex(ContractError, "relation does not match target"):
            validate_cross_fields(review)

    def test_unrun_traceability_is_valid_incomplete_with_issue(self):
        review = read_json(BASE_PATH)
        review["traceability"]["guard_done"] = False
        review["review_status"] = "INCOMPLETE"
        review["execution_issues"] = [
            {
                "id": "E-0001",
                "code": "TRACEABILITY_GUARD_NOT_RUN",
                "message": "Traceability Guard could not run.",
                "blocking": True,
                "artifact_ids": ["A-001"],
                "requirement_ids": ["R-001-0001"],
            }
        ]
        adjudicate(review)
        validate_cross_fields(review)
        self.assertEqual("review_incomplete", review["verdict"])

    def test_verdict_precedence(self):
        review = load_case(read_json(CASES_PATH)["cases"][1])
        review["review_status"] = "INCOMPLETE"
        review["execution_issues"] = [{"id": "E-0001", "code": "CRITICAL_EVIDENCE_UNAVAILABLE", "message": "A required source is unavailable.", "blocking": True, "artifact_ids": ["A-001"], "requirement_ids": ["R-001-0001"]}]
        adjudicate(review)
        self.assertEqual("review_incomplete", review["verdict"])
        self.assertIn("E-0001", review["verdict_reasons"][0])

    def test_risk_pattern_contract(self):
        required = {"id", "name", "applicable_slice_types", "trigger_signals", "failure_mechanism", "user_or_business_impact", "challenge_question", "tags"}
        for name, minimum in (("risk-patterns.json", 11), ("risk-patterns-android.json", 5)):
            value = read_json(SKILL_ROOT / "references" / name)
            self.assertEqual("2.0.0", value["schema_version"])
            self.assertGreaterEqual(len(value["patterns"]), minimum)
            self.assertEqual(len(value["patterns"]), len({item["id"] for item in value["patterns"]}))
            for pattern in value["patterns"]:
                self.assertEqual(required, set(pattern))
        android = read_json(SKILL_ROOT / "references" / "risk-patterns-android.json")
        self.assertTrue(android["activation"]["requires_explicit_platform_scope"])
        self.assertTrue(android["activation"]["requires_matching_risk_signal"])

    def test_schema_declares_draft_and_closes_root(self):
        schema = read_json(SKILL_ROOT / "references" / "review.schema.json")
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertIs(False, schema["additionalProperties"])
        self.assertEqual("2.0.0", schema["properties"]["schema_version"]["const"])

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
            traceability={"guard_done": False},
            execution_issues=[{"id": "E-0001", "code": "NO_REQUIREMENT_INPUT", "message": "No requirement artifact was supplied.", "blocking": True, "artifact_ids": [], "requirement_ids": []}],
            coverage={"artifacts": {"total": 0, "parsed": 0, "failed": 0}, "requirements": {"total": 0, "assigned": 0, "standalone": 0, "excluded": 0, "unassigned": 0}, "review_slices": {"total": 0, "integrity_valid": 0, "fast_scan_done": 0, "minimal_challenge_done": 0, "deep_challenge_done": 0, "deep_challenge_not_required": 0}, "behavior_dimensions": {"total": 0, "defined": 0, "partial": 0, "missing": 0, "not_applicable": 0}, "verification": {"total": 0, "complete": 0, "partial": 0, "missing": 0, "not_applicable": 0}, "critical_decision_guard_done": False, "completion_guard_done": True},
            metrics={"raw_candidate_count": 0, "qualified_candidate_count": 0, "confirmed_candidate_count": 0, "rejected_candidate_count": 0, "dropped_candidate_count": 0, "deep_challenge_trigger_count": 0, "review_slice_count": 0},
        )
        review["review_context"]["input_fingerprint"] = expected_input_fingerprint(review)
        adjudicate(review)
        self.assertEqual("review_incomplete", review["verdict"])
        validate_cross_fields(review, check_verdict=True)

    def test_answer_required_question_does_not_make_review_incomplete(self):
        review = load_case(read_json(CASES_PATH)["cases"][7])
        review["open_questions"] = [{"id": "Q-0001", "question": "What performance threshold applies?", "reason": "The linked Finding requires a product answer.", "requirement_ids": ["R-001-0001"], "finding_ids": ["F-0001"], "answer_required": True, "requested_from": "PRODUCT"}]
        review["summary"]["open_question_count"] = 1
        adjudicate(review)
        self.assertEqual("COMPLETED", review["review_status"])
        self.assertEqual("review_passed", review["verdict"])

    def test_answer_required_question_must_link_finding(self):
        review = read_json(BASE_PATH)
        review["open_questions"] = [{"id": "Q-0001", "question": "What result applies?", "reason": "A decision is requested.", "requirement_ids": ["R-001-0001"], "finding_ids": [], "answer_required": True, "requested_from": "PRODUCT"}]
        review["summary"]["open_question_count"] = 1
        with self.assertRaisesRegex(ContractError, "answer_required question must link"):
            validate_cross_fields(review)

    def test_traceability_gaps_are_derived_not_persisted(self):
        review = read_json(BASE_PATH)
        review["review_slices"][0]["requirement_bindings"][0]["roles"] = ["DEFINES_BEHAVIOR"]
        gaps = derive_traceability_gaps(review)
        self.assertIn({"kind": "ORPHAN_ACCEPTANCE_CRITERION", "id": "R-001-0001"}, gaps)

    def test_semantic_evaluator_accepts_clean_case(self):
        review = read_json(BASE_PATH)
        expected = load_expected(SKILL_ROOT / "evals" / "cases" / "SEM-012" / "expected.json")
        self.assertEqual([], evaluate(review, expected))

    def test_semantic_corpus_has_twelve_complete_cases(self):
        cases = sorted((SKILL_ROOT / "evals" / "cases").glob("SEM-*"))
        self.assertEqual(12, len(cases))
        for case in cases:
            with self.subTest(case=case.name):
                self.assertTrue((case / "input.md").is_file())
                expected = load_expected(case / "expected.json")
                self.assertEqual(case.name, expected["case_id"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
