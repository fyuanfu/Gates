import sys
import unittest
from pathlib import Path

TEST_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TEST_ROOT / 'scripts'))

from aggregate_results import aggregate  # noqa: E402


class AggregateTests(unittest.TestCase):
    def test_precision_requires_expert_adjudication_for_unexpected_findings(self):
        runs = [
            {
                'score': {
                    'required_total': 1, 'required_detected': 1,
                    'forbidden_detected': 0, 'verdict_allowed': True,
                    'needs_expert_adjudication': ['F-002']
                },
                'finding_ids': ['F-001', 'F-002']
            }
        ]
        result = aggregate(runs, adjudications={})
        self.assertIsNone(result['finding_precision'])
        self.assertEqual(['F-002'], result['unresolved_adjudications'])

    def test_precision_uses_expert_labels_when_available(self):
        runs = [
            {
                'score': {
                    'required_total': 1, 'required_detected': 1,
                    'forbidden_detected': 0, 'verdict_allowed': True,
                    'needs_expert_adjudication': ['F-002']
                },
                'finding_ids': ['F-001', 'F-002']
            }
        ]
        result = aggregate(runs, adjudications={'F-002': 'invalid'})
        self.assertEqual(0.5, result['finding_precision'])
        self.assertEqual([], result['unresolved_adjudications'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
