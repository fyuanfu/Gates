import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from aggregate_semantic_results import aggregate_semantic


class AggregateSemanticResultsTests(unittest.TestCase):
    def test_computes_stability_clean_fp_scope_and_failure_classes(self):
        runs = [
            {
                "case_id": "case-a", "run_id": "run-01", "clean_case": False,
                "outcome_signature": "BLOCKED|findings=IDEMPOTENCY_GAP|rg=0|eg=0|od=0",
                "finding_ids": ["F-001"], "finding_types": ["IDEMPOTENCY_GAP"],
                "score": {"required_total": 1, "required_detected": 1, "forbidden_detected": 0, "verdict_allowed": True, "needs_expert_adjudication": []},
            },
            {
                "case_id": "case-a", "run_id": "run-02", "clean_case": False,
                "outcome_signature": "BLOCKED|findings=IDEMPOTENCY_GAP|rg=0|eg=0|od=0",
                "finding_ids": ["F-001"], "finding_types": ["IDEMPOTENCY_GAP"],
                "score": {"required_total": 1, "required_detected": 1, "forbidden_detected": 0, "verdict_allowed": True, "needs_expert_adjudication": []},
            },
            {
                "case_id": "case-a", "run_id": "run-03", "clean_case": False,
                "outcome_signature": "PASS_WITH_ACTIONS|findings=|rg=0|eg=1|od=0",
                "finding_ids": [], "finding_types": [],
                "score": {"required_total": 1, "required_detected": 0, "forbidden_detected": 0, "verdict_allowed": False, "needs_expert_adjudication": []},
            },
            {
                "case_id": "clean", "run_id": "run-01", "clean_case": True,
                "outcome_signature": "PASS_WITH_ACTIONS|findings=ARCHITECTURE_CONFORMANCE_GAP|rg=0|eg=0|od=0",
                "finding_ids": ["F-009"], "finding_types": ["ARCHITECTURE_CONFORMANCE_GAP"],
                "score": {"required_total": 0, "required_detected": 0, "forbidden_detected": 0, "verdict_allowed": False, "needs_expert_adjudication": ["F-009"]},
            },
            {
                "case_id": "clean", "run_id": "run-02", "clean_case": True,
                "outcome_signature": "PASS|findings=|rg=0|eg=0|od=0",
                "finding_ids": [], "finding_types": [],
                "score": {"required_total": 0, "required_detected": 0, "forbidden_detected": 0, "verdict_allowed": True, "needs_expert_adjudication": []},
            },
        ]
        adjudications = {
            "clean/run-01/F-009": {
                "label": "invalid",
                "scope_expansion": True,
                "failure_class": "G_SCOPE",
            }
        }

        result = aggregate_semantic(runs, adjudications)

        self.assertAlmostEqual(2/3, result["critical_defect_recall"])
        self.assertAlmostEqual(2/3, result["case_stability"]["case-a"])
        self.assertAlmostEqual(1/2, result["clean_case_false_positive_rate"])
        self.assertEqual(1, result["scope_expansion_finding_count"])
        self.assertEqual({"G_SCOPE": 1}, result["failure_class_counts"])
        self.assertEqual([], result["unresolved_adjudications"])

    def test_precision_is_undefined_until_unexpected_findings_are_adjudicated(self):
        runs = [{
            "case_id": "clean", "run_id": "run-01", "clean_case": True,
            "outcome_signature": "PASS_WITH_ACTIONS|findings=STATE_MODEL_GAP|rg=0|eg=0|od=0",
            "finding_ids": ["F-002"], "finding_types": ["STATE_MODEL_GAP"],
            "score": {"required_total": 0, "required_detected": 0, "forbidden_detected": 0, "verdict_allowed": False, "needs_expert_adjudication": ["F-002"]},
        }]
        result = aggregate_semantic(runs, {})
        self.assertIsNone(result["finding_precision"])
        self.assertIsNone(result["clean_case_false_positive_rate"])
        self.assertEqual(["clean/run-01/F-002"], result["unresolved_adjudications"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
