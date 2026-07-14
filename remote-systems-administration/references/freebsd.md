# FreeBSD Overlay

## Scope and discovery

FreeBSD has separate base-system, rc, package, ports, firewall, jail, and storage control planes.
Do not transplant Linux systemd, APT/RPM, or nftables instructions onto a FreeBSD host.
Record FreeBSD release, patch level, architecture, kernel, virtualization, and support/lifecycle context.
Discover active services, package origin, ports use, jail context, filesystem layout, network owner, and firewall owner.
Determine whether the command target is the host, a jail, or an application inside a jail.
Identify ZFS boot environments, snapshots, backups, and console/recovery access before lifecycle work.
Treat host/jail ambiguity and unknown firewall ownership as blockers for mutation.

## Read-only preflight

Inspect rc configuration layers, installed rc scripts, enabled service variables, and daemon-specific configuration provenance.
Inspect bounded syslog/application evidence, process/listener state, and the relevant client or dependent boundary.
Inspect installed packages, package repository policy, package audit state, ports usage, disk space, and planned service impact.
Inspect base release and update state separately from third-party package state.
Inspect active PF, IPFW, or IPFILTER ownership and whether network state is host or jail scoped.
Inspect filesystems, mounts, ZFS datasets, boot environments, snapshot scope, and backup/recovery evidence.
End discovery when the requested scope, active owners, and validation boundary are established.

## Command preflight

Run only commands that exist on the observed host or jail. Firewall commands identify state, not the policy owner or permission to alter it. PF inspection requires authorized privilege on the target; a missing, empty, or permission-denied PF result is `unknown`, not evidence that PF is inactive.

| Question | Read-only command |
|---|---|
| Base release and kernel | `freebsd-version -ku`; `uname -a` |
| rc service and bounded state | `service <service> status`; `sysrc -a | grep '^<service>_'`; `sockstat -4 -6 -l` |
| Package versus base state | `pkg info <package>`; `pkg -vv`; `pkg which <path>` |
| Jail scope | `jls`; `sysctl security.jail.jailed` |
| Firewall owner evidence | `command -v pfctl >/dev/null 2>&1 && sudo -n pfctl -s info`; `command -v ipfw >/dev/null 2>&1 && ipfw list`; `command -v ipfstat >/dev/null 2>&1 && ipfstat -io` |

## Services and logs

FreeBSD normally uses rc scripts and local configuration centered on `/etc/rc.conf` and `/etc/rc.conf.local`.
`/etc/defaults/rc.conf` supplies defaults and is not the local override target.
Package and ports configuration commonly lives under `/usr/local/etc`; base configuration commonly lives under `/etc`.
Use the observed rc script and service interface for inspection; its supported actions are script-specific.
Before an authorized lifecycle action, inspect configuration, enabled variables, bounded logs, process, and listener.
Afterward, verify rc/service result, logs, listener, and the intended application or dependency boundary.
A successful service action is component evidence only, not proof of user-visible availability.

## Packages, ports, and repositories

`pkg` manages prebuilt binary packages; ports is a separate source-build framework with compile-time choices.
Do not treat packages and ports as interchangeable update paths or mix their assumptions without ownership review.
Inspect installed packages, repositories, candidate changes, disk capacity, dependency impact, and service restart requirements.
`pkg audit -F` is advisory evidence and does not replace package/update planning.
Unexpected removals, repository changes, ABI transitions, or local-port rebuild requirements are stop conditions.
Do not force dependency, signature, or file-conflict behavior merely to complete an automation run.
Verify package database state and expected service/application behavior after an authorized transaction.

## Release and base lifecycle

FreeBSD base-system updates, release upgrades, and third-party packages are separate lifecycle paths.
Do not use `pkg` as a substitute for a release upgrade or kernel/base-system procedure.
Use release-specific FreeBSD documentation for supported base update and upgrade decisions.
Plan bootloader, kernel, module, jail, and application compatibility before an authorized lifecycle action.
On an appropriate ZFS system, `bectl` can provide a deliberate boot-environment recovery option.
Verify boot-environment health, dataset scope, excluded data, and boot selection before calling it rollback.
Reboot only with explicit authorization, recovery access, and post-boot service plus boundary verification.

## Networking and firewall ownership

FreeBSD supports PF, IPFW, and IPFILTER; their grammars, state, and persistence are distinct.
Discover the active packet filter and the owner of routes, DNS, interfaces, and jail networking before edits.
Do not copy OpenBSD PF assumptions or translate firewall rules mechanically across FreeBSD control planes.
For firewall, route, DNS, interface, SSH, or jail-network changes, use the [connectivity safety gate](safety-and-verification.md#connectivity-preserving-changes).
The gate requires explicit directive, retained session, independent recovery, validated rollback, small scope, and stop condition.
Verify retained administration access and the intended allow/deny or service flow before closing the change.

## Storage, jails, and persistence

Jails have host/jail boundaries for processes, packages, filesystems, and network interfaces.
Identify the jail manager and whether the requested operation belongs to the jail or the host.
Do not expect a jail-local change to control host services, host firewall policy, or host storage.
ZFS snapshots can help recovery but are not authorization for destructive rollback.
Confirm datasets, boot/data inclusion, dependent services, replication/backup state, and application consistency.
Mount, dataset, encryption, partition, and deletion work requires the shared lifecycle or destructive gate.

## Failure signatures

### Service action has no effect

Symptom: A service action succeeds or returns quietly, but the daemon is absent or unchanged.
Cause: The rc variable is not enabled, the script lacks that action, or another supervisor owns the process.
Evidence: rc configuration, rc script behavior, process state, and bounded logs establish the owner.
Safe next action: Inspect the script and configuration; do not repeat lifecycle actions blindly.

### Package update breaks base assumption

Symptom: A package operation is expected to update a base component or resolve a base release issue.
Cause: Package/ports and the FreeBSD base system are distinct lifecycle paths.
Evidence: Installed file/package ownership and release state show separate provenance.
Safe next action: Stop and route base maintenance through release-specific FreeBSD guidance.

### PF rule copied from OpenBSD fails

Symptom: Candidate PF syntax or behavior differs from an OpenBSD-derived expectation.
Cause: FreeBSD's PF integration and target release behavior must be validated locally.
Evidence: Target parser output, active ruleset, and FreeBSD documentation identify the difference.
Safe next action: Retain current policy and use FreeBSD-specific validation under the connectivity gate.

### Jail change cannot affect host policy

Symptom: A jail-local package or service change does not alter host networking or firewall behavior.
Cause: The operation was performed on the wrong side of the host/jail boundary.
Evidence: Jail identity, interface assignment, package database, and process scope show the boundary.
Safe next action: Re-establish authorized host versus jail scope before any further change.

### Boot-environment rollback misses data

Symptom: A proposed boot-environment restore does not cover application data or required datasets.
Cause: The boot environment's dataset scope is narrower than the recovery claim.
Evidence: `bectl` and ZFS dataset relationships plus backup records show exclusions.
Safe next action: Do not execute rollback until data recovery and application consistency are planned.

### Active service lacks usable listener

Symptom: The service reports running but clients cannot reach its protocol endpoint.
Cause: Configuration, socket binding, dependency, jail/network scope, or application failure is present.
Evidence: Process arguments, bounded logs, socket state, and boundary probe disagree.
Safe next action: Diagnose read-only at the failed layer before any restart or package change.

## Handoff

Report host versus jail scope, release/base state, package/ports provenance, and service/network/firewall owners.
Include bounded rc, package, log, listener, filesystem, and external-boundary evidence.
State recovery path, boot-environment/data scope, and every remaining uncertainty.
For mutation, provide exact target, rollback artifact, independent recovery, validation, and stop condition.
Exclude secrets, full configuration files, unrestricted logs, and assumptions imported from Linux or OpenBSD.

## Official sources

- [FreeBSD Handbook: configuration](https://docs.freebsd.org/en/books/handbook/config/)
- [FreeBSD Handbook: ports and packages](https://docs.freebsd.org/en/books/handbook/ports/)
- [FreeBSD Handbook: firewalls](https://docs.freebsd.org/en/books/handbook/firewalls/)
- [bectl(8)](https://man.freebsd.org/cgi/man.cgi?query=bectl&sektion=8)
- [Source index](source-index.md)
