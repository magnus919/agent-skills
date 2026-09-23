# Performance optimization skill: evidence-led improvement plan

Status: plan only. Base: upstream `main` at `43b93284c0bc36db3aec60810f381dfeb0bab774`, the merge of PR #563. The execution branch must be refreshed against upstream `main` before implementation starts.

## Objective and boundary

Make `performance-optimization` reliably help an agent move from an observed slow user journey to a measured, reviewable experiment and an honest decision about field impact. Keep it a cross-stack methodology skill. Frontend, backend, telemetry, capacity, and release skills retain their tool-specific responsibilities. Do not add a benchmark runner or a mandatory statistical threshold merely to make the skill look comprehensive.

Known gaps: no demonstrated improvement over a no-skill agent; no complete worked investigation; weak guidance for choosing the next diagnostic signal; underspecified variance, proxy, and field-decision rules. The current six `evals/evals.json` cases are a structural contract. PR CI's fake paired-eval smoke is not behavioral evidence; model and Jev jobs were skipped on that PR.

## Execution roles and workspaces

I own the plan, task boundaries, review of raw evidence, integration, and go/stop judgments. Execution is delegated to **Luna-pinned sub-agents** (`gpt-6-luna`), each given a bounded deliverable and a separate worktree or branch based on a freshly fetched upstream `main`. No two agents edit the same file concurrently. Agents return evidence and a diff; I decide whether it enters the integration branch. Use at most three Luna agents at once, keeping one slot for orchestration.

| Agent | Bounded assignment | Initial output |
|---|---|---|
| Luna A: evaluation | Build a small, source-backed task set and trigger probes; run clean-context, paired with-skill/no-skill trials with a real agent harness when available. Preserve prompts, model/harness version, outputs, time/tokens, and execution traces. | Baseline evidence packet and independently reviewable rubric; no skill edits. |
| Luna B: diagnostic workflow | From baseline failures, draft a symptom-to-signal decision guide and one complete, reproducible worked example on a non-production fixture. Route named tool operations to existing specialist skills. | Reference/example diff plus raw measurements or explicit fixture limitations. |
| Luna C: experiment decisions | From baseline failures and primary sources, draft precise rules for noisy comparisons, proxy calibration, field verification, and performance ratchets. | Reference/template diff with source notes and challenge examples. |

Luna A does not grade its own prose by assertion presence. I review semantic outcomes as `met`, `not_met`, or `not_shown` from the response and artifact, and retain near misses. Jev may provide advisory triage only; it cannot certify passes or approve a release.

## Sequence and gates

### 1. Establish a behavioral baseline before editing the skill

- Freeze the merged skill version and current six case IDs. Add a small separate trigger set: at least three should-trigger requests and two near misses (incident/SLO policy and named-tool operation). Do not mix trigger probes into `evals/evals.json`.
- Select **two representative end-to-end tasks** for the first screen: one user-visible client journey with incomplete field telemetry, and one service hot path with a profile and noisy benchmark data. Include realistic code/data fixtures or sanitized artifacts and a correctness requirement. Record exactly which boundaries can be executed locally and which require a deployment that is unavailable.
- Run each task in clean contexts with the same model/harness, once with the skill and once without it. Verify activation and keep raw outputs, commands, fixture versions, and provenance. `python3 -m eval_runner.paired --adapter fake` only checks harness mechanics; use a real CLI or configured model adapter for behavioral comparison. If no real harness can be run, stop at a documented evidence gap rather than calling the baseline complete.
- Judge whether the skill changes: measurement choice, actual instrumentation/profiling, benchmark fidelity, experiment validity, correctness/countermetrics, and honest field claims. Record misses and unnecessary work, including duration and token cost. Keep the human/domain judgment separate from deterministic checks.

**Gate:** Proceed to broad revisions only if the first two tasks expose concrete, repeatable failures or there is a clearly demonstrated missing capability. If the skill already handles a task, preserve that behavior. Do not expand the task set simply to find a failing example.

### 2. Improve the method where the baseline fails

- Add a concise diagnostic decision guide: critical path first; CPU versus off-CPU wait; allocation/GC; lock contention; storage/query; network/queue; and client render/layout. For each branch give the discriminating observation, suitable signal, likely confounder, and when to route to a specialist. Avoid a catalog of vendor commands in the core skill.
- Create one complete example that begins with a reported user delay, defines start/end events, checks missingness, captures a baseline, profiles the representative slow slice, runs one reversible change with correctness checks, compares raw baseline/candidate measurements, and reaches a supported/unsupported/inconclusive decision. Show an unavailable field read as pending, never as a win. Include commands and fixed fixture identity only where they are reproducible.
- Tighten decision guidance: predeclare the minimum practical gain and countermetrics; use repeated/interleaved runs when host drift matters; use an A/A or other stability check before a strict ratchet; include failed/time-out attempts and materially different user slices. Treat confidence methods as tools chosen for the data, not a universal sample-size or p-value recipe.
- Replace the current “two representative changes or cases” proxy shortcut with a calibration protocol: specify intended workload domain; test both improvements and plausible regressions; compare the proxy against wall time and user outcome; inspect exceptions and countermetrics; retain it as diagnostic only when prediction is weak. Require a documented stable fixture and explicit threshold-refresh process for a CI gate.
- Update `SKILL.md`, README, references, template, and existing eval assertions only where behavior changes. Preserve stable eval IDs; add a new case only for a newly distinct failure mode. Record material rubric edits with before/after challenge examples.

**Gate:** I review each agent's evidence and diff. Reject material that is merely more prose, tool-specific sprawl, an uncalibrated numerical gate, or a claim unsupported by the worked example.

### 3. Run a held-out comparison and decide whether to ship

- Re-run the two baseline tasks with the candidate skill and compare to the frozen merged version as well as no skill. Add a small held-out task only for a failure mode uncovered during the first screen; keep its rubric hidden from the authoring agent until outputs are captured.
- Independently inspect actual outputs and artifacts. Require improved behavior on the predeclared failures, no material regressions in correctness, authority, or routing, and a clear distinction among local, staging, and field evidence. Report inconclusive comparisons as inconclusive. If the candidate only grows token/time cost without a material behavior gain, narrow or reject it.
- Run repository gates: `ruby scripts/validate-skills.rb`, `ruby scripts/validate-skill-quality.rb --base origin/main`, `python3 scripts/test-eval-validation.py`, `python3 scripts/validate-evals.py`, `python3 scripts/eval-coverage.py --modified-from origin/main`, `python3 scripts/check-skill-tests.py --check`, generated-catalog checks, and `git diff --check`. Run a script's focused tests if executable code is added. Open a focused review PR and verify required CI on its current head.

**Stop rule:** One representative two-task screen, one evidence-led revision pass, and one held-out comparison. If those do not converge, stop, publish the raw findings and specific unresolved question, and seek a human decision before further expansion. Do not promote advisory semantic grading or a proxy metric into a required release gate without independently labeled real outputs and a versioned gate contract.

## Expected review packet

The execution PR should link a baseline-versus-candidate table, raw run artifacts, the worked example, changed rubrics and challenge cases, validator results, and any unresolved field-verification boundary. “World-class” remains a hypothesis until the skill consistently helps on real optimization tasks across more than this first screen; this plan tests whether the next revision is materially better, not whether every stack is covered.
