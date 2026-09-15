# Implementation contracts

Use for a build request. These are required behaviors for generated code, not
a claim that this skill contains a deployed service. Implement only the chosen
pattern. Default interest capture does not need a ranking engine or inventory.

## Public API

Use same-origin `/api/v1/` routes with bounded JSON bodies (start at 16 KB),
`Cache-Control: no-store`, and server-side validation. Unknown fields fail
validation; clients cannot set proof status, priority, consent timestamps, or
CRM IDs. Set allowed methods explicitly. Provider secrets stay server-side.

| Route | Request and authorization | Result |
| --- | --- | --- |
| `POST /entries` | Program, email, optional phone, explicit consent choices, attribution, challenge token, idempotency key | `202` generic acknowledgement after entry and outbox commit |
| `POST /verification/start` | Opaque flow session, channel, CSRF token; destination is read from the pending entry | `202` with safe pending state; resend is rate limited |
| `POST /verification/check` | Flow session, local attempt ID, code or provider token, CSRF token | `200` on accepted proof; neutral `422` invalid/expired |
| `GET /status` | Opaque flow cookie; no lookup by email or guessable entry ID | Only this flow's permitted status; no stored PII before proof |
| `POST /contact/change` | Flow ownership plus fresh proof for an existing verified entry; CSRF | Invalidate old channel attempts; new destination is unverified |
| `POST /leave` | Scoped authenticated session or one-purpose leave proof; CSRF | Idempotent local suppression and outbound suppression intent |
| `POST /webhooks/{provider}` | Provider signature over the required raw payload; timestamp/replay policy | Acknowledge only after durable event receipt |
| Worker endpoint | Scheduler authentication; no browser access | Bounded leased batch; safe on duplicate invocation |

Error shape: `{ "error": { "code": "try_again", "message": "Please try again shortly." }, "request_id": "opaque" }`.
Use `400` malformed request, `403` failed authorization/origin, `413` oversize,
`422` input validation, `429` throttled with `Retry-After`, and `503` unavailable
before commit. Never report success for a failed database commit. After commit,
provider delay does not undo registration; expose pending work honestly.

Persist the idempotency key scoped to program and operation with a canonical
request digest and safe response. An identical retry reuses the result;
reusing a key with different input returns `409`. Default retention: 24 hours,
after which database uniqueness still prevents duplicate entries. A duplicate
email must not grant control over the original entry. Issue an unprivileged
new flow and require channel proof before linking it to the existing record.

## Persistence and transactions

Use versioned SQL migrations and UTC database timestamps. Minimum tables:

- `programs`: immutable ID, promise, policy version, configuration revision.
- `entries`: opaque ID, program, lifecycle status, immutable arrival sequence,
  row version, timestamps. Uniqueness scope is one program, not the whole CRM.
- `contacts`: entry, channel, original protected value, canonical lookup value,
  normalization version, verification version and time, suppression status.
- `proof_attempts`: local ID, entry/channel/destination version, provider
  reference, method, expiry, status, attempt counters. Never retain OTPs.
- `consents`: purpose, channel, decision, disclosure version, event time,
  collection source; withdrawal is an event, not deletion of history.
- `outbox`: event ID, aggregate/version, operation, mapping revision,
  available time, lease expiry, attempts, status, redacted last error.
- `crm_links`: adapter/tenant/entry unique key, provider ID, last synced version.
- `audit_events` and `webhook_receipts`: unique event IDs, minimal metadata.

Commit entry + contact + consent + outbound intent together. Unique constraints
handle concurrent duplicates. A proof completion uses compare-and-set on the
attempt and destination version, updates the contact, reevaluates eligibility,
and inserts the CRM intent in one transaction. External network calls happen
outside database transactions; lease outbox rows using `FOR UPDATE SKIP LOCKED`,
commit the lease, then call the provider. Expired leases are recoverable.

Email normalization: trim surrounding whitespace, normalize the domain with a
tested IDNA parser, preserve local-part spelling; document any case-folding
rule. Do not strip dots or plus tags globally. Normalize phones using a tested
library and explicit country context to E.164. Syntax is not reachability.
Do not merge people merely because they share a phone number.

Default to managed storage encryption, TLS, and least-privilege database roles.
If field encryption/keyed lookup hashes are introduced, retain a key ID and
normalization version, plan dual-read/dual-write rotation and uniqueness during
migration, and keep keys outside Postgres. A bare hash of a phone or email is
not anonymous. Expire unconfirmed records after 7 days by default; confirmed
retention is a campaign decision captured before launch. Deletion covers
providers, backups under their retention schedule, exports, and queued payloads.

## Managed proof binding

The application owns membership and eligibility. The provider owns challenge
issuance and checking. Store its challenge/method identifier with the exact
entry, channel, destination version, and program. Never accept a client-supplied
provider user ID or a generic provider session as proof of both contacts.

On check, call the provider from the server; verify the returned approved
channel and destination match the pending attempt. Recheck attempt/version
under a database lock before recording success. A contact edit or superseding
attempt must win over an old in-flight response. If the provider accepted a
proof but the database write failed, reconcile using a supported provider status
lookup; otherwise issue a new challenge. Never invent success from a timeout.

Issue an opaque flow cookie (`Secure`, `HttpOnly`, `SameSite=Lax`) and store its
hash server-side. Check Origin against the configured canonical origin plus
CSRF on browser mutations. A cross-device magic link creates a limited recovery
flow, not an admin session; explicit confirmation performs the server exchange.
Use a canonical configured callback, never a host-header-derived or arbitrary
`next` URL. Provider callback parameters are untrusted until checked.

Codes: let the provider generate, expire, and check them. Use the stricter of
provider limits and local caps; start with a 60-second resend cooldown, 3 sends
per destination per hour, 5 local failed checks per attempt, and configured
country and account spend limits. Limits are atomic shared state, not process
memory. Provider resend may reuse a code; invalidating a local attempt does not
necessarily revoke the provider's code. Test the actual provider semantics.

Magic-link extension: retain provider scanner protection. The callback loads
no analytics/media and uses no-store/no-referrer headers. Remove tokens from
browser history after secure transfer; redact them at proxy and app log layers.
GET must not activate membership or CRM delivery. For custom SMS links use
at least 32 random bytes, hash at rest, a short expiry, scoped purpose, atomic
single use, and an explicit confirmation POST. Link text never contains PII.

## CRM adapter contract

Configure the provider through a server-side registry of supported adapters;
runtime configuration selects an adapter, not arbitrary downloaded code. A new
CRM requires an implemented and tested adapter. Validate tenant, credentials,
field types, scopes, configured API version, allowed domains, and unique key
before enabling delivery. Never accept a CRM URL or credentials from public forms.

The adapter supplies `validateConfig`, `upsertContact`, `suppressContact`,
`deleteContact`, and `reconcileContact`. Each operation returns provider ID,
applied version, or a typed retryable/permanent/authentication error plus optional
retry-after. Keep provider SDK models outside the domain layer.

Canonical intent:

```json
{
  "event_id": "opaque-event-id",
  "operation": "upsert",
  "program_id": "launch-autumn",
  "entry_id": "opaque-entry-id",
  "entry_version": 8,
  "mapping_version": 2,
  "adapter": "hubspot",
  "tenant_ref": "server-config-reference"
}
```

Build the contact payload from current eligible state immediately before send.
For each channel require its own proof and purpose permission; do not include an
unverified optional phone just because email was confirmed. Marketing enrollment
is a separate provider operation from storing a contact; default it off unless
explicitly selected. CRM-not-connected means hold no external writes, display
connection status, and backfill eligible current records when connected.

Use program + entry as the external identity, adding provider/tenant scope.
Do not treat an event idempotency key as a provider uniqueness constraint. Verify
the chosen CRM supports a unique external property/upsert, or implement lookup,
serialization and reconciliation. A timeout after an unknown outcome triggers
lookup before another create. If neither is possible, mark uncertain and require
reconciliation rather than creating duplicates. Email-only upsert is unsuitable
for phone-only programs and can merge unrelated records across campaigns.

Serialize effects per entry. Version 8 cannot overwrite version 9. Supersede
stale queued upserts; prioritize suppression/deletion and recheck eligibility
before sends. If withdrawal races with an in-flight upsert, enqueue and verify
the compensating suppression. CRM edits to unrelated sales fields are preserved;
local consent controls cannot be broadened by CRM edits. Receive supported CRM
opt-outs as suppression events and reconcile missed webhooks.

Retry `429`, network timeouts and `5xx` with jittered exponential backoff,
honoring a longer provider `Retry-After`; start at 5 seconds, cap ordinary delay
at 1 hour, dead-letter after 24 hours. Pause authentication failures pending
credential repair; dead-letter invalid mappings with redacted diagnostics.
Batch adapters must classify each record independently. No promise of exactly
once delivery: use at-least-once work with idempotent effects and reconciliation.

## Fairness extensions

Interest capture has no rank. FIFO uses a database-assigned immutable sequence
and deterministic tie-break, not browser time. PostgreSQL sequence gaps are
allowed; document assignment order rather than claiming strict commit order.
Referral score is derived from distinct eligible conversions with a cap and
stable sequence tie-break. Publish whether points change priority or merely
eligibility; do not promise a fixed number of places when other scores change.
Policy revisions do not silently mutate past promises. Store the policy and
inputs used for each invitation. Lotteries need a frozen eligible population,
documented random selection, draw evidence, and separate allocation authority.
