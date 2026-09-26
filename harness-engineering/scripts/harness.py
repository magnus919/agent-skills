#!/usr/bin/env python3
"""Structural discovery, non-overwriting scaffolds, and explicit check execution."""

import argparse
import contextlib
import datetime
import hashlib
import html
import json
import os
import selectors
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = {
    "instructions": ["AGENTS.md", "CLAUDE.md"],
    "tools": [".mcp.json", "mcp.json"],
    "environment": [
        "package.json",
        "pyproject.toml",
        "go.mod",
        "Cargo.toml",
        "package-lock.json",
        "uv.lock",
        ".python-version",
        ".nvmrc",
    ],
    "state": ["harness-state.json", "feature_list.json", "progress.md", "PROGRESS.md"],
    "feedback": ["Makefile", "init.sh", "checks.json"],
    "lifecycle": ["handoff.md", "session-handoff.md"],
}


def write_new(path, content):
    """Exclusive creation rejects existing files and symlinks."""
    with path.open("x", encoding="utf-8") as stream:
        stream.write(content)


def audit(target):
    findings = []
    for subsystem, names in CANDIDATES.items():
        found = [name for name in names if (target / name).is_file()]
        findings.append(
            {
                "area": subsystem,
                "artifacts": found,
                "observation": "artifacts_present" if found else "not_discovered",
                "interpretation": "Inspect content and enforcement; filenames do not prove behavior.",
            }
        )
    ci = target / ".github/workflows"
    if ci.is_dir():
        findings.append(
            {
                "area": "feedback",
                "artifacts": sorted(
                    str(p.relative_to(target)) for p in ci.iterdir() if p.is_file()
                ),
                "observation": "ci_files_present",
                "interpretation": "CI execution not assessed.",
            }
        )
    return {
        "schema_version": 1,
        "kind": "structural_audit",
        "target": str(target),
        "behavior": "not_assessed",
        "causal_bottleneck": "not_assessed",
        "limits": "Known root filenames only; alternative stores and nested routing require inspection.",
        "findings": findings,
    }


def scaffold(target, apply):
    mappings = {
        "AGENTS.md": "AGENTS.md",
        "state.json": "harness-state.json",
        "handoff.md": "handoff.md",
    }
    planned = [
        {
            "template": src,
            "path": dst,
            "action": "skip_existing" if os.path.lexists(target / dst) else "create",
        }
        for src, dst in mappings.items()
    ]
    if apply:
        target.mkdir(parents=True, exist_ok=True)
        for item in planned:
            if item["action"] == "create":
                try:
                    write_new(
                        target / item["path"], (ROOT / "templates" / item["template"]).read_text()
                    )
                except FileExistsError:
                    item["action"] = "skip_existing"
    return {
        "schema_version": 1,
        "kind": "scaffold",
        "applied": apply,
        "target": str(target),
        "files": planned,
        "behavior": "not_assessed",
        "next_action": "Reconcile with existing state stores and replace acceptance placeholders.",
    }


def commands_from(path):
    data = json.loads(path.read_text())
    if not isinstance(data, list) or not data:
        raise ValueError("commands must be a nonempty JSON list of argv lists")
    for argv in data:
        if (
            not isinstance(argv, list)
            or not argv
            or any(not isinstance(value, str) or not value or "\x00" in value for value in argv)
        ):
            raise ValueError("each command must be a nonempty argv list of nonempty strings")
    return data


def revision(target):
    try:
        return subprocess.run(
            ["git", "-C", str(target), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def dirty_state(target):
    try:
        output = subprocess.run(
            ["git", "-C", str(target), "status", "--porcelain"],
            capture_output=True,
            timeout=5,
            check=True,
        ).stdout
        return {"dirty": bool(output), "status_sha256": hashlib.sha256(output).hexdigest()}
    except (OSError, subprocess.SubprocessError):
        return {"dirty": None, "status_sha256": None}


def execute(argv, target, timeout, max_output_bytes=4_194_304):
    """Bound time/output without storing or printing raw command output."""
    started = time.monotonic()
    proc = None
    hashes = {"stdout": hashlib.sha256(), "stderr": hashlib.sha256()}
    sizes = {"stdout": 0, "stderr": 0}
    status = None
    try:
        proc = subprocess.Popen(
            argv,
            cwd=target,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        with selectors.DefaultSelector() as selector:
            selector.register(proc.stdout, selectors.EVENT_READ, "stdout")
            selector.register(proc.stderr, selectors.EVENT_READ, "stderr")
            while selector.get_map():
                remaining = timeout - (time.monotonic() - started)
                if remaining <= 0:
                    status = "timeout"
                    break
                for key, _ in selector.select(min(remaining, 0.1)):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    budget = max_output_bytes - sum(sizes.values())
                    hashes[key.data].update(chunk[:budget])
                    sizes[key.data] += len(chunk[:budget])
                    if len(chunk) > budget:
                        status = "output_limit"
                        break
                if status is not None:
                    break
            if status is None:
                remaining = max(0.001, timeout - (time.monotonic() - started))
                try:
                    proc.wait(timeout=remaining)
                    status = "exit_zero" if proc.returncode == 0 else "failed"
                except subprocess.TimeoutExpired:
                    status = "timeout"
    except KeyboardInterrupt:
        status = "cancelled"
    except OSError:
        status = "launch_error" if proc is None else "io_error"
    finally:
        if proc is not None:
            if status not in {"exit_zero", "failed"}:
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(proc.pid, signal.SIGKILL)
            for stream in [proc.stdout, proc.stderr]:
                if stream is not None:
                    stream.close()
            proc.wait()
    return {
        "argv": argv,
        "status": status,
        "returncode": proc.returncode if proc is not None else None,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "stdout_sha256": hashes["stdout"].hexdigest(),
        "stderr_sha256": hashes["stderr"].hexdigest(),
        "output_bytes": sizes,
        "output_complete": status in {"exit_zero", "failed"},
        "output_evidence": "hash_only; partial hashes on interruption/output limit; inspect authorized output separately",
    }


def verify(
    target, commands, execute_requested, timeout, max_output_bytes=4_194_304, checkpoint=None
):
    result = {
        "schema_version": 1,
        "kind": "command_execution",
        "target": str(target),
        "executed": execute_requested,
        "commands": commands,
        "acceptance": "not_assessed",
        "feature_state_changed": False,
    }
    if not execute_requested:
        return result
    result["started_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result["revision_before"] = revision(target)
    result["working_tree_before"] = dirty_state(target)
    result["results"] = []
    result["execution_state"] = "running"
    if checkpoint:
        checkpoint(result)
    for argv in commands:
        result["current_command"] = argv
        if checkpoint:
            checkpoint(result)
        outcome = execute(argv, target, timeout, max_output_bytes)
        result["results"].append(outcome)
        if checkpoint:
            checkpoint(result)
        if outcome["status"] != "exit_zero":
            break
    result["all_commands_exit_zero"] = len(result["results"]) == len(commands) and all(
        r["status"] == "exit_zero" for r in result["results"]
    )
    result["execution_state"] = "finished"
    result.pop("current_command", None)
    result["revision_after"] = revision(target)
    result["working_tree_after"] = dirty_state(target)
    result["limits"] = (
        "Exit codes do not establish test collection, semantic acceptance, or release approval."
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    for mode in ["audit", "scaffold", "verify"]:
        command = sub.add_parser(mode)
        command.add_argument("--target", type=Path, required=True)
        if mode == "audit":
            command.add_argument("--html", type=Path)
        if mode == "scaffold":
            command.add_argument("--apply", action="store_true")
        if mode == "verify":
            command.add_argument("--commands", type=Path, required=True)
            command.add_argument("--execute", action="store_true")
            command.add_argument("--timeout", type=float, default=60)
            command.add_argument("--report", type=Path)
            command.add_argument("--max-output-bytes", type=int, default=4_194_304)
    args = parser.parse_args()
    target = args.target.resolve()
    # Check prospective outputs before any command is run.
    output = getattr(args, "report", None) or getattr(args, "html", None)
    if output is not None:
        if os.path.lexists(output):
            parser.error("output already exists; choose a new report path")
        if not output.parent.is_dir():
            parser.error("output parent must already exist")
    if args.mode != "scaffold" and not target.is_dir():
        parser.error("target must be an existing directory")
    if target.exists() and not target.is_dir():
        parser.error("target must be a directory")
    try:
        if args.mode == "audit":
            result = audit(target)
            if args.html:
                write_new(
                    args.html,
                    '<!doctype html><meta charset="utf-8"><title>Harness audit</title>'
                    "<h1>Structural harness audit</h1><pre>"
                    + html.escape(json.dumps(result, indent=2))
                    + "</pre>",
                )
        elif args.mode == "scaffold":
            result = scaffold(target, args.apply)
        else:
            if not 0 < args.timeout <= 3600:
                parser.error("timeout must be greater than zero and at most 3600 seconds")
            commands = commands_from(args.commands)
            if args.execute and args.report is None:
                parser.error("--execute requires a new --report path")
            if not 1 <= args.max_output_bytes <= 67_108_864:
                parser.error("max-output-bytes must be between 1 and 67108864")
            if args.report:
                write_new(
                    args.report,
                    json.dumps({"execution_state": "prepared", "acceptance": "not_assessed"}),
                )

                def persist(record):
                    descriptor, name = tempfile.mkstemp(
                        prefix=".harness-report-", dir=args.report.parent
                    )
                    temporary = Path(name)
                    try:
                        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                            stream.write(json.dumps(record, indent=2) + "\n")
                            stream.flush()
                            os.fsync(stream.fileno())
                        os.replace(temporary, args.report)
                    finally:
                        temporary.unlink(missing_ok=True)

                result = verify(
                    target, commands, args.execute, args.timeout, args.max_output_bytes, persist
                )
                persist(result)
            else:
                result = verify(target, commands, args.execute, args.timeout, args.max_output_bytes)
        print(json.dumps(result, indent=2))
        return 1 if result.get("executed") and not result["all_commands_exit_zero"] else 0
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    sys.exit(main())
