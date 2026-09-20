import sys
import unittest
from pathlib import Path

TEST_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TEST_ROOT / 'scripts'))

from score_case import score_case  # noqa: E402


class ScoreTests(unittest.TestCase):
    def test_scores_known_findings_and_forbidden_findings(self):
        expected = {
            'must_detect': [{'type': 'IDEMPOTENCY_GAP'}],
            'must_not_detect': ['SECURITY_GAP'],
            'allowed_verdicts': ['BLOCKED'],
            'expected_requirement_gap_count': 0,
            'expected_evidence_gap_count': 0
        }
        report = {
            'verdict': 'BLOCKED',
            'findings': [{'type': 'IDEMPOTENCY_GAP'}],
            'requirement_gaps': [],
            'evidence_gaps': []
        }
        score = score_case(report, expected)
        self.assertEqual(1, score['required_detected'])
        self.assertEqual(0, score['forbidden_detected'])
        self.assertTrue(score['verdict_allowed'])

    def test_unexpected_finding_is_left_for_expert_adjudication(self):
        expected = {
            'must_detect': [], 'must_not_detect': [], 'allowed_verdicts': ['PASS_WITH_ACTIONS'],
            'expected_requirement_gap_count': 0, 'expected_evidence_gap_count': 0
        }
        report = {
            'verdict': 'PASS_WITH_ACTIONS',
            'findings': [{'id': 'F-007', 'type': 'CONCURRENCY_GAP'}],
            'requirement_gaps': [], 'evidence_gaps': []
        }
        score = score_case(report, expected)
        self.assertEqual(['F-007'], score['needs_expert_adjudication'])

    def test_scores_open_decision_count(self):
        expected = {
            'must_detect': [], 'must_not_detect': [], 'allowed_verdicts': ['NEEDS_DECISION'],
            'expected_requirement_gap_count': 0, 'expected_evidence_gap_count': 0,
            'expected_open_decision_count': 1
        }
        report = {
            'verdict': 'NEEDS_DECISION',
            'findings': [], 'requirement_gaps': [], 'evidence_gaps': [],
            'open_decisions': [{'id': 'OD-001'}]
        }
        score = score_case(report, expected)
        self.assertTrue(score['open_decision_count_match'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
