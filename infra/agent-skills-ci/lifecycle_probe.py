#!/usr/bin/env python3
"""Explicit live, idle-only lifecycle checks for an approved runner controller."""

import argparse
import signal
import subprocess
import tempfile
import time
import urllib.error
from pathlib import Path

import supervise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", choices=["saru", "gpuslut01"])
    args = parser.parse_args()
    worker = "agent-skills-ci-" + args.host
    guard = worker + "-network"
    credential = Path.home() / ".config/agent-skills-ci/controller-token"
    state = Path.home() / ("." + worker + ".registration")
    base = [
        "python3",
        str(Path(__file__).with_name("supervise.py")),
        "--host",
        args.host,
        "--token-file",
        str(credential),
        "--deny-file",
        str(credential.with_name("denied-public-addresses")),
        "--validation-only",
        "--once",
        "--listener-timeout",
        "45",
    ]

    def absent(runner_id=None):
        for name in (worker, guard):
            result = supervise.docker(
                "ps", "-aq", "--filter", "name=^/" + name + "$", capture_output=True, text=True
            )
            assert not result.stdout.strip(), "controller left a container behind"
        assert not state.exists(), "registration recovery file remains"
        if runner_id is not None:
            try:
                supervise.api(credential, f"/{runner_id}")
            except urllib.error.HTTPError as error:
                assert error.code == 404
            else:
                raise AssertionError("expired runner still registered")

    def start(log):
        process = subprocess.Popen(base, stdout=log, stderr=log)
        deadline = time.monotonic() + 35
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(
                    "controller exited before validation listener ready; inspect host-only lifecycle log"
                )
            if state.exists():
                runner_id = int(state.read_text())
                record = supervise.api(credential, f"/{runner_id}")
                if record["status"] == "online":
                    labels = {label["name"] for label in record["labels"]}
                    assert not record["busy"], "validation listener unexpectedly took work"
                    assert (
                        "agent-skills-ci" not in labels and "agent-skills-ci-validation" in labels
                    )
                    print(
                        f"PASS {args.host}: validation runner {runner_id} online/idle; production label absent",
                        flush=True,
                    )
                    return process, runner_id
            time.sleep(1)
        process.terminate()
        process.wait(timeout=60)
        raise RuntimeError("validation listener readiness deadline exceeded")

    # Production supervisor must be stopped: the shared flock enforces exclusion.
    with tempfile.TemporaryFile(mode="w+") as log:
        first, first_id = start(log)
        try:
            supervise.docker("exec", worker, "mkdir", "-p", "/home/runner/_work")
            supervise.docker("exec", worker, "touch", "/home/runner/_work/old-job-marker")
            assert first.wait(timeout=60) != 0, "short host deadline did not fail the controller"
        finally:
            if first.poll() is None:
                first.send_signal(signal.SIGTERM)
                first.wait(timeout=60)
        absent(first_id)
        print(
            f"PASS {args.host}: watchdog removed both containers and registration {first_id}",
            flush=True,
        )
        second, second_id = start(log)
        try:
            assert second_id != first_id
            supervise.docker("exec", worker, "test", "!", "-e", "/home/runner/_work/old-job-marker")
        finally:
            second.send_signal(signal.SIGTERM)
            second.wait(timeout=60)
        absent(second_id)
        print(
            f"PASS {args.host}: replacement {second_id} fresh; SIGTERM cleanup verified", flush=True
        )

    with tempfile.TemporaryDirectory(prefix="agent-skills-ci-guard-failure-") as directory:
        Path(directory, "Dockerfile").write_text(
            'FROM local/agent-skills-ci-guard:reviewed\nENTRYPOINT ["/bin/false"]\n'
        )
        supervise.docker(
            "build",
            "-t",
            "local/agent-skills-ci-guard:failure-probe",
            directory,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    failed = subprocess.run(
        [*base, "--guard-image", "local/agent-skills-ci-guard:failure-probe"],
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert failed.returncode != 0 and "Network guard did not become ready" in failed.stderr
    absent()
    runners = supervise.api(credential, "?per_page=100")["runners"]
    assert not any(r["name"] == worker for r in runners)
    print(
        f"PASS {args.host}: guard failure started no worker; no registration/container remains",
        flush=True,
    )


if __name__ == "__main__":
    main()
