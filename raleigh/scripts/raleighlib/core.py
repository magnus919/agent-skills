"""Shared HTTP, cache, and configuration utilities."""

from __future__ import annotations

import json
import os
import stat
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_TIMEOUT = 30
ENV_TIMEOUT = "RALEIGH_TIMEOUT"

# Fixed service hosts that the CLI may dereference. Any URL whose host is not in
# this allowlist is rejected before a network request is made. Hosts are stored
# without scheme/port and matched case-insensitively.
ALLOWED_HOSTS: frozenset[str] = frozenset({
    "data.raleighnc.gov",
    "ral.maps.arcgis.com",
    "services.arcgis.com",
    "maps.raleighnc.gov",
    "maps.wake.gov",
    "maps.wakegov.com",
    "services1.arcgis.com",
    "services3.arcgis.com",
    "utility.arcgis.com",
    "raleighnc-energovpub.tylerhost.net",
    "goraleigh.org",
    "www.goraleighlive.org",
    "www.goraleigh.org",
    "raleighnc.gov",
    "pub-raleighnc.escribemeetings.com",
})


USER_AGENT = (
    "RaleighCivicDataCLI/2.0 (read-only public data; Python urllib)"
)

# Maximum number of HTTP redirects the CLI will follow automatically.
MAX_REDIRECTS = 5

# Default response size caps, in bytes.
DEFAULT_MAX_JSON_BYTES = 5 * 1024 * 1024
DEFAULT_MAX_RAW_BYTES = 10 * 1024 * 1024


class SecurityError(Exception):
    """Raised when a requested URL is outside the fixed allowlist."""


class RequestPolicyError(SecurityError):
    """Raised when the HTTP method or path is not allowed."""


class ResponseTooLargeError(Exception):
    """Raised when a response exceeds the endpoint-appropriate size cap."""


def _get_timeout() -> int:
    """Return the active timeout, preferring the environment override."""
    env = os.environ.get(ENV_TIMEOUT)
    if env:
        try:
            return int(env)
        except ValueError:
            pass
    return DEFAULT_TIMEOUT


def is_allowed_host(url: str) -> bool:
    """Return True if url uses HTTPS and its final host is in the allowlist."""
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        return False
    if parsed.scheme != "https":
        return False
    try:
        port = parsed.port
    except ValueError:
        return False
    if port not in (None, 443) or parsed.username is not None or parsed.password is not None:
        return False
    host = parsed.hostname or ""
    return host.lower() in {h.lower() for h in ALLOWED_HOSTS}


def _origin(url: str) -> tuple[str, str, int]:
    """Return a normalized origin tuple for an already-validated HTTPS URL."""
    parsed = urllib.parse.urlparse(url)
    return (parsed.scheme.lower(), (parsed.hostname or "").lower(), parsed.port or 443)


def _request_headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {"User-Agent": USER_AGENT}
    if extra:
        headers.update(extra)
    return headers


# Service-specific headers that must be stripped when a redirect crosses hosts.
_SENSITIVE_HEADERS = frozenset({
    "tenantid",
    "tenantname",
    "tyler-tenanturl",
    "tyler-tenant-culture",
    "authorization",
    "cookie",
})


class AllowlistRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Follow redirects only to HTTPS allowlisted hosts.

    Service-specific headers are stripped on cross-origin redirects, and the
    total number of redirects is bounded.
    """

    max_redirections = MAX_REDIRECTS

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not is_allowed_host(newurl):
            raise SecurityError(f"Redirect led to a non-allowlisted host: {newurl}")
        # Strip sensitive headers when crossing origins.
        old_origin = _origin(req.full_url)
        new_origin = _origin(newurl)
        new_headers = dict(req.headers)
        if old_origin != new_origin:
            for name in list(new_headers):
                if name.lower() in _SENSITIVE_HEADERS:
                    del new_headers[name]
        # Preserve method/body only for 307/308; otherwise downgrade to GET.
        if code not in (307, 308):
            new_headers.pop("Content-Length", None)
            new_headers.pop("Content-Type", None)
            method = "GET"
            data = None
        else:
            method = req.get_method()
            data = req.data
        if data is not None and old_origin != new_origin:
            raise SecurityError("Cross-origin redirects cannot preserve a request body")
        _enforce_method_policy(method, newurl)
        return urllib.request.Request(
            newurl,
            headers=new_headers,
            method=method,
            data=data,
            origin_req_host=req.origin_req_host,
            unverifiable=True,
        )


# Prebuilt opener with the bounded allowlisted redirect handler.
_OPENER = urllib.request.build_opener(AllowlistRedirectHandler)


# Regex patterns for verified ArcGIS read-only POST endpoints.
_ARCGIS_POST_PATTERNS = (
    r"/arcgis/rest/services/.*/(FeatureServer|MapServer)/\d+/query$",
    r"/server/rest/services/.*/(FeatureServer|MapServer)/\d+/query$",
    r"/arcgis/rest/services/.*/GeocodeServer/geocodeAddresses$",
    r"/server/rest/services/.*/GeocodeServer/geocodeAddresses$",
)

_ARCGIS_POST_HOSTS = frozenset({
    "maps.raleighnc.gov",
    "maps.wake.gov",
    "maps.wakegov.com",
    "services.arcgis.com",
    "services1.arcgis.com",
    "services3.arcgis.com",
    "utility.arcgis.com",
})

_HOST_SCOPED_POST_PATHS: dict[str, frozenset[str]] = {
    "raleighnc-energovpub.tylerhost.net": frozenset({
        "/apps/selfservice/api/energov/search/search",
        "/apps/selfservice/api/energov/entity/inspections/search/search",
    }),
    "pub-raleighnc.escribemeetings.com": frozenset({
        "/MeetingsCalendarView.aspx/PastMeetings",
    }),
}


def _is_allowed_post(url: str) -> bool:
    """Return True if url is a known read-only POST endpoint."""
    import re
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.rstrip("/")
    host = (parsed.hostname or "").lower()
    host_paths = _HOST_SCOPED_POST_PATHS.get(host)
    if host_paths and path in host_paths:
        return True
    if host in _ARCGIS_POST_HOSTS:
        for pattern in _ARCGIS_POST_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                return True
    return False


def _enforce_method_policy(method: str | None, url: str) -> None:
    """Reject disallowed methods before any network I/O."""
    method = (method or "GET").upper()
    if method == "GET":
        return
    if method == "POST" and _is_allowed_post(url):
        return
    raise RequestPolicyError(
        f"HTTP {method} is not allowed for {url}"
    )


def require_object(payload: Any, operation: str = "JSON request") -> dict[str, Any]:
    """Return an object-shaped JSON value or raise an explicit protocol error."""
    if not isinstance(payload, dict):
        raise ValueError(f"{operation} returned a non-object JSON document")
    return payload


def require_object_list(payload: Any, operation: str) -> list[dict[str, Any]]:
    """Return a list of objects or raise an explicit protocol error."""
    if not isinstance(payload, list) or any(not isinstance(item, dict) for item in payload):
        raise ValueError(f"{operation} returned an invalid object list")
    return payload


def require_positive_limit(limit: int | None, *, allow_none: bool = False) -> int | None:
    """Validate a public library limit consistently with the CLI contract."""
    if limit is None and allow_none:
        return None
    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive integer")
    return limit


def raise_for_arcgis_error(payload: Any, operation: str = "ArcGIS request") -> None:
    """Raise a concise error for ArcGIS HTTP-200 error envelopes."""
    payload = require_object(payload, operation)
    error = payload.get("error")
    if not error:
        return
    message = error.get("message") if isinstance(error, dict) else str(error)
    details = error.get("details", []) if isinstance(error, dict) else []
    suffix = f": {'; '.join(str(item) for item in details)}" if details else ""
    raise ValueError(f"{operation} failed: {message or 'unknown error'}{suffix}")


def _check_content_length(headers: dict[str, list[str]] | None, max_bytes: int) -> None:
    """Raise if the declared Content-Length exceeds the cap."""
    if headers is None:
        return
    # HTTPMessage.get can return a string or None.
    cl = headers.get("Content-Length")
    if cl:
        try:
            length = int(cl)
        except (TypeError, ValueError):
            return
        if length > max_bytes:
            raise ResponseTooLargeError(
                f"Content-Length {length} exceeds maximum {max_bytes}"
            )


def _read_limited(resp, max_bytes: int) -> bytes:
    """Read up to max_bytes from a response, raising if the cap is exceeded."""
    _check_content_length(resp.headers, max_bytes)
    chunks: list[bytes] = []
    total = 0
    while total < max_bytes:
        chunk = resp.read(min(65536, max_bytes - total))
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
    else:
        # We reached the cap; ensure there is no more data.
        extra = resp.read(1)
        if extra:
            raise ResponseTooLargeError(
                f"Response exceeds maximum {max_bytes} bytes"
            )
    return b"".join(chunks)


def json_request(
    url: str,
    timeout: int | None = None,
    method: str | None = None,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    max_bytes: int = DEFAULT_MAX_JSON_BYTES,
) -> dict[str, Any]:
    """Fetch JSON from an allowlisted URL and return the parsed body."""
    if not is_allowed_host(url):
        raise SecurityError(f"URL host is not allowlisted: {url}")
    effective_method = method or ("POST" if data is not None else "GET")
    _enforce_method_policy(effective_method, url)
    req_headers = _request_headers({"Accept": "application/json"})
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(
        url, headers=req_headers, method=effective_method, data=data
    )
    with _OPENER.open(req, timeout=timeout or _get_timeout()) as resp:
        final_url = resp.geturl()
        if not is_allowed_host(final_url):
            raise SecurityError(f"Redirect led to a non-allowlisted host: {final_url}")
        body = _read_limited(resp, max_bytes)
        if not body:
            return {}
        payload = json.loads(body.decode("utf-8"))
        return require_object(payload)


def raw_request(
    url: str,
    timeout: int | None = None,
    method: str | None = None,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    max_bytes: int = DEFAULT_MAX_RAW_BYTES,
) -> bytes:
    """Fetch raw bytes from an allowlisted URL."""
    if not is_allowed_host(url):
        raise SecurityError(f"URL host is not allowlisted: {url}")
    effective_method = method or ("POST" if data is not None else "GET")
    _enforce_method_policy(effective_method, url)
    req_headers = _request_headers()
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(
        url, headers=req_headers, method=effective_method, data=data
    )
    with _OPENER.open(req, timeout=timeout or _get_timeout()) as resp:
        final_url = resp.geturl()
        if not is_allowed_host(final_url):
            raise SecurityError(f"Redirect led to a non-allowlisted host: {final_url}")
        return _read_limited(resp, max_bytes)


def cache_dir() -> Path:
    """Return the cache directory."""
    base = os.environ.get("RALEIGH_CACHE")
    if base:
        return Path(base)
    return Path.home() / ".cache" / "raleigh"


def cache_path(key: str) -> Path:
    """Return a cache file path for the given key."""
    return cache_dir() / key


def read_cache(key: str, max_age_seconds: int | None = None) -> Any | None:
    """Read a cached JSON value if present and fresh."""
    path = cache_path(key)
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > DEFAULT_MAX_JSON_BYTES:
            os.close(fd)
            return None
        if max_age_seconds is not None and time.time() - info.st_mtime > max_age_seconds:
            os.close(fd)
            return None
        with os.fdopen(fd, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def read_cache_bytes(
    key: str,
    *,
    max_age_seconds: int | None = None,
    max_bytes: int = DEFAULT_MAX_RAW_BYTES,
) -> bytes | None:
    """Read a bounded binary cache value if present, regular, and fresh."""
    path = cache_path(key)
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > max_bytes:
            os.close(fd)
            return None
        if max_age_seconds is not None and time.time() - info.st_mtime > max_age_seconds:
            os.close(fd)
            return None
        with os.fdopen(fd, "rb") as stream:
            data = stream.read(max_bytes + 1)
        return data if len(data) <= max_bytes else None
    except OSError:
        return None


def _atomic_write(path: Path, data: bytes | str, *, replace: bool = True) -> None:
    """Atomically write through a unique, exclusively-created sibling file."""
    fd, temp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temp = Path(temp_name)
    try:
        if isinstance(data, bytes):
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        else:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        if replace:
            os.replace(temp, path)
        else:
            os.link(temp, path)
            temp.unlink()
    except Exception:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass
        raise


def write_cache(key: str, value: Any) -> None:
    """Write a JSON value to the cache atomically."""
    path = cache_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(path, json.dumps(value, indent=2))


def write_cache_bytes(key: str, value: bytes) -> None:
    """Write a binary cache value atomically."""
    path = cache_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(path, value)


def clear_cache() -> None:
    """Remove all cached files."""
    cd = cache_dir()
    if not cd.exists():
        return
    for entry in cd.iterdir():
        if entry.is_file():
            entry.unlink()
        elif entry.is_dir():
            import shutil

            shutil.rmtree(entry)


def safe_write(path: Path, data: bytes | str, *, force: bool = False) -> None:
    """Write data atomically, rejecting symlinks and existing files by default."""
    path = Path(path)
    if path.is_symlink() or path.exists() and not force:
        raise FileExistsError(f"Destination exists (use --force to overwrite): {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(path, data, replace=force)
