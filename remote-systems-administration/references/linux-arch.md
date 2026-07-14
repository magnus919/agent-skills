# Arch Linux Overlay

## Scope and discovery

Use this overlay after observing Arch Linux and pacman on the target.
Confirm the actual distribution because an Arch derivative can have different repositories and support policy.
Record release context, kernel, architecture, enabled repositories, mirrors, package cache, and local package sources.
Identify AUR/local builds, package hooks, service manager, logger, network owner, firewall owner, and automation.
Establish recovery media, boot arrangement, storage scope, and independent administrative access before broad lifecycle work.
Arch's rolling-release model makes current maintenance guidance part of safe planning.
Treat unknown repository or local-build provenance as a blocker for a broad update.

## Read-only preflight

Read current Arch news and relevant package-maintenance guidance before a planned full-system upgrade.
Inspect synchronization state, installed packages, package origins, local/AUR builds, cache availability, and pending `.pacnew`/`.pacsave` files.
Preview the proposed full transaction and record installs, upgrades, removals, replacements, and hook effects.
Inspect service state, bounded logs, process/listener state, and the affected client or dependency boundary.
Discover systemd, network configuration, firewall, and configuration-management ownership from the live host.
Record free space, snapshots/backups, boot recovery, and package rebuild impact.
Stop preflight when the requested scope and all durable owners are evidenced.

## Command preflight

These commands inspect existing local and sync state; they do not refresh databases. Their output never authorizes a partial upgrade.

| Question | Read-only command |
|---|---|
| Platform and init | `uname -r`; `ps -p 1 -o pid= -o comm=` |
| Unit and bounded logs | `systemctl status <unit> --no-pager`; `journalctl -u <unit> -n 50 --no-pager` |
| Installed package and update state | `pacman -Q <package>`; `pacman -Qu`; `pacman -Qdt` |
| Repository and package files | `pacman-conf`; `pacman -Qo <path>` |
| Network and firewall owner | `command -v nmcli >/dev/null 2>&1 && nmcli general status`; `networkctl status --no-pager 2>/dev/null`; `command -v nft >/dev/null 2>&1 && nft list ruleset` |

## Services and logs

Most Arch installations use systemd and journald, but this must be observed rather than assumed.
Inspect unit state, enablement, dependencies, bounded logs, process, and listener before a lifecycle action.
Identify socket, timer, container, or application-supervisor activation before changing a service directly.
Use native configuration validation when the component provides it before an authorized reload or restart.
Verify service-manager state, logs, listener, and the real application boundary after a change.
Never use a successful unit action as the only availability claim.

## Packages and repositories

Arch supports full-system upgrades; do not perform partial upgrades.
Do not refresh sync databases and then install or upgrade isolated packages from a mismatched system state.
Inspect official repository policy separately from AUR helpers, manually built packages, and local repositories.
Signature, dependency, file-conflict, and hook failures are safety boundaries, not errors to force past.
Reconcile `.pacnew` and `.pacsave` changes deliberately with configuration ownership before claiming durable configuration.
The package cache may help recovery, but it is not a complete rollback plan or a substitute for tested restoration.
Verify package database results and the affected binary/service behavior after an authorized transaction.

## Release and base lifecycle

Arch is rolling release; a full package transaction is still not permission for an unbounded change window.
Use current official maintenance notices and explicit workload compatibility review for broad upgrades.
Plan kernel, initramfs, bootloader, driver, local-module, and service-restart impact before authorizing the update.
Do not combine repository migration, AUR rebuild work, configuration cleanup, and recovery changes without scoped approval.
Reboot only with explicit lifecycle authorization, recovery access, and a post-boot boundary verification plan.
If recovery is needed, use authorized recovery media and the documented procedure instead of forced package overwrites.

## Networking and firewall ownership

Network state may be owned by NetworkManager, systemd-networkd, iwd, netctl-era tooling, or automation.
Firewall state may be direct nftables, an iptables compatibility layer, a manager, or external policy.
Discover the active source of truth before changing DNS, routes, interfaces, SSH, VPN, or packet filtering.
For every connectivity-sensitive change, follow the [connectivity safety gate](safety-and-verification.md#connectivity-preserving-changes).
Retain the working session, provide independent recovery, validate rollback, use canary scope, and name the stop condition.
Verify retained access and the intended traffic or service boundary after the change.

## Storage and persistence

Identify root/data filesystems, mounts, encryption, RAID/LVM, snapshots, backup policy, and boot artifacts.
Confirm space for downloads, cache, unpacking, initramfs, and logs before a full-system transaction.
For image-built or declaratively managed systems, establish whether a local package/configuration edit survives deployment.
Do not call a snapshot a complete rollback without checking boot scope, data scope, and application consistency.
Storage, mount, partition, encryption, and deletion operations require the shared lifecycle or destructive gate.
Preserve recovery evidence before any authorized broad maintenance.

## Failure signatures

### Partial upgrade attempted

Symptom: Sync databases are refreshed and a single package is selected without a full system upgrade.
Cause: Package and library versions can become inconsistent in a rolling-release repository model.
Evidence: Pacman history and synchronization/transaction intent show the split operation.
Safe next action: Stop and plan a supported full-system transaction with current maintenance guidance.

### `.pacnew` or `.pacsave` is present

Symptom: Package maintenance leaves a new or saved configuration file.
Cause: Local configuration and packaged defaults diverged.
Evidence: The files, package metadata, and configuration owner establish the required reconciliation.
Safe next action: Compare and merge through the owner-approved process, validate, then verify active configuration.

### Signature or file conflict failure

Symptom: Pacman rejects a package signature or reports file ownership conflict.
Cause: Repository/key state, local modification, or package ownership requires investigation.
Evidence: Pacman output, keyring status, and file ownership evidence identify the boundary.
Safe next action: Investigate provenance; do not disable verification or force overwrite.

### Local/AUR package blocks update

Symptom: A locally built package or dependency cannot satisfy the current transaction.
Cause: Local build provenance and rebuild requirements lag the rolling repository state.
Evidence: Package origin, build metadata, and solver output show the incompatible package.
Safe next action: Scope and approve a rebuild or replacement separately from the base update.

### Reboot restores SSH but not workload

Symptom: The host boots but the application is unavailable.
Cause: Kernel, module, initramfs, unit dependency, configuration, or upstream dependency failed.
Evidence: Booted artifacts, bounded logs, unit/socket state, and boundary probes isolate the fault.
Safe next action: Preserve recovery access and diagnose read-only before additional changes.

### Network change strands host

Symptom: The expected management path fails after interface, DNS, route, or firewall modification.
Cause: The wrong owner was changed or the connectivity gate was not satisfied.
Evidence: Manager provenance, retained-session status, and route/firewall state show the failure.
Safe next action: Use the independent recovery path and restore the validated prior state.

## Handoff

Report distribution evidence, repositories, local/AUR package scope, current maintenance notices, and owner discovery.
Include bounded transaction, service, log, listener, and external-boundary evidence.
State recovery media/access, storage constraints, and all unknown package or configuration provenance.
For a mutation, name exact scope, rollback, recovery route, validation, and stop condition.
Do not disclose keys, full configs, unrestricted logs, or unverified conclusions.

## Official sources

- [Arch system maintenance](https://wiki.archlinux.org/title/System_maintenance)
- [Arch Pacman](https://wiki.archlinux.org/title/Pacman)
- [Arch nftables](https://wiki.archlinux.org/title/Nftables)
- [systemctl manual](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)
- [Source index](source-index.md)
