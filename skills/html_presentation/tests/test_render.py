"""Smoke test the conservative renderer across the public CLI artifact seam."""
import pathlib, shutil, subprocess, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
class Rendering(unittest.TestCase):
 def test_single_file_renders_sections_and_claim_sources(self):
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'sample';shutil.copytree(ROOT/'fixtures/valid',p,ignore=shutil.ignore_patterns('output','qa'))
   run=subprocess.run([sys.executable,str(ROOT/'scripts/render_html.py'),'--project',str(p)],capture_output=True,text=True)
   self.assertEqual(run.returncode,0,run.stderr)
   html=(p/'output/index.html').read_text('utf-8')
   self.assertIn('<style>',html);self.assertIn('id="S-01"',html);self.assertIn('ref-C-001',html)
   self.assertNotIn('{{claim:',html);self.assertNotIn('https://fonts.',html)
if __name__=='__main__':unittest.main()
