# Outcome-partnership economics and cash reconciliation

Use when pricing acquisition/operating services against appointments, sales or
collected revenue. Read `go-to-market` for model selection, role/control and legal
gates. Use `templates/outcome-economics-worksheet.md` for the model. This is an
analytical aid, not accounting policy, a legal agreement or payment authorization.

## Distinguish the amounts

An accepted order is not completed work, an invoice is not collected cash, and
cash held for someone else is not automatically operator revenue. Define the fee
trigger and eligible base before calculating. Identify whose cash is modeled,
who contracts/invoices/collects, whether the operator handles customer funds, and
which party bears fees, taxes, refunds, chargebacks and nonpayment. Principal/
agent revenue recognition and tax treatment need specialist review.

For a collected-revenue arrangement, calculate eligible receipts and signed
reversals at transaction level, then apply the agreed attribution and fee rules.
Specify taxes, tips, financing proceeds, pass-through materials, discounts,
retentions, deposits and partial collections. Do not subtract a discount twice
if it is already absent from receipts. A pending or failed payment is not settled
cash; a missing export is unknown, not zero. Separate unmatched/disputed items
from an approved payable rather than estimating them silently.

## Two-sided contribution, not headline revenue

Build a cohort funnel with explicit denominators and maturation windows:

`inquiries × qualified/inquiries × closed/qualified × collected/closed × eligible cash per collected job`

That simplified formula assumes all-or-none collection and homogeneous jobs.
For partial payments/refunds or variable job sizes, use the actual ledger or a
collection-weighted model rather than multiplying another collection factor into
already net collected amounts. Use capacity-constrained volumes.

- **Operator contribution:** fixed/hybrid/variable fee earned less acquisition,
  amortized content/site costs, partner acquisition/onboarding, sales/support
  labor, tooling, reconciliation and costs/losses borne by the operator. Keep
  fixed overhead, taxes and financing separate but visible.
- **Client contribution:** eligible job receipts less incremental delivery,
  materials, labor, support/warranty/rework and other costs, then operator fee.
  Include any excluded pass-through receipts and matching costs separately when
  they affect whole-job profitability. Revenue share is not profit share.
- **Incremental client benefit:** compare the client's entire changed workflow
  with a credible counterfactual, including substituted channels, displaced jobs
  and capacity opportunity costs. Contractually attributed revenue or contribution
  cannot establish incremental benefit on its own.

### Synthetic scenario: arithmetic, not a market benchmark

Assume 100 inquiries, 40% qualification, 50% close, 90% all-or-none collection,
$2,000 eligible cash per collected job, a 15% fee and $4,500 operator cost. Assume
client delivery contribution before the fee is 35% of eligible receipts and all
relevant job costs are included in that assumption.

| Scenario | Eligible cash | Fee | Operator contribution | Client contribution after fee |
|---|---:|---:|---:|---:|
| Base | $36,000 | $5,400 | $900 | $7,200 |
| Close rate falls to 35%, same operator cost | $25,200 | $3,780 | -$720 | $5,040 |
| Client pre-fee margin only 15%, base volume | $36,000 | $5,400 | $900 | $0 |

At these assumptions the operator fee break-even rate is $4,500 / $36,000 = 12.5%
**before fixed overhead/tax**, while the client needs a fee below its pre-fee
contribution margin to retain positive contribution. This is a feasibility range,
not a recommended commission. Neither party's positive attributed contribution
proves incremental profit. Price, labor and conversion may change together; test
that interaction rather than treating costs as fixed in every scenario.

Compare fixed, variable-only, hybrid and capped-investment offers on the same
service scope and volume. A hybrid “floor” can mean an additive retainer, a
minimum total fee, or a recoupable advance; write the formula so it cannot be
charged twice. Specify tier/cap order and whether percentages are marginal or
retroactive. Test low conversion, high rework/refunds, slow collections, partner
loss, search traffic loss, ramp/indexing lag, seasonality and concentration.

## Reconcile with events, not one overwritten status

Use the analytics measurement contract for opaque referral and source IDs,
authorized source access, timestamps, idempotency and status mapping. Maintain
receipts, reversals, fee accruals and fee payments as separate linked records;
preserve corrections and reason codes. Reference the original transaction for
each reversal, and prevent both replayed events and duplicate reporting channels
from earning the fee twice. Keep currencies separate until an explicit dated FX
policy is applied. Use decimal/minor-unit amounts and document rounding.

Synthetic example, USD, 15% fee, no tax/pass-through exclusions, no reserve:

| Event | Eligible cash movement | Fee movement | Cumulative fee earned | Operator fee cash received |
|---|---:|---:|---:|---:|
| $2,000 order booked | $0 | $0 | $0 | $0 |
| Settled deposit D1 | $500 | $75 | $75 | $0 |
| D1 delivered again (duplicate) | $0 | $0 | $75 | $0 |
| Settled balance P2 | $1,500 | $225 | $300 | $0 |
| Fee payout F1 | $0 | $0 | $300 | $300 |
| $400 refund R1 linked to P2 | -$400 | -$60 | $240 | $300 |

Eligible net cash is $1,600, fee earned $240, and $60 previously paid must be
returned or offset under the agreement. Do not erase the payout or clamp the
negative fee balance to zero. Distinguish owed, disputed, withheld and paid
amounts; a reserve changes availability, not automatically the fee earned.
Contractual treatment of late reversals and termination must be explicit.

Close each period with:

1. Reconcile source receipts/reversals to processor or bank evidence and eligible
   amounts. Check known exclusions, duplicates, unknown mappings and missing
   exports. Document access limits; avoid retaining unnecessary customer data.
2. Calculate current-period fee movements under the versioned rules, including
   eligible signed adjustments and fixed fees where applicable.
3. Reconcile `closing fee balance = opening balance + fee movements - net fee
   cash paid`, where a returned fee is negative cash paid. Reconcile reserves and
   disputes in separate subledgers to avoid counting them twice.
4. Review exceptions, approvals and challenge-period outcomes before a payout.
   Preserve an audit trail and bound any later adjustments/termination tail.

Payment infrastructure does not eliminate collection risk. Stripe's separate
charges/transfers configuration debits the platform for fees, refunds and
chargebacks and has async reversal responsibilities. This is specific to that
configuration, not a rule for all integrations; route operation to `stripe`.

## Model cash timing independently

For each party, by week/month: opening cash + actual cash inflows - actual cash
outflows = closing cash. Distinguish earned fee, invoice, collection, available
processor balance and payout. Show initial acquisition/onboarding expense,
working-capital trough, collection lags, payout delays, reserves, refunds and
termination recovery. A positive eventual contribution can still exhaust cash.
Amortization belongs in contribution analysis; actual setup spend belongs in the
cash timeline. Do not charge both again in the same view.

Complete with reconciled scenarios, a readable fee formula, ledger example,
cash-loss budget and a decision for both parties. Stop a scale recommendation if
cash evidence, cost ownership, lawful compensation or attribution rules remain
unresolved; name the missing input and owner rather than inventing a market rate.

## Provenance

Method and synthetic arithmetic synthesized from the public-source review dated
2026-11-06. Mechanism examples: [Airbnb co-host payouts](https://www.airbnb.com/help/article/3389)
and [Stripe separate charges/transfers](https://docs.stripe.com/connect/separate-charges-and-transfers).
Neither validates this model's profitability. For evidence scope and legal
screening sources, read the [GTM source ledger](../../go-to-market/references/outcome-partnership-sources.md);
no direct comparative performance
study of microsite partnerships was identified in that targeted review.
