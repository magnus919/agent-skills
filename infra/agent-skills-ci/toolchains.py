#!/usr/bin/env python3
"""Exercise actual pinned setup actions without a GitHub token or registration."""

import io
import os
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path("/home/runner/toolchain-probe")
ROOT.mkdir()
for name in ("path", "env", "output", "summary"):
    (ROOT / name).touch()
environment = dict(os.environ)
environment.update(
    {
        "RUNNER_OS": "Linux",
        "RUNNER_ARCH": "X64",
        "RUNNER_ENVIRONMENT": "self-hosted",
        "RUNNER_TEMP": "/tmp",
        "RUNNER_TOOL_CACHE": "/opt/hostedtoolcache",
        "AGENT_TOOLSDIRECTORY": "/opt/hostedtoolcache",
        "GITHUB_WORKSPACE": str(ROOT),
        "GITHUB_PATH": str(ROOT / "path"),
        "GITHUB_ENV": str(ROOT / "env"),
        "GITHUB_OUTPUT": str(ROOT / "output"),
        "GITHUB_STEP_SUMMARY": str(ROOT / "summary"),
        "GITHUB_SERVER_URL": "https://github.com",
        "GITHUB_API_URL": "https://api.github.com",
    }
)


def action(repository, revision, entrypoint, inputs):
    url = f"https://codeload.github.com/{repository}/tar.gz/{revision}"
    with urllib.request.urlopen(url, timeout=60) as response:
        archive = response.read()
    target = ROOT / repository.replace("/", "-")
    target.mkdir()
    # Extract public, pinned action sources with traversal/link filtering.
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as source:
        source.extractall(target, filter="data")
    source_dir = next(target.iterdir())
    action_env = {**environment, **{"INPUT_" + key.upper(): value for key, value in inputs.items()}}
    subprocess.run(
        ["node", str(source_dir / entrypoint)], env=action_env, cwd=ROOT, check=True, timeout=600
    )
    added = (ROOT / "path").read_text().splitlines()
    environment["PATH"] = ":".join([*reversed(added), environment["PATH"]])


action(
    "ruby/setup-ruby",
    "de492cf36cbab201753d720ce4f4e336cd688c94",
    "dist/index.js",
    {"ruby-version": "3.3", "bundler-cache": "false"},
)
action(
    "actions/setup-python",
    "5fda3b95a4ea91299a34e894583c3862153e4b97",
    "dist/setup/index.js",
    {
        "python-version": "3.12",
        "check-latest": "false",
        "allow-prereleases": "false",
        "freethreaded": "false",
        "update-environment": "true",
    },
)
subprocess.run(
    ["/home/runner/bin/Runner.Listener", "--version"], env=environment, check=True, timeout=30
)
for command in (
    ["ruby", "--version"],
    ["python3", "--version"],
    ["node", "--version"],
    ["npm", "--version"],
):
    subprocess.run(command, env=environment, check=True, timeout=30)
subprocess.run(
    ["ruby", "-e", 'require "yaml"; require "openssl"; puts "PASS Ruby yaml/openssl"'],
    env=environment,
    check=True,
    timeout=30,
)
subprocess.run(
    ["python3", "-m", "venv", str(ROOT / "venv")], env=environment, check=True, timeout=60
)
subprocess.run(
    [str(ROOT / "venv/bin/python"), "-m", "pip", "--version"],
    env=environment,
    check=True,
    timeout=30,
)
print(
    "PASS pinned Ruby/Python setup actions, Ruby libraries, Python venv/pip, Node/npm", flush=True
)
shutil.rmtree(ROOT)
