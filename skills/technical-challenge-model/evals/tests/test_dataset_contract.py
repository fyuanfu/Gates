import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from validate_dataset import validate_dataset


class DatasetContractTests(unittest.TestCase):
    def test_rejects_incomplete_dataset_and_missing_axis_coverage(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'dev').mkdir(parents=True)
            (root / 'holdout').mkdir(parents=True)
            record = {
                'case_id':'tc-dev-001',
                'metadata':{'design_stage':'high_level','mechanism_lifecycle':'planned','primary_lens':'idempotency','expected_output':'finding','claim_kind':'precondition'},
                'input':'x', 'context':{},
                'expected':{'must_detect':[],'must_not_detect':[],'allowed_verdicts':['PASS'],'expected_requirement_gap_count':0,'expected_evidence_gap_count':0,'expected_open_decision_count':0}
            }
            (root/'dev'/'cases.json').write_text(json.dumps({'cases':[record]}), encoding='utf-8')
            (root/'holdout'/'cases.json').write_text(json.dumps({'cases':[]}), encoding='utf-8')

            errors = validate_dataset(root)

            self.assertTrue(any('expected 20 dev cases' in item for item in errors))
            self.assertTrue(any('expected 10 holdout cases' in item for item in errors))
            self.assertTrue(any('missing design_stage coverage' in item for item in errors))

    def test_repository_dataset_meets_contract(self):
        errors = validate_dataset(ROOT)
        self.assertEqual([], errors)

    def test_eval_operational_files_exist(self):
        self.assertTrue((ROOT / 'README.md').is_file())
        self.assertTrue((ROOT / 'coverage-matrix.json').is_file())
        self.assertTrue((ROOT / 'adjudication-template.json').is_file())


if __name__ == '__main__':
    unittest.main()
