# Alpine Linux Overlay

## Scope and discovery

Use this overlay after observing Alpine Linux and apk on the target.
Record exact release, architecture, repositories, init system, deployment type, and whether the host is installed, data-disk, or diskless.
Do not assume apk changes persist merely because a package transaction completed.
Discover OpenRC or the actual service manager, logging route, network owner, firewall owner, and automation owner.
Identify whether the target is a container, appliance, VM, or bare-metal host because persistence differs.
Separate runtime state, local configuration, and the supported persistence mechanism in all findings.
Treat unknown boot or persistence mode as a blocker for update, reboot, or configuration claims.

## Read-only preflight

Inspect `/etc/apk/repositories`, release branch, package origins, installed set, package constraints, and proposed changes.
Inspect diskless/data-disk mode, local backup/persistence state, mount layout, free space, and reboot route.
Inspect service state, runlevel membership, bounded logs, process/listener state, and the external boundary.
Discover the owner of interfaces, DNS, routes, firewall rules, and generated configuration.
Identify concurrent package activity before any transaction and coordinate with its observed owner.
Record recovery access and application impact before any lifecycle operation.
Stop after establishing platform, persistence, owner, and boundary evidence.

## Command preflight

Run optional commands only when discovered. LBU evidence matters only for an installed diskless or data-disk system using that persistence path.

| Question | Read-only command |
|---|---|
| Release and init | `cat /etc/alpine-release`; `ps -p 1 -o pid= -o comm=` |
| Service and runlevel | `rc-status`; `rc-status -a`; `rc-update show <service>` |
| Repository, world, package | `cat /etc/apk/repositories`; `cat /etc/apk/world`; `apk policy <package>` |
| Persistence evidence | `command -v lbu >/dev/null 2>&1 && lbu status`; `mount | grep -E ' on /( |$|data(/| )|media(/| )|mnt(/| ))' | head -n 20` |
| Network/firewall owner | `command -v rc-service >/dev/null 2>&1 && rc-service networking status`; `command -v nft >/dev/null 2>&1 && nft list ruleset`; `command -v iptables >/dev/null 2>&1 && iptables -S` |

## Services and logs

OpenRC is common on Alpine, but use the observed manager rather than a Linux-wide assumption.
Inspect service status, runlevel configuration, process state, bounded relevant logs, and listener before changing it.
Determine whether a container supervisor, cron-like task, or application manager owns process startup.
Use a component's native configuration validation before an authorized reload or restart where available.
Verify the manager result, process/listener, and client or dependent boundary after a change.
Do not substitute `systemctl` for the observed Alpine control plane.

## Packages and repositories

Inspect apk repository branch, package origin, constraints, and the exact proposed package/configuration changes.
Do not mix stable and edge repositories or bypass signature/conflict protections without approved platform policy.
Reconcile `.apk-new` or other configuration conflict artifacts through the actual configuration owner.
Coordinate package locks or concurrent transactions; never remove state files based only on an error message.
Confirm disk capacity and persistence requirements before authorizing a package change.
Verify installed package state and the intended binary or service behavior afterward.

## Release and base lifecycle

Routine apk maintenance, Alpine branch changes, and image replacement are different lifecycle paths.
Confirm the supported upgrade path for the observed release and deployment model before a branch transition.
For diskless systems, include persistence capture and reboot activation in the lifecycle plan.
Do not combine repository branch changes, broad updates, storage changes, and unrelated configuration cleanup by default.
Explicit authorization, maintenance ownership, recovery access, and post-boot validation are required for reboot work.
After reboot, verify persistence, booted state, service runlevels, networking, and application boundary.

## Networking and firewall ownership

Alpine network configuration can be owned by local scripts, OpenRC, a container platform, cloud tooling, or automation.
Firewall policy can be direct nftables, iptables compatibility tooling, an appliance layer, or external policy.
Identify the durable owner before changing remote login, DNS, routes, interfaces, VPN, or firewall rules.
Use the [connectivity safety gate](safety-and-verification.md#connectivity-preserving-changes) for every access-sensitive mutation.
Require authority, retained session, independent recovery, rollback validation, small scope, and stop condition.
Verify retained administration access and the intended traffic behavior after the change.

## Storage and persistence

Diskless and data-disk modes require the documented persistence workflow for package and configuration changes.
Identify root/data mounts, overlays, writable media, backup/persistence artifacts, and boot-time restoration behavior.
Do not report a change as durable until persistence evidence survives the relevant activation or reboot path.
For containers, establish whether the filesystem is ephemeral and whether a deployment manifest owns the desired state.
Confirm package cache, unpacking, log, and persistence storage space before lifecycle work.
Storage, mount, encryption, and deletion work requires the shared lifecycle or destructive gate.

## Failure signatures

### Change vanishes after reboot

Symptom: A package or configuration change is absent after restart.
Cause: Diskless or data-disk persistence was not completed through the supported workflow.
Evidence: Boot mode, mount layout, and persistence artifact state show the missing durable step.
Safe next action: Use the documented persistence route and verify after the next activation window.

### `.apk-new` appears

Symptom: apk leaves a new configuration candidate beside the active configuration.
Cause: Packaged defaults conflict with a locally managed configuration file.
Evidence: The conflict artifact and configuration provenance identify both owners.
Safe next action: Reconcile deliberately, validate component syntax, and verify the active service.

### `systemctl` is unavailable

Symptom: A Linux-oriented service command does not exist or does not manage the workload.
Cause: The target uses OpenRC or another discovered control plane.
Evidence: Init process, service scripts, and runlevel state identify the actual manager.
Safe next action: Use the observed manager and retain platform-specific evidence.

### Package transaction is blocked

Symptom: apk reports a lock, busy state, or conflicting transaction.
Cause: Another update process or management layer owns the package database.
Evidence: Process, timer, and management records identify the owner.
Safe next action: Coordinate or wait; do not remove lock files blindly.

### Repository branch mismatch

Symptom: Candidate packages require unexpected replacements or incompatible versions.
Cause: Stable, edge, or third-party repository policy is inconsistent.
Evidence: Repository configuration, package origin, and transaction preview expose the mismatch.
Safe next action: Stop and restore or approve a coherent repository policy.

### Network edit loses access

Symptom: SSH or the intended management route fails after network/firewall work.
Cause: The wrong durable owner was edited or safety prerequisites were incomplete.
Evidence: Owner discovery, session state, and routing/firewall evidence show the fault.
Safe next action: Recover through the independent path and restore the validated prior state.

## Handoff

Report observed Alpine release, apk repositories, service/network/firewall owners, and persistence mode.
Include bounded package, persistence, service, logs, listener, and external-boundary evidence.
State whether configuration is runtime-only, persisted, image-managed, or unknown.
For a mutation, hand off scope, rollback, recovery route, validation, and stop condition.
Exclude secrets, full configurations, unbounded logs, and assumptions about diskless behavior.

## Official sources

- [Alpine Package Keeper](https://wiki.alpinelinux.org/wiki/Alpine_Package_Keeper)
- [Alpine diskless mode](https://wiki.alpinelinux.org/wiki/Diskless_Mode)
- [Alpine OpenRC](https://wiki.alpinelinux.org/wiki/OpenRC)
- [Source index](source-index.md)
