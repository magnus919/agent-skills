# Stripe — Read Your Account State (and Guarded Cancellations)

Check Stripe balance, recent payments, and subscriptions from your terminal or agent — and, with explicit confirmation, cancel a subscription — all through a read-only-first CLI.

## Why Install This Skill

Financial questions are the ones agents get wrong when they guess: "what is our Stripe balance?", "did this payment go through?", "which subscriptions are still active?". This skill gives your agent a bounded, read-only path to the real answers, and a deliberately narrow write path: canceling a subscription is a guarded mutation that requires a preview and an explicit confirmation, and it defaults to scheduling cancellation at the end of the billing period rather than cutting service off instantly.

It ships `stripe-cli`, a small Python script that speaks the Stripe API with no third-party dependencies. The read surface is primary — balance, payment intents, subscriptions — and every listing is capped (`--limit`). Output is clean JSON for the agent or readable text for you, and `--help` works with no key and no network. The script verifies Stripe actually confirmed a cancellation before reporting success, so a failed request is never mistaken for a done deal.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating contract, mutation gates, and verification boundaries |
| `references/` | Dated source index and a Stripe read-operations reference (endpoints, pagination, cancellation semantics, errors) |
| `scripts/stripe-cli` | Bounded, stdlib-only CLI: balance, payments list, subscriptions list/get, guarded cancel; `--json`, `--limit`, mutation gated by `--dry-run`/`--yes` |
| `tests/` | 12 deterministic tests against a stub Stripe API, covering the read-only-first contract and mutation gate |
| `evals/evals.json` | Six output-quality evaluation cases for agent runs |

## Quick Start

```bash
# Help works with no key and no network; shows the read-only surface
stripe/scripts/stripe-cli --help

# Account balance (available + pending)
STRIPE_API_KEY=sk_test_... stripe/scripts/stripe-cli --json balance show

# Recent payments (capped)
STRIPE_API_KEY=sk_test_... stripe/scripts/stripe-cli --json --limit 20 payments list

# Active subscriptions
STRIPE_API_KEY=sk_test_... stripe/scripts/stripe-cli --json --limit 20 subscriptions list
STRIPE_API_KEY=sk_test_... stripe/scripts/stripe-cli --json subscriptions get --id sub_123

# Cancel only with a preview first, then explicit confirmation
STRIPE_API_KEY=sk_test_... stripe/scripts/stripe-cli subscriptions cancel --id sub_123 --dry-run
STRIPE_API_KEY=sk_test_... stripe/scripts/stripe-cli subscriptions cancel --id sub_123 --yes
```

## Triggers

Load this skill for `stripe` / payments operations: account balance, whether a payment succeeded, listing payment intents, active subscriptions and their items, or canceling a subscription with confirmation. Do not load it for building Stripe payments into an application, Stripe dashboard administration, refunds or immediate cancellations, or other payment processors.

## Requirements

- Python 3.9+ for `stripe-cli` (stdlib only; `--help` and the read surface need nothing else).
- A Stripe API key (`STRIPE_API_KEY`): a restricted key scoped to `balance:read`, `payment_intents:read`, `subscriptions:read` for reads, plus `subscriptions:write` only if you need cancellations. Prefer test keys (`sk_test_`) for anything non-production.
- Network access to `api.stripe.com` for live reads and cancellations.
