import sys
import unittest
from pathlib import Path

TEST_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = TEST_ROOT.parent
sys.path.insert(0, str(SKILL_ROOT / 'scripts'))

from adjudicate_report import adjudicate  # noqa: E402
from test_validate_report import base_report  # noqa: E402


class AdjudicationTests(unittest.TestCase):
    def test_blocker_drives_blocked(self):
        report = base_report()
        report['findings'] = [{
            'id': 'F-001',
            'type': 'DESIGN_COVERAGE_GAP',
            'title': 'No mechanism covers no-duplicate invariant',
            'severity': 'BLOCKER',
            'linked_obligations': ['OBL-001'],
            'linked_constraints': [],
            'decision_id': 'DEC-001',
            'mechanism_ids': [],
            'claim_id': None,
            'counterexample_id': None,
            'evidence_ids': ['EV-001'],
            'impact': 'Duplicate cloud object',
            'required_action': 'Define idempotency mechanism.',
        }]
        adjudicate(report)
        self.assertEqual('BLOCKED', report['verdict'])

    def test_critical_requirement_gap_drives_needs_decision(self):
        report = base_report()
        report['requirement_gaps'] = [{
            'id': 'RG-001',
            'question': 'Should cancelled uploads resume after network recovery?',
            'blocking': True,
            'source_ref': 'SCN-001',
        }]
        adjudicate(report)
        self.assertEqual('NEEDS_DECISION', report['verdict'])

    def test_critical_evidence_gap_blocks_gate_without_becoming_finding(self):
        report = base_report()
        report['evidence_gaps'] = [{
            'id': 'EG-001',
            'claim_id': 'CLM-001',
            'critical': True,
            'required_evidence': 'fault-injection proof',
        }]
        adjudicate(report)
        self.assertEqual('BLOCKED', report['verdict'])
        self.assertEqual([], report['findings'])

    def test_evidence_gap_drives_pass_with_actions(self):
        report = base_report()
        report['evidence_gaps'] = [{
            'id': 'EG-001',
            'claim_id': 'CLM-001',
            'critical': False,
            'required_evidence': 'benchmark',
        }]
        adjudicate(report)
        self.assertEqual('PASS_WITH_ACTIONS', report['verdict'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
