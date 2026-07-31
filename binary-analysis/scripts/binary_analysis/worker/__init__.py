"""Optional local worker — IPC server and client.

The worker is an optional background process that maintains a warm backend
adapter, reducing cold-start costs for repeated analysis operations. When the
worker is not running, all commands function identically in one-shot mode.

Components:
  - WorkerServer: Unix domain socket IPC server with warm adapter
  - WorkerClient: Client for communicating with the worker
  - get_worker_status(): Convenience function to check worker state
"""

from __future__ import annotations

from binary_analysis.worker.client import WorkerClient, get_worker_status, read_pid
from binary_analysis.worker.server import WorkerServer, run_worker

__all__ = [
    "WorkerClient",
    "WorkerServer",
    "get_worker_status",
    "read_pid",
    "run_worker",
]
