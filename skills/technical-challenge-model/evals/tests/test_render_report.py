import sys
import unittest
from pathlib import Path

TEST_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = TEST_ROOT.parent
sys.path.insert(0, str(SKILL_ROOT / 'scripts'))

from render_report import render  # noqa: E402
from test_validate_report import base_report  # noqa: E402


class RenderTests(unittest.TestCase):
    def test_report_prioritizes_verdict_findings_and_gaps(self):
        report = base_report()
        report['verdict'] = 'PASS_WITH_ACTIONS'
        report['evidence_gaps'] = [{
            'id': 'EG-001', 'claim_id': 'CLM-001', 'critical': False,
            'required_evidence': 'fault injection test'
        }]
        markdown = render(report)
        headings = [
            '## Verdict & Assurance',
            '## Technical Findings',
            '## Requirement Gaps',
            '## Evidence Gaps',
            '## Open Decisions',
            '## Requirement / Constraint Coverage',
        ]
        positions = [markdown.index(item) for item in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertIn('PASS_WITH_ACTIONS', markdown)
        self.assertIn('DOCUMENT_ONLY', markdown)


if __name__ == '__main__':
    unittest.main(verbosity=2)
