#!/usr/bin/env python3
"""Read-only CryptPad discovery. Standard library only; never executes server JS."""

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

MAX_BYTES = 1048576
APPS = {
    "pad",
    "code",
    "sheet",
    "doc",
    "presentation",
    "slide",
    "kanban",
    "whiteboard",
    "diagram",
    "form",
    "file",
    "drive",
}


def origin(value):
    """Require an origin, never accept a document URL as a probe target."""
    if any(ord(c) < 33 for c in value):
        raise ValueError("Origin must not contain whitespace or controls")
    p = urllib.parse.urlsplit(value)
    if (
        p.scheme not in ("https", "http")
        or not p.hostname
        or p.username is not None
        or p.password
        or p.query
        or p.fragment
        or p.path not in ("", "/")
    ):
        raise ValueError("Use a bare HTTPS origin without credentials, path, query or fragment")
    _ = p.port
    if p.scheme == "http" and p.hostname not in ("localhost", "127.0.0.1", "::1"):
        raise ValueError("HTTP is allowed only for loopback development instances")
    return p.scheme + "://" + p.netloc


def parse_config(body):
    # Match only upstream's JSON-in-AMD wrapper. No eval, node, or JS execution.
    match = re.fullmatch(
        r"\s*define\(function\s*\(\)\s*\{\s*;?\s*return\s+(\{.*\})\s*;?\s*\}\);?\s*", body, re.S
    )
    if not match:
        raise ValueError("Unrecognized config wrapper; inspect the deployed version")
    obj = json.loads(match.group(1))
    if not isinstance(obj, dict):
        raise ValueError("Expected a configuration object")
    return obj


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url, timeout):
    opener = urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(url, headers={"User-Agent": "cryptpad-skill-probe/1"})
    with opener.open(request, timeout=timeout) as response:
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("Response exceeds 1 MiB limit")
        return data.decode("utf-8")


def probe(target, timeout, fetcher=fetch):
    base = origin(target)
    result = {"origin": base, "scope": "public HTTP discovery only", "endpoints": {}}
    for path in ("/api/config", "/cryptpad-api.js"):
        try:
            body = fetcher(base + path, timeout)
            if path == "/api/config":
                config = parse_config(body)
                result["config"] = {
                    k: config[k]
                    for k in (
                        "httpUnsafeOrigin",
                        "httpSafeOrigin",
                        "websocketPath",
                        "enableEmbedding",
                        "appsToDisable",
                        "onlyOffice",
                    )
                    if k in config
                }
                result["endpoints"][path] = {"status": "recognized"}
            else:
                recognized = "CryptPadAPI" in body and "onSave" in body and "onNewKey" in body
                result["endpoints"][path] = {
                    "status": "recognized" if recognized else "unrecognized"
                }
        except urllib.error.HTTPError as exc:
            result["endpoints"][path] = {"status": "http_error", "code": exc.code}
            exc.close()
        except (OSError, ValueError, UnicodeError):
            # Do not echo response bodies, redirect URLs, or arbitrary error text.
            result["endpoints"][path] = {"status": "unavailable_or_unrecognized"}
    result["ok"] = all(v["status"] == "recognized" for v in result["endpoints"].values())
    result["limitations"] = (
        "Does not verify WebSockets, browser CSP/CORS, login, editing, save or server version."
    )
    return result


def inspect_link(value):
    value = value.strip()
    if not value or any(ord(c) < 33 for c in value):
        raise ValueError("Provide one URL without whitespace or controls")
    p = urllib.parse.urlsplit(value)
    base = origin(p.scheme + "://" + p.netloc)
    app = p.path.strip("/").split("/")[0]
    return {
        "origin": base,
        "application": app if app in APPS else "unknown",
        "has_fragment": bool(p.fragment),
        "has_query": bool(p.query),
        "key_validity": "not assessed",
        "access_rights": "not assessed",
        "network_requests": 0,
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog="JSON output. Exit 0: success; 1: probe incomplete; 2: invalid input. Link input is stdin to keep secrets out of argv.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("probe", help="GET public config and integration loader; redirects refused")
    p.add_argument("--origin", required=True)
    p.add_argument("--timeout", type=float, default=10)
    sub.add_parser(
        "inspect-link", help="Read one URL from stdin; output no path, key or query values"
    )
    args = parser.parse_args()
    try:
        if args.command == "probe":
            if not 0 < args.timeout <= 60:
                raise ValueError("Timeout must be greater than 0 and at most 60 seconds")
            result = probe(args.origin, args.timeout)
        else:
            value = sys.stdin.read(16385)
            if len(value) > 16384:
                raise ValueError("URL input exceeds 16 KiB")
            result = inspect_link(value)
        print(json.dumps(result, sort_keys=True))
        return 0 if result.get("ok", True) else 1
    except (ValueError, OSError):
        print(
            json.dumps(
                {
                    "error": "Invalid input. Use a bare origin for probe or one valid URL on stdin for inspect-link."
                }
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
