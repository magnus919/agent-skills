#!/usr/bin/env python3
"""Bootstrap script — ensures agent-council CLI is available.

The SKILL.md instructs agents to run this script if `agent-council`
is not found on PATH. It installs the package from the skill directory
using the current Python's pip, with pipx as a fallback.
"""

import shutil
import subprocess
import sys
import os


def ensure_installed(skill_dir: str | None = None) -> str | None:
    """Ensure agent-council CLI is available. Returns path or None."""
    cli_path = shutil.which("agent-council")
    if cli_path:
        return cli_path

    if skill_dir is None:
        skill_dir = os.path.dirname(os.path.abspath(__file__))

    print("agent-council not found. Installing from skill directory...", file=sys.stderr)

    # Try sys.executable -m pip install (works with any Python + venv)
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", skill_dir],
            check=True,
            capture_output=True,
            timeout=60,
        )
        cli_path = shutil.which("agent-council")
        if cli_path:
            print(f"Installed. CLI available at: {cli_path}", file=sys.stderr)
            return cli_path
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass

    # Fallback: pipx
    pipx = shutil.which("pipx")
    if pipx:
        print("pip install failed, trying pipx...", file=sys.stderr)
        try:
            subprocess.run([pipx, "install", skill_dir], check=True, timeout=120)
            cli_path = shutil.which("agent-council")
            if cli_path:
                print(f"Installed via pipx at: {cli_path}", file=sys.stderr)
                return cli_path
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass

    print(
        f"Could not install agent-council automatically.\n"
        f"Run one of:\n"
        f"  {sys.executable} -m pip install -e {skill_dir}\n"
        f"  pipx install {skill_dir}\n"
        f"  pip install agent-council",
        file=sys.stderr,
    )
    return None


if __name__ == "__main__":
    result = ensure_installed()
    sys.exit(0 if result else 1)
