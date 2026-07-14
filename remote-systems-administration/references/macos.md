# macOS Overlay

## Scope and discovery

macOS uses Apple-owned system-management layers, not lightly branded Linux or BSD rc controls.
Record macOS version, architecture, user versus system context, device ownership, and available recovery/console access.
Discover MDM enrollment, configuration profiles, management tooling, FileVault implications, and authorized administration route.
Identify whether the requested state is owned by macOS, a profile, MDM, launchd, application, or third-party package manager.
Discover network-service, VPN, DNS, route, Application Firewall, PF, and remote-login ownership before access-sensitive work.
Identify signed-system-volume, SIP, TCC, privacy, and platform-security constraints as policy boundaries.
Treat unknown management/profile ownership as a blocker for persistent configuration mutation.

## Read-only preflight

Inspect the operating-system version, Apple update availability, reboot implications, and management/profile state.
Inspect launchd domain, label, owner, executable, configuration provenance, process state, and bounded relevant log evidence.
Inspect listener behavior and the actual user, client, or dependent-service boundary.
Inspect installed third-party package managers and their prefixes, provenance, service ownership, and user context.
Inspect active network services, configuration source, firewall/PF ownership, remote-access route, and recovery path.
Inspect storage, FileVault/restart recovery implications, backup scope, free space, and application compatibility for lifecycle work.
End discovery after the durable owner and verification boundary are established; do not bypass platform controls.

## Command preflight

Run only commands applicable to the observed macOS release and domain. `softwareupdate --list` may make an outbound vendor query but does not perform an update; it still needs normal authorized network access. A profile, MDM enrollment, PF state, or Application Firewall state identifies a follow-up ownership question, not permission to change it. PF inspection requires authorized privilege on the target; a missing, empty, or permission-denied PF result is `unknown`, not evidence that PF is inactive. Profile payload inspection is sensitive: scope and redact it through an authorized management path, and do not paste payloads into evidence.

| Question | Read-only command |
|---|---|
| OS and Apple updates | `sw_vers`; `softwareupdate --list` |
| launchd job and bounded logs | `launchctl print system/<label>`; `log show --last 5m --predicate 'process == "<process>"'` |
| Management/profile evidence | `profiles status -type enrollment` |
| Network and firewall ownership | `networksetup -listallnetworkservices`; `command -v /usr/libexec/ApplicationFirewall/socketfilterfw >/dev/null 2>&1 && /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate`; `sudo -n pfctl -s info` |
| Third-party package/service evidence | `command -v brew >/dev/null 2>&1 && brew config`; `command -v brew >/dev/null 2>&1 && brew services list` |

## Services and logs

launchd manages system and user jobs through domains and labels; a label alone is not a portable service identity.
Discover the relevant system or user domain before using `launchctl` for inspection or authorized lifecycle work.
Differentiate LaunchDaemons, LaunchAgents, application helpers, and Homebrew services by their owner and persistence model.
Do not unload, disable, or modify core Apple services casually.
Use bounded unified-log evidence scoped by time, process, subsystem, or predicate; unbounded logs are not useful evidence.
After change, verify launchd state, process/listener, relevant logs, and the user-visible or dependent boundary.
A successful launchctl action proves only a manager-level result.

## Packages, updates, and repositories

`softwareupdate` addresses Apple-provided update workflows; follow the target release's supported management path.
Apple OS/security updates, application updates, Homebrew, MacPorts, and vendor installers are separate lifecycles.
Do not install Homebrew or another package manager merely to obtain a Unix package without an explicit directive.
If Homebrew is present and authorized, discover its prefix rather than hardcoding an architecture-dependent path.
Inspect package provenance, user context, formula/cask/service ownership, and application impact before a transaction.
Treat unexpected replacements, management policy conflict, restart needs, or untrusted provenance as stop conditions.
Verify package/update result and the affected application or service boundary afterward.

## Release and base lifecycle

Apple updates can affect restart, FileVault unlock, management enrollment, extensions, application compatibility, and recovery.
Separate routine Apple update planning from a major macOS upgrade and from third-party package maintenance.
Confirm maintenance window, power/network expectations, management constraints, backup/recovery, and authorized restart path.
Stage or canary fleet work; do not apply broad lifecycle changes to all managed devices first.
Do not bypass SIP, TCC, MDM, profile policy, or signed-system-volume protection to complete a change.
Require explicit lifecycle authorization before an update/restart that impacts availability or remote recovery.
After reboot, verify boot, login/management state, required jobs, network access, and application boundary.

## Networking and firewall ownership

macOS has separate network-service controls, PF packet filtering, and Application Firewall app/service admission controls.
Discover which layer owns the requested behavior; a PF change does not imply an Application Firewall change, or vice versa.
Use target-host `networksetup(8)` documentation for version-specific network-service behavior.
Configuration profiles or MDM may own network and firewall state and can reapply settings after local edits.
For remote login, VPN, DNS, route, network-service, PF, or firewall work, use the [connectivity safety gate](safety-and-verification.md#connectivity-preserving-changes).
Require explicit authority, retained connection, independent recovery, validated rollback, canary scope, and stop condition.
Verify retained administrative access plus intended traffic behavior at the actual policy layer.

## Storage and persistence

Identify APFS volumes, available free space, FileVault implications, backups, recovery mode, and managed-device replacement strategy.
Do not claim a local preference edit is persistent until its MDM/profile and application owner are known.
System volumes and Apple security mechanisms may make direct file edits unsupported or ineffective.
Treat a backup as recovery evidence only after its scope and authorized restoration path are known.
Storage, encryption, volume, deletion, and recovery changes are lifecycle or destructive work under the shared gate.
Preserve management and startup recovery evidence in every lifecycle handoff.

## Failure signatures

### launchctl label works only in one context

Symptom: A launchd label is visible or controllable for one user/domain but not another.
Cause: The job belongs to a distinct system or user launchd domain.
Evidence: Domain, job owner, bootstrap configuration, process, and log evidence establish scope.
Safe next action: Use the confirmed domain and owner; do not treat the label as globally scoped.

### Preference or firewall setting reverts

Symptom: A local change disappears or is overwritten after management activity.
Cause: A configuration profile or MDM owns the durable state.
Evidence: Profile/MDM inventory and setting provenance identify the source of truth.
Safe next action: Route the desired change through the supported management channel.

### Apple and Homebrew updates diverge

Symptom: An Apple update succeeds while a third-party service/package remains unchanged or fails.
Cause: Apple and Homebrew have different package origins, user contexts, and service ownership.
Evidence: Software update and package-manager records show separate lifecycle results.
Safe next action: Assess each lifecycle separately and verify the affected workload boundary.

### Application Firewall does not affect PF traffic

Symptom: An Application Firewall adjustment does not change a packet-filtered connection, or vice versa.
Cause: The two controls own different layers of policy.
Evidence: Active PF rules, firewall configuration, and traffic behavior isolate the policy layer.
Safe next action: Stop and select the confirmed owner under the connectivity gate.

### Unified-log query is inconclusive

Symptom: Log output is too broad, redacted, or unrelated to the service condition.
Cause: The query lacks a bounded time/process/subsystem/predicate scope.
Evidence: Query scope and correlation with process/listener evidence show the gap.
Safe next action: Narrow the evidence and verify the listener or application boundary directly.

### Restart cannot recover remote management

Symptom: An update requires restart but FileVault, enrollment, or remote management recovery is uncertain.
Cause: Startup unlock or management path was not confirmed before lifecycle work.
Evidence: Device security, management, and recovery evidence shows the missing prerequisite.
Safe next action: Stop before restart and establish an authorized recovery plan.

## Handoff

Report macOS version, user/system context, MDM/profile ownership, launchd domain, and network/firewall policy owner.
Include bounded update, job, log, listener, management, and external-boundary evidence.
State FileVault/restart recovery limits, package-manager provenance, and all policy blockers.
For mutation, provide target scope, rollback, independent recovery, validation, and stop condition.
Exclude secrets, profile payloads, unrestricted unified logs, and instructions to bypass Apple security controls.

## Official sources

- [Apple launchd jobs](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)
- [Apple Platform Deployment](https://support.apple.com/guide/deployment/welcome/web)
- [Apple firewall settings](https://support.apple.com/guide/mac-help/change-firewall-settings-mh34041/mac)
- [Firewall payload settings](https://support.apple.com/guide/deployment/firewall-payload-settings-dep8d306275f/web)
- [Homebrew manpage](https://docs.brew.sh/Manpage)
- [Source index](source-index.md)
