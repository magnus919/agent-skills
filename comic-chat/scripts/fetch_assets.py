#!/usr/bin/env python3
"""Fetch the pinned Comic Chat source into a user-controlled cache."""
import argparse
import subprocess
import sys
from pathlib import Path

UPSTREAM = "https://github.com/microsoft/comic-chat.git"
REVISION = "48a162249484ab8d116c243e8203b0956d350c09"
ASSET_RELATIVE = Path("v1.0-pre-modern/comicart")


def run(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "command failed: " + " ".join(args))
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path.home() / ".cache" / "comic-chat")
    parser.add_argument("--repo-url", default=UPSTREAM, help="Git source URL (default: Microsoft archive)")
    parser.add_argument("--revision", default=REVISION, help="Pinned commit or tag to check out")
    args = parser.parse_args()
    checkout = args.cache_dir.expanduser().resolve() / "source"
    try:
        if checkout.exists():
            if not (checkout / ".git").is_dir():
                raise RuntimeError(f"cache path exists but is not a Git checkout: {checkout}")
            run("git", "fetch", "--tags", "--force", "origin", args.revision, cwd=checkout)
        else:
            checkout.parent.mkdir(parents=True, exist_ok=True)
            run("git", "clone", "--no-checkout", args.repo_url, str(checkout))
            run("git", "fetch", "--tags", "--force", "origin", args.revision, cwd=checkout)
        run("git", "checkout", "--detach", "--force", args.revision, cwd=checkout)
        resolved = run("git", "rev-parse", "HEAD", cwd=checkout)
        assets = checkout / ASSET_RELATIVE
        if not (assets / "backdrop").is_dir() or not (assets / "avatars").is_dir():
            raise RuntimeError(f"pinned revision lacks expected assets at {assets}")
    except RuntimeError as error:
        print(f"error: asset setup failed: {error}", file=sys.stderr)
        return 2
    print(f"resolved_commit={resolved}")
    print(f"assets_dir={assets}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
