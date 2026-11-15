import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from record_semantic_run import build_record, load_case_for_scoring


class RecordSemanticRunTests(unittest.TestCase):
    def test_builds_oracle_free_scored_run_record(self):
        case = {
            "case_id": "tc-dev-001",
            "metadata": {"design_stage": "high_level", "expected_output": "finding"},
            "expected": {
                "must_detect": [{"type": "IDEMPOTENCY_GAP"}],
                "must_not_detect": [],
                "allowed_verdicts": ["BLOCKED"],
                "expected_requirement_gap_count": 0,
                "expected_evidence_gap_count": 0,
                "expected_open_decision_count": 0,
            },
        }
        report = {
            "verdict": "BLOCKED",
            "findings": [{"id": "F-001", "type": "IDEMPOTENCY_GAP"}],
            "requirement_gaps": [],
            "evidence_gaps": [],
            "open_decisions": [],
        }

        record = build_record(report, case, "run-03", "abc123")

        self.assertEqual("tc-dev-001", record["case_id"])
        self.assertEqual("run-03", record["run_id"])
        self.assertEqual("abc123", record["baseline_sha"])
        self.assertEqual(["F-001"], record["finding_ids"])
        self.assertEqual(["IDEMPOTENCY_GAP"], record["finding_types"])
        self.assertFalse(record["clean_case"])
        self.assertEqual(1, record["score"]["required_detected"])
        self.assertNotIn("expected", record)
        self.assertNotIn("must_detect", str(record))

    def test_marks_pass_case_as_clean(self):
        case = {
            "case_id": "tc-dev-clean",
            "metadata": {"expected_output": "pass"},
            "expected": {
                "must_detect": [], "must_not_detect": [],
                "allowed_verdicts": ["PASS"],
                "expected_requirement_gap_count": 0,
                "expected_evidence_gap_count": 0,
                "expected_open_decision_count": 0,
            },
        }
        report = {
            "verdict": "PASS", "findings": [], "requirement_gaps": [],
            "evidence_gaps": [], "open_decisions": [],
        }
        record = build_record(report, case, "run-01", "abc123")
        self.assertTrue(record["clean_case"])
        self.assertEqual("PASS|findings=|rg=0|eg=0|od=0", record["outcome_signature"])


class ExternalOracleTests(unittest.TestCase):
    def test_loads_expected_from_separate_oracle(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            public = root / "public.json"
            oracle = root / "oracle.json"
            public.write_text(json.dumps({"cases": [{
                "case_id": "sealed-001",
                "metadata": {"expected_output": "finding"},
                "input": "hidden answer is elsewhere",
                "context": {},
            }]}), encoding="utf-8")
            oracle.write_text(json.dumps({"cases": [{
                "case_id": "sealed-001",
                "expected": {
                    "must_detect": [{"type": "CONCURRENCY_GAP"}],
                    "must_not_detect": [],
                    "allowed_verdicts": ["BLOCKED"],
                    "expected_requirement_gap_count": 0,
                    "expected_evidence_gap_count": 0,
                    "expected_open_decision_count": 0,
                }
            }]}), encoding="utf-8")

            case = load_case_for_scoring(public, "sealed-001", oracle)

            self.assertEqual("sealed-001", case["case_id"])
            self.assertEqual("finding", case["metadata"]["expected_output"])
            self.assertEqual("CONCURRENCY_GAP", case["expected"]["must_detect"][0]["type"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
