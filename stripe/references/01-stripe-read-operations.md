# Stripe Read Operations

> **Last Updated:** 2026-08-03

Operational detail for the Stripe API surface the skill owns: the read-only-first surface (balance, payment intents, subscriptions) and the one guarded mutation (scheduling a subscription cancellation at period end). The bundled `stripe-cli` implements this reference; use this document when a call behaves unexpectedly.

## API conventions

- Base URL: `https://api.stripe.com/v1`. Every request carries `Authorization: Bearer <api_key>`.
- GET endpoints take query-string parameters (`limit`); POST endpoints take form-encoded bodies. `stripe-cli` encodes GET parameters in the URL and POST parameters in the body.
- Keys: `sk_test_` (test data) vs `sk_live_` (real production data) vs `rk_` (restricted). Restricted read-only keys (`balance:read`, `payment_intents:read`, `subscriptions:read`) are the right default for the read surface.

## Endpoint surface

| Operation | Endpoint | Method | Notes |
|---|---|---|---|
| Balance | `/balance` | GET | Available + pending per currency; no pagination |
| List payments | `/payment_intents?limit=N` | GET | Recent intents with amount, currency, status, customer |
| List subscriptions | `/subscriptions?limit=N` | GET | Active subscriptions with status, customer, items |
| Get a subscription | `/subscriptions/{id}` | GET | Single subscription with period end |
| Schedule cancellation | `/subscriptions/{id}` | POST | Guarded mutation: `cancel_at_period_end=true` |

## Pagination and bounded reads

- List endpoints accept `limit` (max 100) and return `has_more` plus a `starting_after` cursor when more records exist.
- **Bounded-read rule:** request only what the task needs; `stripe-cli --limit` caps at the request level. Report `has_more` when summarizing so the reader knows the cap hid further records.

## Read surface semantics

- **Balance**: `available` (settled funds you can pay out) vs `pending` (in transit, e.g. captured but not yet settled). Always distinguish the two when reporting.
- **Payment intents**: statuses include `requires_payment_method`, `requires_confirmation`, `requires_action`, `processing`, `succeeded`, `canceled`. `succeeded` means captured; `requires_action` means the customer must complete authentication. A "charged twice" report must be checked against distinct intent IDs before any refund discussion — and refunds are outside this skill's mutation surface.
- **Subscriptions**: `status` (`active`, `past_due`, `canceled`, `unpaid`, `trialing`) plus `current_period_end` (Unix) and `cancel_at_period_end` (bool). Items carry price, amount, and interval.

## Guarded mutation: cancellation at period end

- `POST /subscriptions/{id}` with `cancel_at_period_end=true` schedules cancellation at the end of the current billing period — the customer keeps service until then and the change is reversible (set it back to `false` before the period ends).
- `stripe-cli` verifies the response has `cancel_at_period_end: true` before reporting success; a mismatch raises an error and no state change is assumed.
- Immediate cancellation (`cancel=true`) and refunds are deliberately out of scope: they are irreversible financial actions that belong to a human decision with dedicated tooling.

## Error handling

- 401 `invalid_request_error`/authentication failure: key invalid or revoked — rotate the key.
- 403: restricted key lacks the scope — grant the needed scope, don't retry blindly.
- 404: object does not exist in the key's mode (test vs live) — verify the key type and object ID before concluding.
- 429 `rate_limit`: slow down; Stripe rate limits per key.
- `stripe-cli` exit 1 with `Stripe API HTTP <code>: <message>` (human) or `{"ok": false, "error": "..."}` (JSON). Exit 2 is a usage error.

## Credential and data hygiene

- Keys are full or scoped account credentials: store in `STRIPE_API_KEY`, never in code, chat, or commits. Use restricted read-only keys for the read surface; add `subscriptions:write` only where cancellations are genuinely needed. Rotate a leaked key immediately.
- Balance, payment, and subscription data is financial and often personal: quote only what the question needs and never dump full customer data or raw payloads into chat.
