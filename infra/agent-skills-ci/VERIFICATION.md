# Deployment checkpoint — 2026-11-02

Prepared from main `1b092570161ec69e9f26efaa9b00c59cf0c9c1e0` in a separate
branch, without modifying PR #785 or its queued runs.

Both hosts have the bundle at `/home/magnus/services/agent-skills-ci` and built
images; no controller credential, runner registration, or user service activation
has been provisioned. Both user systemd managers are running with lingering
enabled. The existing GPU evaluator container remained running throughout.

| Host | CPU worker image ID | Guard image ID |
|---|---|---|
| Saru | `sha256:e6cd45b4539ea0f2c8e964bdefd6e38e3e06ae40181b48e99d8ffbbe41debafa` | `sha256:964d95ab3d866beb8950b55ceb4b8bf7db7a3f56b2dc7417c8ac22dbaccbb914` |
| gpuslut01 | `sha256:d2a6127d13728ad4b35a3c039edcda9f0e410f1f4ab4edae94f2e3c4d8492b11` | `sha256:e0260a075fc9b7fffed2c8bd0356d792f5f218302f404c97bfb02b43c5dc164b` |

`python3 probe.py <host>` passed on both hosts. Verified GitHub port 443 reachable;
private, host bridge, tailnet, metadata, discovered host-public and IPv6 port 443
connections failed. Confirmed UID 1001, zero effective capabilities,
no-new-privileges, sudo denied, no Docker socket or NVIDIA devices, no host mounts,
read-only root and bounded tmpfs, 2-CPU / 2-GiB (Saru) and 2-CPU / 3-GiB
(gpuslut01) effective limits. Fresh container had no prior marker. Both
probe containers were absent afterward. Neither worker requests a GPU.

Six host-controller recovery tests passed locally: startup removes old containers
before missing configuration/credentials can block it, interrupted registration
reconciles only the exact dedicated runner name, wrong registration identity
cannot be removed, failed API deletion retains identity, failed container cleanup
blocks replacement, and failed public-egress discovery fails closed. Independent final code review
found no remaining code blocker for a draft PR; activation gates remain below. Python
compilation, shell syntax, ruff lint/format, and diff whitespace checks passed.

Not yet verified: real runner registration, restart/timeout lifecycle against
GitHub, Ruby 3.3 and Python setup actions, either full deterministic job, production
public-service deny list, or continuous credential renewal. No new workflow has
been dispatched; existing queued runs were neither rerun nor cancelled. Changes
to routing remain a draft until these gates pass and a human merges the PR.

Blocking prerequisite: separately approve/provision a dedicated credential with
repository Administration:write limited to agent-skills, or select an approved
GitHub App broker. The existing desktop token is not copied to the hosts.
