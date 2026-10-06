#!/usr/bin/env python3
"""Focused tests for manifest-driven Headscale backup and restore."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
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
UMBRELLA_BACKUP = HERE.parents[2] / "scripts" / "headscale-backup.sh"
UMBRELLA_RESTORE = HERE.parents[2] / "scripts" / "headscale-restore.sh"


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
        self.db = self.data_dir / "db.sqlite3"
        with sqlite3.connect(self.db) as connection:
            connection.execute("CREATE TABLE nodes (id INTEGER PRIMARY KEY, name TEXT)")
            connection.execute("INSERT INTO nodes(name) VALUES ('fixture-node')")
        (self.config_dir / "config.yaml").write_text(
            f"database:\n  type: sqlite\n  path: {self.db}\n"
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

    def backup(self, script: Path = BACKUP) -> Path:
        if script == UMBRELLA_BACKUP:
            args = ("--json", "--config-dir", str(self.config_dir), "--data-dir", str(self.data_dir),
                    "--certs-dir", str(self.certs_dir), "--output-dir", str(self.backups))
        else:
            args = ("--auto", "--json", "--config", str(self.config_dir / "config.yaml"),
                    "--data-dir", str(self.data_dir), "--certs-dir", str(self.certs_dir), "--output-dir", str(self.backups))
        result = self.run_script(script, *args)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return Path(json.loads(result.stdout)["backup_path"])

    def restore(self, script: Path, path: Path, *, env: dict[str, str] | None = None, extra: tuple[str, ...] = ()) -> subprocess.CompletedProcess[str]:
        return self.run_script(
            script, "--backup", str(path), "--force", "--json", *extra,
            env={**self.env(), "HEADSCALE_SKIP_SERVICE_CONTROL": "1", **(env or {})},
        )

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

    def test_umbrella_backup_and_restore_wrappers_work_end_to_end(self) -> None:
        path = self.backup(UMBRELLA_BACKUP)
        with sqlite3.connect(self.db) as connection:
            connection.execute("DELETE FROM nodes")
        result = self.restore(UMBRELLA_RESTORE, path)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertTrue(json.loads(result.stdout)["restored"])
        with sqlite3.connect(self.db) as connection:
            self.assertEqual(connection.execute("SELECT name FROM nodes").fetchone()[0], "fixture-node")

    def test_both_backup_wrappers_follow_installer_database_path_and_fail_if_missing(self) -> None:
        for script in (BACKUP, UMBRELLA_BACKUP):
            archive = self.backup(script)
            with tarfile.open(archive, "r:gz") as handle:
                manifest_name = next(name for name in handle.getnames() if name.endswith("/manifest.json"))
                manifest = json.load(handle.extractfile(manifest_name))
                database = next(asset for asset in manifest["assets"] if asset["role"] == "database")
                self.assertEqual(Path(database["restore_path"]), self.db)
                self.assertEqual(Path(database["restore_path"]).name, "db.sqlite3")
            self.db.rename(self.data_dir / "saved.sqlite3")
            failed = self.run_script(
                script, *( ("--config-dir", str(self.config_dir), "--data-dir", str(self.data_dir), "--certs-dir", str(self.certs_dir), "--output-dir", str(self.backups)) if script == UMBRELLA_BACKUP else ("--auto", "--config", str(self.config_dir / "config.yaml"), "--data-dir", str(self.data_dir), "--certs-dir", str(self.certs_dir), "--output-dir", str(self.backups)) ),
                "--json",
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("required recovery asset", failed.stdout.lower())
            (self.data_dir / "saved.sqlite3").rename(self.db)

    def test_both_restore_wrappers_reject_manifest_without_database(self) -> None:
        path = self.backup()
        malformed = self.root / "missing-db.tar.gz"
        with tarfile.open(path, "r:gz") as source, tarfile.open(malformed, "w:gz") as target:
            import io
            manifest_name = next(name for name in source.getnames() if name.endswith("/manifest.json"))
            manifest = json.load(source.extractfile(manifest_name))
            database_path = next(asset["archive_path"] for asset in manifest["assets"] if asset["role"] == "database")
            manifest["assets"] = [asset for asset in manifest["assets"] if asset["role"] != "database"]
            base = manifest_name.rsplit("/", 1)[0]
            for member in source.getmembers():
                relative = member.name.removeprefix(base + "/")
                if relative == database_path:
                    continue
                content = json.dumps(manifest).encode() if member.name == manifest_name else (source.extractfile(member).read() if member.isfile() else None)
                info = tarfile.TarInfo(member.name)
                info.mode = member.mode
                info.size = len(content) if content is not None else 0
                target.addfile(info, io.BytesIO(content) if content is not None else None)
        for script in (RESTORE, UMBRELLA_RESTORE):
            result = self.restore(script, malformed)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("mandatory config or database", result.stdout)

    def test_both_restore_wrappers_reject_legacy_archive_without_manifest(self) -> None:
        legacy = self.root / "legacy.tar.gz"
        with tarfile.open(legacy, "w:gz") as archive:
            info = tarfile.TarInfo("config.yaml")
            content = b"database: {}\n"
            info.size = len(content)
            import io
            archive.addfile(info, io.BytesIO(content))
        for script in (RESTORE, UMBRELLA_RESTORE):
            result = self.restore(script, legacy)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exactly one manifest.json", result.stdout)

    def test_migration_dry_run_does_not_claim_restore_completed(self) -> None:
        path = self.backup()
        result = self.run_script(HERE / "hs-migrate.sh", "--target-host", "test-target", "--backup", str(path), "--dry-run", "--json")
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertFalse(json.loads(result.stdout)["restore_completed"])

    def test_restore_copy_failure_leaves_stopped_service_stopped(self) -> None:
        path = self.backup()
        shutil.rmtree(self.data_dir)
        self.data_dir.write_text("blocks database restore directory", encoding="utf-8")
        event_log = self.root / "service.log"
        fake_systemctl = self.bin / "systemctl"
        fake_systemctl.write_text(
            "#!/usr/bin/env bash\nprintf '%s\\n' \"$1\" >> \"$SERVICE_LOG\"\n"
            "if [[ $1 == is-active ]]; then exit 0; fi\nexit 0\n",
            encoding="utf-8",
        )
        fake_systemctl.chmod(0o755)
        fake_sudo = self.bin / "sudo"
        fake_sudo.write_text("#!/usr/bin/env bash\nexec \"$@\"\n", encoding="utf-8")
        fake_sudo.chmod(0o755)
        result = self.restore(
            UMBRELLA_RESTORE, path,
            env={"HEADSCALE_SKIP_SERVICE_CONTROL": "0", "SERVICE_LOG": str(event_log)},
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("service was left stopped", result.stdout)
        events = event_log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(events, ["is-active", "stop"])

    def test_restore_removes_stale_genuine_sqlite_wal_before_database_reuse(self) -> None:
        with sqlite3.connect(self.db) as connection:
            self.assertEqual(connection.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower(), "wal")
        path = self.backup()
        connection = sqlite3.connect(self.db)
        connection.execute("INSERT INTO nodes(name) VALUES ('stale-wal-node')")
        connection.commit()
        wal_path = Path(f"{self.db}-wal")
        shm_path = Path(f"{self.db}-shm")
        self.assertTrue(wal_path.is_file())
        captured_wal = wal_path.read_bytes()
        captured_shm = shm_path.read_bytes() if shm_path.exists() else None
        connection.close()
        wal_path.write_bytes(captured_wal)
        if captured_shm is not None:
            shm_path.write_bytes(captured_shm)

        proof_db = self.root / "wal-proof.sqlite"
        shutil.copy2(self.db, proof_db)
        shutil.copy2(wal_path, Path(f"{proof_db}-wal"))
        if shm_path.exists():
            shutil.copy2(shm_path, Path(f"{proof_db}-shm"))
        with sqlite3.connect(proof_db) as proof:
            names = {row[0] for row in proof.execute("SELECT name FROM nodes")}
        self.assertIn("stale-wal-node", names)

        result = self.restore(RESTORE, path)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertFalse(wal_path.exists())
        self.assertFalse(shm_path.exists())
        with sqlite3.connect(self.db) as restored:
            names = {row[0] for row in restored.execute("SELECT name FROM nodes")}
        self.assertEqual(names, {"fixture-node"})

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
        self.assertIn(str(self.db), (self.config_dir / "config.yaml").read_text(encoding="utf-8"))
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
        self.assertIn("root remapping for database is not safe", result.stdout)
        self.assertEqual((self.config_dir / "config.yaml").read_text(encoding="utf-8"), "keep this file\n")

    def test_tls_root_remapping_is_rejected_before_any_write(self) -> None:
        path = self.backup()
        (self.config_dir / "config.yaml").write_text("keep this config\n", encoding="utf-8")
        result = self.restore(RESTORE, path, extra=("--certs-dir", str(self.root / "new-certs")))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("root remapping for tls_cert is not safe", result.stdout)
        self.assertEqual((self.config_dir / "config.yaml").read_text(encoding="utf-8"), "keep this config\n")
        self.assertFalse((self.root / "new-certs").exists())

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
            f"database_path: {self.db}\n",
            f"database:\n  path: {self.db}\n",
        ):
            config.write_text(contents, encoding="utf-8")
            result = self.run_script(BACKUP, "--dry-run", "--json", "--config", str(config), "--data-dir", str(self.data_dir), "--certs-dir", str(self.certs_dir))
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        config.write_text(
            f"database:\n  type: sqlite3\n  path: {self.db}\n  postgres:\n    host: unused.example\n",
            encoding="utf-8",
        )
        result = self.run_script(BACKUP, "--dry-run", "--json", "--config", str(config), "--data-dir", str(self.data_dir), "--certs-dir", str(self.certs_dir))
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        config.write_text("database:\n  postgres:\n    host: db.example\n", encoding="utf-8")
        result = self.run_script(BACKUP, "--dry-run", "--json", "--config", str(config), "--data-dir", str(self.data_dir), "--certs-dir", str(self.certs_dir))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PostgreSQL", result.stdout)


if __name__ == "__main__":
    if "--help" in sys.argv[1:]:
        print(__doc__)
        raise SystemExit(0)
    if sys.argv[1:] == ["--dry-run"]:
        print("Headscale archive fixture tests; no infrastructure changes are made.")
        raise SystemExit(0)
    unittest.main()
