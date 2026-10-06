#!/usr/bin/env python3
"""Create and restore verified Headscale archives with explicit destination manifests."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

MANIFEST_NAME = "manifest.json"
MANIFEST_VERSION = 1


def fail(message: str) -> None:
    raise RuntimeError(message)


def scalar(value: str) -> str:
    value = value.split(" #", 1)[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return os.path.expanduser(os.path.expandvars(value))


def read_config(path: Path) -> dict[str, str]:
    """Read scalar paths from Headscale's supported flat/nested YAML path keys."""
    if not path.is_file():
        fail(f"Headscale config not found: {path}")
    sections: list[tuple[int, str]] = []
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        indent = len(line) - len(line.lstrip())
        key, raw = line.strip().split(":", 1)
        while sections and sections[-1][0] >= indent:
            sections.pop()
        full_key = ".".join([section for _, section in sections] + [key.strip()])
        raw = raw.strip()
        if not raw:
            sections.append((indent, key.strip()))
        else:
            value = scalar(raw)
            if value:
                values[full_key] = value
    return values


def resolve_config_path(value: str, config_file: Path) -> Path:
    if "$" in value:
        fail(f"unresolved environment variable in configured path: {value}")
    path = Path(value)
    return path if path.is_absolute() else (config_file.parent / path).resolve()


def absolute(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def resolve_assets(config_file: Path, data_dir: Path, certs_dir: Path) -> tuple[dict[str, Path], dict[str, Path], dict[str, bool]]:
    cfg = read_config(config_file)
    database_type = cfg.get("database.type", "").lower()
    postgres_configured = any(key.startswith("database.postgres") for key in cfg) or cfg.get("database", "").lower() in {"postgres", "postgresql"}
    sqlite_path_configured = any(key in cfg for key in ("database.sqlite.path", "database.path", "database_path"))
    if database_type in {"postgres", "postgresql"} or (not database_type and postgres_configured and not sqlite_path_configured):
        fail("PostgreSQL-backed Headscale is not supported by this SQLite backup helper")
    if database_type and database_type not in {"sqlite", "sqlite3"}:
        fail(f"unsupported Headscale database type: {database_type}")
    db_value = cfg.get("database.sqlite.path") or cfg.get("database.path") or cfg.get("database_path")
    if db_value is None:
        configured_database = any(key == "database" or key.startswith("database.") for key in cfg)
        if configured_database:
            fail("Headscale database is configured without a supported SQLite path")
        db_value = str(data_dir / "db.sqlite")
    db_path = resolve_config_path(db_value, config_file)
    policy_value = cfg.get("acl_policy_path") or cfg.get("policy_path") or cfg.get("policy.path")
    cert_value = cfg.get("tls_cert_path")
    key_value = cfg.get("tls_key_path")
    node_key_value = cfg.get("noise.private_key_path") or cfg.get("private_key_path")
    derp_key_value = cfg.get("derp.server.private_key_path")
    if bool(cert_value) != bool(key_value):
        fail("config must set both tls_cert_path and tls_key_path, or neither")

    sources: dict[str, Path] = {"config": config_file, "database": db_path}
    required = {"config": True, "database": True}
    destinations: dict[str, Path] = {"config": config_file.resolve(), "database": db_path}
    if policy_value:
        policy_path = resolve_config_path(policy_value, config_file)
        sources["policy"] = policy_path
        destinations["policy"] = policy_path
        required["policy"] = True
    else:
        policy_path = config_file.parent / "policy.json"
        if policy_path.is_file():
            sources["policy"] = policy_path
            destinations["policy"] = policy_path.resolve()
            required["policy"] = False

    for role, value, fallback in (
        ("tls_cert", cert_value, certs_dir / "server.crt"),
        ("tls_key", key_value, certs_dir / "server.key"),
        ("node_key", node_key_value, data_dir / "private.key"),
        ("derp_key", derp_key_value, data_dir / "derp_server.key"),
    ):
        if value:
            source = resolve_config_path(value, config_file)
            sources[role] = source
            destinations[role] = source
            required[role] = True
        elif fallback.is_file():
            sources[role] = fallback.resolve()
            destinations[role] = fallback.resolve()
            required[role] = False
    if not cert_value and not key_value and (certs_dir / "server.crt").is_file() != (certs_dir / "server.key").is_file():
        fail("standard TLS recovery assets are incomplete; provide both server.crt and server.key or neither")

    derp_path = config_file.parent / "derp.yaml"
    if derp_path.is_file():
        sources["derp"] = derp_path.resolve()
        destinations["derp"] = derp_path.resolve()
        required["derp"] = False

    return sources, destinations, required


def archive_name(role: str, source: Path) -> str:
    if role == "config":
        return "config/config.yaml"
    if role == "database":
        return "database/database.sqlite"
    if role == "policy":
        return "policy/policy.json"
    if role in {"tls_cert", "tls_key", "node_key", "derp_key"}:
        return f"keys/{role}-{source.name}"
    if role == "derp":
        return "derp/derp.yaml"
    return f"assets/{role}-{hashlib.sha256(str(source).encode()).hexdigest()[:12]}-{source.name}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_manifest(sources: dict[str, Path], destinations: dict[str, Path], required: dict[str, bool], root_dirs: dict[str, Path], backup_dir: Path) -> dict[str, Any]:
    assets = []
    seen_destinations: set[Path] = set()
    for role, source in sources.items():
        if not source.is_file():
            if required[role]:
                fail(f"required recovery asset is missing: {source} ({role})")
            continue
        target = destinations[role].resolve()
        if target in seen_destinations:
            fail(f"two archive entries resolve to the same restore path: {target}")
        seen_destinations.add(target)
        archive_path = archive_name(role, source)
        archived_file = backup_dir / archive_path
        archived_file.parent.mkdir(parents=True, exist_ok=True)
        if role == "database":
            db_cli = shutil.which("sqlite3")
            if not db_cli:
                fail("sqlite3 not found; install sqlite3 to take a consistent online database snapshot")
            sql_path = str(archived_file).replace("'", "''")
            proc = subprocess.run([db_cli, str(source), f".backup '{sql_path}'"], capture_output=True, text=True)
            if proc.returncode != 0:
                fail(f"sqlite3 .backup failed: {(proc.stderr or proc.stdout).strip()}")
            if not archived_file.is_file() or archived_file.stat().st_size == 0:
                fail("sqlite3 .backup did not produce a non-empty database snapshot")
            check = subprocess.run([db_cli, str(archived_file), "PRAGMA quick_check;"], capture_output=True, text=True)
            if check.returncode != 0 or check.stdout.strip() != "ok":
                fail(f"SQLite snapshot integrity check failed: {(check.stderr or check.stdout).strip()}")
            shutil.copymode(source, archived_file)
        else:
            shutil.copy2(source, archived_file)
        assets.append({
            "role": role,
            "archive_path": archive_path,
            "restore_path": str(target),
            "mode": source.stat().st_mode & 0o777,
            "size_bytes": archived_file.stat().st_size,
            "sha256": sha256_file(archived_file),
            "required": required[role],
        })
    roles = {asset["role"] for asset in assets}
    if not {"config", "database"}.issubset(roles):
        fail("backup is incomplete: config.yaml and the configured SQLite database are mandatory")
    return {
        "schema_version": MANIFEST_VERSION,
        "roots": {name: str(path.resolve()) for name, path in root_dirs.items()},
        "assets": assets,
    }


def backup(args: argparse.Namespace) -> int:
    config_file = absolute(args.config)
    data_dir = absolute(args.data_dir)
    config_dir = config_file.parent
    certs_dir = absolute(args.certs_dir)
    sources, destinations, required = resolve_assets(config_file, data_dir, certs_dir)
    missing = [f"{role}: {sources[role]}" for role in sources if required[role] and not sources[role].is_file()]
    if missing:
        fail("required recovery asset(s) missing: " + ", ".join(missing))
    if args.dry_run:
        payload = {"action": "backup", "dry_run": True, "output_dir": args.output_dir,
                   "items": [{"role": role, "path": str(path), "exists": path.is_file(), "required": required[role]}
                             for role, path in sources.items()]}
        print(json.dumps(payload, indent=2) if args.json else "\n".join(["Would back up:", *[f"  {x['role']}: {x['path']}" for x in payload["items"]]]))
        return 0
    if not args.auto and not confirm(f"Create a Headscale backup in {args.output_dir}? [y/N] "):
        print("Aborted.")
        return 0
    output_dir = absolute(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = f"headscale-{stamp}"
    destination = output_dir / f"{base}.tar.gz"
    if destination.exists():
        base = f"{base}-{os.getpid()}"
        destination = output_dir / f"{base}.tar.gz"
    with tempfile.TemporaryDirectory(prefix="headscale-backup-") as temporary:
        root = Path(temporary)
        package = root / base
        package.mkdir()
        manifest = make_manifest(sources, destinations, required,
                                 {"config": config_dir, "data": data_dir, "certs": certs_dir}, package)
        (package / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        staged_archive = root / f"{base}.tar.gz"
        with tarfile.open(staged_archive, "w:gz") as archive:
            archive.add(package, arcname=base)
        os.replace(staged_archive, destination)
    checksum = sha256_file(destination)
    payload = {"action": "backup", "dry_run": False, "backup_path": str(destination),
               "checksum_sha256": checksum, "asset_count": len(manifest["assets"]),
               "manifest": f"{base}/{MANIFEST_NAME}"}
    print(json.dumps(payload, indent=2) if args.json else f"Backup created: {destination}\nSHA-256: {checksum}\nRecovery assets: {len(manifest['assets'])}")
    return 0


def safe_member(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        fail(f"unsafe archive member path: {name}")
    return path


def read_archive(backup_path: Path) -> tuple[str, dict[str, Any], dict[str, tarfile.TarInfo]]:
    with tarfile.open(backup_path, "r:gz") as archive:
        members = archive.getmembers()
        member_map: dict[str, tarfile.TarInfo] = {}
        for member in members:
            safe_member(member.name)
            if member.isdir():
                continue
            if not member.isfile():
                fail(f"archive contains unsupported non-file member: {member.name}")
            if member.name in member_map:
                fail(f"archive contains a duplicate member: {member.name}")
            member_map[member.name] = member
        manifests = [name for name in member_map if name.endswith(f"/{MANIFEST_NAME}")]
        if len(manifests) != 1:
            fail("backup must contain exactly one manifest.json")
        manifest_name = manifests[0]
        base = manifest_name.rsplit("/", 1)[0]
        stream = archive.extractfile(member_map[manifest_name])
        if stream is None:
            fail("backup manifest is unreadable")
        manifest = json.load(stream)
    if not isinstance(manifest, dict) or manifest.get("schema_version") != MANIFEST_VERSION or not isinstance(manifest.get("assets"), list):
        fail("unsupported or malformed backup manifest")
    roots = manifest.get("roots")
    if not isinstance(roots, dict) or any(not isinstance(value, str) or not Path(value).is_absolute() for value in roots.values()):
        fail("backup manifest contains malformed root mappings")
    asset_roles: set[str] = set()
    expected_members = {manifest_name}
    known_roles = {"config", "database", "policy", "tls_cert", "tls_key", "node_key", "derp_key", "derp"}
    for asset in manifest["assets"]:
        if not isinstance(asset, dict) or not all(isinstance(asset.get(key), str) for key in ("role", "archive_path", "restore_path", "sha256")):
            fail("backup manifest contains malformed asset mapping")
        if (not isinstance(asset.get("mode"), int) or not 0 <= asset["mode"] <= 0o777
                or not isinstance(asset.get("size_bytes"), int) or asset["size_bytes"] < 0
                or not isinstance(asset.get("required"), bool)
                or len(asset["sha256"]) != 64 or any(char not in "0123456789abcdef" for char in asset["sha256"])):
            fail(f"backup manifest contains invalid metadata for {asset['role']}")
        if asset["role"] not in known_roles and not re.fullmatch(r"extra_tls_[1-9][0-9]*", asset["role"]):
            fail(f"backup manifest contains unsupported asset role: {asset['role']}")
        if asset["role"] in asset_roles:
            fail(f"backup manifest repeats asset role: {asset['role']}")
        asset_roles.add(asset["role"])
        relative = safe_member(asset["archive_path"])
        member_name = f"{base}/{relative.as_posix()}"
        if member_name in expected_members:
            fail(f"backup manifest repeats archive path: {asset['archive_path']}")
        expected_members.add(member_name)
        info = member_map.get(member_name)
        if info is None:
            fail(f"backup is missing manifested asset: {asset['archive_path']}")
        if not Path(asset["restore_path"]).is_absolute() or ".." in Path(asset["restore_path"]).parts:
            fail(f"manifest contains unsafe restore path for {asset['role']}")
        if info.size != asset["size_bytes"]:
            fail(f"backup asset size mismatch: {asset['archive_path']}")
        with tarfile.open(backup_path, "r:gz") as archive:
            stream = archive.extractfile(info)
            if stream is None:
                fail(f"backup asset is unreadable: {asset['archive_path']}")
            digest_state = hashlib.sha256()
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest_state.update(chunk)
            digest = digest_state.hexdigest()
        if digest != asset["sha256"]:
            fail(f"backup asset checksum mismatch: {asset['archive_path']}")
    if not {"config", "database"}.issubset(asset_roles):
        fail("backup manifest omits mandatory config or database recovery asset")
    extras = set(member_map) - expected_members
    if extras:
        fail(f"archive contains files not declared in its manifest: {', '.join(sorted(extras))}")
    return base, manifest, member_map


def target_path(asset: dict[str, Any], roots: dict[str, str], overrides: dict[str, Path]) -> Path:
    original = Path(asset["restore_path"])
    for root_name, override in overrides.items():
        old_root = Path(roots[root_name]) if isinstance(roots.get(root_name), str) else None
        if old_root is not None:
            try:
                relative = original.relative_to(old_root)
            except ValueError:
                continue
            return (override / relative).resolve()
    return original.resolve()


def apply_owner(path: Path, target: Path) -> None:
    """Keep an existing target's ownership; use its parent owner for a new file."""
    source = target if target.exists() else target.parent
    metadata = source.stat()
    os.chown(path, metadata.st_uid, metadata.st_gid)


def confirm(prompt: str) -> bool:
    try:
        return input(prompt).strip().lower() in {"y", "yes"}
    except EOFError:
        return False


def service_command(action: str, service: str) -> tuple[list[str] | None, bool]:
    sudo = [] if os.geteuid() == 0 else ([shutil.which("sudo")] if shutil.which("sudo") else [])
    if os.geteuid() != 0 and not sudo:
        fail("service control requires root privileges or sudo")
    systemctl = shutil.which("systemctl")
    if systemctl:
        status = subprocess.run(sudo + [systemctl, "is-active", "--quiet", service], check=False)
        if action == "stop" and status.returncode != 0:
            return None, False
        return sudo + [systemctl, action, service], True
    service_bin = shutil.which("service")
    if service_bin:
        return sudo + [service_bin, service, action], True
    fail("cannot safely restore because no supported service manager is available")


def restore(args: argparse.Namespace) -> int:
    backup_path = absolute(args.backup)
    if not backup_path.is_file():
        fail(f"backup not found: {backup_path}")
    base, manifest, member_map = read_archive(backup_path)
    roots = manifest.get("roots", {})
    overrides = {
        name: absolute(value)
        for name, value in (("config", args.config_dir), ("data", args.data_dir), ("certs", args.certs_dir))
        if value
    }
    items = []
    targets: set[Path] = set()
    with tarfile.open(backup_path, "r:gz") as archive:
        for asset in manifest["assets"]:
            target = target_path(asset, roots, overrides)
            if target in targets:
                fail(f"two archive assets resolve to the same restore path: {target}")
            targets.add(target)
            original_target = Path(asset["restore_path"]).resolve()
            if target != original_target:
                fail(f"root remapping for {asset['role']} is not safe because config.yaml and the service may still reference archived paths; restore to recorded destinations")
            member_name = f"{base}/{asset['archive_path']}"
            items.append({"role": asset["role"], "archive_path": member_name,
                          "target": str(target), "required": asset.get("required", False),
                          "mode": asset.get("mode", 0o600)})
            if args.dry_run:
                continue
        if args.dry_run:
            payload = {"action": "restore", "dry_run": True, "backup_path": str(backup_path), "backup_id": base, "items": items}
            print(json.dumps(payload, indent=2) if args.json else "\n".join(["Would restore:", *[f"  {x['role']}: {x['archive_path']} -> {x['target']}" for x in items]]))
            return 0
        if not args.force and not confirm(f"Restore {backup_path} to configured targets? This overwrites Headscale state. Type 'yes' to continue: "):
            print("Aborted.")
            return 0
        stopped = False
        restore_complete = False
        if not args.skip_service_control:
            stop_cmd, active = service_command("stop", args.service)
            if active and stop_cmd:
                subprocess.run(stop_cmd, check=True)
                stopped = True
        restored: list[str] = []
        try:
            for item, asset in zip(items, manifest["assets"]):
                target = Path(item["target"])
                target.parent.mkdir(parents=True, exist_ok=True)
                info = member_map[item["archive_path"]]
                stream = archive.extractfile(info)
                if stream is None:
                    fail(f"could not read archived file: {item['archive_path']}")
                descriptor, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.restore-", dir=target.parent)
                temporary = Path(temporary_name)
                try:
                    with os.fdopen(descriptor, "wb") as output:
                        shutil.copyfileobj(stream, output)
                    mode = 0o600 if asset["role"] in {"database", "tls_key", "node_key", "derp_key"} else item["mode"]
                    apply_owner(temporary, target)
                    os.chmod(temporary, mode)
                    os.replace(temporary, target)
                    if asset["role"] == "database":
                        for suffix in ("-wal", "-shm"):
                            Path(f"{target}{suffix}").unlink(missing_ok=True)
                finally:
                    temporary.unlink(missing_ok=True)
                restored.append(asset["role"])
            restore_complete = True
        except Exception as error:
            if stopped:
                fail(f"restore failed after stopping {args.service}; the service was left stopped to avoid running against partially restored state: {error}")
            raise
        finally:
            if stopped and restore_complete:
                start_cmd, active = service_command("start", args.service)
                if active and start_cmd:
                    subprocess.run(start_cmd, check=True)
    payload = {"action": "restore", "dry_run": False, "backup_path": str(backup_path),
               "backup_id": base, "restored": True, "restored_assets": restored}
    print(json.dumps(payload, indent=2) if args.json else f"Restored {len(restored)} verified recovery assets from {backup_path}")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    backup_parser = sub.add_parser("backup")
    backup_parser.add_argument("--config", default=os.environ.get("HEADSCALE_CONFIG", "/etc/headscale/config.yaml"))
    backup_parser.add_argument("--data-dir", default=os.environ.get("HEADSCALE_DATA_DIR", "/var/lib/headscale"))
    backup_parser.add_argument("--certs-dir", default=os.environ.get("HEADSCALE_CERTS_DIR", "/etc/headscale"))
    backup_parser.add_argument("--output-dir", default=str(Path.home() / "backups/headscale"))
    backup_parser.add_argument("--dry-run", action="store_true")
    backup_parser.add_argument("--json", action="store_true")
    backup_parser.add_argument("--auto", action="store_true")
    backup_parser.set_defaults(handler=backup)
    restore_parser = sub.add_parser("restore")
    restore_parser.add_argument("--backup", required=True)
    restore_parser.add_argument("--config-dir", default=os.environ.get("HEADSCALE_CONFIG_DIR"), help="Request a config-root override; rejected if it changes any recorded destination")
    restore_parser.add_argument("--data-dir", default=os.environ.get("HEADSCALE_DATA_DIR"), help="Request a data-root override; rejected if it changes any recorded destination")
    restore_parser.add_argument("--certs-dir", default=os.environ.get("HEADSCALE_CERTS_DIR"), help="Request a certs-root override; rejected if it changes any recorded destination")
    restore_parser.add_argument("--service", default=os.environ.get("HEADSCALE_SERVICE", "headscale"))
    restore_parser.add_argument("--dry-run", action="store_true")
    restore_parser.add_argument("--json", action="store_true")
    restore_parser.add_argument("--force", action="store_true")
    restore_parser.add_argument("--skip-service-control", action="store_true", help=argparse.SUPPRESS)
    restore_parser.set_defaults(handler=restore)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return args.handler(args)
    except (OSError, json.JSONDecodeError, RuntimeError, subprocess.CalledProcessError) as error:
        payload = {"ok": False, "error": str(error)}
        if getattr(args, "json", False):
            print(json.dumps(payload))
        else:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
