import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

from prepare_case import prepare_case


class PrepareCaseTests(unittest.TestCase):
    def test_sandbox_contains_skill_and_input_but_hides_answers(self):
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            skill_root = temp / 'skill'
            (skill_root / 'references').mkdir(parents=True)
            (skill_root / 'SKILL.md').write_text('# Skill\n', encoding='utf-8')
            (skill_root / 'references' / 'challenge-model.md').write_text('# Model\n', encoding='utf-8')

            catalog = temp / 'cases.json'
            catalog.write_text(json.dumps({'cases':[{
                'case_id':'tc-001', 'metadata':{}, 'input':'review me',
                'context':{'api.md':'contract'},
                'expected':{'must_detect':[]}
            }]}), encoding='utf-8')

            out = temp / 'sandbox'
            prepare_case(catalog, 'tc-001', out, skill_root)

            self.assertTrue((out / 'skill' / 'SKILL.md').is_file())
            self.assertTrue((out / 'skill' / 'references' / 'challenge-model.md').is_file())
            self.assertEqual('review me', (out / 'case' / 'input.md').read_text())
            self.assertEqual('contract', (out / 'case' / 'context' / 'api.md').read_text())
            self.assertFalse((out / 'case' / 'expected.json').exists())
            self.assertFalse((out / 'cases.json').exists())

    def test_existing_output_directory_is_replaced(self):
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            skill_root = temp / 'skill'
            (skill_root / 'references').mkdir(parents=True)
            (skill_root / 'SKILL.md').write_text('# Skill\n', encoding='utf-8')
            catalog = temp / 'cases.json'
            catalog.write_text(json.dumps({'cases':[{'case_id':'tc-001','metadata':{},'input':'x','context':{},'expected':{}}]}), encoding='utf-8')
            out = temp / 'sandbox'
            out.mkdir()
            (out / 'stale.txt').write_text('stale', encoding='utf-8')

            prepare_case(catalog, 'tc-001', out, skill_root)

            self.assertFalse((out / 'stale.txt').exists())


if __name__ == '__main__':
    unittest.main()
