# Operations, abuse, email, and privacy

Load this reference when the portal is public, cross-origin, high-volume,
commercial, or collecting more than an email address.

## Abuse controls

Layer controls rather than expecting one CAPTCHA to solve abuse:

1. Apply request size, field, origin, and schema limits.
2. Normalize contacts and enforce per-program uniqueness server-side.
3. Rate-limit by IP/network, contact hash, program, session, and expensive
   downstream action. Make limits observable and configurable.
4. Add a honeypot, minimum form age, and challenge or bot score where traffic
   justifies the friction. Keep an accessible fallback.
5. Require server-side validation of any challenge token. Cloudflare Turnstile's
   Siteverify call is mandatory; client-side widget success is not evidence.
6. Treat referral codes as untrusted attribution. Cap influence and flag
   velocity, repeated devices, disposable patterns, and self-referral signals
   for review rather than silently deleting legitimate entries.

Do not rely on IP address as identity, block entire geographies without a
documented reason, or collect invasive fingerprints by default. Preserve enough
reason codes and aggregate telemetry to tune false positives.

## Contact verification

Load [contact-verification-and-crm.md](contact-verification-and-crm.md) for the
full design. In brief, validate email and phone independently, use
cryptographically random, scoped, single-use, expiring proofs, and record the
method and timestamp. A clicked link proves control of the channel at that
time; it does not prove identity, consent for every message, or permanent
reachability. SMS link verification is an application-owned alternative to a
provider-managed OTP, not the same thing.

## Email lifecycle

Model email as a stateful integration, not a `send()` call in the request
handler:

```text
entry accepted -> notification_intent pending -> sent/provider_id
                                             \-> retry/dead-letter
provider webhook -> delivered | bounced | complained | suppressed
```

Use an outbox or durable job. Make provider webhooks signature-verified and
idempotent; delivery is commonly at-least-once and not necessarily ordered.
Store the provider event ID and ignore repeats. Keep provider payloads bounded
and redact message content from ordinary logs.

Use a verified sending domain, SPF/DKIM/DMARC as appropriate, a monitored reply
address, and bounce/complaint suppression. Confirmed/double opt-in is a strong
default when the person is joining a marketing list or when typo and
third-party signups would damage list quality. It is not a universal substitute
for defining the purpose and legal basis of each message.

Separate:

- verification mail, which proves control of the address;
- an access/invitation message, whose token is scoped and expires;
- operational messages about a confirmed appointment, reservation, or order;
- marketing or launch updates, which need their own consent and unsubscribe
  behavior.

Do not call a launch update “transactional” merely because the recipient once
joined a list. Implement a one-click or one-page unsubscribe where appropriate,
honor suppression before queueing new mail, and retain proof of consent and
unsubscribe events.

## Privacy and administration

- Collect the minimum fields needed for the stated selection or service.
- Give each purpose its own consent flag; do not bundle unrelated marketing
  into a required “join” checkbox.
- Encrypt contact data at rest where the platform supports it and keep keys out
  of client bundles, source control, logs, and analytics events.
- Use opaque IDs and signed, short-lived, single-use links. Do not put email
  addresses in referral URLs, status URLs, or screenshots.
- Define retention, export, correction, deletion, suppression, and provider
  subprocessor handling before launch. A deletion request must not accidentally
  re-enable a suppressed contact.
- Require operator authentication, least privilege, audit history, scoped
  exports, and a preview/confirmation for bulk invitations or status changes.
- Decide whether public social proof (for example, “12,000 people waiting”) is
  a measured count of eligible entries, a rounded estimate, or merely marketing
  copy. Label it honestly.

## Failure and incident controls

Test and instrument:

| Failure | Safe behavior | Signal |
| --- | --- | --- |
| Database unavailable | Generic retryable response; no false success | write failures, latency, accepted-vs-persisted gap |
| Email provider unavailable | Persist intent; retry with backoff; do not duplicate sends | outbox age, retry count, dead letters |
| Bot burst | Challenge/rate-limit or shed load before expensive writes | challenge failures, limit hits, traffic by key |
| Duplicate submission | Idempotent/generic response | duplicate ratio, key collisions |
| Replayed token | Reject and audit; do not repeat side effect | replay count by token family |
| Webhook duplicate/out-of-order | Verify, dedupe by provider event ID, apply state rules | duplicate and stale-event counts |
| Queue datastore unavailable | Explicit fail-open/closed policy; page operator | queue health, bypass admissions |
| Inventory or slot conflict | Re-check in authoritative service; compensate/refund as needed | conflict and compensation count |

Fail-open can preserve availability for a low-risk preview but defeats scarcity
and fairness guarantees. Fail-closed protects hard capacity at the cost of a
customer-visible outage. Make the switch explicit, scoped, audited, and tested.

## Source and legal boundary

This reference is engineering guidance, not legal advice. Email rules vary by
jurisdiction and by message purpose. In the United States, the FTC distinguishes
commercial from transactional/relationship content and requires an effective
opt-out path for commercial email; route the actual program through qualified
privacy/legal review. CRM and SMS providers add their own consent, retention,
regional, sender-registration, and data-processing requirements. See [the
source index](source-index.md) for the primary references used here.
