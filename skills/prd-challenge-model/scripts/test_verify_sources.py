import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from verify_sources import verify


class SourceVerificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'req.md'
        self.raw = b'# Notes\r\nSave keeps edits.\r\nDelete removes a note.\r\n'
        self.path.write_bytes(self.raw)
        self.review = {
            'artifacts': [{'id': 'A-001', 'path': str(self.path), 'required': True,
                           'parse_status': 'PARSED', 'content_sha256': hashlib.sha256(self.raw).hexdigest()}],
            'requirements': [{'id': 'R-001-0001', 'artifact_id': 'A-001', 'text': 'Save keeps edits.'}],
            'findings': [{'id': 'F-0001', 'evidence': [{'artifact_id': 'A-001', 'requirement_id': 'R-001-0001',
                          'source_path': str(self.path), 'quote': 'Save keeps edits.'}]}],
            'observations': [],
        }

    def test_valid(self):
        self.assertEqual(verify(self.review, [self.path]), [])

    def test_fake_quote(self):
        self.review['findings'][0]['evidence'][0]['quote'] = 'Save discards edits.'
        self.assertTrue(any('not found verbatim' in e for e in verify(self.review, [self.path])))

    def test_wrong_anchor(self):
        self.review['findings'][0]['evidence'][0]['quote'] = 'Delete removes a note.'
        self.assertTrue(any('not within anchored' in e for e in verify(self.review, [self.path])))

    def test_changed_source(self):
        self.path.write_text('changed')
        self.assertTrue(any('SHA-256 mismatch' in e for e in verify(self.review, [self.path])))

    def test_unapproved_file(self):
        self.assertTrue(any('not in authorized' in e for e in verify(self.review, [])))

    def test_missing_authorized_source(self):
        other = Path(self.tmp.name) / 'other.md'
        other.write_text('Other rule.')
        self.assertTrue(any('missing from Artifact Index' in e for e in verify(self.review, [self.path, other])))

    def test_fabricated_requirement(self):
        self.review['requirements'][0]['text'] = 'Invented requirement'
        self.assertTrue(any('requirement text not verified' in e for e in verify(self.review, [self.path])))

    def test_normalized_line_endings(self):
        self.review['requirements'][0]['text'] = 'Save keeps edits.\nDelete removes a note.'
        self.assertEqual(verify(self.review, [self.path]), [])


if __name__ == '__main__':
    unittest.main()
