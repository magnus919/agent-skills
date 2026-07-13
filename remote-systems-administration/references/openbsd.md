# OpenBSD Overlay

## OpenBSD control planes

OpenBSD favors a coherent base system but still requires platform discovery. Identify release, architecture, base versus package ownership, active daemons, `/etc/rc.conf.local` state, PF state, and whether the host is a firewall/router before change.

Do not use Linux systemd commands or FreeBSD `service` conventions. OpenBSD's `rcctl` is the normal interface for inspecting, configuring, enabling, and controlling base and package daemons.

## Services with rcctl

`rcctl` can inspect configuration, enable/disable daemons, and invoke actions such as `check`, `configtest`, `reload`, `restart`, `start`, and `stop`. Prefer discovery and config validation before lifecycle changes.

```sh
rcctl ls all
rcctl get <daemon>
rcctl check <daemon>
rcctl configtest <daemon>
```

Enablement and daemon options are represented through rc configuration, including `/etc/rc.conf.local`. A successful restart is not the same as a healthy service. Inspect bounded logs, listening state, and the user-visible/dependent boundary.

## Packages and base updates

OpenBSD separates packages from system distribution files. `pkg_add` installs and updates packages; it is not the base-system updater. Packages are normally signed, and `pkg_add` rejects unsigned packages by default unless a policy override is explicitly used. Do not weaken signature validation to make an automation run pass.

`pkg_add -u` can update installed packages and their dependencies. Before a package update, inspect package origin, dependencies, service impact, disk space, and application compatibility. Use its non-mutating modes only as previews with the documented limitations understood.

For base-system errata and release lifecycle, use the appropriate OpenBSD mechanisms and release documentation, such as `syspatch` where applicable. Do not conflate package updates, syspatch, and a release upgrade.

## PF

PF is a security and availability boundary. Before any PF change:

1. capture the active ruleset and identify configuration ownership;
2. preserve the current SSH/admin session and create an independent authorized recovery path;
3. validate candidate rules before loading them, such as with `pfctl -n -f <file>`;
4. apply the smallest scoped change only after an explicit directive; and
5. verify retained administration access, expected allowed flow, expected denied flow, and relevant application health.

`pfctl -f` replaces a ruleset. `pfctl` options that enable/disable or flush PF state are not routine troubleshooting commands. Treat them as high-risk, scope them precisely, and never use them to “clean up” without explicit authorization and recovery planning.

## Operational character

OpenBSD's secure defaults and clear base/package split do not make remote changes safe by default. Preserve package signature policy, configuration provenance, and connectivity. Prefer documented base controls over improvised wrappers, and use the release-specific manuals before asserting a current lifecycle command or support status.
