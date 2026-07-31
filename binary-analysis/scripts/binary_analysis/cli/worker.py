"""Worker commands — start, stop, and status for the optional local worker.

The worker is an optional background process that maintains a warm
backend adapter, reducing cold-start costs for repeated analysis operations.
When the worker is not running, all commands function identically in
one-shot mode (direct backend adapter initialization).

Worker start is idempotent: if already running, it reports "already running".
Worker stop is idempotent: if not running, it reports "not running".
Worker status reports running/stopped state with PID and uptime_seconds.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import signal
import sys
import time
from typing import Any

from binary_analysis.domain.errors import BinaryAnalysisError

# ---------------------------------------------------------------------------
# Path to the binary CLI entrypoint (for starting worker subprocess)
# ---------------------------------------------------------------------------

_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_BINARY_CLI = os.path.join(_SCRIPTS_DIR, "binary")


def add_subparser(subparsers: Any) -> argparse.ArgumentParser:
    """Register the worker subcommand."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "worker",
        help="Manage the optional local worker daemon.",
        description=(
            "Manage the optional local worker daemon. The worker is an "
            "optional background process that maintains a warm backend "
            "adapter for faster repeated analysis. All CLI commands "
            "function correctly without the worker via one-shot mode."
        ),
    )
    worker_sub = parser.add_subparsers(dest="worker_command", help="Worker subcommands")

    # worker start
    start_parser = worker_sub.add_parser(
        "start",
        help="Start the optional local worker daemon (idempotent).",
        description="Start the local worker daemon. If already running, reports 'already running'.",
    )
    start_parser.add_argument(
        "--daemon",
        action="store_true",
        default=True,
        help=argparse.SUPPRESS,  # Hidden; daemon mode is default
    )

    # worker stop
    _stop_parser = worker_sub.add_parser(
        "stop",
        help="Stop the local worker daemon (idempotent).",
        description="Stop the local worker daemon. If not running, reports 'not running'.",
    )

    # worker status
    _status_parser = worker_sub.add_parser(
        "status",
        help="Report worker daemon state.",
        description="Report whether the worker is running or stopped, with PID and uptime.",
    )

    return parser


def execute(args: argparse.Namespace) -> dict[str, Any]:
    """Dispatch to the appropriate worker subcommand."""
    worker_cmd = getattr(args, "worker_command", None)

    if not worker_cmd:
        raise BinaryAnalysisError("No worker subcommand specified. Available: start, stop, status.")

    if worker_cmd == "start":
        return execute_start(args)
    elif worker_cmd == "stop":
        return execute_stop(args)
    elif worker_cmd == "status":
        return execute_status(args)
    else:
        raise BinaryAnalysisError(f"Unknown worker subcommand: {worker_cmd}")


def execute_start(args: argparse.Namespace) -> dict[str, Any]:
    """Start the worker daemon.

    Idempotent: if the worker is already running, reports success with
    a message indicating "already running".
    """
    from binary_analysis.worker.client import get_worker_status

    status = get_worker_status()

    if status["state"] == "running":
        return {
            "success": True,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "INFO",
                    "category": "worker",
                    "message": f"Worker already running (PID {status['pid']}).",
                }
            ],
            "data": {
                "status": "already_running",
                "pid": status["pid"],
                "uptime_seconds": status["uptime_seconds"],
            },
        }

    # Start the worker in the background
    # The worker runs the server module directly
    import subprocess as _sp

    try:
        proc = _sp.Popen(
            [sys.executable, "-m", "binary_analysis.worker.server"],
            stdout=_sp.DEVNULL,
            stderr=_sp.DEVNULL,
            start_new_session=True,
        )

        # Wait briefly for the worker to start
        deadline = time.monotonic() + 10.0
        started = False
        while time.monotonic() < deadline:
            status = get_worker_status()
            if status["state"] == "running":
                started = True
                break
            time.sleep(0.1)

        if not started and proc.poll() is not None:
            # Worker didn't start in time; check if process is still alive
            return {
                "success": False,
                "partial": False,
                "warnings": [],
                "diagnostics": [
                    {
                        "severity": "ERROR",
                        "category": "worker",
                        "message": f"Worker process exited with code {proc.returncode}.",
                    }
                ],
                "data": {"status": "failed"},
            }

        status = get_worker_status()
        return {
            "success": True,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "INFO",
                    "category": "worker",
                    "message": f"Worker started (PID {status['pid']}).",
                }
            ],
            "data": {
                "status": "started",
                "pid": status["pid"],
            },
        }

    except Exception as e:
        return {
            "success": False,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "ERROR",
                    "category": "worker",
                    "message": f"Failed to start worker: {e}",
                }
            ],
            "data": {"status": "error"},
        }


def execute_stop(args: argparse.Namespace) -> dict[str, Any]:
    """Stop the worker daemon.

    Idempotent: if the worker is not running, reports success with
    a message indicating "not running".
    """
    from binary_analysis.worker.client import WorkerClient, get_worker_status, read_pid

    status = get_worker_status()

    if status["state"] == "stopped":
        return {
            "success": True,
            "partial": False,
            "warnings": [],
            "diagnostics": [
                {
                    "severity": "INFO",
                    "category": "worker",
                    "message": "Worker not running.",
                }
            ],
            "data": {
                "status": "not_running",
            },
        }

    # Try graceful shutdown via the socket
    with contextlib.suppress(OSError, TimeoutError):
        client = WorkerClient(timeout=5.0)
        client.send_request({"action": "shutdown"})

    # Force kill if still running after grace period
    time.sleep(0.5)
    status = get_worker_status()
    if status["state"] == "running":
        pid = read_pid()
        if pid is not None:
            with contextlib.suppress(OSError):
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.5)
                # Check again and use SIGKILL if still alive
                if _is_pid_alive_for_stop(pid):
                    os.kill(pid, signal.SIGKILL)

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [
            {
                "severity": "INFO",
                "category": "worker",
                "message": "Worker stopped.",
            }
        ],
        "data": {
            "status": "stopped",
        },
    }


def execute_status(args: argparse.Namespace) -> dict[str, Any]:
    """Report the current worker status.

    Returns state, pid, and uptime_seconds. PID is null when stopped.
    """
    from binary_analysis.worker.client import get_worker_status

    status = get_worker_status()

    return {
        "success": True,
        "partial": False,
        "warnings": [],
        "diagnostics": [],
        "data": status,
    }


def _is_pid_alive_for_stop(pid: int) -> bool:
    """Check if a PID is alive (used during stop sequence)."""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
