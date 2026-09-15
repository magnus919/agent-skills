# Waiting-list architecture patterns

Use this reference when the request involves more than a single low-volume
email-capture form. The key design question is which scarce thing is being
managed: attention, verified demand, access capacity, appointment slots,
inventory, or a fair allocation opportunity.

## Pattern comparison

| Pattern | Core record | Ordering/selection | Recommended primitives | What it does not provide |
| --- | --- | --- | --- | --- |
| Interest capture | Contact + consent + source | None or operator-selected | Static/SSR page, server action/API, relational DB/CRM/ESP, outbox | A place in line or guaranteed access |
| Verified demand queue | Entry + verification + policy version | FIFO or published segments | Transactional DB, unique contact key, signed one-time links, worker | Inventory hold or purchase |
| Referral overlay | Entry + referral event ledger | Arrival key plus eligible boost | Durable events, fraud limits, recomputable policy | Proof that referrals are genuine or that priority is fair |
| Virtual waiting room | Queue identity + session/admission token | FIFO/capacity/admission policy | Edge/gateway, durable queue, signed token, atomic transition, polling | Product entitlement, reservation, checkout serialization |
| Appointment backfill | Demand profile + slot offer | Fit, preference, time window | Scheduling service, slot inventory, TTL offer, reminder channel | A universal ranking that ignores fit and availability |
| Preorder/deposit | Order intent + payment state | Allocation policy | Inventory ledger, payment provider, idempotent order workflow, refunds | A mere email list; payment creates additional obligations |
| Lottery/curated access | Eligibility + draw/decision event | Random, weighted, or human decision | Versioned policy, auditable seed/process, eligibility snapshot | A deterministic queue position |
| Embedded/headless service | API entry + project/tenant | Service-defined | API key or OAuth boundary, CORS allowlist, rate limits, webhooks | A browser-safe secret or a free-standing admin model |

## Decision sequence

1. If no allocation, capacity, or ordering promise is required, use interest
   capture. A static page with a server-side endpoint is enough; an entire
   microservice may create more failure modes than value.
2. If a person must prove contact ownership before being eligible, add a
   verification state and one-time token. Keep an unverified record separate
   from an active entry.
3. If a traffic surge threatens the origin, put a waiting room in front of the
   protected route. Queue admission is an availability mechanism, not a claim
   on stock.
4. If the scarce resource is a time slot, model slot inventory and preferences;
   a global FIFO list usually causes poor matches and avoidable no-shows.
5. If goods can be promised or money can move, model reservation, payment,
   expiry, inventory decrement, refund, and fulfillment as a separate bounded
   workflow. Attach the waitlist to that workflow.
6. If selection is discretionary, random, or segment-based, show the rule and
   use “interest list,” “eligibility,” or “estimated rank” language instead of
   claiming a fixed queue.

## Headless request contract

For a cross-origin form, design a small versioned contract rather than exposing
the database:

```http
POST /v1/programs/{program_id}/entries
Idempotency-Key: <opaque client retry key>
Origin: https://launch.example
Content-Type: application/json

{
  "email": "person@example.com",
  "consents": {"launch_updates": true},
  "source": {"utm_source": "partner"},
  "referral_code": "optional-attribution-token",
  "captcha_token": "optional-risk-control"
}
```

Return an opaque entry identifier and the next user action. Avoid returning
whether an email already exists; a generic accepted response limits account
enumeration. Restrict origins, validate fields server-side, rate-limit by
multiple dimensions, and make retries idempotent. A public browser key can
identify a project, but it cannot authorize an admin read or be treated as a
secret.

## Stronger queue mechanics

For a real FIFO queue, allocate an immutable monotonic ticket in the same
atomic operation that creates the queue entry. Use a deterministic tie-breaker
if the datastore cannot guarantee a sequence. For admission, transition a
bounded number of entries atomically, mint a short-lived signed token, and
expire abandoned sessions. Keep token verification cheap on the admitted path.

Cookie continuity matters: a client that drops or fails to update the queue
cookie can be treated as a new arrival. For mobile and API clients, expose a
JSON status contract and require a cookie jar or equivalent queue identity.

The Vercel Labs `nextjs-waiting-room` example is a useful reference for atomic
Redis admission, signed admission tokens, adaptive polling, and an explicit
“admission is not purchase authority” boundary. Cloudflare Waiting Room's JSON
guidance is a useful reminder that queue cookies must be returned and refreshed
for non-browser clients.

## Referral policy mechanics

Do not implement a mutable formula such as `position = initial_index - count *
boost` without defining what counts, when it becomes eligible, and how ties and
negative positions are handled. Prefer:

```text
sort_key = (policy_version, priority_band, effective_arrival_key, entry_id)
```

where `priority_band` is derived from durable, eligible events under the named
policy. Store `referral_click`, `referred_submission`, `referred_verified`,
and `reward_issued` separately. This makes abuse review, policy changes, and
recomputation possible. Preserve the original arrival key so a referral
program can be disabled without destroying the underlying list.

## Migration and reversibility

Start with a provider-neutral domain model and adapter interfaces for storage,
email, bot checks, and notifications. Keep raw provider payloads and a local
event ID where practical. A hosted form can migrate to a headless API if the
entry schema, status vocabulary, export path, and consent history were defined
from the beginning. A waiting room should be removable by routing the protected
path directly to the origin; a referral overlay should be removable by sorting
only on the original queue key.
