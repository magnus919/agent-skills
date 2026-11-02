# Deployment checkpoint — 2026-11-02

Prepared from main `1b092570161ec69e9f26efaa9b00c59cf0c9c1e0` in a separate
branch, without modifying PR #785 or its queued runs.

Both hosts have the bundle at `/home/magnus/services/agent-skills-ci` and built
images; both host-only credentials have been provisioned and verified against
the intended repository API without disclosure. Both user services are active
and enabled, using the reviewed immutable image IDs. Both user systemd managers are running with lingering
enabled. The existing GPU evaluator container remained running throughout.

| Host | CPU worker image ID | Guard image ID |
|---|---|---|
| Saru | `sha256:e6cd45b4539ea0f2c8e964bdefd6e38e3e06ae40181b48e99d8ffbbe41debafa` | `sha256:964d95ab3d866beb8950b55ceb4b8bf7db7a3f56b2dc7417c8ac22dbaccbb914` |
| gpuslut01 | `sha256:d2a6127d13728ad4b35a3c039edcda9f0e410f1f4ab4edae94f2e3c4d8492b11` | `sha256:e0260a075fc9b7fffed2c8bd0356d792f5f218302f404c97bfb02b43c5dc164b` |

`python3 probe.py <host>` passed on both hosts. Verified GitHub port 443 reachable;
private, host bridge, tailnet, metadata, discovered host-public port 80/443 and IPv6 port 443
connections failed. Confirmed UID 1001, zero effective capabilities,
no-new-privileges, sudo denied, no Docker socket or NVIDIA devices, no host mounts,
read-only root and bounded tmpfs, 2-CPU / 2-GiB (Saru) and 2-CPU / 3-GiB
(gpuslut01) effective limits. Fresh container had no prior marker. Both
probe containers were absent afterward. Neither worker requests a GPU.

Seven host-controller recovery tests passed locally, including actual BOM-prefixed
runner identity parsing: startup removes old containers
before missing configuration/credentials can block it, interrupted registration
reconciles only the exact dedicated runner name, wrong registration identity
cannot be removed, failed API deletion retains identity, failed container cleanup
blocks replacement, and failed public-egress discovery fails closed. Independent final code review
found no remaining code blocker for a draft PR; activation gates remain below. Python
compilation, shell syntax, ruff lint/format, and diff whitespace checks passed.

Actual credential-free pinned setup actions also passed on both hosts: Ruby
3.3.13 (`yaml`/`openssl` load), Python 3.12.16 (venv/pip), Node 24.22.2,
npm 11.19.1, and the runner 2.338.1 executable. This exposed and fixed Docker's
implicit `noexec` tmpfs behavior: worker home, toolcache, and temp now explicitly
allow execution, retaining bounded tmpfs, nosuid/nodev, dropped capabilities,
read-only root, no-new-privileges, and memory/no-swap limits.

Independent inventory review covered live Docker rules, 46 Traefik YAML provider
files, 63 static router names, the active function wildcard DNS, public upstreams,
and both hosts' public egress. Their current union contains two public IPv4s;
the reviewed union was blocked in live probes on both hosts. Detailed infrastructure
inventory and IPs stay private outside this public repository; drafts are on each
host at `~/services/agent-skills-ci/denied-public-addresses.reviewed`. Refresh on
WAN, DNS, reverse-proxy, public-service, or tunnel changes. Future endpoints are
not automatically covered by this snapshot.

Actionlint 1.7.12 (release checksum verified) passed both modified workflows with
`actionlint.yaml` custom labels. This checked YAML, workflow semantics/expressions,
and action inputs; embedded shell/Python external linters were disabled. Separate
Python, ruff, and guard-shell checks passed.

Live validation-only lifecycle tests passed on both hosts: online/idle registration
without the production label; independent 45-second host watchdog; deletion of
the exact GitHub registration and both containers; a new registration with a
fresh workspace; graceful SIGTERM cleanup; and guard failure creating no job
worker or registration. The initial real registration exposed GitHub's UTF-8 BOM
in `.runner`; the parser was fixed and the orphan registration was reconciled.

The production pool is online with the common `agent-skills-ci` label. Saru
successfully completed `paired-eval-tests` for both initial PR heads, and both
controllers automatically replaced completed single-job workers with new IDs.
The validation job reached deptry and found an infrastructure-local import
classification issue; `supervise` is now declared first-party. The remaining
credential-free paired smoke, Raleigh matrix, and keyless advisory jobs are
routed to this pool; private-credential workflows remain GitHub-hosted.

Full current-head deterministic workflow validation and post-merge integration
checks remain pending. No formal PR approval is implied by the independent code
reviews; normal repository merge gates still apply.

Current-head real CI passed all four Raleigh matrix jobs and paired tests/fake
smoke. Keyless advisory installation succeeded and skill scanning correctly
skipped because no skill changed. Required validation exited137 during pip on
Saru at2GiB; the same install previously succeeded on the3GiB GPU worker. Saru
is now bounded at3GiB as well, with pip cache disabled; the new full validation
run is pending. The7-test controller suite and static workflow checks pass.
