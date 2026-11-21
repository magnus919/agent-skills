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
| 1 | 4-1.5-0.5=2 hours/week | Claims four hours saved weekly | No input-specific treatment of this requirement |
| 2 | 10/2=5 weeks setup payback | Claims setup pays back in one week | No input-specific treatment of this requirement |
| 3 | Include ongoing tool cost before recommending adoption | Declares the automation free | No input-specific treatment of this requirement |
| 4 | Equal quality is a planning assumption, not observed acceptance evidence | Claims production quality has already been verified | No input-specific treatment of this requirement |
| 5 | Founder owns customer promises | Agents may promise any delivery date | No input-specific treatment of this requirement |
| 6 | Return to manual delivery when automation fails | Failures are left without a recovery path | No input-specific treatment of this requirement |

### absence-and-concentration

| Assertion | Satisfying example | Contradictory near miss | Omission / not shown |
|---|---|---|---|
| 1 | 80% marketplace sales creates concentration exposure | Calls the sales channel diversified | No input-specific treatment of this requirement |
| 2 | 24/7 promise needs actual coverage during absence | Says current revenue eliminates the support obligation | No input-specific treatment of this requirement |
| 3 | Arrange coverage or explicitly agree a change with affected customers | Replace existing 24/7 terms with a notice unilaterally | No input-specific treatment of this requirement |
| 4 | Document emergency access and account recovery | Assume another person can access everything without preparation | No input-specific treatment of this requirement |
| 5 | Tell customers what coverage they can rely on | Tell customers nothing about the absence plan | No input-specific treatment of this requirement |
| 6 | Name an available fallback owner | Assume an unnamed person will handle incidents | No input-specific treatment of this requirement |
| 7 | Verify escalation and fallback before relying on the bot | Bot scheduling proves support coverage | No input-specific treatment of this requirement |

### outlier-and-goal

| Assertion | Satisfying example | Contradictory near miss | Omission / not shown |
|---|---|---|---|
| 1 | Wix announcement includes team and earnout terms | Acquisition is typical solo take-home | No input-specific treatment of this requirement |
| 2 | Plan around $5000/month and 20 hours/week | Mandate YC growth regardless of goals | No input-specific treatment of this requirement |
| 3 | Get buyer access, costs, support and collections inputs | Forecast income from acquisition story alone | No input-specific treatment of this requirement |

### anchor-and-pipeline

| Assertion | Satisfying example | Contradictory near miss | Omission / not shown |
|---|---|---|---|
| 1 | 44 minus 40 minus 2 leaves two hours; book two one-hour blocks outside client time | A three-hour weekly floor without a trade-off | No weekly hours check |
| 2 | Follow up with the three known prospects and use an approved sample if useful | Build a web funnel before contacting anyone | No prioritization of the available prospects |
| 3 | Record who owns the next step and when it is due | Record interest without a next action | No dated action |
| 4 | Seek a scoped renewal decision or pivot by a date before the booked end | Wait until the last day to ask about extension | No pre-end decision checkpoint |
| 5 | Separate expressed interest from signed work | Forecast the three contacts as booked revenue | No treatment of their commitment status |

### nontech-seasonal-referrals

| Assertion | Satisfying example | Contradictory near miss | Omission / not shown |
|---|---|---|---|
| 1 | Work one recurring hour outside delivery | Default to the three-hour example | No time budget |
| 2 | Reconnect with the two venues before the booking season | Build pipeline by selling second wedding shoots to past couples | No plausible feeder channel |
| 3 | Arrange a venue follow-up this week and review before bookings open | Wait until the season has opened to reconnect | No dated action |
| 4 | Use an approved sample or a generic shot list | Republish private wedding photos as proof | No consent treatment |

## Trigger boundary probes (manual design review, not harness execution)

Should trigger: “Choose a solo business for my 10-hour week”; “My one-person SaaS support is swallowing sales”; “Can I productize my freelance service without exceeding my cash cap?”

Should not trigger: “Calculate break-even from these costs” → financial-modeling; “Write customer interview questions” → product-discovery; “Triage my calendar” → chief-of-staff-methodology.

A future behavioral run needs fresh contexts, retained candidate outputs, assertion-level evidence and reviewer provenance, plus comparable route-only baseline outputs before claiming improvement. A separate model reviewed the artifacts and prompted rubric, obligation-preservation and claim-calibration repairs; this is not behavioral execution or human certification. Real-user utility remains unassessed.
