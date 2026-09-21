import re
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2]


class SkillStructureTests(unittest.TestCase):
    def test_skill_and_references_exist(self):
        required = [
            'SKILL.md',
            'agents/openai.yaml',
            'references/challenge-model.md',
            'references/challenge-method.md',
            'references/evidence-and-findings.md',
            'references/android-profile.md',
            'references/evaluation-guide.md',
            'references/report.schema.json',
        ]
        missing = [path for path in required if not (SKILL_ROOT / path).exists()]
        self.assertEqual([], missing)

    def test_skill_frontmatter_is_trigger_only_and_compact(self):
        text = (SKILL_ROOT / 'SKILL.md').read_text(encoding='utf-8')
        words = re.findall(r"\b[\w-]+\b", text)
        self.assertLessEqual(len(words), 650)
        self.assertIn('Use when reviewing or challenging an existing technical design', text)
        frontmatter = text.split('---', 2)[1]
        self.assertNotIn('counterexample', frontmatter.lower())
        self.assertNotIn('evidence verification', frontmatter.lower())

    def test_challenge_method_contains_design_stage_and_two_finding_paths(self):
        text = (SKILL_ROOT / 'references/challenge-method.md').read_text(encoding='utf-8')
        for token in ['architecture', 'high_level', 'detailed', 'Coverage Finding', 'Counterexample Finding']:
            self.assertIn(token, text)

    def test_claim_model_unifies_precondition(self):
        text = (SKILL_ROOT / 'references/challenge-model.md').read_text(encoding='utf-8')
        self.assertIn('Precondition is a Claim kind', text)
        self.assertNotIn('separate Precondition collection', text)

    def test_evidence_rules_cover_lifecycle_and_inferred_constraint_gate(self):
        text = (SKILL_ROOT / 'references/evidence-and-findings.md').read_text(encoding='utf-8')
        for token in ['existing', 'planned', 'modified', 'removed', 'inferred SystemConstraint', 'OpenDecision']:
            self.assertIn(token, text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
