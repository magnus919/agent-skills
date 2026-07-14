# RHEL and Fedora Overlay

## Scope and discovery

Use this overlay after observing a RHEL, Fedora, or Yum/DNF/RPM-compatible host.
Record vendor, exact release, architecture, kernel, support entitlement, and whether it is a derivative.
Compatible distributions do not inherit Red Hat support, subscription, or major-upgrade procedures.
Discover service, logging, network, firewall, repository, and configuration-management ownership from the host.
Identify whether the system is a container, cloud image, immutable variant, VM, or bare-metal host.
Separate Red Hat content, Fedora content, vendor content, and local repositories in the evidence.
Treat unknown support status or repository provenance as a blocker for lifecycle work.

## Read-only preflight

Inspect enabled repositories, subscription state where applicable, priorities, excludes, and package origins.
Inspect installed and available package versions, the observed package manager's history, holds or version locks, and module streams only where DNF is present.
Preview the proposed transaction and record every install, upgrade, downgrade, removal, and obsoleted package.
Inspect service state, bounded logs, process/listener state, and the affected external boundary.
Discover NetworkManager, legacy scripts, cloud tooling, or automation before a connectivity change.
Discover whether firewalld or direct nftables owns active packet-filter policy.
Record disk capacity, reboot impact, snapshots/backups, and an authorized recovery route for lifecycle work.

## Command preflight

Run only commands applicable to the observed target. Target-major lifecycle work remains target-version-specific even when `ID_LIKE` routes here. Use DNF module commands only after confirming DNF is available; a yum-only RHEL/CentOS-compatible target does not establish DNF module semantics.

| Question | Read-only command |
|---|---|
| Release and init | `. /etc/os-release; printf '%s %s\n' "$ID" "$VERSION_ID"; ps -p 1 -o pid= -o comm=` |
| Unit and bounded logs | `systemctl status <unit> --no-pager`; `journalctl -u <unit> -n 50 --no-pager` |
| DNF repositories, history, modules | `dnf repolist`; `dnf history list`; `dnf module list --enabled` |
| Yum-only repositories, history, package | `yum repolist`; `yum history`; `yum info <package>` |
| DNF package provenance and locks | `dnf info <package>`; `dnf versionlock list 2>/dev/null` |
| Network and firewall owner | `command -v nmcli >/dev/null 2>&1 && nmcli general status`; `command -v firewall-cmd >/dev/null 2>&1 && firewall-cmd --state`; `command -v nft >/dev/null 2>&1 && nft list ruleset` |

## Services and logs

Most current targets use systemd and journald, but verify this before selecting commands.
Inspect the unit, its enablement, dependency failures, recent bounded journal evidence, process, and listener.
Determine whether a socket, timer, container runtime, or application supervisor owns service activation.
Run the component's native configuration validation before an authorized reload or restart where available.
Verify component state and the relevant client, dependent service, or user-visible boundary after a change.
Do not treat a green unit state or a successful manager action as proof that the workload is healthy.

## Packages and repositories

DNF/Yum and RPM repository policy is part of the system's operational contract. On yum-only targets, use yum inspection commands and do not infer DNF features, including module streams.
Before an authorized update, inspect solver output, package origin, exclusions, version locks, and stream/module state.
Treat unexpected removals, downgrades, stream switches, or third-party replacements as stop conditions.
Do not disable signature checks, force package replacement, or mix vendor repositories to clear a solver error.
Separate Red Hat subscription content from EPEL, Fedora, application-vendor, and local content.
Check service restarts, configuration migrations, disk requirements, and workload compatibility before broad changes.
Verify RPM database state and the intended binary or service boundary after the transaction.

## Release and base lifecycle

Routine DNF updates are not a supported major RHEL upgrade.
Before lifecycle work, select Red Hat documentation matching the observed target major release; RHEL 9 references do not establish a procedure for another major release.
Follow Red Hat's exact release-specific in-place procedure, including prerequisites such as Leapp when documented.
For Fedora, use the Fedora-supported release lifecycle rather than transposing a RHEL procedure.
Confirm source and destination support, subscription/entitlement, repository compatibility, and third-party application support.
Major changes require explicit authorization, maintenance ownership, tested recovery, and post-boot validation.
Do not change release packages, streams, or repositories speculatively to make an upgrade solver succeed.
After a reboot, verify expected kernel, services, network access, application behavior, and management connectivity.

## Networking and firewall ownership

NetworkManager, cloud-init, legacy network scripts, and automation have distinct persistence models.
firewalld is a policy owner above nftables; direct nftables may instead be the active owner.
Do not combine `firewall-cmd` changes with direct nftables edits until the active source of truth is known.
For SSH, route, DNS, interface, VPN, or firewall work, follow the [connectivity safety gate](safety-and-verification.md#connectivity-preserving-changes).
It requires authorization, retained access, independent recovery, validated rollback, canary scope, and a stop condition.
Verify retained administration access plus expected allow and deny behavior at the intended boundary.

## Storage and persistence

Identify root and data filesystems, LVM, RAID, encryption, mount ownership, snapshots, and backup scope.
Confirm transaction and boot space before package or lifecycle work.
Do not describe an LVM or filesystem snapshot as complete recovery without proving included data and application consistency.
For image-managed or immutable targets, establish whether a local package or configuration change survives redeployment.
Mount, partition, encryption, and deletion operations require the lifecycle or destructive shared gate.
Preserve evidence of storage scope and recovery feasibility in the handoff.

## Failure signatures

### Solver proposes removals

Symptom: DNF proposes removing a critical workload, platform, or dependency package.
Cause: Repository drift, incompatible streams, version locks, or conflicting dependencies changed the solution.
Evidence: Transaction preview, package origins, excludes, and stream state identify the conflict.
Safe next action: Stop and reconcile supported repositories and application compatibility.

### Unexpected repository origin

Symptom: A candidate is sourced from an unapproved or surprising repository.
Cause: Repository configuration, priorities, or a third-party package replaced vendor content.
Evidence: Enabled repository list and package provenance show the source.
Safe next action: Restore or approve repository policy before changing the package set.

### firewalld conflicts with direct nftables

Symptom: A rule appears to be overwritten, duplicated, or ineffective.
Cause: Two control planes are being used without a confirmed source of truth.
Evidence: Active service state, ruleset provenance, and configuration-management records reveal the owner.
Safe next action: Stop; select the confirmed policy owner and pass the connectivity gate.

### Major change presented as a normal update

Symptom: A proposed action changes major release or core platform components unexpectedly.
Cause: Lifecycle work was attempted as a routine package transaction.
Evidence: Release packages, repository suites, and transaction output show a platform transition.
Safe next action: Use the vendor-supported, release-specific procedure after explicit authorization.

### Reboot recovers SSH but not workload

Symptom: The host is reachable after reboot but the application is unavailable.
Cause: Kernel, dependency, unit ordering, listener, or external dependency did not recover.
Evidence: Booted kernel, unit state, bounded logs, socket state, and boundary probe isolate the layer.
Safe next action: Keep the recovery route and diagnose read-only before another change.

### Active unit lacks usable listener

Symptom: The service reports active but no expected socket or protocol response exists.
Cause: Misconfiguration, port conflict, startup mode, dependency, or application failure.
Evidence: Unit details, process arguments, bounded logs, and socket evidence disagree.
Safe next action: Validate configuration and ownership before an authorized corrective action.

## Handoff

Report vendor and release evidence, support state, repository origins, and active control-plane owners.
Include bounded transaction, service, logs, listener, and external-boundary evidence.
Classify pending work and explicitly state all unverified assumptions or blockers.
For any mutation, hand off target scope, rollback, recovery path, validation method, and stop condition.
Avoid secrets, unrestricted journal output, full configuration files, and inferred support claims.

## Official sources

- [DNF upstream documentation](https://dnf.readthedocs.io/en/latest/)
- [Red Hat package-management guide (RHEL 9 documentation)](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/managing_software_with_the_dnf_tool/index)
- [RHEL 8 to RHEL 9 upgrade guide (RHEL 9 documentation)](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html-single/upgrading_from_rhel_8_to_rhel_9/index)
- [systemctl manual](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)
- [nftables wiki](https://wiki.nftables.org/wiki-nftables/index.php/Main_Page)
- [Source index](source-index.md)
