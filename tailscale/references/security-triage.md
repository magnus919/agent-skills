# Tailscale / Headscale security triage

## Evidence and freshness

Reviewed 2026-10-25 (America/New_York). [Tailworm](https://www.tailworm.com/)
is Erica Windisch / Cyberdione Labs' primary research report, claiming lab reproductions
against Tailscale 1.104.2 and Headscale 0.29.5 on October 22–24. These are researcher
claims, not independent reproductions by this skill's authors. Internal finding labels
are not CVE identifiers. Do not infer all versions or deployments are affected.

Acquisition: GroktoCrawl, job `7dc84202-8fd0-43c6-8c97-35dd31ab6420`,
depth 10 / cap 150, completed with discovered=1, retained=1, failed=0, blocked=0,
no next page; 53,276 markdown characters. All report navigation was same-page anchors;
the only off-site links were the researcher's company. Named PoC directories in the
text were not downloadable links. No exploit code was executed.

At review, the [vendor bulletin index](https://tailscale.com/security-bulletins)
did not identify a Tailworm fix. Its 1.104.2 recommendation concerns a separate
certificate issue; it does not establish remediation of these findings. Recheck
[Tailscale releases](https://github.com/tailscale/tailscale/releases),
[Headscale releases](https://github.com/juanfont/headscale/releases), advisories and
release notes at execution time. A merged patch or “latest” install does not prove a
shipped fix. Record installed versions, applicable advisory, fixed release and remaining
exposure separately; use unknown when coverage cannot be established.

## Inventory before changes

Identify hosted Tailscale versus Headscale, OS, daemon/client versions, SSH enablement,
policy-permitted source/destination pairs, Serve/Funnel listeners and backends, connector
capabilities, custom DERP maps, registration exposure, tags, route auto-approvers and
credential ownership. Collect without logging auth keys, daemon state or lock secrets.

Read-only starting points (run on authorized nodes; inspect local help for version support):

```sh
tailscale version
tailscale status --json
tailscale serve status --json
tailscale funnel status --json
headscale version
```

Use `headscale version` only on Headscale deployments. Client status alone does not
prove SSH is disabled or reveal the authoritative access policy. Obtain policy and
service configuration from their owners. Record unknowns rather than assuming absence.

## Exposure-to-protection map

All entries below describe the report's tested scope. Validate applicability to the
installed build before calling a deployment vulnerable or fixed.

| Findings | Required exposure and reported boundary | Protective response |
|---|---|---|
| 1–3, T3/T2 and races | Embedded Tailscale SSH, permitted peer and forwarding; privileged Unix-socket operations | Prefer disabling embedded SSH pending a verified fix; narrow reachable pairs. Nonroot login accounts and path allowlists do not resolve the reported privilege crossing. |
| 4, C1 | Experimental conn25 enabled and client entitled to an app; arbitrary connector-side destination selection | Remove unnecessary capabilities; enforce backend destination restrictions outside the connector, including host-local and forwarded traffic, IPv4 and IPv6. Do not generalize this to every app connector. |
| 5, T1 | Policy-authorized SSH session; resource retention | Restrict/disable embedded SSH; monitor memory and availability. Restart supervision limits recovery time, not exploitability. |
| 6, C2/C4 | Headscale embedded-DERP history growth requires an authenticated insider; noise registration-cache eviction is pre-authentication and blocks onboarding | Restrict relay participants and registration exposure as applicable; rate-limit registration, budget memory, supervise service and alert on onboarding degradation. |
| 6, C3 | Client pointed at hostile DERP; oversized relay response | Use trusted relay configuration, audit map changes and bound daemon resources. This is a client risk, not proof that normal DERP decrypts WireGuard payloads. |
| 7, SERVE-F-1 | Operator configured TCP-to-Unix forwarding to privileged local API | Remove the specific forward; never publish tailscaled, Headscale, container-runtime or other administrative sockets. |
| 8, SERVE-F-2 | Attacker can replace a configured Unix backend path after validation | Use administrator-owned backend directories; avoid mutable Unix targets. Report distinguishes a blocked LocalAPI request from remaining privileged-socket reach. |
| 9, SERVE-F-3 | Funnel local configuration plus capable ingress peer | Audit both local configuration and control-plane entitlement. A “Funnel on” label is not proof of public ingress; stock Headscale did not supply the needed capability in the report. |
| 10, SERVE-F-4 | Nondefault TS_SERVE_ALLOW_ALL_INTERFACES | Remove unnecessary override after planning operator dependencies; test LAN/public reachability. This is a configuration risk, not a default exposure claim. |
| 11, SERVE-F-5 | Concurrent HTTP/2 streams, mounts with differing AcceptAppCaps, entitled peer | Require independent application authorization; avoid relying solely on mount capability headers until fixed. Reported bleed stays within the same peer's granted capabilities; Funnel headers are a separate path. |

## Safe mitigation sequence

1. Preserve recovery access and configuration snapshots. Confirm target, scope and rollback
   before mutation. Verify console or separately authenticated OpenSSH access in a second
   session before using `sudo tailscale set --ssh=false`. OpenSSH over the mesh still needs
   narrowly scoped network access and its own authentication. Do not use `tailscale down`
   as a substitute; it can cut off the entire management path. Do not blindly reset Serve.
2. Review the actual policy: restrict network reach and embedded SSH authorization to the
   necessary source/destination pairs. Validate supported selectors against the deployed
   controller. The report says Headscale 0.29.5 grants forwarding on accepted SSH sessions;
   do not invent SaaS forwarding fields for Headscale or claim parser acceptance proves
   enforcement. On hosted deployments use forwarding controls only when current official
   documentation and runtime verification establish support. If forwarding cannot be
   reliably denied, disable embedded SSH or remove the affected grant.
3. Check mode adds authentication before session establishment; it does not constrain
   forwarding inside an approved session. Short approval windows help but do not patch
   this class. Host IP firewalls cannot police Unix-socket operations. Do not present
   nonroot accounts, Tailnet Lock, device approval or reimaging as complete mitigation.
4. For conn25, isolate connectors by trust boundary and permit only intended destinations,
   including needed DNS/control traffic. Kubernetes NetworkPolicy requires an enforcing
   CNI and verified coverage of the privileged pod's real traffic path. Prove permitted
   service access and denial to an owned harmless forbidden endpoint; never probe live
   metadata credentials or administrative APIs. Route approval alone does not validate
   conn25 destinations. The report's failed tailnet-overlay pivot is not a blanket ACL bypass.
5. Save Serve configuration, remove only unsafe listeners with version-supported commands,
   verify legitimate application access and denied peer/LAN access. Do not trust capability
   headers as the application's sole authorization boundary across mounts. Check socket
   directory ownership and daemon environment without exposing environment secrets.
6. Apply Headscale rate/memory limits incrementally while preserving client registration,
   OIDC callbacks and relay connectivity. Size limits from legitimate baseline load and
   test recovery; a memory cap can itself cause outages and is containment, not a fix.

## Suspected compromise and completion

Preserve evidence and isolate through a trusted management path. Obtain an explicit
instruction before device deletion. Revoke the compromised device at the authoritative
control plane and verify loss of access from a controlled test; rebuild alone does not
invalidate an off-host copy of identity state. Rotate exposed enrollment/API/application
credentials; review rogue enrollments, tags, routes, approvers and DERP changes. If lock
signer or recovery material was exposed, follow the vendor's supported lock recovery
procedure. Keep incident evidence and alerts off the compromised host.

Distinguish enrollment-key expiry from node-key expiry. Evaluate server/tagged-node
expiry and hardware-backed state against controller/platform support and recovery needs;
never assert either is already enabled. Monitor unexpected enrollment, socket replacement,
resource spikes and unsolicited authentication prompts; self-test sensors. A clean local
status response is insufficient evidence on a root-compromised machine.

Complete with a per-node matrix: feature, prerequisite, evidence, action, rollback,
allowed/denied verification and residual uncertainty. Mark untested defenses as proposed.
No successful exploit is required to justify disabling an unnecessary feature.

## Official operational references

- [Tailscale SSH](https://tailscale.com/docs/features/tailscale-ssh): disable command,
  alternate-access requirement, network/SSH policy separation and check-mode behavior.
- [Serve CLI](https://tailscale.com/docs/reference/tailscale-cli/serve): inspect status,
  remove individual listeners and persistent background configuration.
- [Policy reference](https://tailscale.com/docs/reference/syntax/policy-file): validate
  current hosted syntax; do not assume parity with a particular Headscale release.
