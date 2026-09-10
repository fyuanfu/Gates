import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from gate import prepare, finalize, write

class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.doc = self.root / 'prd.md'
        self.doc.write_text('全部成功才显示完成\n一项成功就显示完成\n', encoding='utf-8')
        self.out = self.root / 'run'; self.out.mkdir()
        self.manifest = self.root / 'manifest.json'
        write(self.manifest, {'primary_documents': [str(self.doc)]})
        prepare(self.manifest, self.out)
        self.review = {'inventory': [], 'documents_reviewed': [str(self.doc)], 'stages_completed': ['coverage','clarity_verifiability','consistency','confirmation'], 'findings': []}
        self.finding = {'id':'F-1','type':'AMBIGUOUS','severity':'P1','confirmation_status':'confirmed','subject':'upload','claim':'结果有歧义','impact':'核心成功结果不确定','question':'成功条件是什么？','evidence':[{'path':str(self.doc),'line':1,'quote':'全部成功才显示完成'}],'counter_evidence':[],'search_log':[{'path':str(self.doc),'query':'完成','result':'未消除歧义'}],'resolution_reason':'核心结果未确定'}
    def run_review(self):
        path = self.root / 'review.json'; write(path,self.review)
        return finalize(self.out,path)
    def test_status_matrix(self):
        for severity in ['P0','P1','P2','P3']:
            for confirmation in ['confirmed','pending','rejected']:
                with self.subTest(severity=severity, confirmation=confirmation):
                    f=copy.deepcopy(self.finding);f.update(severity=severity,confirmation_status=confirmation)
                    self.review['findings']=[f]
                    expected='review_failed' if severity in ['P0','P1'] and confirmation=='confirmed' else 'review_inconclusive' if severity in ['P0','P1'] and confirmation=='pending' else 'review_passed'
                    self.assertEqual(self.run_review()['status'],expected)
    def test_empty_complete(self):
        result=self.run_review(); self.assertEqual(result['status'],'review_passed');self.assertIsNone(result['highest_severity'])
    def test_failed_precedes_pending(self):
        f=copy.deepcopy(self.finding);f.update(id='F-2',severity='P0',confirmation_status='pending')
        self.review['findings']=[self.finding,f]
        result=self.run_review();self.assertEqual(result['status'],'review_failed');self.assertEqual(result['pending_high_finding_ids'],['F-2'])
    def test_invalid_reviews(self):
        for case in ['stage','coverage','quote','path','search','duplicate','enum','conflict','blank']:
            with self.subTest(case=case):
                original=copy.deepcopy(self.review)
                self.review['findings']=[copy.deepcopy(self.finding)]
                f=self.review['findings'][0]
                if case=='stage':self.review['stages_completed']=[]
                if case=='coverage':self.review['documents_reviewed']=[]
                if case=='quote':f['evidence'][0]['quote']='不存在'
                if case=='path':f['evidence'][0]['path']='/not-authorized.md'
                if case=='search':f['search_log']=[]
                if case=='duplicate':self.review['findings'].append(copy.deepcopy(f))
                if case=='enum':f['severity']='HIGH'
                if case=='conflict':f['type']='INCONSISTENT'
                if case=='blank':f['impact']=' '
                with self.assertRaises(ValueError):self.run_review()
                self.review=original
    def test_changed_source(self):
        self.doc.write_text('changed',encoding='utf-8')
        with self.assertRaises(ValueError):self.run_review()
    def test_cli_execution_error(self):
        write(self.manifest, {'primary_documents':['missing.md']})
        out=self.root/'cli-error'
        result=subprocess.run([sys.executable,str(Path(__file__).with_name('gate.py')),'prepare',str(self.manifest),str(out)],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn('execution_error',result.stdout)
        self.assertTrue((out/'gate-result.json').is_file())
    def test_existing_directory_not_modified(self):
        result=subprocess.run([sys.executable,str(Path(__file__).with_name('gate.py')),'prepare',str(self.manifest),str(self.out)],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertFalse((self.out/'gate-result.json').exists())
    def test_unsupported_format(self):
        write(self.manifest, {'primary_documents':['prd.pdf']})
        with self.assertRaises(ValueError):prepare(self.manifest,self.out)

if __name__=='__main__':unittest.main()
