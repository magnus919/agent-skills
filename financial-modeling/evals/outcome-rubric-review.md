# Outcome-partnership rubric challenge examples

Added 2026-11-06. Existing case IDs and assertions are unchanged. These are authored
rubric checks, not recorded model outputs, independent ground truth or a semantic
release pass. Each row tests whether an assertion distinguishes met, not met and
not shown. Omission snippets are deliberately incomplete, not incorrect answers.

## outcome-fee-two-sided-downside

| Assertion | Satisfying example | Contradiction | Omission example |
|---|---|---|---|
| Computes base eligible cash $36,000, fee $5,400 and operator contribution $900. | 36,000 eligible cash; 5,400 fee; 900 operator contribution. | 40,000 eligible cash; 6,000 fee; 1,500 operator contribution. | The response discusses the service offer without addressing this requirement. |
| Computes the 35% close-rate downside operator contribution as negative $720. | Downside eligible cash is 25,200 and operator contribution is -720. | Downside operator contribution remains positive 900. | The response discusses the service offer without addressing this requirement. |
| Computes client contribution after fee as $7,200 at 35% margin and zero at 15% margin in the base-volume cases. | Base client contribution is 7,200; reducing pre-fee margin to 15% consumes it entirely. | Client retains 12,600 after paying the 5,400 fee. | The response discusses the service offer without addressing this requirement. |
| Labels the fee rate as a synthetic assumption rather than a validated market benchmark. | The 15% share is an illustrative input, not a researched market rate. | The calculation proves that 15% is standard and sustainable. | The response discusses the service offer without addressing this requirement. |

## outcome-fee-refund-after-payout

| Assertion | Satisfying example | Contradiction | Omission example |
|---|---|---|---|
| Does not accrue a collected-cash fee merely from booking the order. | Booking has no cash movement and no collected-cash fee. | Booking creates the full $300 fee before payment. | The response discusses the service offer without addressing this requirement. |
| Counts the repeated D1 event only once. | The replay adds zero eligible cash and zero fee. | The repeated deposit adds another $75 fee. | The response discusses the service offer without addressing this requirement. |
| Computes eligible net cash $1,600 and earned fee $240 after the refund. | 2,000 - 400 = 1,600; fee 240. | Fee remains 300 because it was already paid. | The response discusses the service offer without addressing this requirement. |
| Preserves the $60 overpayment for contract-defined return or offset rather than erasing it. | The fee balance is -60 after 300 paid against 240 earned; return/offset needs the agreement. | Clamp the negative fee balance to zero and discard the adjustment. | The response discusses the service offer without addressing this requirement. |

## outcome-fee-hybrid-cash-gap

| Assertion | Satisfying example | Contradiction | Omission example |
|---|---|---|---|
| Distinguishes an additive retainer from a minimum total fee or recoupable advance before fixing the payable. | If additive the illustrated fee is 5,000; if minimum total it is 3,000; an advance needs recoupment terms. | All three floor designs create the same 5,000 fee. | The response discusses the service offer without addressing this requirement. |
| Identifies the immediate $1,500 funding shortfall before the delayed fee receipt. | 3,000 available minus 4,500 immediate spend leaves a 1,500 cash gap. | Eventual revenue guarantees adequate cash during the 90-day wait. | The response discusses the service offer without addressing this requirement. |
| Treats the missing partner export as unknown evidence rather than a settled zero or invented payment. | Keep the payable unapproved until the missing source evidence is reconciled. | Missing data means zero cash was collected. | The response discusses the service offer without addressing this requirement. |
| Withholds a scale recommendation while the formula, cash funding or source evidence is unresolved. | Hold scaling until formula, liquidity and source reconciliation are resolved. | Scale immediately using assumed fees to fund the gap. | The response discusses the service offer without addressing this requirement. |

## Trigger probes (manual routing checks, not output-quality evals)

Should trigger: “Model both partners' contribution from a 15% fee”; “Reconcile deposits, refunds and fees already paid”; “Compare an additive retainer with a minimum fee and forecast cash.”

Should not trigger as primary: “Design a causal experiment for our referral program” (product-experimentation/data-scientist); “Send the partner a payout” (payment operations, with authorization).
