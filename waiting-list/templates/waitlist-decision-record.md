# Waiting-list decision record

## Promise

- Program/product:
- What joining means:
- What is not guaranteed:
- Advancement event:
- User-visible language:

## Context and constraints

- Expected arrival rate / peak:
- Scarce resource:
- Regions and accessibility needs:
- Data and consent requirements:
- Existing systems and owner:
- Rollback or exit path:

## Pattern decision

- Primary pattern:
- Optional overlays:
- Rejected alternatives and why:
- Observed evidence:
- Assumptions:
- Unknowns requiring validation:

## Implementation and brand

- Default stack: static HTML + Alpine CSP + Vite; TypeScript/Node on Vercel; Neon Postgres.
- Verification: Twilio Verify codes; SendGrid for email; phone off unless enabled.
- Deviations and reason:
- Brand brief, assets, rights and revision:
- Video poster, pause and reduced-motion treatment:
- Preview URL and visual-review evidence:
- Service account ownership, plan limits and cost assumptions:
- Preview/production isolation and worker cadence:

## State and ownership

| State | Entry condition | Owner | Side effects | Exit conditions |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Data and interfaces

- System of record:
- Uniqueness and idempotency:
- PII fields and retention:
- Public endpoints/events:
- Admin operations and audit:

## Contact verification and CRM

- Email proof: off / optional / required; code or magic link and actual provider TTL:
- Phone proof: off / optional / required; SMS link or provider OTP:
- What each proof establishes and does not establish:
- Consent purposes and suppression behavior:
- CRM gate and runtime adapter:
- Allowlisted field mapping and mapping version:
- Provider credential boundary:
- Idempotency, retry, dead-letter, replay:
- Correction, deletion, and unsubscribe propagation:

## Controls

- Abuse and rate limits:
- Challenge/token validation:
- Email, consent, suppression:
- Fairness/ranking/admission:
- Accessibility and privacy:
- Provider and datastore failure mode:

## Delivery gates

- [ ] Concurrent duplicate submissions are tested.
- [ ] Verification/invitation replay and expiry are tested.
- [ ] Email and phone proofs are independently tested for expiry, replay,
      resend throttling, wrong-channel use, and scanner/prefetch behavior.
- [ ] Webhook deduplication and reordering are tested.
- [ ] CRM sync is tested for idempotency, retry, permanent failure, mapping
      changes, suppression, correction, and deletion.
- [ ] Abuse burst and false-positive behavior are measured.
- [ ] Queue/admission does not pretend to reserve inventory.
- [ ] Allocation/appointment conflicts are handled by the authoritative service.
- [ ] Operator bulk actions have preview, audit, and rollback.
- [ ] Mobile, keyboard, slow-network, and no-JavaScript behavior are reviewed.
- [ ] Peak-load evidence and provider outage behavior are retained.
