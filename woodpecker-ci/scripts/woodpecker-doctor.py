#!/usr/bin/env python3
"""Small Woodpecker CI connectivity/configuration probe; stdlib only."""
import argparse, json, os, socket, sys, urllib.error, urllib.request


def check_url(url):
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as r:
            return {"ok": True, "status": r.status, "url": url}
    except urllib.error.HTTPError as e:
        return {"ok": e.code < 500, "status": e.code, "url": url, "error": str(e)}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e)}


def main():
    ap = argparse.ArgumentParser(description="Probe Woodpecker URL and deployment environment")
    ap.add_argument("--url", default=os.getenv("WOODPECKER_HOST", ""), help="Woodpecker HTTP URL")
    ap.add_argument("--server", default=os.getenv("WOODPECKER_SERVER", ""), help="agent gRPC host:port")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = {"checks": [], "environment": {"WOODPECKER_HOST": bool(os.getenv("WOODPECKER_HOST")), "WOODPECKER_AGENT_SECRET": bool(os.getenv("WOODPECKER_AGENT_SECRET")), "WOODPECKER_SERVER": bool(os.getenv("WOODPECKER_SERVER"))}}
    if args.url:
        base = args.url.rstrip("/")
        out["checks"].append(check_url(base))
        out["checks"].append(check_url(base + "/healthz"))
    else:
        out["checks"].append({"ok": False, "error": "set --url or WOODPECKER_HOST"})
    if args.server:
        host, sep, port = args.server.rpartition(":")
        if sep:
            try:
                with socket.create_connection((host or "localhost", int(port)), timeout=5):
                    out["checks"].append({"ok": True, "tcp": args.server})
            except Exception as e:
                out["checks"].append({"ok": False, "tcp": args.server, "error": str(e)})
        else:
            out["checks"].append({"ok": False, "error": "--server must be host:port"})
    out["ok"] = all(c.get("ok", False) for c in out["checks"])
    print(json.dumps(out, indent=2) if args.json else "\n".join([("PASS" if c.get("ok") else "FAIL") + " " + json.dumps(c, sort_keys=True) for c in out["checks"]]))
    return 0 if out["ok"] else 1

if __name__ == "__main__":
    sys.exit(main())
