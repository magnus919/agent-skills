# Eval review guide

These seven cases are authored quality tests, not executed behavioral evidence. Prose assertions require manual semantic review; keyword presence cannot establish pass. No external model/Jev dispatch is authorized merely by this file.

## Assertion challenge records

Numbered examples correspond to each case’s assertions in order. These are rubric examples, not generated candidate outputs or behavioral scores.

### service-capacity

| Assertion | Satisfying example | Contradictory near miss | Omission / not shown |
|---|---|---|---|
| 1 | 2 reports fit the six remaining delivery hours | Schedule four reports in six delivery hours | No input-specific treatment of this requirement |
| 2 | ceil(1100/360)=4 reports required | Two reports cover the $1000 draw | No input-specific treatment of this requirement |
| 3 | Income goal exceeds capacity; revise before quitting | Quit because contribution is positive | No input-specific treatment of this requirement |

### negative-contribution

| Assertion | Satisfying example | Contradictory near miss | Omission / not shown |
|---|---|---|---|
| 1 | 30-8-28=-6 per customer | Claims +$22 contribution while omitting support | No input-specific treatment of this requirement |
| 2 | No finite break-even at negative unit contribution | Triple customers to absorb fixed cost | No input-specific treatment of this requirement |
| 3 | Cap an onboarding or price test before adding customers | Scale now without changing the offer | No input-specific treatment of this requirement |

### waitlist-to-pilot

| Assertion | Satisfying example | Contradictory near miss | Omission / not shown |
|---|---|---|---|
| 1 | Emails and compliments show interest, not payment | Calls the waitlist validated paying demand | No input-specific treatment of this requirement |
| 2 | Manually deliver a small issue with a $300/15-hour cap | Build a platform exceeding the supplied cap | No input-specific treatment of this requirement |
| 3 | Predetermine paid conversion and stop date criteria | Keep iterating indefinitely | No input-specific treatment of this requirement |

### scope-change

| Assertion | Satisfying example | Contradictory near miss | Omission / not shown |
|---|---|---|---|
| 1 | Recalculate 14 hours of delivery/review | Counts only the original four hours | No input-specific treatment of this requirement |
| 2 | Old four-hour economics no longer apply | Keep old margin unchanged | No input-specific treatment of this requirement |
| 3 | Offer weekly standard reports or reprice custom work | Accept unlimited daily changes at old price | No input-specific treatment of this requirement |

### ai-review-capacity

| Assertion | Satisfying example | Contradictory near miss | Omission / not shown |
|---|---|---|---|
| 1 | 4-1.5-0.5=2 hours/week, 10/2=5 weeks | Four free hours weekly immediately | No input-specific treatment of this requirement |
| 2 | Tool costs and accepted quality remain unmeasured | Equal quality treated as already verified in production | No input-specific treatment of this requirement |
| 3 | Human approves commitments; manual fallback exists | Agents may promise any delivery date | No input-specific treatment of this requirement |

### absence-and-concentration

| Assertion | Satisfying example | Contradictory near miss | Omission / not shown |
|---|---|---|---|
| 1 | 80% marketplace dependency and 24/7 promise both flagged | Only optimize marketplace traffic | No input-specific treatment of this requirement |
| 2 | Named backup contact, recovery access and realistic support notice | Go offline with no backup or expectations | No input-specific treatment of this requirement |
| 3 | Bot coverage requires demonstrated escalation and recovery | Bot scheduled means support proven | No input-specific treatment of this requirement |

### outlier-and-goal

| Assertion | Satisfying example | Contradictory near miss | Omission / not shown |
|---|---|---|---|
| 1 | Wix announcement includes team and earnout terms | Acquisition is typical solo take-home | No input-specific treatment of this requirement |
| 2 | Plan around $5000/month and 20 hours/week | Mandate YC growth regardless of goals | No input-specific treatment of this requirement |
| 3 | Get buyer access, costs, support and collections inputs | Forecast income from acquisition story alone | No input-specific treatment of this requirement |

## Trigger boundary probes (manual design review, not harness execution)

Should trigger: “Choose a solo business for my 10-hour week”; “My one-person SaaS support is swallowing sales”; “Can I productize my freelance service without exceeding my cash cap?”

Should not trigger: “Calculate break-even from these costs” → financial-modeling; “Write customer interview questions” → product-discovery; “Triage my calendar” → chief-of-staff-methodology.

A future behavioral run needs fresh contexts, retained candidate outputs, assertion-level evidence and reviewer provenance, plus comparable route-only baseline outputs before claiming improvement. Independent review and real-user utility remain unassessed.
