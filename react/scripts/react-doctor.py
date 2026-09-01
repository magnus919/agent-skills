#!/usr/bin/env python3
"""Bounded, read-only diagnostics for React/Vite projects."""
import argparse
import json
import re
import sys
from pathlib import Path

MAX_BYTES = 512 * 1024
TEXT_FILES = ("package.json", "vite.config.js", "vite.config.ts", "vite.config.mjs", "vite.config.cjs", "tsconfig.json")

def read_text(root, name):
    path = root / name
    try:
        if not path.is_file() or path.stat().st_size > MAX_BYTES:
            return None
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None

def diagnose(root):
    result = {"project": str(root), "checks": [], "warnings": []}
    package_text = read_text(root, "package.json")
    package = None
    if package_text is None:
        result["warnings"].append("package.json is missing or exceeds the read limit")
    else:
        try:
            package = json.loads(package_text)
            if not isinstance(package, dict):
                raise ValueError("not an object")
            deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
            result["checks"].append({"name": "package-json", "status": "ok"})
            result["checks"].append({"name": "react-dependencies", "status": "ok" if "react" in deps and "react-dom" in deps else "warning"})
        except (ValueError, TypeError, json.JSONDecodeError):
            result["warnings"].append("package.json is not valid JSON")
    config_name = next((name for name in TEXT_FILES[1:5] if read_text(root, name) is not None), None)
    result["checks"].append({"name": "vite-config", "status": "ok" if config_name else "info", "file": config_name})
    source_files = []
    for directory in (root / "src", root / "app"):
        if directory.is_dir():
            source_files.extend(p for p in directory.rglob("*") if p.is_file() and p.suffix in {".jsx", ".tsx", ".js", ".ts"})
    result["checks"].append({"name": "source-entry", "status": "ok" if source_files else "warning", "file_count": len(source_files)})
    env_names = set()
    for path in root.glob(".env*"):
        text = read_text(root, path.name) or ""
        env_names.update(re.findall(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=", text, re.MULTILINE))
    result["checks"].append({"name": "public-env-names", "status": "ok", "names": sorted(n for n in env_names if n.startswith("VITE_"))})
    if any(not n.startswith("VITE_") for n in env_names):
        result["warnings"].append(".env files contain non-public names; keep them server-side and never import secrets into client code")
    lockfiles = [name for name in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "bun.lock") if (root / name).is_file()]
    result["checks"].append({"name": "lockfile", "status": "ok" if lockfiles else "warning", "files": lockfiles})
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only React/Vite project diagnostics")
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        print("ERROR: project directory does not exist", file=sys.stderr)
        return 2
    result = diagnose(root)
    if args.as_json:
        print(json.dumps(result, sort_keys=True))
    else:
        print("React/Vite doctor: " + result["project"])
        for check in result["checks"]:
            print("- {name}: {status}".format(**check))
        for warning in result["warnings"]:
            print("WARNING: " + warning)
    return 0

if __name__ == "__main__":
    sys.exit(main())
