"""Worker IPC server — maintains a warm backend adapter for fast reuse.

The worker listens on a Unix domain socket (loopback only — no network exposure).
It uses a simple JSON-line protocol: each request is a single JSON line,
each response is a single JSON line.

The worker maintains a single FakeAdapter instance (or GhidraAdapter when
configured) that stays warm across requests, avoiding cold-start costs.
"""

from __future__ import annotations

import contextlib
import json
import os
import signal
import socket
import time
from typing import Any

from binary_analysis.adapters.fake import FakeAdapter

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORKER_DIR = os.path.join(os.path.expanduser("~"), ".binary-analysis")
DEFAULT_BUFFER_SIZE = 65536


# ---------------------------------------------------------------------------
# PID file helpers
# ---------------------------------------------------------------------------


def _ensure_worker_dir() -> str:
    """Create the worker runtime directory if it doesn't exist."""
    os.makedirs(WORKER_DIR, exist_ok=True)
    return WORKER_DIR


def _pid_path() -> str:
    """Return the path to the worker PID file."""
    return os.path.join(WORKER_DIR, "worker.pid")


def _socket_path() -> str:
    """Return the path to the worker Unix domain socket."""
    return os.path.join(WORKER_DIR, "worker.sock")


def _started_at_path() -> str:
    """Return the path to the worker started-at timestamp file."""
    return os.path.join(WORKER_DIR, "worker.started_at")


# ---------------------------------------------------------------------------
# Worker server
# ---------------------------------------------------------------------------


class WorkerServer:
    """IPC server that maintains a warm backend adapter.

    The server accepts connections on a Unix domain socket and processes
    JSON-line requests. Each request must include an "action" field
    ("execute", "ping", or "shutdown").

    The server runs in the foreground; daemonization is handled by the
    ``binary worker start`` CLI command via fork.
    """

    def __init__(self) -> None:
        self._adapter: FakeAdapter | None = None
        self._running = False
        self._started_at: float = 0.0
        self._socket: socket.socket | None = None

    @property
    def adapter(self) -> FakeAdapter:
        """Return the warm backend adapter, initializing on first access."""
        if self._adapter is None:
            self._adapter = FakeAdapter()
            self._adapter.set_fixture("pe-default", FakeAdapter.pe_fixture())
            self._adapter.set_fixture("elf-default", FakeAdapter.elf_fixture())
            self._adapter.set_fixture("macho-default", FakeAdapter.macho_fixture())
        return self._adapter

    @property
    def started_at(self) -> float:
        """Return the monotonic start time of the worker."""
        return self._started_at

    def start(self) -> None:
        """Start the worker server.

        Creates the PID file, socket, and starts accepting connections.
        Blocks until shutdown is requested.
        """
        _ensure_worker_dir()

        # Remove any stale socket
        sock_path = _socket_path()
        if os.path.exists(sock_path):
            os.unlink(sock_path)

        # Write PID file
        pid = os.getpid()
        with open(_pid_path(), "w") as f:
            f.write(str(pid))

        # Write started_at timestamp
        self._started_at = time.monotonic()
        with open(_started_at_path(), "w") as f:
            f.write(str(self._started_at))

        # Pre-warm the adapter
        _ = self.adapter

        # Create and bind socket
        server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_sock.bind(sock_path)
        server_sock.listen(5)
        self._socket = server_sock
        self._running = True

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

        while self._running:
            try:
                server_sock.settimeout(1.0)
                conn, _addr = server_sock.accept()
                self._handle_connection(conn)
            except TimeoutError:
                continue
            except OSError:
                break

        self._cleanup()

    def stop(self) -> None:
        """Signal the server to stop."""
        self._running = False
        if self._socket:
            with contextlib.suppress(OSError):
                self._socket.close()

    def _handle_signal(self, signum: int, frame: Any) -> None:
        """Handle SIGTERM/SIGINT for graceful shutdown."""
        self.stop()

    def _handle_connection(self, conn: socket.socket) -> None:
        """Handle a single client connection."""
        conn.settimeout(30.0)
        data = b""
        while True:
            try:
                chunk = conn.recv(DEFAULT_BUFFER_SIZE)
                if not chunk:
                    break
                data += chunk
                if b"\n" in data:
                    break
            except TimeoutError:
                break

        if data:
            # Parse request (single JSON line)
            try:
                request: dict[str, Any] = json.loads(data.decode("utf-8").strip())
            except (json.JSONDecodeError, UnicodeDecodeError):
                response: dict[str, Any] = {"success": False, "error": "Invalid JSON request"}
                conn.sendall((json.dumps(response) + "\n").encode("utf-8"))
            else:
                action = request.get("action", "")

                if action == "ping":
                    response = {"success": True, "pong": True, "pid": os.getpid()}
                elif action == "shutdown":
                    response = {"success": True, "message": "Shutting down"}
                    conn.sendall((json.dumps(response) + "\n").encode("utf-8"))
                    self.stop()
                    with contextlib.suppress(OSError):
                        conn.close()
                    return
                elif action == "execute":
                    response = self._execute_command(request)
                else:
                    response = {"success": False, "error": f"Unknown action: {action}"}

                conn.sendall((json.dumps(response) + "\n").encode("utf-8"))

        with contextlib.suppress(OSError):
            conn.close()

    def _execute_command(self, request: dict[str, Any]) -> dict[str, Any]:
        """Execute a command through the warm backend adapter.

        In the current version, the worker serves a subset of commands.
        For commands not yet routed through the worker, the CLI falls back
        to one-shot mode transparently.
        """
        cmd = request.get("command", "")

        if cmd == "metadata":
            return self._exec_metadata(request)
        else:
            return {"success": False, "error": f"Unsupported worker command: {cmd}"}

    def _exec_metadata(self, request: dict[str, Any]) -> dict[str, Any]:
        """Execute a metadata request through the warm adapter."""
        project_path = request.get("project_path", "")

        from uuid import UUID

        from binary_analysis.domain.entities import Binary
        from binary_analysis.projects.manifest import load_manifest

        manifest = load_manifest(project_path)
        binary_data = manifest.get("binary", {})
        raw_id = str(binary_data.get("id", ""))
        try:
            binary_uuid = UUID(raw_id) if raw_id else UUID(int=0)
        except ValueError:
            binary_uuid = UUID(int=0)

        binary_entity = Binary(
            id=binary_uuid,
            sha256=str(binary_data.get("sha256", "")),
            path=str(binary_data.get("path", "")),
            format=str(binary_data.get("format", "unknown")),
            size_bytes=int(binary_data.get("size_bytes", 0)),
        )

        metadata = self.adapter.get_metadata(binary_entity)
        entry_point = metadata.entry_point
        return {
            "success": True,
            "data": {
                "format": metadata.format,
                "architecture": metadata.architecture,
                "endianness": metadata.endianness,
                "size_bytes": metadata.size_bytes,
                "entry_point": (
                    {
                        "space": entry_point.space,
                        "offset": entry_point.offset,
                        "display": entry_point.display,
                    }
                    if entry_point
                    else None
                ),
            },
        }

    def _cleanup(self) -> None:
        """Clean up PID file, socket, and other resources."""
        # Remove PID file
        pid_path = _pid_path()
        if os.path.exists(pid_path):
            with contextlib.suppress(OSError):
                os.unlink(pid_path)

        # Remove socket
        sock_path = _socket_path()
        if os.path.exists(sock_path):
            with contextlib.suppress(OSError):
                os.unlink(sock_path)

        # Close socket
        if self._socket:
            with contextlib.suppress(OSError):
                self._socket.close()

        self._running = False


def run_worker() -> None:
    """Entry point for running the worker server in the foreground.

    Used by ``binary worker start`` after forking.
    """
    server = WorkerServer()
    server.start()


if __name__ == "__main__":
    run_worker()
