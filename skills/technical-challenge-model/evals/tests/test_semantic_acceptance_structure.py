import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SemanticAcceptanceStructureTests(unittest.TestCase):
    def test_semantic_acceptance_docs_exist(self):
        required = [
            ROOT / "semantic" / "curator-guide.md",
            ROOT / "semantic" / "runner-contract.md",
            ROOT / "semantic" / "adjudication-template.json",
        ]
        self.assertEqual([], [str(p) for p in required if not p.is_file()])

    def test_curator_guide_requires_unseen_cases_and_hard_negatives(self):
        text = (ROOT / "semantic" / "curator-guide.md").read_text(encoding="utf-8")
        self.assertIn("independent curator", text)
        self.assertIn("hard negative", text)
        self.assertIn("oracle must stay outside", text)

    def test_runner_contract_contains_failure_taxonomy(self):
        text = (ROOT / "semantic" / "runner-contract.md").read_text(encoding="utf-8")
        for token in [
            "A_ANCHOR", "B_DECISION_EXTRACTION", "C_PRECONDITION",
            "D_COUNTEREXAMPLE", "E_EVIDENCE", "F_ADJUDICATION", "G_SCOPE"
        ]:
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
