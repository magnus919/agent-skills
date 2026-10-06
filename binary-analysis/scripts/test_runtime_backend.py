"""Production CLI regression tests: never substitute fixtures for user binaries."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from uuid import uuid4

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))


class RuntimeBackendTests(unittest.TestCase):
    def test_no_fixture_imports_in_runtime_paths(self):
        for directory in ('cli', 'worker'):
            for path in (SCRIPTS / 'binary_analysis' / directory).glob('*.py'):
                for node in ast.walk(ast.parse(path.read_text())):
                    if isinstance(node, ast.ImportFrom):
                        self.assertNotEqual(node.module, 'binary_analysis.adapters.fake', path)

    def test_factory_and_worker_fail_without_fixture_fallback(self):
        from binary_analysis.adapters.runtime import get_adapter
        from binary_analysis.domain.errors import BackendFailureError
        from binary_analysis.worker.resolver import resolve_adapter
        from binary_analysis.worker.server import WorkerServer
        for operation in (get_adapter, resolve_adapter, lambda: WorkerServer().adapter):
            with self.subTest(operation=operation):
                with self.assertRaisesRegex(BackendFailureError, 'not implemented'):
                    operation()

    def test_commands_reject_legacy_projects_for_distinct_binaries(self):
        from binary_analysis.projects.manifest import create_manifest, save_manifest
        commands = [
            ['metadata'], ['sections'], ['entrypoints'], ['imports'], ['exports'],
            ['symbols'], ['strings'], ['functions'], ['decompile', 'main'],
            ['disassemble', 'main'], ['bytes', '0x401000', '4'],
            ['xrefs', '0x401000'], ['callers', 'main'], ['callees', 'main'],
            ['callgraph', 'main'], ['search', 'main'],
            ['trace', '--from', 'main', '--to', 'check_password'],
            ['triage'], ['suspicious-apis'], ['capability-map'],
            ['export-report', '--type', 'triage', '--format', 'json'], ['analyze'],
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {**os.environ, 'BINARY_WORKSPACE_ROOT': str(root)}
            for index, content in enumerate((b'MZ'+b'A'*512, b'\x7fELF'+b'B'*1024)):
                project = root / f'legacy-{index}'
                project.mkdir()
                sample = root / f'sample-{index}'
                sample.write_bytes(content)
                manifest = create_manifest(str(uuid4()), project.name)
                manifest['state'] = 'IMPORTED'
                manifest['current_binary'] = {
                    'id': str(uuid4()), 'sha256': hashlib.sha256(content).hexdigest(),
                    'path': str(sample), 'format': 'PE' if index == 0 else 'ELF',
                    'size_bytes': len(content), 'import_mode': 'reference',
                }
                save_manifest(str(project), manifest)
                before = (project / 'project.json').read_bytes()
                for command in commands + [['import', str(sample)]]:
                    with self.subTest(binary=index, command=command):
                        result = subprocess.run(
                            [sys.executable, str(SCRIPTS / 'binary'), *command,
                             '--project', project.name, '--json'], env=env,
                            capture_output=True, text=True, timeout=10,
                        )
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        payload = json.loads(result.stdout)
                        self.assertFalse(payload['success'])
                        self.assertIsNone(payload['data'])
                        self.assertIn('not implemented', json.dumps(payload['diagnostics']))
                        self.assertEqual((project / 'project.json').read_bytes(), before)
                self.assertEqual(sample.read_bytes(), content)
                self.assertFalse((project / 'reports').exists())


if __name__ == '__main__':
    unittest.main()
