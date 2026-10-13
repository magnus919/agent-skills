import contextlib
import gzip
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path


class EvidenceVerifierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'evidence'
        shutil.copytree(Path(__file__).parent, self.root)
        spec = importlib.util.spec_from_file_location('verifier', self.root / 'verify_evidence.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def tearDown(self):
        self.temp.cleanup()

    def rehash(self, name):
        import hashlib
        p = self.root / 'evidence-manifest.json'
        m = json.loads(p.read_text())
        m['sha256'][name] = hashlib.sha256((self.root / name).read_bytes()).hexdigest()
        p.write_text(json.dumps(m))

    def test_complete_package(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.module.verify()

    def test_metric_corruption_even_after_rehash(self):
        p = self.root / 'analysis-final.json'
        m = json.loads(p.read_text());m['arms']['P']['ndcg5'] = 1.
        p.write_text(json.dumps(m));self.rehash(p.name)
        with self.assertRaisesRegex(ValueError, 'aggregate metric mismatch'):
            self.module.verify()

    def test_dropped_receipt_even_after_rehash(self):
        p = self.root / 'response-ledger-public.json.gz'
        m = json.loads(gzip.decompress(p.read_bytes()));m.pop()
        p.write_bytes(gzip.compress(json.dumps(m).encode(),mtime=0));self.rehash(p.name)
        with self.assertRaisesRegex(ValueError, 'paid attempt count mismatch'):
            self.module.verify()

    def test_model_drift_even_after_rehash(self):
        p = self.root / 'response-ledger-public.json.gz'
        m = json.loads(gzip.decompress(p.read_bytes()));m[-1]['response']['model'] = 'jev-latest'
        p.write_bytes(gzip.compress(json.dumps(m).encode(),mtime=0));self.rehash(p.name)
        with self.assertRaisesRegex(ValueError, 'model drift'):
            self.module.verify()


if __name__ == '__main__':
    unittest.main()
