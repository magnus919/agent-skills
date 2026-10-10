# Fair six-skill evaluation pilot

[`fair-skill-evaluation-pilot-v1.json`](fair-skill-evaluation-pilot-v1.json) tracks six representative cases, the historical candidate and baseline snapshots, independent source pins, oracle scope, and mutation targets. `inventory_present` remains distinct from `behavior_verified`; the pilot is still `plan_only` and has made no generation or Jev calls.

The primary comparison is `pinned_skill_vs_skill` with `complete_package`. Both skill roots must be clean Git snapshots at the declared full revisions. The paired runner verifies both snapshot identities, resolves each arm's references only from that arm, and preflights both context hashes before the first adapter call. The candidate and historical source maps cover all six case IDs:

- [`fair-skill-evaluation-candidate-references-v1.json`](fair-skill-evaluation-candidate-references-v1.json)
- [`fair-skill-evaluation-baseline-references-v1.json`](fair-skill-evaluation-baseline-references-v1.json)

Pass both maps with `--candidate-reference-map` and `--baseline-reference-map`. A map may contain other pilot case IDs when running one selected case; each selected candidate case must have an entry. A reference path and hash must match bytes in that arm's pinned snapshot. The paired runner also checks both maps and the revisions against the v2 evidence contract. It never copies a candidate reference into the historical arm. `instruction_only` remains a separate diagnostic; `skill_vs_no_skill` is not the primary comparison.

The optional pilot evidence contract is [`eval_runner/fair-pilot-evidence-contracts-v2.json`](../eval_runner/fair-pilot-evidence-contracts-v2.json). For each case it binds the task-prompt hash, both revisions, each arm's reference hashes, expected outcomes, prohibited behavior, required evidence, and source-grounded review criteria. It keeps judging data out of generation inputs. UX, PydanticAI, product-discovery, and System One remain conceptual prose cases requiring independent review; their criteria are not execution or usability oracles. Raleigh retains its offline command and query-shape tests. The policy recipe has an independent clause-transcribed fixture; its synthetic clauses are not policy-owner-approved fidelity evidence.

Run the production-shaped policy CLI oracle and bounded mutation suite offline:

```sh
python3 -m eval_runner.fair_pilot_mutations --json
python3 -m pytest eval_runner/tests/test_fair_pilot_increment_three.py eval_runner/tests/test_fair_pairing.py eval_runner/tests/test_evidence_contract.py
```

The suite sends eight production-shaped JSON inputs through `spec-driven-development/scripts/business_policy.py`. It separately reports valid behavioral defects (four killed), an equivalent comparison (accepted), a deliberately unmatched/invalid mutation, a controlled runtime/infrastructure error, and checks still requiring conceptual review. Gap and overlap cases exercise the evaluator with custom version intervals. Passing this harness demonstrates only that these specific oracle fixtures distinguish those mutations; it does not establish policy correctness.

[`fair-skill-evaluation-qualification-v1.json`](fair-skill-evaluation-qualification-v1.json) freezes 12 proposed Jev request cases: six development and six held-out. It includes positive, negative, contradictory, missing-evidence, and paraphrase-invariance examples; response, prompt, and source hashes; source facts; and proposed labels with rationales. Three are bounded excerpts from prior generated outputs and nine are authored controls. The excerpts retain their original artifact hashes, while the submitted excerpt has its own hash. Authored controls are not production outputs. Every proposed label is marked `pending_independent_agent_review`; none is human validation or calibrated ground truth.

Preflight the exact request bodies without sending them:

```sh
python3 -m eval_runner.fair_pilot_qualification --json
```

The report should show 12 request-level payloads, exact payload and question hashes, the six/six split, pinned context, and `dispatch_authorized: false`. The initial request cap is 12; a further 12 attempts are reserved for diagnosed follow-up and require a separate parent allocation. The shared cap remains 100, current usage is zero, and no provider or Jev request is made by these commands. Do not tune against held-out cases.

## Staged ledger

- **Completed in this increment:** six-case candidate and historical source maps; v2 arm evidence contracts and review criteria; candidate-map support and preflight; clause-transcribed policy fixtures; a bounded code mutation report; frozen Jev request dossier and offline payload preflight.
- **Next, before any Jev request:** independent agent review of labels and code/payload validity; correct any findings; obtain explicit allocation for at most 12 initial requests. Keep a separate 12-attempt reserve for a diagnosed follow-up. No human validation has occurred.
- **Still needed for fair comparison:** explicitly authorized candidate and historical baseline generation on identical task/wrapper settings, with exact per-arm revisions and references; preserve partial infrastructure failures; then independently review actual output artifacts. Synthetic fixtures and old `model_teacher` labels cannot show improvement.
- **Migration/backlog:** identify which skills merit migration only after this representative comparison; track case-level defects, evidence gaps, and owner separately. Do not create a broad agentic-apps or policy-to-code skill from this pilot.
- **CI rollout:** remains out of scope until independent held-out review, error/abstention analysis, repeatability, and a versioned release-gate contract justify it. The existing grader and Jev remain advisory; this increment does not declare the full refit complete.
