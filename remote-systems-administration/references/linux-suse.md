# SUSE and openSUSE Overlay

## Scope and discovery

Use this overlay after observing a SUSE or openSUSE host using zypper and RPM.
Record product, exact release/service pack, registration state, architecture, and support status.
Discover enabled repositories, service manager, logger, network owner, firewall owner, and automation owner.
Establish whether the root is conventional read-write or transactional/read-only before planning persistence.
Do not generalize SLES, openSUSE Leap, Tumbleweed, MicroOS, or SLE Micro lifecycle rules.
Identify whether the target is image-managed, a container, VM, or physical system.
Treat product and root-mode ambiguity as a blocker for update or recovery claims.

## Read-only preflight

Inspect zypper repositories, priorities, vendor policy, registration, enabled modules, and proposed transaction.
Inspect installed packages, locks, patches, running package activity, and current booted snapshot where applicable.
Inspect units, bounded journal evidence, processes, listeners, and the relevant external boundary.
Identify NetworkManager, wicked, YaST, cloud tooling, or automation before changing connectivity.
Identify firewalld, direct nftables, or another firewall owner before touching policy.
Record snapshot, bootloader, disk-space, backup, and independent recovery evidence for lifecycle operations.
Stop once platform, owner, and requested boundary evidence is sufficient.

## Command preflight

Run only commands available on the observed product. `transactional-update` evidence is relevant only when that binary and root model are present.

| Question | Read-only command |
|---|---|
| Product and init | `. /etc/os-release; printf '%s %s\n' "$ID" "$VERSION_ID"; ps -p 1 -o pid= -o comm=` |
| Unit and bounded logs | `systemctl status <unit> --no-pager`; `journalctl -u <unit> -n 50 --no-pager` |
| Repositories, locks, patches | `zypper repos`; `zypper locks`; `zypper --no-refresh patches` |
| Package state | `zypper info <package>`; `rpm -q <package>` |
| Network, firewall, transactional root | `command -v nmcli >/dev/null 2>&1 && nmcli general status`; `command -v firewall-cmd >/dev/null 2>&1 && firewall-cmd --state`; `command -v transactional-update >/dev/null 2>&1 && transactional-update status` |

## Services and logs

Most supported SUSE targets use systemd and journald; confirm that from the target.
Inspect unit state, enablement, dependency status, bounded logs, process state, and listener before change.
Determine whether a timer, socket, container layer, or application supervisor owns activation.
Use component-native syntax validation before an authorized reload or restart where supported.
Verify manager state, logs, listener, and client or dependent-service behavior afterward.
Do not equate a successful systemd action with application availability.

## Packages and repositories

For conventional roots, inspect zypper's exact solver proposal before an authorized transaction.
Vendor changes, unexpected removals, repository changes, and unsupported package replacements are stop conditions.
Do not override solver, signature, or vendor protections simply to force an update through.
Confirm maintenance ownership, restart effects, configuration migrations, disk capacity, and workload compatibility.
Keep third-party repositories separate from vendor-supported lifecycle assumptions.
Verify package state and the expected binary or service boundary after a successful transaction.

## Release and base lifecycle

On a transactional root, `transactional-update` creates a new root snapshot for later boot activation.
Its successful completion does not mean the running root changed; reboot and selected snapshot evidence matter.
Discover automatic update and reboot scheduling before scheduling competing maintenance.
Use the documented transactional workflow rather than direct modification of the read-only root.
Do not claim a snapshot is rollback until its bootability, dataset scope, and application data implications are verified.
Ordinary package updates, transactional changes, and product release migrations remain separate lifecycle classes.
Any reboot requires the shared lifecycle gate and post-boot workload verification.

## Networking and firewall ownership

YaST, NetworkManager, wicked, cloud tooling, and configuration management can own durable network state.
firewalld and direct nftables are separate policy control planes with different ownership boundaries.
Do not edit a generated file or mix firewall layers as a durable solution.
For network, SSH, DNS, routes, interface, VPN, or firewall changes, use the [connectivity safety gate](safety-and-verification.md#connectivity-preserving-changes).
Require explicit authority, retained session, independent recovery, tested rollback, canary scope, and a stop condition.
Verify the administrative path and intended traffic behavior after the smallest authorized change.

## Storage and persistence

Identify root mode, snapshots, filesystems, mounts, encryption, RAID/LVM, bootloader, and backup ownership.
Confirm free space for RPM transactions and snapshots before update work.
On transactional systems, confirm which paths and datasets persist across snapshot activation.
Do not treat local runtime changes as durable when an image, snapshot, or automation layer replaces them.
Storage or mount changes are lifecycle work; rollback must cover data scope, not only the root filesystem.
Preserve storage and snapshot evidence in any handoff.

## Failure signatures

### zypper changes vendor or removes packages

Symptom: The solver proposes vendor switches, unexpected removals, or broad replacement.
Cause: Repository policy, product mismatch, or incompatible third-party content changed resolution.
Evidence: Repository list, priorities, vendor policy, and transaction preview show the cause.
Safe next action: Stop and reconcile supported repository and workload policy.

### Change is absent before reboot

Symptom: A completed transactional operation is not visible in the running root.
Cause: The update was staged in a snapshot pending boot activation.
Evidence: Transactional-update result and booted snapshot identity show the pending state.
Safe next action: Coordinate an authorized reboot and verify the selected snapshot and workload afterward.

### Repeated transactional operations surprise operators

Symptom: Multiple operations produce separate snapshots or unexpected staged results.
Cause: Transactional semantics and continuation/reboot requirements were not accounted for.
Evidence: Snapshot and transactional operation records show each pending root.
Safe next action: Follow the documented continuation or reboot path; do not modify the live root directly.

### Automatic update schedules reboot

Symptom: An update service indicates a pending or scheduled reboot.
Cause: Transactional automation owns part of the maintenance lifecycle.
Evidence: Observed timers, service configuration, and transactional logs establish ownership.
Safe next action: Coordinate maintenance and recovery access; do not race the automation.

### Direct root edit fails or disappears

Symptom: A root edit is denied, ineffective, or lost after activation.
Cause: A transactional read-only-root design owns the system state.
Evidence: Root mount mode, product documentation, and snapshot behavior confirm the model.
Safe next action: Use the documented transactional configuration path after confirming persistence.

### Active unit is not usable

Symptom: systemd reports success but clients cannot reach the expected service.
Cause: Listener, dependency, configuration, or external service health is failing.
Evidence: Bounded journal, process/socket evidence, and boundary checks disagree with unit state.
Safe next action: Diagnose the failing layer read-only before another lifecycle action.

## Handoff

Report observed product, release, root mode, repositories, service/network/firewall owners, and support state.
Include bounded solver, snapshot, service, log, listener, and boundary evidence.
Classify the work and state all lifecycle, persistence, and recovery uncertainties.
For changes, specify scope, rollback snapshot or artifact, recovery route, validation, and stop condition.
Exclude secrets, full configuration contents, and unbounded logs.

## Official sources

- [Zypper (SLES 15 SP6 documentation)](https://documentation.suse.com/sles/15-SP6/html/SLES-all/cha-sw-cl.html)
- [SUSE lifecycle](https://www.suse.com/lifecycle/)
- [openSUSE lifetime](https://en.opensuse.org/Lifetime)
- [SLES transactional updates](https://documentation.suse.com/sles/15-SP6/html/SLES-all/cha-transactional-updates.html)
- [SLE Micro transactional updates](https://documentation.suse.com/sle-micro/6.0/html/Micro-transactional-updates/index.html)
- [systemctl manual](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)
- [Source index](source-index.md)
