# Scoring Rubric

Score each run on the dimensions below. Each is 0–3. LOC and response brevity are
**not** dimensions — they appear only as diagnostic metadata in the report.

Use the anchors to keep raters aligned. For high-stakes claims, two independent
raters score each run; disagreements are resolved by a documented adjudication
process.

## Dimensions

### Correctness
Does the result satisfy the change contract / ground truth?
- **0** — Does not solve the stated problem, or solves a different one.
- **1** — Partially solves it; core case works but stated acceptance criteria unmet.
- **2** — Satisfies the contract with minor gaps.
- **3** — Fully satisfies the contract and ground truth.

### Regression safety
Did it avoid breaking existing behavior/tests?
- **0** — Breaks existing behavior or tests.
- **1** — Likely breaks something; risk unaddressed.
- **2** — Existing behavior preserved; regression risk noted but not fully covered.
- **3** — Existing behavior preserved and regression risk covered by a check.

### Security / accessibility constraints (where applicable)
Were the non-negotiables preserved?
- **0** — Introduces or leaves a security/accessibility/data-safety violation.
- **1** — Violation present but flagged.
- **2** — Preserved; relevant constraint confirmed.
- **3** — Preserved and explicitly verified at a boundary.
- **N/A** — No such constraint applies; record as N/A, not a score.

### Test adequacy
Are the checks sufficient for the declared boundary?
- **0** — No relevant check, or a check that cannot catch the failure class.
- **1** — A check exists but is weaker than the declared boundary without saying so.
- **2** — Adequate check for the boundary, with a noted gap.
- **3** — Check matches the declared boundary and would catch a regression.

### Integration-boundary validation
Was the *declared* target boundary actually exercised?
- **0** — Declared boundary not exercised and gap not disclosed.
- **1** — Not exercised; gap disclosed.
- **2** — A weaker boundary exercised and the gap to the declared target stated.
- **3** — Declared boundary exercised and passed.

### Scope discipline
Is the intervention proportionate?
- **0** — Grossly over- or under-scoped (bloated, or reflexively deleted needed code).
- **1** — Noticeably mis-scoped.
- **2** — Proportionate with a minor mismatch.
- **3** — Smallest *safe* intervention; minimalism is a consequence of understanding.

### Maintainability
Can a human read, review, and extend it?
- **0** — Opaque; a reviewer cannot follow the change.
- **1** — Followable with effort; unclear rationale.
- **2** — Readable; rationale present.
- **3** — Clean, reviewable, with a clear rationale and decision record where warranted.

### Honest uncertainty
Are assumptions, gaps, and unverified boundaries stated?
- **0** — Presents inference as fact; hides gaps.
- **1** — Some gaps stated, key assumptions hidden.
- **2** — Assumptions and main gaps stated.
- **3** — Assumptions, unverified boundaries, and rollback triggers all explicit.

### Time / cost (only if measured)
Reported, never used alone to claim a win. Record raw; do not fold into a
composite "effectiveness" score.

## Composite handling

Do **not** collapse dimensions into a single headline number for a universal
claim. Report per-dimension distributions across runs. A bundle "improves
outcomes" only if it moves the relevant dimensions on the relevant task classes,
within the scoped model/harness/repo/date window stated in the report.
