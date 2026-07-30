"""Worker IPC client — connects to the worker server for warm-backend requests.

When the worker is available, commands can route through the client for
faster response times (avoiding cold-start costs). When the worker is
unavailable, commands fall back to one-shot mode transparently.
"""

from __future__ import annotations

import contextlib
import json
import os
import socket
from typing import Any

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

WORKER_DIR = os.path.join(os.path.expanduser("~"), ".binary-analysis")


def _socket_path() -> str:
    """Return the path to the worker Unix domain socket."""
    return os.path.join(WORKER_DIR, "worker.sock")


def _pid_path() -> str:
    """Return the path to the worker PID file."""
    return os.path.join(WORKER_DIR, "worker.pid")


def _started_at_path() -> str:
    """Return the path to the worker started-at timestamp file."""
    return os.path.join(WORKER_DIR, "worker.started_at")


# ---------------------------------------------------------------------------
# Worker client
# ---------------------------------------------------------------------------


class WorkerClient:
    """Client for communicating with the worker IPC server.

    Usage::

        client = WorkerClient()
        if client.is_available():
            result = client.send_request({"action": "execute", "command": "metadata", ...})
            # use worker-backed result
        else:
            # fall back to one-shot mode
    """

    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = timeout

    def is_available(self) -> bool:
        """Check whether the worker is running and reachable.

        Returns True if we can connect to the worker socket and get a
        successful ping response.
        """
        sock_path = _socket_path()
        if not os.path.exists(sock_path):
            return False

        # Also check that the PID file is valid
        if not _is_pid_alive():
            return False

        try:
            result = self.send_request({"action": "ping"})
            return result.get("success", False) is True
        except (OSError, ConnectionRefusedError, TimeoutError):
            return False

    def send_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Send a request to the worker and return the response.

        Args:
            request: A dict with at minimum an "action" field.

        Returns:
            The JSON-decoded response dict.

        Raises:
            OSError: If connection fails.
            TimeoutError: If the connection times out.
            json.JSONDecodeError: If the response is not valid JSON.
        """
        sock_path = _socket_path()
        if not os.path.exists(sock_path):
            raise OSError(f"Worker socket not found: {sock_path}")

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(self._timeout)

        try:
            sock.connect(sock_path)

            # Send request (single JSON line)
            payload = json.dumps(request).encode("utf-8") + b"\n"
            sock.sendall(payload)

            # Read response (single JSON line)
            response_data = b""
            while b"\n" not in response_data:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                response_data += chunk

            if not response_data:
                raise OSError("Worker closed connection without response")

            result: dict[str, Any] = json.loads(response_data.decode("utf-8").strip())
            return result
        finally:
            with contextlib.suppress(OSError):
                sock.close()


# ---------------------------------------------------------------------------
# Process management helpers
# ---------------------------------------------------------------------------


def _is_pid_alive() -> bool:
    """Check if the PID in the PID file corresponds to a running process."""
    pid_path = _pid_path()
    if not os.path.exists(pid_path):
        return False

    try:
        with open(pid_path) as f:
            pid_str = f.read().strip()
        if not pid_str:
            return False
        pid = int(pid_str)
    except (ValueError, OSError):
        return False

    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def read_pid() -> int | None:
    """Read the worker PID from the PID file.

    Returns None if the PID file doesn't exist, is empty, or is invalid.
    """
    pid_path = _pid_path()
    if not os.path.exists(pid_path):
        return None

    try:
        with open(pid_path) as f:
            pid_str = f.read().strip()
        if not pid_str:
            return None
        return int(pid_str)
    except (ValueError, OSError):
        return None


def read_started_at() -> float | None:
    """Read the worker started_at timestamp from the file.

    Returns None if the file doesn't exist or is invalid.
    """
    path = _started_at_path()
    if not os.path.exists(path):
        return None

    try:
        with open(path) as f:
            value = f.read().strip()
        if not value:
            return None
        return float(value)
    except (ValueError, OSError):
        return None


def get_worker_status() -> dict[str, Any]:
    """Get the current worker status.

    Returns a dict with:
      - state: "running" or "stopped"
      - pid: integer PID when running, null when stopped
      - uptime_seconds: float when running, null when stopped
    """
    pid = read_pid()
    if pid is not None and _is_pid_alive():
        started_at = read_started_at()
        import time

        uptime = None
        if started_at is not None:
            uptime = time.monotonic() - started_at

        return {
            "state": "running",
            "pid": pid,
            "uptime_seconds": round(uptime, 3) if uptime is not None else None,
        }
    else:
        return {
            "state": "stopped",
            "pid": None,
            "uptime_seconds": None,
        }
