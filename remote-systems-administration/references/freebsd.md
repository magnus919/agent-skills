# FreeBSD Overlay

## FreeBSD is not Linux

FreeBSD uses its own base system, release engineering, rc framework, package toolchain, configuration conventions, and optional subsystems such as jails and ZFS. Do not transplant Linux systemd, APT/RPM, or nftables instructions.

Start by identifying the FreeBSD release, architecture, active services, package state, jail context, filesystem layout, and firewall implementation. When a host is inside a jail, distinguish a jail-level operation from a host-level operation before acting.

## Services and configuration

FreeBSD uses rc scripts and configuration conventions centered on files such as `/etc/rc.conf` and site-local `/etc/rc.conf.local`; `service` is the customary control interface for installed rc.d scripts. Inspect current configuration and the relevant rc script before enabling, restarting, or changing boot persistence.

```sh
service <name> status
service <name> onestatus
service <name> restart
```

The exact behavior belongs to the service's rc script. “Running” or a successful `service` exit does not prove that a daemon is listening or serving its dependency chain. Follow it with bounded logs/socket checks and the relevant external validation.

## Packages, ports, and base-system lifecycle

Use `pkg` for binary packages. The FreeBSD Handbook distinguishes packages from ports: packages are prebuilt artifacts, while ports automate source builds and permit compile-time choices. A package operation can affect dependencies and running services; plan the resulting restart/reload and validation.

Base-system updates and third-party packages are distinct lifecycles. Do not use package commands as a substitute for an OS release procedure. For release changes, kernel/base updates, boot-environment strategy, and ZFS rollback planning, follow the release-specific FreeBSD documentation.

On a ZFS host that supports it, `bectl` manages bootable ZFS clones. It can provide a deliberate pre-change recovery path because a boot environment can be selected by the boot loader. First verify `bectl check`, dataset scope, and excluded datasets; do not present a ZFS snapshot or boot environment as a universal rollback mechanism.

Before a broad package operation, inventory installed packages, update candidates, held policy if applicable, application compatibility, disk space, backups/snapshots, and restart impact. `pkg audit -F` is an advisory/vulnerability check, not a change command.

## Firewalls and networking

FreeBSD may use PF, IPFW, or another installed system. Discover the active firewall and configuration owner. PF and IPFW have distinct grammars and persistence mechanisms. Validate FreeBSD PF rules on the target and do not copy OpenBSD PF syntax or assumptions.

Firewall, route, DNS, interface, and remote-access changes require a retained session plus another recovery path. Validate syntax/configuration, make the smallest change, confirm that the administrator path remains open, then test the intended traffic flow.

## Jails and storage

Jails are an operating-system-level isolation mechanism with host/jail boundaries. Identify whether the target process, package database, network interface, and filesystem belong to a jail or its host. Do not administer a jail as if it controlled host services or firewall policy.

FreeBSD deployments often use ZFS. A snapshot can be a valuable rollback primitive, but it is not an authorization to use destructive rollback commands. Identify dataset scope, dependent services, replication/backup state, and recovery impact before snapshot, rollback, or dataset operations.
