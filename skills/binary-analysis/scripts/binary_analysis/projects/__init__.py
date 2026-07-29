"""Project lifecycle — workspace, manifests, locking, and cache.

All persistent state mutations use atomic write patterns (tempfile + os.rename)
to ensure project.json is never partially written. File locks serialize
concurrent access. The manifest system detects corrupted project manifests
and raises InvalidConfigError (exit code 4) with diagnostic information.
"""

from __future__ import annotations

from binary_analysis.projects.atomic import (
    atomic_append_text,
    atomic_write_binary,
    atomic_write_json,
    atomic_write_lines,
    atomic_write_text,
)
from binary_analysis.projects.cache import (
    cache_clear,
    cache_delete,
    cache_get,
    cache_list,
    cache_set,
)
from binary_analysis.projects.lock import (
    LockError,
    acquire_lock,
    get_lock_holder,
    is_locked,
    release_lock,
)
from binary_analysis.projects.manifest import (
    create_manifest,
    load_manifest,
    save_manifest,
    update_manifest_field,
)
from binary_analysis.projects.workspace import (
    create_workspace,
    get_project_path,
    get_workspace_root,
    get_workspace_subdirs,
    list_workspaces,
    remove_workspace,
    validate_project_name,
    workspace_exists,
)

__all__ = [
    "LockError",
    "acquire_lock",
    "atomic_append_text",
    "atomic_write_binary",
    "atomic_write_json",
    "atomic_write_lines",
    "atomic_write_text",
    "cache_clear",
    "cache_delete",
    "cache_get",
    "cache_list",
    "cache_set",
    "create_manifest",
    "create_workspace",
    "get_lock_holder",
    "get_project_path",
    "get_workspace_root",
    "get_workspace_subdirs",
    "is_locked",
    "list_workspaces",
    "load_manifest",
    "release_lock",
    "remove_workspace",
    "save_manifest",
    "update_manifest_field",
    "validate_project_name",
    "workspace_exists",
]
