#!/usr/bin/env python3
"""Non-credentialed worker isolation probe. Does not register a GitHub runner."""

import argparse
import ipaddress
import json
import subprocess
from pathlib import Path

import supervise

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("host", choices=["saru", "gpuslut01"])
parser.add_argument("--toolchains", action="store_true")
parser.add_argument("--deny-file", type=Path)
args = parser.parse_args()
host = args.host
worker = "agent-skills-ci-probe-" + host
guard = worker + "-network"
public_addresses = supervise.addresses()
if args.deny_file:
    additional = [
        str(ipaddress.IPv4Address(line.strip()))
        for line in args.deny_file.read_text().splitlines()
        if line.strip()
    ]
    public_addresses += " " + " ".join(additional)
probe = r"""
import glob, os, socket, subprocess
from pathlib import Path
assert not Path('/var/run/docker.sock').exists()
assert not glob.glob('/dev/nvidia*')
assert not Path('/home/magnus/.config/agent-skills-ci/controller-token').exists()
assert os.getuid() == 1001
status = Path('/proc/self/status').read_text()
assert 'CapEff:\t0000000000000000' in status
assert 'NoNewPrivs:\t1' in status
result = subprocess.run(['sudo', '-n', 'true'], capture_output=True)
assert result.returncode != 0, 'sudo became root'
with socket.create_connection(('github.com', 443), 10):
    print('PASS github.com:443 reachable')
for target in ['10.0.0.1', '172.17.0.1', '192.168.1.1', '100.64.0.1',
               '169.254.169.254', *os.environ['BLOCKED_PUBLIC'].split()]:
    for port in (80, 443):
        try:
            socket.create_connection((target, port), 1).close()
        except OSError:
            pass
        else:
            raise AssertionError('private/host destination reachable: ' + target + ':' + str(port))
try:
    socket.create_connection(('2606:4700:4700::1111', 443), 1).close()
except OSError:
    pass
else:
    raise AssertionError('IPv6 unexpectedly reachable')
print('PASS denied private/tailnet/metadata/host/IPv6, no privileges/socket/GPU')
assert not os.access('/opt/runner-template', os.W_OK)
Path('/tmp/replacement-marker').write_text('must not persist')
"""
try:
    supervise.cleanup(worker, guard)
    supervise.docker(
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
        "--dns=1.1.1.1",
        "-e",
        "HOST_ADDRESSES=" + public_addresses,
        "local/agent-skills-ci-guard:reviewed",
        stdout=subprocess.DEVNULL,
    )
    import time

    for _ in range(30):
        ready = subprocess.run(["docker", "exec", guard, "test", "-f", "/tmp/ready"])
        if ready.returncode == 0:
            break
        time.sleep(1)
    else:
        raise RuntimeError("Network guard failed")
    supervise.docker(
        "run",
        "-d",
        "--name",
        worker,
        "--network=container:" + guard,
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--user=1001:1001",
        "--read-only",
        "--tmpfs",
        "/home/runner:rw,exec,nosuid,nodev,size=2g,uid=1001,gid=1001",
        "--tmpfs",
        "/opt/hostedtoolcache:rw,exec,nosuid,nodev,size=1g,uid=1001,gid=1001",
        "--cpus=2",
        "--memory=3g",
        "--memory-swap=3g",
        "--pids-limit=512",
        "--tmpfs",
        "/tmp:rw,exec,nosuid,nodev,size=512m,mode=1777",
        "-e",
        "BLOCKED_PUBLIC=" + public_addresses,
        "--entrypoint",
        "/bin/bash",
        "local/agent-skills-ci:reviewed",
        "-c",
        "cp -a /opt/runner-template/. /home/runner/ && touch /home/runner/.seeded && exec sleep infinity",
        stdout=subprocess.DEVNULL,
    )
    for _ in range(60):
        if (
            subprocess.run(
                ["docker", "exec", worker, "test", "-f", "/home/runner/.seeded"]
            ).returncode
            == 0
        ):
            break
        time.sleep(1)
    else:
        raise RuntimeError("Seed failed")
    supervise.docker("exec", worker, "python3", "-c", probe)
    if args.toolchains:
        supervise.docker(
            "exec",
            "-i",
            worker,
            "python3",
            "-",
            input=Path(__file__).with_name("toolchains.py").read_text(),
            text=True,
            timeout=900,
        )
    report = supervise.docker("inspect", worker, capture_output=True, text=True)
    data = json.loads(report.stdout)[0]
    config = data["HostConfig"]
    assert not data["Mounts"], "unexpected volume or bind mounts"
    assert not config["Privileged"] and config["CapDrop"] == ["ALL"]
    assert config["NanoCpus"] == 2_000_000_000 and config["Memory"] == 3_221_225_472
    print("PASS effective mounts/capabilities/CPU/memory limits")
finally:
    supervise.cleanup(worker, guard)
# Fresh overlay proves a job-created file is not shared with replacement.
supervise.docker(
    "run",
    "--rm",
    "--network=none",
    "--cap-drop=ALL",
    "--security-opt=no-new-privileges",
    "--user=1001:1001",
    "--entrypoint",
    "test",
    "local/agent-skills-ci:reviewed",
    "!",
    "-e",
    "/tmp/replacement-marker",
)
print("PASS fresh replacement has no marker; probe containers removed")
