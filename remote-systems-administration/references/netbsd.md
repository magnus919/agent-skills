# NetBSD Overlay

## Scope and discovery

NetBSD has separate base-system, rc.d, firewall, and pkgsrc control planes.
Do not use FreeBSD release tooling, OpenBSD `rcctl`, or Linux systemd/package commands as NetBSD controls.
Record NetBSD release, architecture, kernel, virtualization, base-update state, and support context.
Discover rc configuration, active services, package source, pkgsrc branch/prefix, network owner, firewall owner, and automation.
Identify whether the target is a host, virtual guest, container-like environment, or restricted administrative domain.
Separate base ownership from pkgsrc ownership before making a lifecycle claim.
Treat unknown firewall or configuration provenance as a blocker for mutation.

## Read-only preflight

Inspect `/etc/rc.conf`, `/etc/rc.conf.d`, rc.d scripts, local overrides, and package-provided script locations.
Inspect bounded relevant logs, process/listener state, and the affected user, client, or dependent boundary.
Inspect pkgsrc repository branch, binary repository configuration, installed packages, prefix, disk space, and transaction impact.
Inspect base release/update state separately from binary package and source-build state.
Discover whether NPF, PF, IPF, or another owner controls active packet filtering.
Identify owner of interfaces, DNS, routes, and persistent network configuration before connectivity work.
Record snapshot/backup and independent recovery evidence for lifecycle operations.

## Command preflight

Run only commands available on the observed NetBSD installation. Substitute `<service>` with the observed rc.d service name. Firewall binary presence is evidence to investigate ownership, not a selection rule. PF inspection requires authorized privilege on the target; a missing, empty, or permission-denied PF result is `unknown`, not evidence that PF is inactive.

| Question | Read-only command |
|---|---|
| Base release and kernel | `sysctl kern.osrelease`; `uname -a` |
| rc.d service and bounded state | `service <service> status`; `grep '^<service>=' /etc/rc.conf /etc/rc.conf.d/* 2>/dev/null`; `netstat -an` |
| Binary package versus pkgsrc state | `pkg_info <package>`; `command -v pkgin >/dev/null 2>&1 && pkgin list <package>`; `pkg_admin config-var PKG_PATH` |
| rc/network ownership | `ls /etc/rc.d`; `grep -E '^(ifconfig|defaultroute|dhcpcd)' /etc/rc.conf` |
| Firewall owner evidence | `command -v npfctl >/dev/null 2>&1 && npfctl show`; `command -v pfctl >/dev/null 2>&1 && sudo -n pfctl -s info`; `command -v ipfstat >/dev/null 2>&1 && ipfstat -io` |

## Services and logs

NetBSD rc.d uses `/etc/rc`, `/etc/rc.conf`, `/etc/rc.d`, and documented local override layers.
Do not edit `/etc/defaults` to make a site-local override.
`service` is the normal alias for rc.d script actions, but script actions must be confirmed on the target.
Package-installed rc.d scripts may require activation under `/etc/rc.d` according to package policy.
Before authorized change, inspect enablement, script configuration, bounded logs, process, and listener.
Afterward, verify rc state, logs, listener, and the actual client or dependent-service boundary.
Do not claim service health based only on a script exit status.

## Packages and repositories

pkgsrc supports binary packages and source builds; `pkg_add` operates on binary packages and `pkgin` may be installed.
Inspect package origin, repository branch, `LOCALBASE`, dependencies, installed set, and source/binary policy before upgrade.
Changing binary repository branch or package prefix is not an ordinary package update.
Do not mix package locations, alter `LOCALBASE`, or override dependency protections without following pkgsrc guidance.
Plan disk capacity, service effects, rebuild needs, and application compatibility before broad maintenance.
Verify installed-package state and the expected binary/service boundary after an authorized transaction.

## Release and base lifecycle

NetBSD base-system maintenance is distinct from pkgsrc package maintenance.
Use release-specific NetBSD instructions for base updates and release upgrades.
Do not substitute `pkg_add`, pkgin, or pkgsrc builds for a base-system lifecycle procedure.
Plan kernel, bootloader, drivers, package ABI, service, and application compatibility before an authorized upgrade.
Require explicit lifecycle authorization, maintenance owner, rollback/recovery plan, and post-boot verification.
After reboot, verify host reachability, booted state, critical services, networking, and application boundary.

## Networking and firewall ownership

NPF is NetBSD's native packet filter, but a target may use PF, IPF, or another policy owner.
Discover active rules, configuration provenance, interface ownership, route, DNS, and automation boundaries before edits.
Do not infer the active firewall merely because a command is installed.
For firewall, SSH, DNS, routes, interfaces, or VPN changes, pass the [connectivity safety gate](safety-and-verification.md#connectivity-preserving-changes).
It requires explicit authority, retained access, independent recovery, validated rollback, scoped application, and stop condition.
Verify administration access and intended traffic or service behavior after the smallest authorized change.

## Storage and persistence

Identify root/data filesystems, mounts, encryption, RAID/LVM where present, snapshots, backup scope, and boot recovery.
Confirm package/build, log, and temporary-space requirements before lifecycle maintenance.
Do not label a snapshot complete recovery without proving boot/data inclusion and application consistency.
Persist configuration in the documented local configuration layer rather than a package example or defaults file.
For image-managed systems, establish whether local state survives replacement or deployment.
Storage, mount, encryption, partition, and deletion work requires the shared lifecycle or destructive gate.

## Failure signatures

### Defaults-file edit disappears

Symptom: A setting reverts or does not override expected service behavior.
Cause: `/etc/defaults` was edited instead of the documented local configuration layer.
Evidence: rc configuration precedence and file provenance show the ineffective edit.
Safe next action: Restore ownership and apply the setting through the supported local override path.

### Package daemon absent after reboot

Symptom: A package is installed but its daemon does not start during boot.
Cause: The package rc.d script was not activated, copied, or enabled under the applicable policy.
Evidence: Script location, rc configuration, run output, process, and listener state show the gap.
Safe next action: Follow the documented rc.d activation procedure and verify the service boundary.

### Package repository or prefix mismatch

Symptom: A binary package transaction expects a different branch, ABI, or prefix.
Cause: pkgsrc repository or `LOCALBASE` policy drifted from the installed set.
Evidence: Repository configuration, installed package metadata, and prefix paths show inconsistency.
Safe next action: Stop and reconcile pkgsrc policy; do not mix prefixes to clear the error.

### Base update attempted with pkg tools

Symptom: A package command is proposed to address a base-system or release transition.
Cause: Base and third-party package lifecycles were conflated.
Evidence: File ownership and NetBSD release state identify base provenance.
Safe next action: Route the task to release-specific NetBSD lifecycle documentation.

### Firewall command targets inactive plane

Symptom: A rule command succeeds but policy or traffic does not change as expected.
Cause: NPF, PF, IPF, or automation ownership was assumed incorrectly.
Evidence: Active ruleset, loaded service/configuration, and traffic evidence reveal the owner.
Safe next action: Stop and select the confirmed owner under the connectivity gate.

### Service is running but unavailable

Symptom: An rc.d action reports success while clients cannot use the service.
Cause: Configuration, listener, dependency, or network path is failing.
Evidence: Bounded logs, process/socket state, and boundary probe disagree with rc status.
Safe next action: Diagnose the failed layer read-only before another restart.

## Handoff

Report NetBSD release, base versus pkgsrc scope, rc.d configuration, package prefix/branch, and network/firewall owners.
Include bounded service, package, logs, listener, storage, and external-boundary evidence.
State every recovery limitation, lifecycle uncertainty, and unverified assumption.
For a mutation, identify scope, rollback artifact, independent recovery route, validation, and stop condition.
Exclude sensitive configuration values, unrestricted logs, and cross-platform command assumptions.

## Official sources

- [NetBSD rc.d guide](https://www.netbsd.org/docs/guide/en/chap-rc.html)
- [pkgsrc guide](https://www.netbsd.org/docs/pkgsrc/using.html)
- [pkg_add(1)](https://man.netbsd.org/pkg_add.1)
- [NetBSD networking guide](https://www.netbsd.org/docs/guide/en/chap-net-practice.html)
- [Source index](source-index.md)
