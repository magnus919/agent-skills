# Typed decisions inside a harness

Use this reference when a harness may call a bounded decision model to select a
skill, tool, action, route, or candidate. It covers where the decision belongs
and what evidence the harness must supply and verify. It does not replace the
[System One model contract, calibration, and integration guidance](../../system-one/SKILL.md).

Evidence review date: 26 September 2026. Recent research window: 12–26 September
2026. This is a targeted primary-source review, not a systematic survey.

## Evidence labels and scope

Treat these as tested patterns for the cited configuration, not a universal
standard. Mark claims in design and review records with one of these labels:

- **Measured** — a retained comparison or dataset was inspected/recomputed;
  report its task, model, input, candidate set, and limits.
- **Implemented** — source code exposes a concrete control or data path; this
  shows implementation, not that it improves accepted task outcomes.
- **Reported** — a first-party account reports a small trial or observation
  without enough retained evidence for independent confirmation.
- **Proposed** — a design to evaluate on the target workload, not established
  effectiveness.

The evidence review is a targeted primary-source read, not an exhaustive review
or independent reproduction of live provider calls. See the source links below
and the sibling [round-trip examples](system-one-examples.md).

## Harness decisions to preserve

1. **Compile a finite offer from current state.** Give a selector real candidate
   identifiers from the active tool, skill, or UI inventory. Bind each result to
   the inventory revision and candidate IDs used for that request. Re-read or
   reject the result if the state, inventory, goal, or policy revision changed
   before execution. Never turn a model response into a newly invented command,
   coordinate, or resource identifier.
2. **Ask applicability separately from relative preference.** A ranking over
   supplied candidates always has a winner, even when every item is irrelevant
   or unsafe. Define an explicit applicable / none-applicable / insufficient-
   evidence question or deterministic eligibility gate, then rank only eligible
   options. Test false applicability and omitted-candidate cases; do not infer
   applicability from the top score. The TypeSafe skill-suggestion cookbook
   demonstrates shortlist-then-inspect as a vendor proposal; it is not a
   catalog-wide result.
3. **Match question and state to the target decision.** Write down the decision
   target, available deployment alternatives, action consequences, and evidence
   at decision time. Ensure the question asks about that target using state that
   actually contains the relevant history, outcomes, and candidate set. A
   benchmark's label may encode a different decision from the production choice.
4. **Keep selection separate from execution and completion.** Validate typed
   IDs, response shape, freshness, and policy in ordinary code. Execute only the
   authorized candidate. Capture the before/after effect and verify success at
   the user-visible or durable-state boundary with an independent observable
   check. A valid response or `DONE` answer does not prove the action worked.
5. **Define every outcome lane before rollout.** Specify the behavior for
   selected, no applicable candidate, ambiguous/low-evidence, stale state,
   malformed response, provider failure/timeout, policy denial, action failure,
   and unknown effect. Unknown remains incomplete and goes to a named retry,
   review, or defer path; it does not fall through to a permissive default.
   Record the exact question/config/model version and actual task outcome.
6. **Evaluate the whole path.** On frozen comparable tasks, measure candidate
   recall/coverage, selection errors, false applicability, stale-result rejects,
   action effects, accepted outcomes, false stops, recoveries, human
   intervention, failure lanes, latency, and cost. Keep model-level judgment
   calibration under System One ownership and end-to-end journey/outcome,
   trajectory, side effects, and cost/latency under
   [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md).
   Do not transfer thresholds or gains to another model, workload, state format,
   or candidate set without a new evaluation.

Use [decision placement](../templates/decision-placement.md) to capture the
boundary and evidence before implementation. For a LangChain integration, route
adapter details to [LangChain](../../langchain/SKILL.md), typed model semantics
to [System One](../../system-one/SKILL.md), and return actual task outcomes to
this harness workflow.

## Evidence ledger

| Evidence | Label | What it supports | Limits |
|---|---|---|---|
| [Jev harness lab](https://github.com/Aitejiu/jev-harness-lab), inspected report, retained rows, and request builders; reviewed at commit `29ddf8210e3a96f9d383e9b479e3e5c39455c394` | **Measured** | On published RouterBench rows, recomputed accuracy at threshold 0.5 is 51.27% against a 50.91% majority baseline. On Who&When rows, recomputed pairwise AUROC is 0.56016. These results caution against generic prompt-only difficulty routing and isolated-step failure attribution with the supplied state. | Arithmetic on published rows does not authenticate API provenance, labels, omitted failures, or live inference. In RouterBench, the label asks whether the oracle lies outside the cheap-model set, while the Jev question asks generic model difficulty; that mismatch weakens transfer to deployment routing. Who&When asks about later correction/final failure but supplies a truncated single step without the necessary trajectory/outcome. These negatives do not rule out better aligned questions. |
| [Browser Use Jev performance report](https://github.com/browser-use/jev-ultrafast/blob/1231850a0bf1a0c0341fe408ef1668dbbfdfac46/docs/performance.md), pinned at the reported source revision | **Measured / implemented** | The report retains six alternating attempts on one Google Flights task, with independent result checks; indexed controls, target/context guards, event waits, and effect-aware retry handling are visible in implementation. Three matched pairs favored the optimized version; median time was reported 25% lower. | Three pairs on one live task are a local runtime observation, not evidence that Jev beats an LLM or that broader task success/reliability improves. The timed boundary excludes initial navigation and independent post-run verification. |
| [Veso desktop harness report](https://veso.ai/blog/a-harness-for-a-model-that-only-chooses/), published 22 September 2026 | **Reported / implemented** | Its finite action offer, separate feasibility and relative-choice questions, effect observation, and code-checked pane arrival address concrete failures in that harness. The report describes a 4/8 to 7/8 change across eight Mac settings goals after adding a small navigation map. | A first-party, small developer trial is not an independent replication; thresholds, candidate counts, and effect sizes are specific to this system. |
| [SystemOneHarness](https://github.com/HarnessRouter/SystemOneHarness), project docs and benchmark rows inspected at review time | **Implemented / measured** | The code documents finite action compilation, explicit terminal reasons, versioned config, and escalation handoffs. Its published measurements show five runs on each of three small deterministic scenarios. | Those runs show that this configuration completed these scenarios, not protocol-to-task correctness generally, cross-model parity, or broad reliability. |
| [TypeSafe skill-suggestion cookbook](https://docs.typesafe.ai/cookbooks/skill_suggestion) | **Proposed / vendor-reported** | Two-stage shortlist then instruction inspection and a no-match lane are integration patterns to test. It keeps selection suggestion separate from the agent actually loading a skill. | Vendor results on one roster and agent do not establish a catalog-wide guarantee. |
| [Weave router field report](https://weaveos.com/blog/why-you-shouldnt-use-jev-for-coding-agents-and-routing) | **Reported** | The account suggests trajectory features may matter more than classifier architecture for its routing design. | Cohort, labels, splits, and artifacts are not published sufficiently for independent verification or causal transfer. |

Related constraints matter when adding judges or pruning context. The
[rubric-judge study](https://arxiv.org/html/2609.29769v1) reports correlated
confident errors between cheaper and stronger judges; replay estimates do not
establish live cascade benefit. Measure rescue and regression on labeled target
tasks, following System One's [rubric-judge](../../system-one/references/rubric-judge-research.md)
and [cascade-economics](../../system-one/references/cascade-economics.md)
references. The [scientific-decisions study](https://arxiv.org/html/2609.24965v1)
shows that correct final labels can conceal wrong intermediate quantities; its
small repeated cases motivate scoring intermediate and downstream evidence, not
broad claims of scientific competence. The [fast Jev compaction implementation](https://github.com/tamaratran/fast-jev-compaction)
and [Pi adaptation](https://github.com/QuentinDanblon/pi-fast-jev-compaction)
preserve retained messages verbatim and pair tool calls with results, but pruning
still removes evidence and no held-out end-to-end task-success comparison was
found in the reviewed material. Treat each as an implementation constraint or
test proposal, not proven general efficacy.

The two negative lab findings are especially useful as challenge cases, not as a
reason to ban routing or diagnosis. Avoid claiming that apparent prompt difficulty
alone reliably selects model class, or that an isolated step identifies the
trajectory's eventual cause. A proposed richer-state router or diagnosis model
still needs task-aligned labels, held-out evaluation, and the actual execution
outcomes.

## Source ownership

- **System One** owns typed question and answer semantics, model-specific
  capabilities, calibration, and model-level latency. Read its matching model
  and calibration references rather than restating their manuals here.
- **Harness Engineering** owns candidate enumeration, applicability inputs,
  current-state/freshness binding, deterministic policy, authorization,
  execution, effect observation, independent completion evidence, and
  end-to-end task comparison.
- **Framework skills** own their adapter and orchestration details: [LangChain](../../langchain/SKILL.md), [LangGraph](../../langgraph/SKILL.md), and [PydanticAI](../../pydanticai/SKILL.md). Preserve the versioned decision contract across each framework; its convenience does not validate model semantics or task success.

Return model-level errors to System One, framework adapter defects to LangChain,
and journey/side-effect/freshness failures to the harness owner. Recombine the
evidence before claiming the application works.
