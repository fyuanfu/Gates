"""Behavior tests for reportctl's public CLI, not private methods."""
import json, pathlib, shutil, subprocess, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parent.parent
CLI=ROOT/'scripts/reportctl.py'

class WorkflowTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=pathlib.Path(self.tmp.name);self.report='demo-report';self.proj=self.base/self.report
 def tearDown(self):self.tmp.cleanup()
 def call(self,*args,expected=0):
  p=subprocess.run([sys.executable,str(CLI),*args,'--root',str(self.base)],capture_output=True,text=True)
  self.assertEqual(p.returncode,expected,p.stdout+p.stderr)
  return json.loads(p.stdout)
 def initialize(self):return self.call('init',self.report)
 def populate_g1(self):
  self.initialize(); shutil.copy(ROOT/'fixtures/valid/brief.yaml',self.proj/'brief.yaml')
  a=(self.proj/'brief.yaml').read_text();(self.proj/'brief.yaml').write_text(a.replace('sample-report','demo-report'))
 def confirm(self,gate,digest):
  p=self.proj/'approval.txt';p.write_text(f'我明确批准 {gate}，摘要 {digest}',encoding='utf-8')
  return self.call('approve',self.report,'--gate',gate,'--digest',digest,'--confirmation-file',str(p))
 def approve_g1(self):
  self.populate_g1();sub=self.call('submit',self.report,'--gate','G1');self.confirm('G1',sub['digest'])
 def test_init_and_no_gate_skip(self):
  self.initialize();self.assertEqual(self.call('start-stage',self.report,'--stage','S2',expected=3)['code'],'E_GATE')
 def test_requires_g1_brief(self):
  self.initialize();self.assertEqual(self.call('submit',self.report,'--gate','G1',expected=4)['code'],'E_CONTRACT')
 def test_approve_requires_matching_digest_and_explicit_confirmation(self):
  self.populate_g1();s=self.call('submit',self.report,'--gate','G1')
  p=self.proj/'approval.txt';p.write_text('好的')
  self.assertEqual(self.call('approve',self.report,'--gate','G1','--digest',s['digest'],'--confirmation-file',str(p),expected=3)['code'],'E_CONFIRM')
  self.assertEqual(self.call('approve',self.report,'--gate','G1','--digest','0'*64,'--confirmation-file',str(p),expected=3)['code'],'E_HASH')
  self.confirm('G1',s['digest']);self.assertEqual(self.call('status',self.report)['state']['stages']['S1']['status'],'approved')
 def test_brief_change_invalidates_approval(self):
  self.approve_g1();self.call('start-stage',self.report,'--stage','S2')
  p=self.proj/'brief.yaml';p.write_text(p.read_text()+'\n# revised\n')
  self.call('sync',self.report)
  self.assertEqual(self.call('status',self.report)['state']['stages']['S1']['status'],'stale')
 def test_reject_and_revise_preserve_history(self):
  self.populate_g1();s=self.call('submit',self.report,'--gate','G1')
  f=self.proj/'feedback.txt';f.write_text('需要调整内容');c=self.proj/'reject.txt';c.write_text('我明确拒绝 G1 摘要 '+s['digest'])
  self.call('reject',self.report,'--gate','G1','--feedback-file',str(f),'--confirmation-file',str(c))
  self.call('revise',self.report,'--stage','S1')
  state=self.call('status',self.report)['state'];self.assertEqual(state['stages']['S1']['status'],'in_progress');self.assertEqual(len(state['approvals']),1)
 def test_release_blocked_without_g5(self):
  self.initialize();self.assertEqual(self.call('release',self.report,expected=3)['code'],'E_GATE')
if __name__=='__main__':unittest.main()
