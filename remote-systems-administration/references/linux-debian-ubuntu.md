# Debian and Ubuntu Overlay

## Scope and discovery

Use this overlay only after observing a Debian or Ubuntu host with APT/dpkg.
Record `/etc/os-release`, architecture, kernel, virtualization, and support state.
Record the actual init, log, network, firewall, cloud-init, and configuration-management owners.
Do not infer systemd, Netplan, NetworkManager, or unattended upgrades from the distribution name.
Identify whether the target is a container, immutable image, VM, or bare-metal host.
Separate the requested component from its package, configuration, and service owners.
Treat an unsupported release as a lifecycle finding, not permission for an unreviewed upgrade.

## Read-only preflight

Inspect package origins, enabled suites, pinning, holds, and the candidate package version.
Inspect package-manager activity and identify the process or timer holding any lock.
Inspect service state, recent bounded logs, listening sockets, and the relevant client boundary.
Inspect network configuration provenance before touching addresses, DNS, routes, or interfaces.
Identify whether Netplan, NetworkManager, systemd-networkd, cloud-init, or automation owns it.
Inspect firewall ownership before assuming UFW, nftables, iptables compatibility tooling, or another layer.
Record disk capacity, reboot indicators, backup or snapshot scope, and recovery access for lifecycle work.
Stop discovery when the active owners and requested boundary are evidenced.

## Command preflight

Run only commands applicable to the observed host; an absent optional command means its control plane is unconfirmed.

| Question | Read-only command |
|---|---|
| Release and init | `. /etc/os-release; printf '%s %s\n' "$ID" "$VERSION_ID"; ps -p 1 -o pid= -o comm=` |
| Unit and bounded logs | `systemctl status <unit> --no-pager`; `journalctl -u <unit> -n 50 --no-pager` |
| Candidate, installed, and held package | `apt-cache policy <package>`; `dpkg-query -W -f='${Status} ${Version}\n' <package>`; `apt-mark showhold` |
| Network/configuration owner | `command -v netplan >/dev/null 2>&1 && netplan get`; `command -v nmcli >/dev/null 2>&1 && nmcli general status`; `networkctl status --no-pager 2>/dev/null` |
| Firewall and cloud-init owner | `command -v ufw >/dev/null 2>&1 && ufw status`; `command -v nft >/dev/null 2>&1 && nft list ruleset`; `command -v cloud-init >/dev/null 2>&1 && cloud-init status --long` |

## Services and logs

Use the observed service manager; systemd is common but remains a target fact.
For a systemd host, inspect unit state and recent bounded journal evidence before restart or reload.
Inspect the daemon process and listener because an active unit alone does not prove usability.
Check configuration syntax with the component's native validator where it has one.
Determine whether a package maintainer script, timer, socket unit, or application supervisor starts the service.
After an authorized change, verify manager state, logs, listener, and the user or dependent-service boundary.
Do not use a live log follow as routine evidence; bound by time, unit, process, or line count.

## Packages and repositories

APT metadata refresh and package installation are distinct operations with different impact.
Before an authorized transaction, inspect proposed installs, upgrades, removals, held packages, and origins.
Treat unexpected removals, suite changes, vendor changes, or unauthenticated packages as stop conditions.
dpkg conffile decisions require deliberate ownership and active-configuration verification.
Do not bypass signature, dependency, or conffile protections merely to make automation complete.
Third-party repositories, PPAs, backports, and vendor repositories require explicit compatibility review.
Coordinate with the owner of `apt-daily`, `unattended-upgrades`, or another package transaction; do not delete locks.
Verify the package database result and the expected binary or service behavior after a transaction.

## Release and base lifecycle

Routine package updates are not Debian or Ubuntu release upgrades.
Debian and Ubuntu each require their own release-specific upgrade procedure, separate from routine APT package maintenance.
Use the applicable vendor procedure for a supported distribution upgrade only after explicit authorization.
Confirm supported source and destination releases, repository policy, maintenance window, and rollback/recovery plan.
For Ubuntu, distinguish Canonical-managed release upgrades from ordinary APT package maintenance; for Debian, use the Debian release notes for the observed source and destination releases.
Inspect reboot requirements and coordinate kernel, bootloader, out-of-tree module, and workload impact.
Do not change release sources, force a release tool, or combine a major upgrade with unrelated repository cleanup.
After an authorized reboot, verify reachability, booted kernel, critical units, network path, and application boundary.

## Networking and firewall ownership

Network configuration may be generated by Netplan, cloud-init, NetworkManager, systemd-networkd, or automation.
Firewall policy may be owned by UFW, nftables, iptables compatibility rules, a cloud layer, or automation.
Do not translate rules mechanically between these control planes or edit generated configuration as a durable fix.
For any SSH, DNS, route, interface, VPN, or firewall mutation, use the [safety gate](safety-and-verification.md#connectivity-preserving-changes).
The gate requires explicit authority, a retained session, independent recovery, validated rollback, and stop condition.
Verify retained administration access and intended traffic behavior before considering a network change complete.

## Storage and persistence

Identify root and data filesystems, mount units, encryption, LVM/RAID, snapshots, and backup ownership before lifecycle work.
Do not confuse a filesystem snapshot with an application-consistent backup or an authorized rollback.
Confirm free space for package caches, unpacking, logs, and any planned boot artifacts.
For containers or image-built hosts, determine whether a local edit survives replacement or redeployment.
Persist service configuration in the owner-approved location, not only in a generated runtime file.
Storage, mount, encryption, or deletion work is lifecycle or destructive work and requires the shared mutation gate.

## Failure signatures

### APT lock

Symptom: APT reports a lock held by another process.
Cause: An active package transaction, timer, or administrator owns the package database.
Evidence: The observed lock holder and timer or process state identify the owner.
Safe next action: Wait or coordinate with that owner; never remove a lock by guesswork.

### Unexpected package removals

Symptom: The proposed transaction removes workload or platform packages.
Cause: Repository, pinning, dependency, or release-policy drift changed the solver result.
Evidence: Candidate versions, origins, holds, and the proposed transaction show the delta.
Safe next action: Stop and reconcile policy and compatibility before any transaction.

### Conffile prompt or retained local file

Symptom: dpkg requests a conffile decision or preserves a local version.
Cause: The package-provided configuration differs from a locally managed file.
Evidence: dpkg output and configuration-management ownership establish both versions.
Safe next action: Make an owned decision, validate syntax, and verify the active service configuration.

### Network edit reverts

Symptom: A manually changed network file is overwritten or does not affect runtime state.
Cause: A higher-level generator or manager owns the configuration.
Evidence: Netplan, cloud-init, NetworkManager, systemd-networkd, or automation provenance is present.
Safe next action: Route the change through the confirmed owner after the connectivity gate.

### Reboot-required state

Symptom: The host indicates a reboot is required or an update policy schedules one.
Cause: A kernel, library, or policy update requires a new boot or process restart.
Evidence: Release policy, reboot markers, unit state, and pending update records support the finding.
Safe next action: Use an approved maintenance and recovery plan; do not reboot opportunistically.

### Active unit, unavailable application

Symptom: A service manager reports active while users cannot use the application.
Cause: Listener, dependency, credentials, configuration, or upstream health is failing.
Evidence: Bounded logs, socket state, local protocol check, and boundary probe disagree with unit state.
Safe next action: Diagnose the failed layer read-only before considering a restart or config change.

## Handoff

Report target, release, package and service owners, and all unknowns from observed evidence.
Include bounded package, service, log, listener, and external-boundary evidence.
State whether the requested work is read-only, reversible, connectivity-sensitive, lifecycle, or destructive.
For a mutation, name exact scope, rollback artifact, recovery path, validation, and stop condition.
Do not include secrets, full configuration files, unrestricted logs, or unverified assumptions.

## Official sources

- [Ubuntu software management](https://documentation.ubuntu.com/server/tutorial/managing-software)
- [Ubuntu automatic updates](https://documentation.ubuntu.com/server/how-to/software/automatic-updates/)
- [Debian stable upgrade guide](https://www.debian.org/releases/stable/release-notes/upgrading.en.html)
- [Ubuntu release-upgrade guide](https://documentation.ubuntu.com/server/how-to/software/upgrade-your-release/)
- [systemctl manual](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)
- [nftables wiki](https://wiki.nftables.org/wiki-nftables/index.php/Main_Page)
- [Source index](source-index.md)
