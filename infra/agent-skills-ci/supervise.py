#!/usr/bin/env python3
"""One fresh, network-restricted, repo-scoped ephemeral worker per host.

Run from a trusted host checkout, never from a CI checkout. The host-only token
file must grant Administration:write solely on magnus919/agent-skills.
"""

import argparse
import fcntl
import ipaddress
import json
import os
import signal
import stat
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

REPOSITORY = "magnus919/agent-skills"
LABELS = "self-hosted,linux,x64,agent-skills-ci"


def docker(*args, **kwargs):
    return subprocess.run(["docker", *args], check=True, **kwargs)


def api(path, suffix, method="GET"):
    info = path.stat()
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
        raise RuntimeError("Controller token must be owned by this user, mode 0600")
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPOSITORY}/actions/runners{suffix}",
        data=b"{}" if method == "POST" else None,
        headers={
            "Authorization": "Bearer " + path.read_text().strip(),
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method=method,
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response) if response.status != 204 else None


def unregister(path, state, name):
    if not state.exists():
        return
    runner_id = int(state.read_text())
    try:
        registered = api(path, f"/{runner_id}")
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
    else:
        if registered["name"] != name:
            raise RuntimeError("Refusing to remove a different runner identity")
        api(path, f"/{runner_id}", "DELETE")
    state.unlink()


def reconcile(token_path, worker):
    """Recover registration interrupted before local ID recording.

    Call only after the fixed-name local containers are verified absent and the
    host controller lock is held. Never remove another runner pool's identities.
    """
    page = 1
    while True:
        runners = api(token_path, f"?per_page=100&page={page}")["runners"]
        for registered in runners:
            if registered["name"] == worker:
                api(token_path, "/" + str(int(registered["id"])), "DELETE")
        if len(runners) < 100:
            return
        page += 1


def addresses():
    output = subprocess.check_output(["ip", "-j", "address"], text=True)
    assigned = [
        item["local"]
        for interface in json.loads(output)
        for item in interface.get("addr_info", [])
        if item["family"] == "inet" and ipaddress.ip_address(item["local"]).is_global
    ]
    with urllib.request.urlopen("https://api.ipify.org", timeout=15) as response:
        external = str(ipaddress.IPv4Address(response.read().decode().strip()))
    if not ipaddress.IPv4Address(external).is_global:
        raise RuntimeError("Public egress discovery returned a non-global address")
    return " ".join([*assigned, external])


def cleanup(worker, guard):
    for name in (worker, guard):
        exists = subprocess.run(
            ["docker", "inspect", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if exists.returncode == 0:
            docker("rm", "-fv", name, stdout=subprocess.DEVNULL)
        result = docker(
            "ps", "-aq", "--filter", "name=^/" + name + "$", capture_output=True, text=True
        )
        if result.stdout.strip():
            raise RuntimeError("Container cleanup not confirmed: " + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True, choices=["saru", "gpuslut01"])
    parser.add_argument("--token-file", type=Path, required=True)
    parser.add_argument("--once", action="store_true")
    parser.add_argument(
        "--deny-file",
        type=Path,
        required=True,
        help="Reviewed host/public-service IPv4 addresses, one per line",
    )
    parser.add_argument("--runner-image", default="local/agent-skills-ci:reviewed")
    parser.add_argument("--guard-image", default="local/agent-skills-ci-guard:reviewed")
    args = parser.parse_args()
    worker = f"agent-skills-ci-{args.host}"
    guard = worker + "-network"
    with open(Path.home() / ("." + worker + ".lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # Kill old workloads before any configuration, credential, or network reads.
        cleanup(worker, guard)
        state = Path.home() / ("." + worker + ".registration")
        denied = [
            str(ipaddress.IPv4Address(line.strip()))
            for line in args.deny_file.read_text().splitlines()
            if line.strip()
        ]
        if not denied:
            raise RuntimeError("Explicit reviewed public-service deny list is required")
        stopping = False

        def stop(_signum, _frame):
            nonlocal stopping
            stopping = True
            raise SystemExit(0)

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        # Fail before creating containers if the credential is unavailable.
        unregister(args.token_file, state, worker)
        reconcile(args.token_file, worker)
        while not stopping:
            try:
                token = api(args.token_file, "/registration-token", "POST")["token"]
                cleanup(worker, guard)
                docker(
                    "run",
                    "-d",
                    "--name",
                    guard,
                    "--cap-drop=ALL",
                    "--cap-add=NET_ADMIN",
                    "--security-opt=no-new-privileges",
                    "--read-only",
                    "--tmpfs",
                    "/tmp:rw,noexec,nosuid,size=1m",
                    "--tmpfs",
                    "/run:rw,noexec,nosuid,size=1m",
                    "--memory=64m",
                    "--pids-limit=32",
                    "--cpus=0.1",
                    "--dns=1.1.1.1",
                    "-e",
                    "HOST_ADDRESSES=" + addresses() + " " + " ".join(denied),
                    args.guard_image,
                    stdout=subprocess.DEVNULL,
                )
                for _ in range(30):
                    ready = subprocess.run(
                        ["docker", "exec", guard, "test", "-f", "/tmp/ready"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    if ready.returncode == 0:
                        break
                    time.sleep(1)
                else:
                    raise RuntimeError("Network guard did not become ready")
                docker(
                    "run",
                    "-d",
                    "--name",
                    worker,
                    "--network=container:" + guard,
                    "--cap-drop=ALL",
                    "--security-opt=no-new-privileges",
                    "--read-only",
                    "--log-driver=none",
                    "--tmpfs",
                    "/home/runner:rw,exec,nosuid,nodev,size=2g,uid=1001,gid=1001",
                    "--tmpfs",
                    "/opt/hostedtoolcache:rw,exec,nosuid,nodev,size=1g,uid=1001,gid=1001",
                    "--user=1001:1001",
                    "--cpus=2",
                    "--memory=" + ("2g" if args.host == "saru" else "3g"),
                    "--memory-swap=" + ("2g" if args.host == "saru" else "3g"),
                    "--pids-limit=512",
                    "--init",
                    "--tmpfs",
                    "/tmp:rw,exec,nosuid,nodev,size=512m,mode=1777",
                    "-e",
                    "RUNNER_TOOL_CACHE=/opt/hostedtoolcache",
                    "--entrypoint",
                    "/bin/bash",
                    args.runner_image,
                    "-c",
                    "cp -a /opt/runner-template/. /home/runner/ && touch /home/runner/.seeded && exec sleep infinity",
                    stdout=subprocess.DEVNULL,
                )
                for _ in range(60):
                    seeded = subprocess.run(
                        ["docker", "exec", worker, "test", "-f", "/home/runner/.seeded"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    if seeded.returncode == 0:
                        break
                    time.sleep(1)
                else:
                    raise RuntimeError("Worker seed did not become ready")
                # Send the short-lived token through stdin, not Docker environment
                # or command arguments. The durable controller credential never enters.
                docker(
                    "exec",
                    "-i",
                    worker,
                    "/bin/bash",
                    "-c",
                    "read -r token; ./config.sh --unattended --ephemeral "
                    "--disableupdate --url https://github.com/"
                    + REPOSITORY
                    + " --name "
                    + worker
                    + " --labels "
                    + LABELS
                    + ' --work _work --token "$token"',
                    input=token + "\n",
                    text=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=120,
                )
                identity = docker("exec", worker, "cat", ".runner", capture_output=True, text=True)
                runner_id = int(json.loads(identity.stdout)["agentId"])
                temporary = state.with_suffix(".new")
                temporary.write_text(str(runner_id))
                temporary.chmod(0o600)
                temporary.replace(state)
                token = None
                print(f"{worker}: registered ephemeral worker", flush=True)
                # Independent host deadline cannot be disabled by a CI job.
                docker("exec", worker, "./run.sh", timeout=2700)
            finally:
                cleanup(worker, guard)
                unregister(args.token_file, state, worker)
            if args.once:
                return
            if not stopping:
                time.sleep(5)


if __name__ == "__main__":
    main()
