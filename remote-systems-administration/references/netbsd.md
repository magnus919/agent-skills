# NetBSD Overlay

## NetBSD is a separate platform

NetBSD uses its own rc.d system, base-system lifecycle, and pkgsrc package framework. Do not treat FreeBSD's release tooling, OpenBSD `rcctl`, or Linux systemd/package commands as NetBSD controls.

Discover the NetBSD release, architecture, active service configuration, package source, firewall implementation, and whether a setting belongs to the base system, pkgsrc, or another management layer.

## rc.d services

NetBSD's rc.d system uses `/etc/rc`, `/etc/rc.conf`, `/etc/rc.d`, `/etc/rc.local`, `/etc/rc.shutdown`, `/etc/rc.subr`, defaults under `/etc/defaults`, and optional overrides under `/etc/rc.conf.d`. Do not edit defaults to override a setting; use the documented configuration layer.

`service` is the normal alias for invoking rc.d scripts. Scripts support at least lifecycle actions such as `start`, `stop`, `restart`, and `status`; some support actions including `reload`. Verify the script and its configuration before relying on an action.

```sh
service <name> status
service <name> restart
```

A package can install an rc.d script, but that does not automatically make it an active boot service. Identify the script location, enablement/configuration, daemon process/listener, and dependent application boundary before declaring success.

## pkgsrc and packages

pkgsrc is the framework for third-party software. It can use prebuilt binary packages or build packages from source. `pkg_add` operates on binary packages; `pkgin` is a user-friendly frontend when installed. Package origins, repository branch, local prefix, dependencies, and source/binary policy matter before any upgrade.

Before an upgrade, inspect the repository configuration, installed set, compatibility implications, disk space, planned service effects, and rollback/recovery option. A pkgsrc quarterly branch or binary repository change is not an ordinary single-package update. Do not mix package locations or change `LOCALBASE` on an existing system without following the pkgsrc guidance.

Base-system maintenance is separate from pkgsrc. Use release-specific NetBSD documentation for base updates and release upgrades; do not substitute a package-manager operation for an OS lifecycle procedure.

## Firewalls, networking, and verification

Discover the active firewall and network configuration owner before changing rules, routes, interfaces, or DNS. Preserve remote access with a retained session and an independent authorized recovery channel. Validate candidate configuration where possible, apply the smallest scoped change, test the administration path and intended flow, then validate the application boundary.
