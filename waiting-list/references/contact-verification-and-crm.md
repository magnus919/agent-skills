# Contact verification and CRM delivery

Load this reference when a portal must prove control of an email address or
phone number, or when validated entries should be sent to a CRM at runtime.

## What the proof means

Keep these claims separate:

| Claim | Evidence |
| --- | --- |
| Address/number is syntactically valid | Parser and normalization only |
| Person controls the channel now | Successful, scoped email link, SMS link, or OTP |
| Person consented to a purpose | Explicit, recorded purpose-specific consent |
| Person is who they claim to be | An identity/KYC process, if actually required |
| Contact is reachable later | A current delivery signal; never a permanent guarantee |

The waitlist should store the first two as channel-specific facts and the third
as a separate consent record. Do not turn an email click into identity proof or
assume that a carrier delivery receipt proves phone ownership.

## Verification policy

The default path uses Twilio Verify codes for both email (through SendGrid)
and SMS. Phone collection starts off. The example below enables required phone
proof and optional email proof to illustrate independent campaign choices; it
does not override the email-only default. Provider-managed checking owns the
challenge lifecycle; the application still binds proof to its pending contact.

Represent policy as configuration, not scattered conditionals:

```yaml
verification:
  email: optional       # off | optional | required
  phone: required       # off | optional | required
  email_method: provider_otp # provider_otp | magic_link
  phone_method: provider_otp # provider_otp | sms_link
  ttl_seconds: 600 # request only when supported; enforce actual provider expiry
  max_resends_per_hour: 3
crm:
  mode: after_required_proofs # disabled | on_active | after_required_proofs | on_invite
  adapter: hubspot
  mapping_version: 1
```

The policy must define whether an unverified entry is retained, whether a
person can proceed with one verified channel, how changing a contact starts a
new proof, and whether a proof expires and must be renewed.

## Email magic links

This is an optional extension, not the default verification implementation.
Prefer a documented provider-managed link flow. The custom-token rules below
apply when the application owns token issuance; do not duplicate a provider's
token store or invent local expiry that exceeds its actual validity.

1. Accept and normalize the address server-side, then create a random
   cryptographically strong token scoped to the entry, channel, purpose, and
   policy version. Store only a keyed hash plus expiry, issued time, and used
   time; never store the bearer token in plaintext.
2. Send a link over HTTPS from a verified domain. Keep the URL free of email,
   CRM IDs, and other PII. Use a referrer policy that prevents token leakage.
3. On presentation, rate-limit by entry, destination, token family, and source
   signals; verify expiry, signature/hash, purpose, and unused status; then
   consume the token atomically and record `email_verified_at` and proof ID.
4. Make resends invalidate or supersede prior tokens according to a documented
   rule. Keep responses generic enough that the endpoint cannot enumerate
   whether an address is on the list.
5. Treat email-security scanners and link prefetchers as a real failure mode.
   Let the GET render a confirmation page and use a
   same-site POST to consume the proof, or require a second explicit action.
   Test the chosen UX against the email clients the audience uses.

OWASP's token guidance is a useful baseline: tokens should be random, stored
securely, single-use, expiring, and protected against brute force. Email proof
still does not establish a person's legal identity.

## Phone verification by SMS

Normalize and validate phone numbers to E.164 before sending. State the SMS
purpose, frequency expectations, and opt-out/support path where applicable.

There are two distinct implementations:

- `provider_otp`: use a verification provider's managed challenge and check
  endpoint. The user types the code, and the provider manages much of the
  attempt/expiry lifecycle. Twilio Verify's standard SMS flow is this model.
- `sms_link`: generate the application's own short-lived, single-use signed
  link and send it with a programmable SMS API. The user taps the link, which
  returns to the portal and consumes the proof. This is not the same as an OTP
  and places token, deep-link, logging, and abuse responsibilities on the
  application.

For either model, rate-limit sends and attempts by number, entry, IP/network,
and provider account; cap spend; detect repeated destination abuse; and handle
  unsupported, landline, recycled, or unreachable numbers without revealing
  list membership. Do not log full numbers, tokens, or SMS bodies. Provider
  status callbacks are delivery telemetry, not ownership proof.

## Both channels

Use fields such as:

```text
contact_proofs(
  entry_id, channel, method, destination_hash, proof_id,
  issued_at, verified_at, expires_at, revoked_at, provider_event_id
)
```

The unique key should prevent two active proofs for the same entry/channel, or
the application should explicitly supersede the previous proof. Verification
completion must be an atomic state transition, safe to retry, and auditable.
The user-visible status should say “email confirmed” or “phone confirmed,” not
“identity verified.”

## Runtime CRM adapter

Treat the CRM as a downstream projection, not the waitlist's source of truth.
Configure an adapter at deployment/runtime with:

- provider and API version, server-side credential reference, workspace/tenant;
- eligibility gate (`on_active`, `after_required_proofs`, or `on_invite`);
- allowlisted field mapping and consent mapping, including verification
  timestamps and source attribution;
- provider upsert key and local idempotency strategy;
- retry/backoff, dead-letter or manual replay behavior, rate limits, and
  provider record ID storage;
- suppression, correction, deletion, and retention propagation rules.

The durable path is:

```text
local entry/proof event -> crm_outbox pending -> adapter upsert
                                      \-> retry/dead-letter -> operator replay
```

Use an immutable event ID for delivery deduplication and include entry version
in the outbound work identity. A key containing only program, entry, mapping
and gate versions would incorrectly deduplicate later contact corrections.
Use a separate stable program/entry external identity for the CRM upsert.
Never put a CRM secret or
admin read capability in browser code. Do not send unverified or unconsented
fields merely because the CRM accepts them. A successful CRM write must not
replace the local audit record; a failed CRM write must not erase the local
waitlist entry.

HubSpot's current contacts API illustrates the shape: scoped contact-write
access, create/update/upsert operations, associations, and custom properties.
Its API/version and property semantics are provider-specific; use the adapter
contract rather than hard-coding HubSpot assumptions into the portal.

## CRM acceptance tests

- Required proof missing: local entry persists, CRM outbox is not eligible.
- Proof completes twice: one local transition and one CRM effect.
- CRM timeout or 429: local entry remains active; outbox retries without
  duplicate contact creation.
- Provider returns a permanent validation error: dead-letter with redacted
  reason and operator replay after mapping correction.
- Consent is withdrawn or contact is suppressed: no new CRM marketing sync;
  apply the documented provider update/delete path.
- Mapping changes: old records retain their mapping version and can be
  reconciled without silently rewriting history.
