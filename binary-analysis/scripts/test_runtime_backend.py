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
from unittest import mock
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

    def test_importing_runtime_backend_does_not_load_fake_adapter(self):
        check = subprocess.run(
            [sys.executable, '-c',
             "import sys; "
             f"sys.path.insert(0, {str(SCRIPTS)!r}); "
             "import binary_analysis.adapters.runtime; "
             "assert 'binary_analysis.adapters.fake' not in sys.modules; "
             "from binary_analysis.adapters import FakeAdapter; "
             "assert FakeAdapter.__name__ == 'FakeAdapter'"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(check.returncode, 0, check.stderr)

    def test_factory_and_worker_fail_without_fixture_fallback(self):
        from binary_analysis.adapters.runtime import get_adapter
        from binary_analysis.domain.errors import BackendFailureError
        from binary_analysis.worker.resolver import resolve_adapter
        from binary_analysis.worker.server import WorkerServer
        for operation in (get_adapter, resolve_adapter, lambda: WorkerServer().adapter):
            with self.subTest(operation=operation):
                with self.assertRaisesRegex(BackendFailureError, 'not implemented'):
                    operation()

    def test_worker_start_refuses_backend_without_stale_status_or_false_success(self):
        from argparse import Namespace

        from binary_analysis.cli.worker import execute_start
        from binary_analysis.domain.errors import BackendFailureError
        from binary_analysis.worker import client, server

        with tempfile.TemporaryDirectory() as tmp:
            worker_dir = Path(tmp) / 'worker-state'
            pid_path = worker_dir / 'worker.pid'
            started_path = worker_dir / 'worker.started_at'
            socket_path = worker_dir / 'worker.sock'

            with (
                mock.patch.object(server, 'WORKER_DIR', str(worker_dir)),
                mock.patch.object(client, 'WORKER_DIR', str(worker_dir)),
                mock.patch.object(server, '_pid_path', lambda: str(pid_path)),
                mock.patch.object(server, '_started_at_path', lambda: str(started_path)),
                mock.patch.object(server, '_socket_path', lambda: str(socket_path)),
                mock.patch.object(client, '_pid_path', lambda: str(pid_path)),
                mock.patch.object(client, '_started_at_path', lambda: str(started_path)),
                mock.patch.object(client, '_socket_path', lambda: str(socket_path)),
            ):
                with self.assertRaisesRegex(BackendFailureError, 'not implemented'):
                    server.WorkerServer().start()

                self.assertFalse(worker_dir.exists())
                self.assertFalse(pid_path.exists())
                self.assertFalse(started_path.exists())
                self.assertFalse(socket_path.exists())

                class FailedProcess:
                    returncode = 13

                    def poll(self):
                        return self.returncode

                def run_child_start(*_args, **_kwargs):
                    try:
                        server.WorkerServer().start()
                    except BackendFailureError:
                        return FailedProcess()
                    self.fail('worker unexpectedly started without a backend')

                with mock.patch('subprocess.Popen', side_effect=run_child_start) as popen:
                    result = execute_start(Namespace())

                self.assertEqual(popen.call_count, 1)
                self.assertFalse(result['success'])
                self.assertEqual(result['data']['status'], 'failed')
                self.assertEqual(client.get_worker_status()['state'], 'stopped')
                self.assertFalse(pid_path.exists())
                self.assertFalse(started_path.exists())
                self.assertFalse(socket_path.exists())

    def test_worker_server_cleans_state_after_socket_bind_failure(self):
        from binary_analysis.worker import client, server

        with tempfile.TemporaryDirectory() as tmp:
            worker_dir = Path(tmp) / 'worker-state'
            pid_path = worker_dir / 'worker.pid'
            started_path = worker_dir / 'worker.started_at'
            socket_path = worker_dir / 'worker.sock'

            class BrokenSocket:
                closed = False

                def bind(self, _path):
                    raise OSError('bind failed')

                def close(self):
                    self.closed = True

            broken_socket = BrokenSocket()
            with (
                mock.patch.object(server, 'WORKER_DIR', str(worker_dir)),
                mock.patch.object(server, '_pid_path', lambda: str(pid_path)),
                mock.patch.object(server, '_started_at_path', lambda: str(started_path)),
                mock.patch.object(server, '_socket_path', lambda: str(socket_path)),
                mock.patch.object(server.runtime, 'get_adapter', return_value=object()),
                mock.patch.object(server.socket, 'socket', return_value=broken_socket),
            ):
                with self.assertRaisesRegex(OSError, 'bind failed'):
                    server.WorkerServer().start()

            self.assertTrue(broken_socket.closed)
            self.assertFalse(pid_path.exists())
            self.assertFalse(started_path.exists())
            self.assertFalse(socket_path.exists())

    def test_worker_status_rejects_live_pid_without_reachable_socket(self):
        from binary_analysis.worker import client

        with tempfile.TemporaryDirectory() as tmp:
            worker_dir = Path(tmp) / 'worker-state'
            worker_dir.mkdir()
            pid_path = worker_dir / 'worker.pid'
            pid_path.write_text(str(os.getpid()))
            with (
                mock.patch.object(client, 'WORKER_DIR', str(worker_dir)),
                mock.patch.object(client, '_pid_path', lambda: str(pid_path)),
                mock.patch.object(client, '_started_at_path', lambda: str(worker_dir / 'worker.started_at')),
                mock.patch.object(client, '_socket_path', lambda: str(worker_dir / 'worker.sock')),
            ):
                self.assertEqual(client.get_worker_status()['state'], 'stopped')

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
