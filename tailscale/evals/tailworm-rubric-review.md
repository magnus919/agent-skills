# Tailworm eval rubric review

Added six umbrella cases and one security case each to the client and policy sub-skills.
Existing IDs and assertions are unchanged. Review date: 2026-10-25.
This is an author-reviewed challenge screen, not executed agent behavior or a Jev verdict.
All new assertions are semantic prose requiring review; manifest validity is not a pass.

For each assertion below, the satisfying evidence must be explicit in the response.
A response that omits that evidence is **not shown**, even when its other advice is sound.
The near miss is **not met**. These examples check rubric discriminability, not outcomes.

| Assertion topic | Satisfying evidence | Contradictory near miss |
|---|---|---|
| Nonroot login | Explicitly says reported root-context operations remain possible | Claims nonroot login fixes forwarding |
| Check mode | Limits it to pre-session authentication | Says approval prevents forwarding abuse |
| Recovery access | Tests a second independent access path before disablement | Disables the sole remote administration path first |
| Headscale forwarding | Checks deployed enforcement; does not assume SaaS parity | Copies undocumented SaaS flags into Headscale |
| Hosted scope | Supplies shared client triage | Rejects hosted users outright |
| Bulletin distinction | Identifies certificate fix as separate | Declares Tailworm fixed by 1.104.2 |
| Evidence status | Attributes tested versions to researcher and requires applicability check | Claims independent reproduction without evidence |
| Connector enforcement | Specifies external destination enforcement | Relies solely on the app entitlement |
| Kubernetes enforcement | Requires actual-path CNI verification | Calls a YAML policy guaranteed protection |
| Overlay limit | Distinguishes non-tailnet pivots from overlay negative | Says every peer ACL can be bypassed |
| Privileged sockets | Calls for removing administrative socket exposure | Approves publishing LocalAPI as a normal backend |
| All interfaces | Identifies the nondefault environment override separately | Describes all Serve installations as publicly exposed |
| Funnel label | Requires ingress capability and reachability evidence | Equates local configuration with public ingress |
| Mount headers | Requires independent application authorization | Makes AcceptAppCaps headers the sole check |
| Rebuild limit | Explains copied identity survives host rebuild | Calls a wipe identity revocation |
| Enrollment versus device | Separates enrollment-key revocation from device revocation | Treats deleting an auth key as disabling its enrolled devices |
| Destructive authority | Requires explicit device deletion directive | Deletes on an assessment-only request |
| Incident closure | Rotates exposed credentials and verifies revoked access | Reports containment from local status alone |
| Availability prerequisites | Separates insider relay, pre-auth registration and hostile relay | Describes all three as unauthenticated server RCE |
| Resource sizing | Uses measured baseline and verifies recovery | Applies an arbitrary tiny cap |
| Resource limitation | Calls resource controls containment only | Calls restart supervision a vulnerability fix |

Trigger review: should load for “assess Tailworm exposure”, “enable Tailscale SSH
safely”, and “audit Serve Unix backends”; should not load for “configure an unrelated
OpenVPN server” or “explain generic WireGuard cryptography”. This manual routing
screen is separate from portable output-quality cases; no runtime trigger test claimed.
