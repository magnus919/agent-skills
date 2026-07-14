---
name: remote-systems-administration
description: >-
  Administer and troubleshoot remote Linux, FreeBSD, NetBSD, OpenBSD, and macOS systems
  safely, one host or a fleet at a time. Use when a task requires SSH, Ansible,
  Paramiko, POSIX diagnostics, service management, software updates, system
  configuration, firewall changes, or evidence-led remote operations.
license: MIT
compatibility: Requires legitimate remote access. Native SSH is the baseline; Ansible or Python with Paramiko is optional for fleet automation.
---

# Remote Systems Administration

Use this as an operating decision layer, not a bag of remote commands. Unix-like systems share a vocabulary but not an implementation. Identify the target's platform and active control plane before choosing a command.

## Operating contract

1. **Discover before changing.** Record target identity, production status, OS and release, service manager, package manager, firewall, access route, privilege path, and current state. Do not infer them from hostname, memory, or inventory labels.
2. **Use the smallest valid control plane.** Native SSH for a bounded one-host task; Ansible for repeatable desired state across a fleet; Paramiko only when a Python program genuinely needs SSH protocol control that the first two cannot provide.
3. **Protect access first.** Before changing SSH, routing, DNS, a firewall, privilege escalation, or a network interface, establish a tested rollback and a second recovery path. Keep the current session alive until the new path works.
4. **Preview, constrain, verify.** Limit the target set; use native validation, dry-run, diff, or a canary when available; then verify the affected service and its user-visible boundary. A zero exit code proves only that command ran.
5. **Report evidence, not a story.** Preserve bounded per-host results: target, command category, before/after evidence, failures, rollback state, and the remaining uncertainty. Never paste secrets, keys, full configuration files, or unbounded logs into the response.

Run the shared classification probe in `references/portable-operations.md`, then load the matching OS/family overlay and run its command preflight. Select a mutation command only after the required preflight and safety gate.

## Read-only discovery handoff

Use this compact format after a preflight. Fill a field only from observed evidence; otherwise write `unknown` or `not supplied`.

- **Target and scope:**
- **Observed platform and control planes:**
- **Bounded evidence:**
- **Unknown or blocked:**
- **Next safe action:**

## First response: classify the job

| Situation | Default path | Do not do |
|---|---|---|
| Diagnose or make one bounded change on one host | Native `ssh` with a read-only preflight and bounded command/range; do not use a live-follow stream such as `tail -f` | Do not open an interactive shell and make unrecorded edits |
| Repeat the same desired state across hosts | Ansible inventory + playbook, canary/serial rollout | Do not loop `ssh` blindly across production hosts |
| Python must coordinate SSH channels, SFTP, or a custom protocol flow | Paramiko with strict host-key verification and explicit timeouts | Do not disable host-key checks or turn a script into ad hoc fleet control |
| The platform/control plane is unknown | Run bounded discovery from `references/portable-operations.md` | Do not use `systemctl`, `apt`, `pfctl`, or `launchctl` based on a guess |
| Change affects connectivity, firewall, authentication, reboot, storage, or deletion | Load `references/safety-and-verification.md` first | Do not mutate before a rollback and recovery path are explicit |

## Required preflight for every mutation

Before the first state-changing command, confirm:

- exact host(s), environment, and authorized scope;
- OS/release and applicable platform overlay;
- service manager, package manager, firewall implementation, and configuration owner;
- access identity, elevation method, and whether the connection traverses a bastion;
- intended state, expected blast radius, rollback command or artifact, and stop condition;
- validation at both the component layer and the relevant external boundary.

> **Connectivity/access pre-execution gate:** explicitly name authorization, retained session, independent recovery path, tested rollback, stop condition, and component plus external-boundary verification. If any is unknown, stop before execution.

Read-only discovery may proceed without confirmation. **Read-only means no persistent state:** do not create rollback scripts or captures, stage update metadata, alter files, or call a state-changing operation `preflight`. Stop once the needed platform and control-plane evidence is established. Destructive actions, privilege changes, firewall/remote-access changes, package removals, storage operations, and reboot/shutdown require an explicit directive after this preflight.

## Routing references

| Need | Load | File |
|---|---|---|
| SSH, POSIX diagnostics, bounded output, file transfer, logs, and host discovery | Portable operations | `references/portable-operations.md` |
| Ansible administration, inventories, roles, collections, secrets, linting, Molecule, rollout, troubleshooting, or platform-specific automation | Ansible administration | `references/ansible.md` |
| Paramiko, or a compact comparison of fleet-control choices and result-accounting requirements | Fleet automation | `references/fleet-automation.md` |
| Linux classification, init discovery, cross-family safety, or an unknown/minimal derivative | Linux classification | `references/linux.md` |
| Debian, Ubuntu, or an APT/dpkg host after release and ownership discovery | Debian/Ubuntu overlay | `references/linux-debian-ubuntu.md` |
| RHEL, Fedora, or a compatible RPM/DNF host after vendor support and lifecycle discovery | RHEL/Fedora overlay | `references/linux-rhel-fedora.md` |
| SLES, openSUSE, or a zypper/RPM host, including transactional-root discovery | SUSE overlay | `references/linux-suse.md` |
| Arch Linux or an Arch-derived pacman host after support/repository discovery | Arch overlay | `references/linux-arch.md` |
| Alpine Linux or an apk/OpenRC host after persistence-mode discovery | Alpine overlay | `references/linux-alpine.md` |
| FreeBSD rc(8), rc.conf, pkg, jails, and pf/ipfw routing | FreeBSD overlay | `references/freebsd.md` |
| NetBSD rc.d, rc.conf, service, and pkgsrc routing | NetBSD overlay | `references/netbsd.md` |
| OpenBSD rcctl, rc.conf.local, pkg_add, syspatch, and pf | OpenBSD overlay | `references/openbsd.md` |
| launchd, softwareupdate, configuration profiles, pf, and macOS operational limits | macOS overlay | `references/macos.md` |
| Mutation gates, safety classes, rollback, and verification evidence | Safety and verification | `references/safety-and-verification.md` |
| Primary documentation and source freshness | Source index | `references/source-index.md` |

## Platform boundary

Do not flatten platform differences:

- `systemctl` is not a BSD or macOS service manager.
- `rcctl` is OpenBSD-specific; FreeBSD uses rc scripts and `service`.
- `launchctl` domains and labels are not systemd units.
- `apt`, `dnf`, `pacman`, `pkg`, `pkg_add`, `softwareupdate`, and `brew` have different update, rollback, and package-origin semantics.
- Linux nftables, BSD PF, and the macOS Application Firewall are separate control planes. Never translate rules mechanically.

## Scope boundaries

This skill covers host-level Unix operations. Route containers to `docker-compose`, clusters to `kubernetes`, encrypted tailnet policy to `tailscale`, detection/remediation components to `crowdsec`, and reliability process design to `site-reliability-engineering`.

It does not authorize credential recovery, security-boundary bypass, production deletion, provider-console operations, or an unreviewed operating-system upgrade.

## Common pitfalls

1. **Running the right command on the wrong platform.** Discover the service/package/firewall manager before acting.
2. **Treating an SSH connection as proof of authority.** Connection success does not confirm sudo policy, host identity, or authorization for the change.
3. **Using `StrictHostKeyChecking=no` or Paramiko `AutoAddPolicy`.** An unknown host key is an identity event, not a convenience prompt.
4. **Parallelizing first.** Establish the procedure on one canary, then roll out in bounded batches with a stop condition.
5. **Calling a service healthy because it started.** Check process/unit state, logs, listening endpoint, and the relevant dependent or external boundary.
6. **Confusing package upgrades with OS upgrades.** Platform release lifecycle, kernel/base-system updates, and third-party packages have different procedures.
7. **Repairing a remote host through an access-path change without a rollback.** Preserve a live session and independent recovery channel.

## Verification checklist

- [ ] Target and platform were discovered from the live host.
- [ ] Mutation had explicit scope, rollback, and recovery path.
- [ ] The control plane matched the target platform.
- [ ] Fleet work used an inventory, bounded concurrency, and a stop condition.
- [ ] Sensitive values and unbounded output were excluded from evidence.
- [ ] Verification covered the changed component and its relevant external boundary.
- [ ] Per-host success, failure, and rollback status are explicit.
