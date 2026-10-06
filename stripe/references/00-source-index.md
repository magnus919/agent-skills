# Stripe — Source Index

> **Last Updated:** 2026-10-06

This skill is a distilled operating layer over Stripe's public API documentation. Facts and endpoint names in this skill are grounded in the sources below; refresh this index when Stripe ships API changes.

| Topic | Source | URL |
|---|---|---|
| API reference | Stripe API reference | https://docs.stripe.com/api |
| Balance | Balance API | https://docs.stripe.com/api/balance |
| Payment Intents | Payment Intents API | https://docs.stripe.com/api/payment_intents |
| Subscriptions | Subscriptions API | https://docs.stripe.com/api/subscriptions |
| Authentication and keys | Authentication | https://docs.stripe.com/api/authentication |
| Restricted API keys | Restricted keys | https://docs.stripe.com/keys#limit-access |
| Currency amount units | Supported currencies | https://docs.stripe.com/currencies |
| Balance amount fields | Balance API | https://docs.stripe.com/api/balance/balance_object |
| Payment amount fields | PaymentIntent API | https://docs.stripe.com/api/payment_intents/object |
| Subscription price amount fields | Price API | https://docs.stripe.com/api/prices/object |

## Refresh procedure

- Re-check the Subscriptions API before changing anything in `subscriptions cancel`; cancellation semantics (`cancel_at_period_end`, immediate `cancel`) have changed across API versions and the safe period-end default is deliberate.
- Re-check the Payment Intents API when payment statuses behave unexpectedly; status names evolve with new confirmation flows.
- Stripe's currency guide says API amounts use minor units, with two decimal places by default and a documented zero-decimal set. Preserve the raw integer and currency in output. For charge and price displays, ISK and UGX retain two-decimal API values for backward compatibility; an amount of `500` means `5.00` in either currency. HUF and TWD are two-decimal for charges/prices, though Stripe applies whole-unit divisibility to manual payouts. Reject three-decimal currencies absent from Stripe's supported presentment list.
- Update `research_checked` in `SKILL.md` frontmatter and this file's `Last Updated` when you verify the sources again.
