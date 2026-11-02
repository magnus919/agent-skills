# Dedicated agent-skills CPU CI pool

One clean, single-job worker on Saru (2 CPU / 2 GiB) and one on gpuslut01
(2 CPU / 3 GiB). Neither receives a GPU, host directory, Docker socket,
SSH identity, durable GitHub credential, shared cache, or privileged capability.
The existing GPU evaluator stays separate. Common routing labels are
`[self-hosted, linux, x64, agent-skills-ci]`.

## Activation gate

This deployment is a draft until an independent isolation review and the network
probes below pass on each host. Do not merge workflow routing before both workers
are online. The public repository currently requires approval for all external
contributors; preserve that setting and the `pull_request` trigger. Do not replace
it with `pull_request_target`. External PR approval is not a sandbox.

Create a reviewed `~/.config/agent-skills-ci/denied-public-addresses` file, one IPv4
address per line, covering each host and publicly exposed internal service. Empty
lists fail closed. Automatic assigned-address and public-egress discovery supplements
this list; it does not replace the inventory.

Continuous single-job replacement requires a controller credential stored **only
on the host** in `~/.config/agent-skills-ci/controller-token`, owned by the service
user, mode 0600. A fine-grained PAT must select only `magnus919/agent-skills` and
requires repository **Administration: write** (GitHub does not expose a narrower
repo-runner permission). That is repository administration authority, not merely
permission to execute CI. Creating/provisioning this credential needs explicit
approval of that scope. Never copy the desktop's broader GitHub token. Never put
it in an Actions secret, Docker environment, image, CI workspace, or job mount.
The controller sends only a short-lived runner registration token into each fresh
container through stdin. Runner credentials still exist inside that one-job
container; remove the entire container after completion or at the host deadline.

For credential handoff and the GitHub App alternative, see [PROVISIONING.md](PROVISIONING.md).

## Install from a reviewed, trusted checkout

Copy only this directory to `~/services/agent-skills-ci` on each host. Do not run
controller code from a pull-request checkout. Build the images there:

```sh
docker build -f Guard.Dockerfile -t local/agent-skills-ci-guard:reviewed .
docker build -f Runner.Dockerfile -t local/agent-skills-ci:reviewed .
```

Record image IDs and use immutable local image IDs with `--guard-image` and
`--runner-image` for deployment. Verify that image runner version is still
supported by GitHub before activation; `--disableupdate` requires rebuilding
within GitHub's update window. The Dockerfiles are reproducible build recipes
using version tags, not a fully locked supply-chain manifest.

Copy `agent-skills-ci@.service` to `~/.config/systemd/user/`, set the reviewed image
IDs in ExecStart, then `systemctl --user daemon-reload`. After the credential and
isolation gates pass, enable only the local host instance, for example
`systemctl --user enable --now agent-skills-ci@saru`. Verify user-manager boot
persistence/lingering before claiming the service survives reboot.

The worker root filesystem is read-only. Runner state/workspace (2 GiB),
toolcache (1 GiB), and temporary files (512 MiB) use explicitly executable,
nosuid/nodev bounded tmpfs charged to
the worker memory limit, with no swap. Jobs cannot grow the host root overlay;
resource exhaustion may fail their own job. Docker worker logging is disabled.

The supervisor obtains a fresh repo registration token for each worker, uses
`--ephemeral`, destroys worker and guard in that order, and verifies removal
before the next iteration. A host lock prevents duplicate controllers. Exact-ID cleanup removes abandoned registrations; startup reconciles only the
expected host worker name after confirming local containers are absent. Its
45-minute deadline bounds jobs even if they tamper with the runner listener;
the routed workflows also have a 40-minute timeout. Failures restart through
systemd, with no bypass of the network-ready gate.

## Network and behavioral verification

The network guard shares only its network namespace with the worker. Only the
guard has NET_ADMIN; the job drops every capability and has no-new-privileges.
IPv6 is denied. IPv4 blocks private, link-local, CGNAT, multicast, reserved,
assigned host public addresses, and the host's public egress address. Remaining
egress is TCP 80/443 and DNS to 1.1.1.1; incoming traffic must be established or
loopback. The guard must finish configuring every rule before the runner starts.
If a host has additional public ingress/NAT addresses beyond its assigned and
public egress addresses, add them to the deny list before activation.

Run `python3 probe.py <host> --deny-file denied-public-addresses.reviewed --toolchains`
for the credential-free network/resource and actual setup-action probes.

Before registration, probe from an otherwise identical non-credentialed worker:

- GitHub HTTPS succeeds; RFC1918, host bridge, tailnet, metadata, host public IP,
  and IPv6 connections fail, including TCP 80/443.
- The worker cannot change iptables, obtain root via sudo, access Docker, read
  controller credentials or host files, or see `/dev/nvidia*`.
- Inspect effective limits: CPU, memory, swap, PIDs, capabilities, mounts/devices.
- Force a listener timeout and a guard startup failure; no next worker may start
  until both old containers are absent. Create a marker in the first job and
  confirm it is absent in its replacement.
- Run the deterministic paired-eval workflow with model smoke disabled; confirm
  actual job assignment to this pool. Validate Ruby 3.3 / Python 3.12 tool setup
  and the validation job as well. No model credentials are required or supplied.

This is shared-kernel container isolation, not a VM boundary. A kernel/runtime
escape can compromise the host, including GPU workloads. Keep host/runtime
patched and use separate VMs if that residual risk is unacceptable. Jobs may
contact public Internet services; this is not a domain allowlist. Publicly exposed
internal services on other public addresses need explicit additional blocking.

## Rollback

Revert the two workflow routing lines to `ubuntu-latest`. Stop/disable the two
user service instances. Remove only `agent-skills-ci-<host>` and its `-network`
container, then remove the matching repo runner registrations by exact name.
Revoke the dedicated controller credential. Do not touch the GPU evaluator,
other runners, networks, or workloads. No queued job cancellation is necessary.
