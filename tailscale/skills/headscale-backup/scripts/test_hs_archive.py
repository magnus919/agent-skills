#!/usr/bin/env python3
"""Focused tests for manifest-driven Headscale backup and restore."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKUP = HERE / "hs-backup.sh"
RESTORE = HERE / "hs-restore.sh"


class HeadscaleArchiveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="hs-archive-test-")
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self._fake_sqlite3()
        self.config_dir = self.root / "etc" / "headscale"
        self.data_dir = self.root / "var" / "lib" / "headscale"
        self.certs_dir = self.config_dir / "certs"
        self.config_dir.mkdir(parents=True)
        self.data_dir.mkdir(parents=True)
        self.certs_dir.mkdir()
        self.db = self.data_dir / "state.sqlite"
        with sqlite3.connect(self.db) as connection:
            connection.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY, name TEXT)")
            connection.execute("INSERT INTO nodes(name) VALUES ('fixture-node')")
        (self.config_dir / "config.yaml").write_text(
            "database:\n  type: sqlite\n  sqlite:\n    path: ../..//var/lib/headscale/state.sqlite\n"
            "tls_cert_path: certs/server.crt\ntls_key_path: certs/server.key\n",
            encoding="utf-8",
        )
        (self.config_dir / "policy.json").write_text('{"acls": []}\n', encoding="utf-8")
        (self.certs_dir / "server.crt").write_text("fixture-cert\n", encoding="utf-8")
        (self.certs_dir / "server.key").write_text("fixture-key\n", encoding="utf-8")
        self.backups = self.root / "backups"
        self.backups.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _fake_sqlite3(self) -> None:
        binary = self.bin / "sqlite3"
        binary.write_text(
            "#!/usr/bin/env python3\n"
            "import re, sqlite3, sys\n"
            "db, command = sys.argv[1], sys.argv[2]\n"
            "if command.startswith('.backup '):\n"
            "    target = command[len('.backup '):].strip().strip(\"'\").replace(\"''\", \"'\")\n"
            "    with sqlite3.connect(db) as src, sqlite3.connect(target) as dst: src.backup(dst)\n"
            "elif command.strip().upper() == 'PRAGMA QUICK_CHECK;':\n"
            "    with sqlite3.connect(db) as conn: print(conn.execute('PRAGMA quick_check').fetchone()[0])\n"
            "else: sys.exit(2)\n",
            encoding="utf-8",
        )
        binary.chmod(0o755)

    def env(self) -> dict[str, str]:
        return {**os.environ, "PATH": f"{self.bin}:{os.environ.get('PATH', '')}"}

    def run_script(self, script: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run([str(script), *args], text=True, capture_output=True, env=env or self.env())

    def backup(self) -> Path:
        result = self.run_script(
            BACKUP, "--auto", "--json", "--config", str(self.config_dir / "config.yaml"),
            "--data-dir", str(self.data_dir), "--certs-dir", str(self.certs_dir), "--output-dir", str(self.backups),
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return Path(json.loads(result.stdout)["backup_path"])

    def test_backup_contains_consistent_verified_assets_and_manifest(self) -> None:
        path = self.backup()
        with tarfile.open(path, "r:gz") as archive:
            manifest_name = next(name for name in archive.getnames() if name.endswith("/manifest.json"))
            base = manifest_name.rsplit("/", 1)[0]
            manifest = json.load(archive.extractfile(manifest_name))
            by_role = {asset["role"]: asset for asset in manifest["assets"]}
            self.assertTrue({"config", "database", "policy", "tls_cert", "tls_key"}.issubset(by_role))
            db_bytes = archive.extractfile(f"{base}/{by_role['database']['archive_path']}").read()
            self.assertEqual(hashlib.sha256(db_bytes).hexdigest(), by_role["database"]["sha256"])
            with tempfile.NamedTemporaryFile() as snapshot:
                snapshot.write(db_bytes)
                snapshot.flush()
                with sqlite3.connect(snapshot.name) as connection:
                    self.assertEqual(connection.execute("PRAGMA quick_check").fetchone()[0], "ok")
                    self.assertEqual(connection.execute("SELECT name FROM nodes").fetchone()[0], "fixture-node")

    def test_restore_preserves_archived_destinations_and_restores_bytes(self) -> None:
        path = self.backup()
        (self.config_dir / "config.yaml").write_text("modified after backup\n", encoding="utf-8")
        with sqlite3.connect(self.db) as connection:
            connection.execute("DELETE FROM nodes")
        self.db.unlink()
        (self.certs_dir / "server.key").unlink()
        result = self.run_script(
            RESTORE, "--backup", str(path), "--force", "--json",
            env={**self.env(), "HEADSCALE_SKIP_SERVICE_CONTROL": "1"},
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["restored"])
        self.assertEqual((self.config_dir / "config.yaml").read_bytes(), b"database:\n  type: sqlite\n  sqlite:\n    path: ../..//var/lib/headscale/state.sqlite\ntls_cert_path: certs/server.crt\ntls_key_path: certs/server.key\n")
        self.assertEqual((self.certs_dir / "server.key").stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.certs_dir / "server.key").stat().st_uid, self.certs_dir.stat().st_uid)
        with sqlite3.connect(self.db) as connection:
            self.assertEqual(connection.execute("SELECT name FROM nodes").fetchone()[0], "fixture-node")
        self.assertEqual(self.db.stat().st_uid, self.data_dir.stat().st_uid)

    def test_database_root_remapping_is_rejected_before_any_write(self) -> None:
        path = self.backup()
        (self.config_dir / "config.yaml").write_text("keep this file\n", encoding="utf-8")
        result = self.run_script(
            RESTORE, "--backup", str(path), "--force", "--json", "--data-dir", str(self.root / "new-data"),
            env={**self.env(), "HEADSCALE_SKIP_SERVICE_CONTROL": "1"},
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("database path remapping is not safe", result.stdout)
        self.assertEqual((self.config_dir / "config.yaml").read_text(encoding="utf-8"), "keep this file\n")

    def test_restore_rejects_tampered_asset_before_writing(self) -> None:
        path = self.backup()
        tampered = self.root / "tampered.tar.gz"
        with tarfile.open(path, "r:gz") as source, tarfile.open(tampered, "w:gz") as target:
            for member in source.getmembers():
                content = source.extractfile(member).read() if member.isfile() else None
                if member.name.endswith("config/config.yaml"):
                    content += b"# tampered\n"
                info = tarfile.TarInfo(member.name)
                info.mode = member.mode
                info.size = len(content) if content is not None else 0
                import io
                target.addfile(info, io.BytesIO(content) if content is not None else None)
        result = self.run_script(RESTORE, "--backup", str(tampered), "--dry-run", "--json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mismatch", result.stdout)

    def test_restore_rejects_unsafe_archive_path(self) -> None:
        path = self.backup()
        unsafe = self.root / "unsafe.tar.gz"
        with tarfile.open(path, "r:gz") as source, tarfile.open(unsafe, "w:gz") as target:
            import io
            for member in source.getmembers():
                content = source.extractfile(member).read() if member.isfile() else None
                if member.name.endswith("/manifest.json"):
                    manifest = json.loads(content)
                    manifest["assets"][0]["archive_path"] = "../../outside"
                    content = json.dumps(manifest).encode()
                info = tarfile.TarInfo(member.name)
                info.mode = member.mode
                info.size = len(content) if content is not None else 0
                target.addfile(info, io.BytesIO(content) if content is not None else None)
        result = self.run_script(RESTORE, "--backup", str(unsafe), "--dry-run", "--json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe archive member path", result.stdout)

    def test_target_path_failure_does_not_leave_restore_temp_files(self) -> None:
        path = self.backup()
        blocked = self.root / "blocked-config-dir"
        blocked.write_text("not a directory", encoding="utf-8")
        result = self.run_script(
            RESTORE, "--backup", str(path), "--force", "--json", "--config-dir", str(blocked),
            env={**self.env(), "HEADSCALE_SKIP_SERVICE_CONTROL": "1"},
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(self.root.glob(".config.yaml.restore-*")), [])

    def test_database_path_formats_and_postgres_rejection(self) -> None:
        config = self.config_dir / "config.yaml"
        for contents in (
            "database_path: ../..//var/lib/headscale/state.sqlite\n",
            "database:\n  path: ../..//var/lib/headscale/state.sqlite\n",
        ):
            config.write_text(contents, encoding="utf-8")
            result = self.run_script(BACKUP, "--dry-run", "--json", "--config", str(config), "--data-dir", str(self.data_dir), "--certs-dir", str(self.certs_dir))
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        config.write_text("database:\n  postgres:\n    host: db.example\n", encoding="utf-8")
        result = self.run_script(BACKUP, "--dry-run", "--json", "--config", str(config), "--data-dir", str(self.data_dir), "--certs-dir", str(self.certs_dir))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PostgreSQL", result.stdout)


if __name__ == "__main__":
    unittest.main()
