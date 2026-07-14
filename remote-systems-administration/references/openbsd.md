# OpenBSD Overlay

## Scope and discovery

OpenBSD has coherent base controls, but base, packages, rcctl, PF, and release lifecycle remain separate concerns.
Record release, architecture, kernel, virtualization, patch state, active daemons, and whether the host routes or filters traffic.
Discover `/etc/rc.conf.local` ownership, package provenance, PF state, network configuration owner, and automation before change.
Do not edit defaults where `rc.conf.local` is the local override layer.
Do not use Linux systemd commands or FreeBSD `service` conventions as OpenBSD controls.
Identify backup, disk, boot, console, and independent recovery capability before lifecycle work.
Treat unknown PF ownership or host-router role as a blocker for firewall or network mutation.

## Read-only preflight

Inspect base release and patch state separately from installed package state.
Inspect `rcctl` daemon inventory, configuration, enablement, check/configtest capability, and bounded relevant logs.
Inspect process and listener state plus the client, dependent-service, or user-visible boundary.
Inspect package source, signature policy, planned package impact, disk space, and service restart implications.
Inspect active PF rules/configuration provenance and owner of interfaces, routes, DNS, and remote access.
Inspect filesystems, mounts, backup scope, boot recovery, and rollback feasibility for lifecycle work.
Stop once the target scope, owner, and proof boundary are established from evidence.

## Command preflight

These are inspection commands. `syspatch -c` may make an outbound vendor query to check the base patch state, but it does not perform an update; it still needs normal authorized network access. PF inspection requires authorized privilege on the target; a missing, empty, or permission-denied PF result is `unknown`, not evidence that PF is inactive.

| Question | Read-only command |
|---|---|
| Base release and patch state | `sysctl kern.version`; `syspatch -c` |
| Daemon and bounded logs | `rcctl ls all`; `rcctl get <daemon>`; `tail -n 50 /var/log/messages` |
| Package state | `pkg_info <package>`; full inventory: `pkg_info -a | grep -F '<package-or-prefix>' | head -n 50` |
| PF state and configuration owner | `sudo -n pfctl -s info`; `sudo -n pfctl -sr`; `test -r /etc/pf.conf && ls -l /etc/pf.conf` |
| Network/persistence owner | `grep -E '^(hostname|inet|inet6|dhcp)' /etc/hostname.* 2>/dev/null`; `test -r /etc/rc.conf.local && ls -l /etc/rc.conf.local` |

## Services and logs

`rcctl` is the normal interface to inspect, configure, enable, and control base and package daemons.
Use read-only `rcctl` inspection and daemon-native validation before lifecycle actions.
Actions such as `check`, `configtest`, `reload`, and `restart` must be supported by the target daemon.
Enablement and daemon options are represented through rc configuration, including `/etc/rc.conf.local`.
Inspect bounded logs, process state, listener, and dependency/client behavior before an authorized action.
After a change, verify daemon state, logs, listener, and the actual boundary that motivated the work.
A successful rcctl result is not a claim that the service is usable.

## Packages and repositories

OpenBSD packages are separate from the system distribution files.
`pkg_add` installs or updates packages; it is not a base-system updater or release upgrade mechanism.
Inspect package origin, signed-package policy, dependencies, disk space, service impact, and application compatibility before updates.
Do not weaken signature verification, force a package origin, or bypass policy merely to complete automation.
Treat unexpected dependency changes or package-source changes as stop conditions until reconciled.
Use documented non-mutating previews only with their stated limitations understood.
Verify package database state and expected binary or service behavior after an authorized transaction.

## Release and base lifecycle

`syspatch` handles applicable official-release binary patches and is distinct from package updates and release upgrades.
It fetches, verifies, installs, and can revert supported binary patches within its documented boundaries.
A no-applicable-patch result does not establish that the host has completed a release upgrade or package maintenance.
Use official release documentation for base updates and upgrades; do not improvise distribution-file changes.
Plan boot, driver, service, package compatibility, maintenance window, recovery, and post-boot validation.
Require explicit authorization before lifecycle change or reboot.
After reboot, verify reachability, booted state, required daemons, PF/network path, and application boundary.

## Networking and PF ownership

PF is a security and availability boundary; identify active ruleset and configuration ownership before any change.
Do not use PF commands that flush, disable, or broadly replace state as casual troubleshooting.
Validate candidate configuration with the target parser before loading it where applicable.
For PF, SSH, routing, DNS, interface, or VPN work, pass the [connectivity safety gate](safety-and-verification.md#connectivity-preserving-changes).
Keep the current administrative session, provide independent authorized recovery, validate rollback, use minimal scope, and set a stop condition.
Verify retained administration, expected allowed flow, expected denied flow, and affected application health.

## Storage and persistence

Identify root/data filesystems, mounts, encryption, RAID, snapshots, backup scope, and boot recovery before lifecycle work.
Do not treat a filesystem snapshot as application-consistent backup or approved destructive rollback.
Confirm capacity for package, patch, log, and boot work before an authorized transaction.
Persist daemon configuration in the documented local rc layer, not only in runtime state or defaults.
For image-managed systems, establish whether local changes survive replacement.
Storage, mounts, encryption, partitions, and deletion are lifecycle or destructive operations under the shared gate.

## Failure signatures

### syspatch finds no patch

Symptom: `syspatch` reports no applicable patch or skips a patch.
Cause: It applies applicable cumulative binary patches for official releases, not package updates or release upgrades.
Evidence: Release state, syspatch output, and package inventory show distinct lifecycle scopes.
Safe next action: Classify the actual lifecycle need and consult the official release procedure.

### Package update is treated as base update

Symptom: A package action is expected to update system distribution files or change the release.
Cause: Package and base-system lifecycles were conflated.
Evidence: File ownership, package inventory, and release/patch state identify the split.
Safe next action: Stop and use the appropriate official base or package path.

### PF candidate fails validation

Symptom: PF parser validation rejects a proposed ruleset.
Cause: Syntax, interface, macro, table, or rule logic is invalid for the target.
Evidence: Parser output and active ruleset/context identify the failed candidate.
Safe next action: Retain current rules and correct the candidate; never trial-load over the only access path.

### rcctl succeeds but service is unavailable

Symptom: A daemon action returns successfully but the expected service is unreachable.
Cause: Configuration, listener, dependency, privilege, or network path is failing.
Evidence: rcctl configuration, bounded logs, process/socket state, and boundary probe disagree.
Safe next action: Diagnose the failed layer read-only before another action.

### Signature policy blocks a package

Symptom: Package installation or update is rejected by signature policy.
Cause: Source, key, mirror, or policy provenance requires investigation.
Evidence: pkg_add output and configured package source establish the verification boundary.
Safe next action: Investigate legitimate provenance; do not weaken signature policy.

### Remote firewall change loses access

Symptom: SSH or the intended management flow fails after PF/network modification.
Cause: The active owner, rollback, or recovery prerequisite was not satisfied.
Evidence: Session/recovery status, active policy, and configuration provenance show the failure.
Safe next action: Use the independent recovery path and restore the validated prior policy.

## Handoff

Report release/patch state, base/package split, rcctl and PF ownership, host-router role, and recovery evidence.
Include bounded daemon, package, logs, listener, PF validation, and external-boundary evidence.
State lifecycle classification, remaining uncertainty, and any reason the mutation gate is not satisfied.
For changes, hand off scope, prior state, rollback, independent recovery, validation, and stop condition.
Exclude secrets, complete rulesets, unrestricted logs, and unverified security conclusions.

## Official sources

- [rcctl(8)](https://man.openbsd.org/rcctl)
- [pkg_add(1)](https://man.openbsd.org/pkg_add)
- [syspatch(8)](https://man.openbsd.org/syspatch)
- [pfctl(8)](https://man.openbsd.org/pfctl)
- [pf.conf(5)](https://man.openbsd.org/pf.conf)
- [Source index](source-index.md)
