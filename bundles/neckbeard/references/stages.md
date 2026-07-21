# SDLC Stages

Each stage below defines **entry conditions** (what must be true to start),
**required evidence** (what you must gather or produce), **exit conditions**
(what must be true to leave), and **escalation rules** (when to stop and hand to
a human). The spine in `SKILL.md` is the order; this file is the detail.

A stage may be skipped only when its entry conditions are already met by the
incoming request (e.g. a fully-specified contract skips most of Framing). Record
every skip and why in the evidence ledger.

---

## Stage 1 — Frame the change contract

**Entry:** A request that could justify a change.

**Do:**
- State the user-visible problem in one or two sentences.
- List constraints (platform, compatibility, performance, policy), the affected
  system boundary, and the risks you can already see.
- State explicit **non-goals** — what this change will *not* do.
- Classify authority: is this *explore only*, or *modify / publish / deploy /
  merge*? When unclear, assume explore and ask.
- Decide whether any change is justified at all. "No change needed" is a valid,
  evidence-backed outcome.

**Required evidence:** the request text, the authority classification, and (if
available) the project's contribution guidance.

**Exit:** A change contract exists (use [../templates/change-contract.md](../templates/change-contract.md))
OR a documented decision that no change is warranted.

**Escalate:** when the request is ambiguous between explore and modify, or when
the stated goal conflicts with a hard constraint.

---

## Stage 2 — Discover before designing

**Entry:** A framed contract (or a documented no-change decision to confirm).

**Do:**
- Inspect the *actual* repository: structure, contribution docs, architecture,
  the real call path, tests, configuration, and recent changes to the area.
- Prefer primary evidence — code, tests, runtime output, project docs — over a
  plausible architecture narrative.
- If a specialist owns this (reverse-engineering a codebase →
  `software-architecture-analysis`; root cause → `systematic-debugging`), load
  it and follow it. Note in the ledger if the specialist was unavailable.
- Write down every unverified assumption and every access gap.

**Required evidence:** the inspected artifacts (paths/commits/outputs), the real
call path for the affected behavior, and an explicit assumptions list.

**Exit:** You can describe the real current behavior and the gap to the desired
behavior, citing artifacts — not a guess.

**Escalate:** when the behavior cannot be reproduced or observed and the gap
blocks design.

---

## Stage 3 — Select the smallest safe intervention

**Entry:** A verified understanding of current vs. desired behavior.

**Do:**
- Reuse existing code and platform capabilities first. Then choose the smallest
  implementation that satisfies the verified contract.
- Treat "smallest diff" as a **consequence of understanding**, not an
  optimization target. Do not compress to win a metric.
- **Minimalism is conditional.** The correct answer may be a larger change, a
  new dependency, a process/config change, or no code change. Pick by evidence,
  not by reflex.
- Preserve non-negotiables: trust-boundary validation, data safety, security,
  accessibility, observability, operational recovery, and explicitly requested
  behavior. Never trade these for brevity.
- If you deliberately choose a simple design with a known ceiling, record the
  ceiling and its upgrade trigger in a decision record
  ([../templates/decision-record.md](../templates/decision-record.md)).

**Required evidence:** the alternatives considered and why each was rejected; the
non-negotiables checked; any ceiling + trigger.

**Exit:** One chosen approach with a stated rationale and a rejected-alternatives
list.

**Escalate:** when two materially different approaches are both defensible and
the choice is consequential or hard to reverse.

---

## Stage 4 — Execute by stage

Route the chosen work to the stage that owns it and follow that stage's method
(load the specialist skill where one exists):

- **Discovery / requirements** → problem framing, stakeholders, acceptance
  criteria, edge cases. Specialist: `product-discovery`.
- **Design** → architecture fit, alternatives, a decision record when the choice
  is consequential. Specialist: `spec-driven-development` for formal specs;
  `product-design-and-ux` for user-facing behavior, interaction, or information
  architecture; `api-design-and-evolution` for an interface contract.
- **Implementation** → trace the real flow, fix root cause (not symptom), produce
  a minimal viable diff and reviewable commits. Specialist: `systematic-debugging`
  for bugs. For security-sensitive changes (untrusted input, auth, secrets,
  trust-boundary crossings), load `secure-software-engineering`; for accessible
  UI, load `web-accessibility`.
- **Verification** → layered checks from focused tests through integration to
  delivery-boundary validation, plus rollback/recovery evidence where relevant.
  Specialist: `verification-methodology`; `qa-methodology` for test strategy and
  regression coverage.
- **Delivery & learning** → release/deployment evidence, documentation updates
  (specialist: `technical-documentation`), post-delivery findings, and reusable
  lessons captured back into skills/memory. For reliability objectives, incident
  response, or operational recovery, load `site-reliability-engineering`.

**Required evidence:** per-stage artifacts as defined by the specialist or, if
absent, the minimal method noted in the ledger.

**Exit:** The stage's own exit conditions, plus an updated ledger.

**Escalate:** per the stage's rules and the global gates in
[risk-authority-gates.md](risk-authority-gates.md).

---

## Stage 5 — Verify at the target boundary

**Entry:** An implementation that claims to satisfy the contract.

**Do:**
- Exercise the **declared verification target** — the boundary the contract
  actually cares about (unit, integration, end-to-end, production).
- Distinguish a component-level check from an end-to-end or production-boundary
  check. State which one ran.
- If the target boundary cannot be exercised, say so and report the unverified
  gap. Do not substitute a weaker check and call it done.

**Required evidence:** the commands/checks run, their observed output, and the
boundary each one actually covers.

**Exit:** The declared target was exercised and passed, **or** an honest
statement of the unverified gap.

**Escalate:** when the only available check is weaker than the declared target
and the gap is material.

---

## Stage 6 — Deliver and learn

**Entry:** A verified (or honestly gap-declared) change with authority to deliver.

**Do:**
- Produce release/deployment evidence appropriate to the change.
- Update documentation affected by the change.
- Capture post-delivery findings and reusable lessons back into the appropriate
  durable layer (skill, memory, or project docs).

**Required evidence:** delivery evidence, doc updates, and any captured lesson.

**Exit:** Delivered with evidence, or blocked with a stated reason.

**Escalate:** before any deploy, merge, or irreversible act unless authority was
explicitly granted (see [risk-authority-gates.md](risk-authority-gates.md)).
