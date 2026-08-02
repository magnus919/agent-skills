# AI Code Quality Gates: QA Ownership in AI Factories

## Independent Verification Principle

**NORMATIVE: The implementing agent MUST NOT self-verify its own output.**

This is the structural foundation of quality in agentic workflows. Evidence: IBM Research (Ahmed et al., 2025, arXiv:2511.16858) measured LLM-based automated program repair on SWE-bench Verified and found test overfitting rates of **21.8% (Claude-3.7-Sonnet) to 35.9% (GPT-4o)** — patches that pass white-box tests but fail held-out black-box tests. Critically, test-based refinement *increases* overfitting (21.8% → 25.5% for Claude; 33.0% → 35.9% for GPT-4o), because exposing tests to the generating model creates a feedback loop that games the oracle rather than fixing the code.

### Independence in Agentic Workflows

In an agentic workflow, independence requires a **separate agent session** — a different instance with no shared context, conversation history, or memory with the implementing agent.

> **WARNING — Same-session self-review is NOT independent.** An agent that implements code in one turn and reviews it in the next turn of the SAME session shares priors, blind spots, and confirmation bias within that context window. The reviewing turn has already "seen" the implementation rationale and will anchor on it. This is the agentic equivalent of a developer approving their own PR.

| Verification Model | Independence? | Why |
|-------------------|--------------|-----|
| Same agent, same session, next turn | NO | Shared context, shared priors, confirmation bias |
| Same agent, fresh session, no memory | YES | No shared state; fresh evaluation against spec |
| Different agent model, fresh session | YES (strongest) | Different training distribution catches different failure modes |
| Human reviewer | YES | Different cognitive frame entirely |

## QA-Owned Artifacts per Gate

Pipeline phases and gate verdict formats belong to [spec-driven-development](../../spec-driven-development/SKILL.md). QA owns the **verification layer** at each gate:

| Gate | QA-Owned Artifact | What QA Does |
|------|------------------|--------------|
| **Gate 1** (spec review) | Spec testability review | Run [../scripts/check-ac-testability.py](../scripts/check-ac-testability.py) to flag untestable ACs; verify every AC has an observable outcome and verification method |
| **Gate 2** (plan review) | Verification plan | Produce the plan artifact mapping every AC to a verification method, verifier, and evidence format |
| **Gate 3** (implementation review) | Independent verification | Execute the verification plan in a SEPARATE agent session; record pass/fail per AC with evidence |
| **Gate 4** (acceptance) | Verdict with evidence dossier | QA issues the final verdict: every AC verified, NFR evidence attached, no AC unmapped |
| **Post-merge** | Canary observation plan | Define AC-tied success metrics and rollback triggers for progressive rollout |

### Verification Plan Structure

Use [templates/verification-plan.md](../templates/verification-plan.md) as the fillable artifact when producing a verification plan. The plan must contain:

1. **AC→verification-method traceability matrix** — every acceptance criterion maps to one of: test, inspection, analysis, or demonstration. No AC may be unmapped.
2. **Verifier assignment** — who/what performs each verification (independent agent session, human, automated script).
3. **Evidence format** — what artifact proves the verification (test output log, screenshot, metrics snapshot).
4. **NFR verification approach** — how non-functional requirements (latency, throughput, security) are measured.
5. **Exit criteria** — the observable state that means "verification complete" (e.g., 100% AC coverage, zero critical findings, NFR thresholds met).

### Non-Determinism Handling Decision Rule

AI-generated code often exhibits non-deterministic behavior (LLM outputs, randomized algorithms, concurrency).

| Condition | Verification Approach |
|-----------|----------------------|
| Output is deterministic (same input → same output always) | Single-run equality check |
| Output varies across N runs but has invariants | Property-based assertions (shape, bounds, invariants) + N-run sampling (N≥5) |
| Output is probabilistic with known distribution | Statistical tolerance bands (e.g., p95 latency < X) |
| Output depends on external state (time, random seed) | Pin the external state; verify under controlled conditions |

**Decision rule:** Run the implementation 5 times with identical inputs. If any output differs, the code is non-deterministic — use property-based or statistical verification. Never assert exact equality on non-deterministic output.

## Agent-Generated Test Quality

### The Mirrored-Bug Risk

When an agent generates both code AND tests in the same session, both artifacts share the same misunderstanding of the spec. The test passes because it encodes the same bug, not because the code is correct. This is the test-overfitting problem (IBM, 21.8–35.9%) manifesting at the test-authoring level.

**Mitigation:** Tests must be written from the SPEC, not from the implementation. The test author (agent or human) must not see the implementation source before writing assertions.

### Quality Techniques for Agent-Generated Tests

| Technique | What It Catches | Tools |
|-----------|----------------|-------|
| **Mutation testing** | Tests that never fail (vacuous assertions) | PIT (Java), Stryker (JS/TS), mutmut (Python) |
| **Property-based testing** | Missing edge cases, boundary violations | Hypothesis (Python), fast-check (JS/TS) |
| **Differential testing** | Divergence between implementations or spec interpretations | Custom harnesses comparing two implementations |
| **Independent oracle** | Mirrored bugs from shared context | Tests written in separate session from implementation |

## Regression Under AI PR Volume

AI code factories generate PRs at 5–50× human velocity. Traditional "run everything" regression is infeasible.

| Strategy | Mechanism | When |
|----------|-----------|------|
| **Risk-weighted selection** | Score tests by (change overlap × historical failure rate × business criticality); run top-K | Every PR |
| **Capability→regression graduation** | New capability tests run in a "capability" suite; after 3 consecutive green merges, promote to regression suite | Ongoing |

**Graduation rule:** A test enters the regression suite only after it has passed on 3 consecutive unrelated merges without flaking. Tests that flake during the capability phase are quarantined, not promoted.

## Human-in-the-Loop Review

### The ~400-Line Threshold

Research (Bacchelli & Bird, 2013; Microsoft code review studies) shows review effectiveness drops sharply above ~400 changed lines. AI agents routinely produce 500–2000 line PRs.

| PR Size | Review Strategy |
|---------|----------------|
| < 200 lines | Single human reviewer, standard review |
| 200–400 lines | Two reviewers; focus on architecture and spec compliance |
| > 400 lines | **Require decomposition** OR risk-tiered escalation: security-sensitive paths reviewed by security engineer; business logic by domain expert; mechanical changes spot-checked |

### Gate-Fatigue Countermeasures

When AI generates 20+ PRs/day, reviewers rubber-stamp. Countermeasures:
- Rotate reviewers on a schedule (not ad hoc)
- Require at least one substantive comment per review (not just "LGTM")
- Sample 10% of approved PRs for re-review by a second reviewer
- Track escaped-defect rate per reviewer as a calibration signal

### Agent-Specific Code Review Heuristics

| Failure Mode | Detection Heuristic |
|-------------|-------------------|
| **Hallucinated APIs/imports** | Verify every import statement resolves to a real package; every API call matches documented signatures. Run `python -c "import X"` or equivalent per dependency. |
| **Plausible-but-wrong logic** | Trace at least one critical business path end-to-end against the spec's expected behavior, not just syntax correctness. Compare output to a hand-computed example. |
| **Silent error swallowing** | Flag `except: pass`, `catch(e) {}`, `if err != nil { return nil }` patterns that discard or log-and-continue without surfacing failures to callers. |
| **Over-engineering / spec-letter compliance** | Check whether the solution satisfies the spec's INTENT. An agent may add 300 lines of abstraction to satisfy one AC literally while missing the user's actual need. Ask: "Would a senior engineer write it this way?" |

## Contract Testing

Consumer-driven contracts (Pact) verify service boundaries without full integration:
- Consumer publishes expectations → provider verifies in its own CI
- Critical for AI factories: when multiple agents build different services independently, contract tests catch boundary violations before deployment

For SDET-level contract testing architecture, see [sdet-engineering.md](./sdet-engineering.md).

## Canary / Progressive Rollout with AC-Tied Rollback

| Stage | Traffic | Success Criterion | Rollback Trigger |
|-------|---------|-------------------|-----------------|
| Canary | 1–5% | Error rate ≤ baseline; AC-tied metrics within tolerance | Any AC metric degrades > threshold |
| Progressive | 25% → 50% → 100% | Same as canary + latency p95 stable | SLO breach or new error pattern |

**AC-tied rollback:** Each acceptance criterion that has a measurable production proxy (e.g., "checkout success rate > 99.5%") becomes a canary metric. If the proxy degrades, auto-rollback triggers without human intervention.

## Security Gates

Pearce et al. (2022) found GitHub Copilot generated **vulnerable code in ~40% of scenarios** across CWE categories. AI-generated code requires mandatory security scanning:

| Gate | Tool Category | Blocking? |
|------|--------------|-----------|
| Pre-merge SAST | Static analysis (Semgrep, CodeQL) | Yes, for critical/high |
| Dependency audit | SCA (npm audit, pip-audit, Trivy) | Yes, for known CVEs |
| Secrets detection | Pattern scanning (gitleaks, trufflehog) | Yes, always |

For full security testing methodology, see [secure-software-engineering](../../secure-software-engineering/SKILL.md).

## Worked Example: Gate 3 Independent Verification

**Context:** An agent implemented "AC-7: Users can reset their password via email link expiring in 24h."

| Step | Action | Evidence |
|------|--------|----------|
| 1 | QA opens a SEPARATE agent session with ONLY the spec (no implementation context) | Session ID logged |
| 2 | QA agent writes verification: request reset → check email sent → click link → set new password → verify old password fails | Test script |
| 3 | QA agent tests boundary: link at 23h59m (should work), link at 24h01m (should fail) | Boundary test output |
| 4 | QA agent tests negative: reuse expired link (should 403) | Negative test output |
| 5 | Verdict: AC-7 PASS (3/3 verifications green) | Evidence attached to gate record |

**Anti-pattern avoided:** Had the implementing agent run its own tests, it would have tested only the happy path it coded — missing the expiry boundary entirely (mirrored-bug risk).

## Decision Table: Which Verification Approach?

| Situation | Approach | Exit Condition |
|-----------|----------|----------------|
| Deterministic function, clear spec | Single-run equality test | Test passes with expected output |
| Non-deterministic output | Property-based + N-run sampling | All N runs satisfy invariants |
| Multi-service integration | Contract test + canary | Contracts green; canary metrics stable for 1h |
| Security-sensitive change | SAST + human security review | Zero critical findings; reviewer sign-off |
| UI/UX requirement | Demonstration + human inspection | Reviewer confirms visual/interaction matches spec |

## Exit Conditions

You are done applying this reference when:
- Every AC in the spec maps to a verification method with an assigned independent verifier (100% traceability)
- Gate 3 verification was executed in a separate agent session (or by a human) — NOT by the implementing agent
- Evidence for each AC verdict is attached and reproducible
- Security scan passes with zero critical/high findings
- Non-deterministic outputs use statistical/property-based verification (not exact equality)

## Composition

- **Pipeline mechanics** (phase ordering, gate verdict format APPROVED/CONDITIONS/REJECTED, revision loop, methodology selection): delegated to [spec-driven-development](../../spec-driven-development/SKILL.md). This file adds only the QA ownership layer: WHO verifies, HOW, and WHAT beyond-spec checks apply.
- **For measuring agent capability over time** (eval datasets, judge calibration, CI gate architecture for evals, benchmark interpretation): see [agentic-eval-design.md](./agentic-eval-design.md).
- SDET test infrastructure patterns: [sdet-engineering.md](./sdet-engineering.md)
- Quality metrics and gate design: [quality-gates-and-metrics.md](./quality-gates-and-metrics.md)

---

*Sources: Ahmed, Ganhotra, Shinnar, Hirzel, "Is the Cure Still Worse Than the Disease? Test Overfitting by LLMs in APR" (IBM Research, arXiv:2511.16858, 2025); Pearce et al., "Examining Zero-Shot Vulnerability Repair with Large Language Models" (IEEE S&P, 2022, ~40% vulnerable code rate); Bacchelli & Bird, "Expectations, Outcomes, and Challenges of Modern Code Review" (ICSE, 2013); Pact Foundation (docs.pact.io); METR, "Recent Frontier Models Are Reward Hacking" (metr.org, 2025, 30.4% reward-hacking rate on RE-Bench).*
