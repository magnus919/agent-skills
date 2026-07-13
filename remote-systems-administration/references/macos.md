# macOS Overlay

## Establish the management boundary

macOS is a Unix platform with Apple-owned system management layers. Before acting, identify the macOS version, whether the target is a user or system domain, device-management/profile ownership, FileVault or recovery implications, installed management tooling, and whether a setting belongs to macOS, a configuration profile, an MDM, or a third-party package manager.

Do not manage macOS as a lightly branded Linux host. `systemctl`, Linux package managers, and BSD rc tools are not macOS control planes.

## launchd and launchctl

launchd manages system and user services through domains and labels. `launchctl` operations are scoped to the relevant domain; a label alone is not a portable service identity. Discover the existing launchd job, its owner, program path, logs, and bootstrap configuration before changing it.

Use `launchctl` for inspection and lifecycle work only after identifying the correct system/user context. Do not unload or disable core services casually. Verify the job's state, process/listener behavior, relevant logs, and the application boundary after a change.

A Homebrew service, an application helper, a LaunchDaemon, and a LaunchAgent can have different ownership and persistence semantics. Follow the manager that owns the job rather than mixing control planes.

## Updates and software installation

`softwareupdate` addresses Apple-provided update workflows. Use Apple deployment documentation and the target release's supported management path before planning an update. An OS update can affect restarts, FileVault unlock, management enrollment, kernel/system extensions, application compatibility, and recovery behavior.

Homebrew is a separate third-party package manager. If it is present and authorized for the target, use its documented commands and respect formula/cask provenance, update behavior, service ownership, and user context. Do not install Homebrew merely to obtain a Unix package without an explicit directive.

Before any broad update:

1. distinguish Apple OS/security updates from Homebrew or other third-party packages;
2. establish maintenance window, power/network requirements, restart expectations, and recovery access;
3. inventory critical applications and management/profile constraints;
4. stage or canary where multiple hosts are involved; and
5. verify boot, login/management state, required launchd jobs, networking, and the affected application boundary.

## Configuration and profiles

Managed configuration profiles and MDM policy can reapply settings. Discover the source of truth before editing preferences or configuration files. A local change that is overwritten by management is not a successful operational fix.

System Integrity Protection, privacy controls, TCC, signed system volumes, and Apple platform security may make a direct Unix-style edit unsupported or ineffective. Do not attempt to weaken these controls or bypass authorization. Report the governing policy and the legitimate administration route.

## Networking and firewall

macOS has multiple security/networking layers, including PF and the Application Firewall. They serve different purposes. Discover which layer owns the requested policy before altering it. Never assume a PF rule changes application-level firewall behavior, or vice versa.

Network, PF, remote-login, VPN, DNS, routing, and firewall changes can strand a remote session. Preserve a current session and an independent authorized recovery path, validate candidate configuration, make the smallest change, and verify both retained administrative access and intended traffic behavior. Apple's Application Firewall is app/service admission control, whereas PF is a packet-filter control plane; identify which question is being asked before changing either.

## Logs and verification

Use bounded, relevant evidence. macOS unified logging can be extensive; scope by process, subsystem, predicate, or time range. A `launchctl` result or a successful command is component evidence only. Verify the actual listener, app behavior, dependent service, or user-visible workflow that motivated the change.
