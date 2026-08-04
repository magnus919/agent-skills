# Stripe — Source Index

> **Last Updated:** 2026-08-03

This skill is a distilled operating layer over Stripe's public API documentation. Facts and endpoint names in this skill are grounded in the sources below; refresh this index when Stripe ships API changes.

| Topic | Source | URL |
|---|---|---|
| API reference | Stripe API reference | https://docs.stripe.com/api |
| Balance | Balance API | https://docs.stripe.com/api/balance |
| Payment Intents | Payment Intents API | https://docs.stripe.com/api/payment_intents |
| Subscriptions | Subscriptions API | https://docs.stripe.com/api/subscriptions |
| Authentication and keys | Authentication | https://docs.stripe.com/api/authentication |
| Restricted API keys | Restricted keys | https://docs.stripe.com/keys#limit-access |

## Refresh procedure

- Re-check the Subscriptions API before changing anything in `subscriptions cancel`; cancellation semantics (`cancel_at_period_end`, immediate `cancel`) have changed across API versions and the safe period-end default is deliberate.
- Re-check the Payment Intents API when payment statuses behave unexpectedly; status names evolve with new confirmation flows.
- Update `research_checked` in `SKILL.md` frontmatter and this file's `Last Updated` when you verify the sources again.
