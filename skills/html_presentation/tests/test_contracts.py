"""Executable contract fixtures. Run: python -m unittest discover -s tests -v"""
import pathlib,sys,unittest,copy,tempfile,shutil,yaml
ROOT=pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'scripts'))
from validate_contracts import validate_project
from jsonschema import Draft202012Validator
import json
class ContractTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.root=pathlib.Path(self.temp.name)/'project'
  shutil.copytree(ROOT/'fixtures/valid',self.root)
 def tearDown(self):self.temp.cleanup()
 def read(self,p):return yaml.safe_load((self.root/p).read_text())
 def write(self,p,obj):(self.root/p).write_text(yaml.safe_dump(obj,allow_unicode=True,sort_keys=False))
 def test_valid_project(self):self.assertEqual([],validate_project(self.root))
 def test_source_hash_change(self):
  (self.root/'inputs/raw/quality-stats.md').write_text('changed')
  self.assertIn('SHA-256 mismatch',str(validate_project(self.root)))
 def test_dangling_claim(self):
  x=self.read('report-plan.yaml');x['sections'][0]['claim_refs']=['C-999'];self.write('report-plan.yaml',x)
  self.assertIn('unknown claim',str(validate_project(self.root)))
 def test_duplicate_id(self):
  x=self.read('evidence.yaml');x['claims'].append(copy.deepcopy(x['claims'][0]));self.write('evidence.yaml',x)
  self.assertIn('duplicate id',str(validate_project(self.root)))
 def test_unverified_factual(self):
  x=self.read('evidence.yaml');x['claims'][0]['verification']='pending';self.write('evidence.yaml',x)
  self.assertIn('not verified',str(validate_project(self.root)))
 def test_body_marker_mismatch(self):
  (self.root/'content/S-01.md').write_text('Text {{claim:C-999}}')
  self.assertIn('body marker not declared',str(validate_project(self.root)))
 def test_path_escape(self):
  x=self.read('report-plan.yaml');x['sections'][0]['content_path']='../../secret.md';self.write('report-plan.yaml',x)
  self.assertIn('unsafe path',str(validate_project(self.root)))
 def test_schema_invalid_cases(self):
  cases=[('brief-missing-audience','brief'),('evidence-bad-enum','evidence'),('plan-unsafe-path','report-plan')]
  for filename,schemaname in cases:
   with self.subTest(filename=filename):
    data=yaml.safe_load((ROOT/f'fixtures/invalid/{filename}.yaml').read_text())
    schema=json.loads((ROOT/f'schemas/{schemaname}.schema.json').read_text())
    self.assertTrue(list(Draft202012Validator(schema).iter_errors(data)))
if __name__=='__main__':unittest.main()

class AdditionalSchemaTests(unittest.TestCase):
 def test_ready_skill_requires_lock_and_smoke(self):
  import json,yaml
  lock=yaml.safe_load((ROOT/'fixtures/skills.lock.example.yaml').read_text())
  lock['skills'][0]['status']='ready'
  schema=json.loads((ROOT/'schemas/skills-lock.schema.json').read_text())
  self.assertTrue(list(Draft202012Validator(schema).iter_errors(lock)))
 def test_source_registry_mismatch(self):
  with tempfile.TemporaryDirectory() as temp:
   project=pathlib.Path(temp)/'project';shutil.copytree(ROOT/'fixtures/valid',project)
   e=yaml.safe_load((project/'evidence.yaml').read_text());e['sources'][0]['manifest_ref']='SRC-900';(project/'evidence.yaml').write_text(yaml.safe_dump(e,allow_unicode=True))
   self.assertIn('invalid source registry link',str(validate_project(project)))
