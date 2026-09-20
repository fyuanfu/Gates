import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

TEST_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = TEST_ROOT.parent
sys.path.insert(0, str(SKILL_ROOT / 'scripts'))

from validate_report import ContractError, validate_report  # noqa: E402


def base_report():
    return {
        'schema_version': '1.0.0',
        'design_stage': 'high_level',
        'verdict': 'PASS',
        'assurance_level': 'DOCUMENT_ONLY',
        'obligations': [
            {
                'id': 'OBL-001',
                'source_ref': 'SCN-001',
                'statement': 'Pending uploads resume after connectivity recovery.',
                'invariants': ['No duplicate cloud object.'],
            }
        ],
        'system_constraints': [],
        'decisions': [
            {
                'id': 'DEC-001',
                'statement': 'Use WorkManager for retry scheduling.',
                'supports': ['OBL-001'],
                'preserves': [],
            }
        ],
        'mechanisms': [
            {
                'id': 'MEC-001',
                'decision_id': 'DEC-001',
                'type': 'retry-scheduler',
                'lifecycle': 'planned',
                'statement': 'A WorkManager worker retries pending uploads.',
            }
        ],
        'claims': [
            {
                'id': 'CLM-001',
                'kind': 'precondition',
                'statement': 'Retries of one logical upload resolve to one cloud object.',
                'decision_id': 'DEC-001',
                'mechanism_ids': ['MEC-001'],
                'status': 'SUPPORTED',
            }
        ],
        'coverage': [
            {
                'anchor_type': 'obligation',
                'anchor_id': 'OBL-001',
                'decision_ids': ['DEC-001'],
                'mechanism_ids': ['MEC-001'],
                'status': 'COVERED',
            }
        ],
        'counterexamples': [],
        'evidence': [
            {
                'id': 'EV-001',
                'claim_id': 'CLM-001',
                'type': 'DESIGN_SPEC',
                'source': 'design.md#Idempotency',
                'summary': 'Design defines stable logical-upload id and server deduplication.',
                'adequacy': 'APPROPRIATE',
            }
        ],
        'findings': [],
        'requirement_gaps': [],
        'evidence_gaps': [],
        'open_decisions': [],
    }


class ValidationTests(unittest.TestCase):
    def test_valid_report_passes(self):
        self.assertEqual([], validate_report(base_report()))

    def test_finding_requires_anchor_and_existing_evidence_reference(self):
        report = base_report()
        report['verdict'] = 'BLOCKED'
        report['findings'] = [
            {
                'id': 'F-001',
                'type': 'IDEMPOTENCY_GAP',
                'title': 'Retry can duplicate cloud objects',
                'severity': 'BLOCKER',
                'linked_obligations': [],
                'linked_constraints': [],
                'decision_id': 'DEC-001',
                'mechanism_ids': ['MEC-001'],
                'claim_id': 'CLM-001',
                'counterexample_id': None,
                'evidence_ids': ['EV-999'],
                'impact': 'Duplicate cloud object',
                'required_action': 'Define end-to-end idempotency.',
            }
        ]
        errors = validate_report(report)
        self.assertIn('F-001: missing requirement/system anchor', errors)
        self.assertIn('F-001: unknown evidence id EV-999', errors)

    def test_inferred_constraint_cannot_anchor_blocker_without_verification(self):
        report = base_report()
        report['system_constraints'] = [
            {
                'id': 'CON-001',
                'statement': 'Pending task keeps origin account identity.',
                'authority': 'inferred',
                'source': 'feature-tree inference',
            }
        ]
        report['verdict'] = 'BLOCKED'
        report['findings'] = [
            {
                'id': 'F-001',
                'type': 'ARCHITECTURE_CONFORMANCE_GAP',
                'title': 'Account identity may drift',
                'severity': 'BLOCKER',
                'linked_obligations': [],
                'linked_constraints': ['CON-001'],
                'decision_id': 'DEC-001',
                'mechanism_ids': ['MEC-001'],
                'claim_id': 'CLM-001',
                'counterexample_id': None,
                'evidence_ids': ['EV-001'],
                'impact': 'Wrong account upload',
                'required_action': 'Verify the existing account invariant first.',
            }
        ]
        errors = validate_report(report)
        self.assertIn('F-001: blocker cannot rely only on inferred constraints', errors)

    def test_planned_mechanism_code_absence_is_not_encoded_as_negative_evidence(self):
        report = base_report()
        report['evidence'].append(
            {
                'id': 'EV-002',
                'claim_id': 'CLM-001',
                'type': 'CODE_SEARCH_ABSENCE',
                'source': 'repo: upload/',
                'summary': 'No idempotency key found in current code.',
                'adequacy': 'INAPPROPRIATE_FOR_PLANNED_MECHANISM',
            }
        )
        self.assertEqual([], validate_report(report))

    def test_evidence_gap_must_reference_existing_claim(self):
        report = base_report()
        report['evidence_gaps'] = [{
            'id': 'EG-001',
            'claim_id': 'CLM-999',
            'critical': True,
            'required_evidence': 'benchmark',
        }]
        errors = validate_report(report)
        self.assertIn('EG-001: unknown claim id CLM-999', errors)

    def test_cross_reference_integrity(self):
        report = base_report()
        report['mechanisms'][0]['decision_id'] = 'DEC-999'
        errors = validate_report(report)
        self.assertIn('MEC-001: unknown decision id DEC-999', errors)


if __name__ == '__main__':
    unittest.main(verbosity=2)


class SchemaAndFindingPathTests(unittest.TestCase):
    def test_load_report_rejects_unknown_root_field(self):
        from validate_report import ContractError, load_report
        report = base_report()
        report['unexpected'] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'report.json'
            path.write_text(json.dumps(report), encoding='utf-8')
            with self.assertRaises(ContractError):
                load_report(path)

    def test_coverage_finding_does_not_require_counterexample(self):
        report = base_report()
        report['verdict'] = 'BLOCKED'
        report['findings'] = [{
            'id': 'F-002',
            'type': 'DESIGN_COVERAGE_GAP',
            'path': 'coverage',
            'title': 'No mechanism covers no-duplicate invariant',
            'severity': 'BLOCKER',
            'linked_obligations': ['OBL-001'],
            'linked_constraints': [],
            'decision_id': 'DEC-001',
            'mechanism_ids': [],
            'claim_id': None,
            'counterexample_id': None,
            'evidence_ids': ['EV-001'],
            'impact': 'Duplicate cloud object remains possible.',
            'required_action': 'Add an explicit idempotency mechanism.',
        }]
        self.assertEqual([], validate_report(report))

    def test_counterexample_finding_requires_claim_and_counterexample(self):
        report = base_report()
        report['verdict'] = 'BLOCKED'
        report['findings'] = [{
            'id': 'F-003',
            'type': 'IDEMPOTENCY_GAP',
            'path': 'counterexample',
            'title': 'Retry can duplicate cloud object',
            'severity': 'BLOCKER',
            'linked_obligations': ['OBL-001'],
            'linked_constraints': [],
            'decision_id': 'DEC-001',
            'mechanism_ids': ['MEC-001'],
            'claim_id': None,
            'counterexample_id': None,
            'evidence_ids': ['EV-001'],
            'impact': 'Duplicate cloud object',
            'required_action': 'Define end-to-end idempotency.',
        }]
        errors = validate_report(report)
        self.assertIn('F-003: counterexample finding requires claim_id', errors)
        self.assertIn('F-003: counterexample finding requires counterexample_id', errors)
