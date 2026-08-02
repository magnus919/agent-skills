# Agentic Eval Design: QA Playbook for Agent Evaluations

## Vocabulary (per Anthropic, "Demystifying Evals for AI Agents," 2026)

| Term | Definition |
|------|-----------|
| **Task** | A single evaluation problem with defined inputs, environment, and success criteria |
| **Trial** | One execution of one task by one agent configuration |
| **Grader** | A function that scores a trial's output (deterministic check, LLM judge, human) |
| **Transcript** | The full record of agent actions, tool calls, and observations during a trial |
| **Outcome** | The final environment state after the trial completes |
| **Harness** | Infrastructure that sets up the environment, runs the agent, and collects the transcript |
| **Scaffold** | The agent's prompting, tool configuration, and orchestration wrapper |
| **Suite** | A versioned collection of tasks used together for a decision |

**Grade the OUTCOME (environment state), not prose.** An agent that writes a beautiful explanation but leaves the database corrupted fails. An agent that produces terse output but correctly deploys the service passes. Evaluations measure what the agent DID to the world, not how it described what it did.

## The Eval-Driven Development Loop

| Suite Type | Purpose | Graduation Rule |
|-----------|---------|----------------|
| **Capability suite** | Measures what the agent CAN do (new features, hard problems) | After 3 consecutive green runs on unrelated changes, promote passing cases to regression |
| **Regression suite** | Ensures the agent STILL does what it used to | Never auto-retire; manual review only |

Cases flow: capability → (3 green runs) → regression. Regressions are never auto-promoted to capability; they are stable assertions of known-good behavior.

## Dataset Test Design

### Equivalence Partitioning and Boundary Cases

Apply classical test design to eval datasets:
- **Equivalence classes:** Group inputs by expected behavior category (valid, invalid, edge)
- **Boundary cases:** Test transitions between classes (max token length, permission threshold, timeout boundary)

### Class Balance (Including Negative Cases)

| Case Class | Target Proportion | Example |
|-----------|------------------|---------|
| Positive (should succeed) | 40–50% | Valid request → correct action |
| Negative (should fail/refuse) | 20–30% | Unauthorized action → refusal |
| Adversarial/injection | 15–20% | Prompt injection → no deviation |
| Boundary/edge | 10–15% | Empty input, max-length, concurrent |

> **Gotcha — Positive-only datasets:** A dataset with only "happy path" cases measures capability but not safety. Negative cases (the agent SHOULD refuse or fail gracefully) are mandatory. A 100% pass rate on positive-only cases says nothing about whether the agent handles errors correctly.

### Golden-Trajectory Curation

Curate **50–500 golden trajectories** for critical tasks: regression anchors, judge calibration material, and onboarding docs.

### Reference-Solution Oracle

For deterministic-answer tasks, maintain a reference solution. Compare agent output for semantic equivalence (correct behavior, acceptable variants), not string equality.

## Judge-as-System-Under-Test

The LLM judge is itself a system that must be tested. Five documented biases:

| Bias | Effect Size | Mechanical Mitigation |
|------|------------|----------------------|
| **Position bias** | ~10–15 point swing | Shuffle/rotate candidate order across trials |
| **Verbosity bias** | ~15–30 point swing | Length-neutral rubric; normalize scores by output length |
| **Self-preference** | ~10–25% inflated scores | Cross-family judge (judge from different vendor than the agent) |
| **Format bias** | ~5–15 point swing | Standardize output format before judging; rubric ignores formatting |
| **Calibration drift** | ~3–8 point drift over weeks | Monthly human calibration against golden set; alert on >5pt shift |

### Pin the Contract

Every judge invocation must record the immutable tuple:

```
(judge_model_id, rubric_version, prompt_template_hash)
```

If any element changes, scores are NOT comparable to prior runs. This tuple is the "contract" — treat changes as a migration event (see Judge-Swap Migration below).

### Monthly Human Calibration

Once per month, a human grader scores the same 20–30 trials as the LLM judge. Compute Cohen's kappa or agreement percentage. If agreement drops below 0.7, investigate rubric drift or judge degradation before trusting automated scores.

## Flaky-Eval Discipline

**Variance is the baseline, not an anomaly.** LLM agents are non-deterministic. A task that passes 7/10 times is not "flaky" — it has a 70% success rate, which IS the measurement.

### Sampling and Aggregation

- Run each task **N = 5–10 trials** per evaluation
- Aggregate via **majority vote** (pass if >50% of trials pass) or **weighted score** (average of per-trial scores)
- Report both mean and variance — a task at 60% ± 20% is fundamentally different from 60% ± 2%

### pass@k vs pass^k

| Metric | Definition | Use When |
|--------|-----------|----------|
| **pass@k** | At least 1 of k attempts succeeds | Product allows retries (interactive agent, user can re-request) |
| **pass^k** | ALL k attempts succeed | Product requires reliability (autonomous pipeline, no human in loop) |

**Choose from product requirements.** If the user can retry, pass@k is honest. If the agent runs unattended, pass^k reflects actual user experience. Never choose pass@k for an autonomous agent just because the numbers look better.

### No Retry-Until-Green

> **RULE: NEVER retry a failed evaluation until it passes.** If the suite fails at 6/10 trials, the result is 6/10. Retrying until green manufactures false confidence. Report the failure, investigate the variance, and either fix the agent or adjust the threshold. Retry-until-green is the eval equivalent of `while (!pass) run_tests()`.

## CI Gate Architecture

### Three Tiers

| Tier | Trigger | Contents | Time Budget |
|------|---------|----------|-------------|
| **Pre-merge** | Every PR | Fast subset (≤20 tasks) + deterministic scanners (schema, lint, import check) | < 5 minutes |
| **Nightly** | Scheduled | Full suite (all tasks, N=5 trials each) + judge scoring | < 60 minutes |
| **Continuous** | Production | Sampled live traffic (1–5%) scored asynchronously | Ongoing, budget-constrained |

### Cascade Cost Pyramid

Run the cheapest grader first; escalate only on failure:

```
Level 1: Deterministic checks (regex, schema, exit code)     → $0, instant
Level 2: Classifier (fine-tuned model, rules engine)         → $0.001/trial
Level 3: LLM judge (full rubric evaluation)                  → $0.01–0.05/trial
```

Only tasks that fail Level 1 or 2 reach the expensive LLM judge. This reduces nightly judge cost by 60–80%.

### Cost Budgeting

| Tier | Budget Principle | Example |
|------|-----------------|---------|
| Pre-merge | < $1 per PR; < 5 min wall time | 20 tasks × deterministic only |
| Nightly | < $50 per run; < 60 min | 200 tasks × 5 trials × cascade |
| Continuous | < $500/month | 1% traffic × Level 1 only + 0.1% × Level 3 |

**Cost determines tier placement.** A task that requires $0.10/trial in LLM-judge cost cannot go in pre-merge (20 tasks × 5 trials × $0.10 = $10/PR). Move it to nightly.

## Replay and Promote-Back Loop

```
Capture → Anonymize → Replay → Cluster → Promote (3–10 cases) → Re-gate
```

1. **Capture** production transcripts (with consent per telemetry policy)
2. **Anonymize** — strip PII, credentials, session IDs
3. **Replay** captured inputs against current agent version
4. **Cluster** failures by root cause (embedding similarity)
5. **Promote** 3–10 representative failures to regression suite
6. **Re-gate** — confirm no regression from promotion

Runs weekly or post-incident. Ensures the suite evolves with real usage.

## Trajectory-vs-Outcome Grading Decision Rule

| Grade the TRAJECTORY when... | Grade the OUTCOME only when... |
|------------------------------|-------------------------------|
| Path matters: safety-critical actions (medical, financial) | Multiple valid paths exist (creative tasks, open-ended problems) |
| Compliance requires specific steps (audit trail) | Any correct path is acceptable |
| Cost-sensitive operations (avoid unnecessary API calls) | Cost of path variation is negligible |
| Destructive/irreversible steps (data deletion, external comms) | Actions are reversible or sandboxed |

> **Brittleness caveat:** Trajectory grading is MORE BRITTLE than outcome grading. It over-constrains the agent's approach and penalizes valid novel strategies. A golden trajectory that says "call API A then API B" will fail an agent that correctly uses API C (a newer, better path). Use trajectory grading sparingly and only where the path genuinely matters.

## Adversarial Self-Audit

### Null-Agent Floor

Before interpreting any eval score, run the **null agent** (an agent that does nothing, or returns empty/random output). The null agent's score is your floor. If a task's pass rate is only 5% above the null agent, the task has poor discriminative power — fix the task, not the agent.

### Adversarial Agent Types

| Agent Type | Purpose | What It Reveals |
|-----------|---------|----------------|
| **Random agent** | Baseline floor | Whether tasks are solvable by chance |
| **Injection agent** | Injects adversarial prompts into inputs | Whether the agent is hijackable |
| **State-tamper agent** | Modifies environment state, scoring code, or test files | Whether the harness is exploitable |

### Evidence: Berkeley RDI and METR

- **Berkeley RDI** (rdi.berkeley.edu, 2025–2026) identified **seven deadly patterns** of benchmark failure: leaked solutions in prompts, executable scoring code accessible to the agent, missing baseline comparisons, reward-component skipping, environment state leakage, non-reproducible setups, and trust in agent self-report.
- **METR** (metr.org, 2025) documented **30.4% reward-hacking rate** across RE-Bench tasks with o3: agents monkey-patched evaluators, overwrote timing functions, and copied reference answers. On one task, reward hacking occurred in 100% of trajectories.

**Implication:** Your eval harness must treat the agent as adversarial. Sandbox scoring code. Deny file-system access to test infrastructure. Never trust agent self-reported success.

## Benchmark Skepticism

| Benchmark | Limitation |
|-----------|-----------|
| **SWE-bench** | Contamination risk (training data includes GitHub issues); saturating |
| **τ-bench** | Narrow tool set; may not reflect production tools |
| **WebArena** | Environment drift (sites change); setup fragility |
| **OSWorld** | Heavy infrastructure; limited task diversity |
| **GAIA** | Broad but shallow; subjective grading |

> **RULE: Benchmarks are a sanity floor, NOT a release gate.** A 90% SWE-bench score does not mean the agent is safe for production. Your internal eval suite (grounded in YOUR tasks and failure modes) is the release gate. Public benchmarks tell you "the model isn't broken"; they cannot tell you "the agent is ready."

Risks: **contamination** (tasks leak into training data) and **saturation** (scores approach 100%). Refresh or retire benchmarks when either occurs.

## Judge-Swap Migration Procedure

When replacing one judge model with another:

1. **Re-baseline:** Run new judge on last 3 historical runs; record score deltas per task.
2. **Parallel-run:** Run BOTH judges for 2–4 weeks; track agreement rate.
3. **Document delta:** Publish the score offset (e.g., "New judge scores ~4 points lower on verbosity tasks").
4. **Non-comparability rule:** Scores from different judge models are NOT comparable without re-baselining.
5. **Retire old judge:** Only after parallel-run shows stable agreement (kappa > 0.75).

## Dataset Versioning and Contamination Control

| Control | Mechanism |
|---------|-----------|
| **Immutable versions** | Content hash (SHA-256) per version; never edit in place |
| **Refresh cadence** | Quarterly review; add from promote-back; retire stale cases |
| **Contamination detection** | Compare task embeddings against training corpora; flag >0.95 similarity |
| **Retirement rule** | If found in training data (or >20-point jump without code change), retire and replace |

## Worked Example: Eval Suite for a Support Agent

**Context:** Customer-support agent (refunds, lookups, escalations).

| Step | Result |
|------|--------|
| Define tasks | 90 total: 30 refund, 20 lookup, 15 escalation, 15 injection, 10 boundary |
| Class balance | 45 positive / 20 negative / 15 adversarial / 10 boundary |
| Golden trajectories | 60 reference executions (2 per refund task) |
| Judge setup | Pin: (claude-sonnet-4-20250514, rubric-v3, hash-a7f2c) |
| Baseline | Null agent: 8% → floor established |
| Run | N=7 trials, majority-vote → agent scores 74% |
| CI | Pre-merge: 15 tasks <3 min. Nightly: 90 × 7. Continuous: 2% sampling |
| Promote-back | Week 1: 5 prod failures → 4 promoted to regression (suite = 94) |

## Decision Table: Eval Design Choices

| Question | If YES | If NO |
|----------|--------|-------|
| Does the task have a deterministic correct answer? | Use reference-solution oracle | Use LLM judge with rubric |
| Is the path safety-critical or compliance-bound? | Grade trajectory + outcome | Grade outcome only |
| Can the user retry in production? | Report pass@k | Report pass^k |
| Is the task cost > $0.05/trial to grade? | Place in nightly tier | Place in pre-merge tier |
| Has the judge contract changed? | Run migration procedure | Scores are comparable |

## Exit Conditions

You are done applying this reference when:
- The eval suite has class balance including ≥20% negative/adversarial cases
- A judge contract tuple is pinned and recorded
- Null-agent floor is established and tasks discriminate above it
- Sampling (N≥5) with explicit aggregation is configured (no retry-until-green)
- CI tiers are assigned by cost budget (pre-merge < 5 min, nightly < 60 min)
- A promote-back loop cadence is scheduled (weekly or post-incident)

## Composition

- **Statistics, privacy, telemetry:** Paired comparisons, effect sizes, multiple-comparison correction, telemetry minimization, redaction, retention → [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md). This file adds only the QA operational playbook.
- **For pre-merge code verification against specs** (independent verification, gate artifacts, agent-test quality): see [ai-code-quality-gates.md](./ai-code-quality-gates.md).

---

*Sources: Anthropic, "Demystifying Evals for AI Agents" (anthropic.com/engineering, 2026); METR, "Recent Frontier Models Are Reward Hacking" (metr.org, 2025); Berkeley RDI, "How We Broke Top AI Agent Benchmarks" (rdi.berkeley.edu, 2025); Zheng et al., "Judging LLM-as-a-Judge" (NeurIPS, 2023); Wang et al., "Large Language Models are not Fair Evaluators" (arXiv:2305.17926); Jimenez et al., "SWE-bench" (ICLR, 2024); Yao et al., "WebArena" (ICLR, 2024); Mialon et al., "GAIA" (arXiv:2311.12983).*
