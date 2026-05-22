# Python API Client Pattern

Use this pattern when your CLI wraps an HTTP API. Two key design decisions:
1. **Lazy auth** — credentials checked at request time, not client creation time
2. **Pre-parsed global flags** — `--json` and `--dry-run` work in any position

## Client Class

```python
import json, os, sys, warnings
import requests
from typing import Dict, Any, Optional, List

DEFAULT_SERVER = os.getenv("MYTOOL_SERVER", "http://localhost:8080")
ENV_API_KEY = os.getenv("MYTOOL_API_KEY", "")


class MyToolError(Exception):
    pass


class MyToolClient:
    """API client with lazy auth, dry-run, and error wrapping."""

    def __init__(self, server: str, api_key: str = "", dry_run: bool = False):
        self.server = server.rstrip("/")
        self.api_key = api_key or ENV_API_KEY
        self.dry_run = dry_run
        self._token: Optional[str] = None
        self._token_file = os.path.expanduser("~/.mytool_token")

        # Auto-load saved JWT token
        if not self.api_key:
            try:
                with open(self._token_file) as f:
                    saved = f.read().strip()
                    if saved:
                        self._token = saved
            except (OSError, IOError):
                pass

    # ── Auth Headers ──────────────────────────────────────────

    def _headers(self) -> Dict[str, str]:
        """Build auth headers. Priority: JWT token > API key > no auth."""
        h: Dict[str, str] = {}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        elif self.api_key:
            # VERIFY header name against YOUR server.
            # Common options: X-API-Key, Authorization: Bearer, Authorization: Token
            h["X-API-Key"] = self.api_key
        if not any("files" in k for k in ["_files"]):
            h["Content-Type"] = "application/json"
        return h

    # ── Centralized HTTP Request ──────────────────────────────

    def _request(self, method: str, path: str,
                 params: Optional[Dict] = None,
                 json_data: Any = None,
                 files: Optional[Dict] = None) -> Dict[str, Any]:
        """Centralized HTTP request with error wrapping.

        Credentials checked HERE, not in __init__.
        This lets --help and --dry-run work without any API key configured.
        """
        url = f"{self.server}{path}"
        headers = self._headers()

        if files:
            headers.pop("Content-Type", None)  # requests sets multipart boundary

        # Dry-run: return a safe empty shape matching what the handler expects
        if self.dry_run:
            msg = f"[dry-run] {method.upper()} {path}"
            info = {"dry_run": True, "method": method.upper(), "url": url,
                    "params": params, "json": json_data}
            print(msg, file=sys.stderr)
            # Return empty shape that won't crash the handler
            return {"items": [], "total_count": 0}

        # Check credentials only on real API calls
        if not self.api_key and not self._token:
            raise MyToolError(
                "No credentials configured.\n"
                "  Set MYTOOL_API_KEY environment variable or login with:\n"
                "  mytool login --username <user> --password <pass>"
            )

        try:
            resp = requests.request(method=method, url=url,
                                    params=params, json=json_data,
                                    files=files, headers=headers, timeout=120)
        except requests.ConnectionError as e:
            raise MyToolError(
                f"Cannot connect to {self.server}: {e}\n"
                f"  Is the server running? Set MYTOOL_SERVER or use --server."
            )

        if resp.status_code == 204:
            return {}

        try:
            body = resp.json()
        except (json.JSONDecodeError, ValueError):
            body_text = resp.text.strip()
            if not body_text:
                return {}
            body = {"raw": body_text[:500]}

        if resp.status_code == 401:
            raise MyToolError(
                f"Auth failed (401). Check your credentials.\n"
                f"  Server response: {body.get('detail', body.get('message', str(body)))}"
            )
        if resp.status_code >= 400:
            detail = body.get("detail", body.get("message", str(body)))
            raise MyToolError(f"API error ({resp.status_code}): {detail}")

        return body

    # ── Form-Encoded Login ────────────────────────────────────

    def _form_post(self, path: str, data: Dict[str, str]) -> Dict[str, Any]:
        """For login/oauth endpoints that need form-encoded data, not JSON."""
        url = f"{self.server}{path}"
        if self.dry_run:
            return {"dry_run": True, "method": "POST", "url": url, "form": data}
        try:
            resp = requests.post(url, data=data, timeout=30)
        except requests.ConnectionError as e:
            raise MyToolError(f"Cannot connect: {e}")
        try:
            body = resp.json()
        except (json.JSONDecodeError, ValueError):
            body = {"raw": resp.text[:500]}
        if resp.status_code == 401:
            raise MyToolError("Login failed: incorrect credentials")
        if resp.status_code >= 400:
            detail = body.get("detail", body.get("message", str(body)))
            raise MyToolError(f"Login error ({resp.status_code}): {detail}")
        return body

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Form-based login with token persistence."""
        result = self._form_post("/login", {"username": username, "password": password})
        if "token" in result:
            self._token = result["token"]
            try:
                with open(self._token_file, "w") as f:
                    f.write(self._token)
            except OSError:
                pass
        return result

    # ── Endpoint Methods ──────────────────────────────────────

    def list_items(self, limit: int = 50) -> Dict[str, Any]:
        return self._request("GET", "/items", params={"limit": limit})

    def get_item(self, item_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/items/{item_id}")

    def create_item(self, name: str, **kwargs) -> Dict[str, Any]:
        return self._request("POST", "/items", json_data={"name": name, **kwargs})

    def delete_item(self, item_id: str) -> Dict[str, Any]:
        return self._request("DELETE", f"/items/{item_id}")

    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """File upload using multipart — Content-Type set by requests."""
        with open(os.path.abspath(file_path), "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            return self._request("POST", "/items/upload", files=files)
```

## Argparse Dispatch with Pre-Parsed Global Flags

The fundamental argparse pitfall: argparse routes all unrecognized flags after a subcommand name to that subparser. If `--json` is only defined on the main parser, `tool subcommand --json` fails.

**Fix: pre-parse global flags from argv before argparse sees them.**

```python
def _preparse_global_flags(argv: List[str]) -> tuple[Dict[str, Any], List[str]]:
    """Strip global flags from argv regardless of position.

    Returns (globals_dict, filtered_argv) where filtered_argv has only
    positional args and subcommand-specific flags, ready for argparse.
    """
    GLOBAL_BOOLS = {"--json", "--dry-run", "--force", "--quiet", "--verbose"}
    GLOBAL_VALUES = {"--server", "--key"}
    globals_map: Dict[str, Any] = {}
    filtered: List[str] = [argv[0]]
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg in GLOBAL_BOOLS:
            globals_map[arg.lstrip("-").replace("-", "_")] = True
            i += 1
        elif arg in GLOBAL_VALUES:
            key = arg.lstrip("-").replace("-", "_")
            if i + 1 < len(argv) and not argv[i + 1].startswith("-"):
                globals_map[key] = argv[i + 1]
                i += 2
            else:
                globals_map[key] = ""
                i += 1
        elif arg == "--":
            filtered.extend(argv[i:])
            break
        else:
            filtered.append(arg)
            i += 1
    return globals_map, filtered


def main():
    # 1. Strip global flags from anywhere in argv
    global_flags, filtered_argv = _preparse_global_flags(sys.argv)

    # 2. Suppress Python warnings in machine mode
    if global_flags.get("json"):
        warnings.simplefilter("ignore")

    # 3. Let argparse handle the filtered args
    parser = argparse.ArgumentParser(prog="mytool")
    parser.add_argument("--server", default="")
    # ... subparsers, etc.
    args = parser.parse_args(filtered_argv[1:])

    # 4. Merge: explicit argparse value > pre-parsed global > env var
    server = args.server or global_flags.get("server") or os.getenv("MYTOOL_SERVER", DEFAULT_SERVER)
    dry_run = global_flags.get("dry_run", False)
    json_mode = global_flags.get("json", False)

    client = MyToolClient(server=server, dry_run=dry_run)
    # ... dispatch to subcommand handlers ...
```

This handles `--json` in any position:
- `mytool --json subcommand --flag value` (before subcommand)
- `mytool subcommand --flag value --json` (after subcommand)
- `mytool subcommand --json subsub --name foo` (deep nesting)

## Env Var File-Read Fallback

Terminal subprocesses may not inherit environment variables from the parent agent process. Always implement a file-read fallback:

```python
def _get_env(key: str, default: str = "") -> str:
    """Get env var with ~/.mytool.env file-read fallback."""
    val = os.getenv(key)
    if val:
        return val
    env_path = os.path.expanduser("~/.mytool.env")
    if os.path.isfile(env_path):
        try:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("export "):
                        line = line[len("export "):]
                    if line.startswith(f"{key}="):
                        return line.split("=", 1)[1].strip("\"'")
        except OSError:
            pass
    return default
```

Call this at module level to set defaults even when env vars aren't inherited.
