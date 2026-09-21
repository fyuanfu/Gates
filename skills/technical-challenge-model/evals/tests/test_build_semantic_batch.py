import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_semantic_batch import build_batch


class BuildSemanticBatchTests(unittest.TestCase):
    def test_builds_isolated_repeated_sandboxes_without_oracle(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            skill = root / "skill"
            (skill / "references").mkdir(parents=True)
            (skill / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
            (skill / "references" / "challenge-model.md").write_text("# Model\n", encoding="utf-8")
            catalog = root / "cases.json"
            catalog.write_text(json.dumps({"cases": [{
                "case_id": "tc-dev-001",
                "input": "review me",
                "context": {"api.md": "contract"},
                "metadata": {"expected_output": "finding"},
                "expected": {"must_detect": [{"type": "IDEMPOTENCY_GAP"}]},
            }]}), encoding="utf-8")

            output = root / "batch"
            manifest = build_batch(
                catalog=catalog,
                skill_root=skill,
                output_dir=output,
                repetitions=2,
                baseline_sha="abc123",
            )

            self.assertEqual(2, len(manifest["runs"]))
            self.assertEqual("abc123", manifest["baseline_sha"])
            payload = json.dumps(manifest)
            self.assertNotIn("must_detect", payload)
            self.assertNotIn("expected", payload)
            for run in manifest["runs"]:
                sandbox = output / run["sandbox"]
                self.assertTrue((sandbox / "skill" / "SKILL.md").is_file())
                self.assertTrue((sandbox / "case" / "input.md").is_file())
                self.assertTrue((sandbox / "case" / "context" / "api.md").is_file())
                self.assertFalse((sandbox / "case" / "expected.json").exists())
                self.assertFalse((sandbox / "cases.json").exists())

    def test_rejects_non_positive_repetitions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            skill = root / "skill"
            (skill / "references").mkdir(parents=True)
            (skill / "SKILL.md").write_text("# Skill\n", encoding="utf-8")
            catalog = root / "cases.json"
            catalog.write_text(json.dumps({"cases": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                build_batch(catalog, skill, root / "batch", 0, "abc123")


if __name__ == "__main__":
    unittest.main(verbosity=2)
