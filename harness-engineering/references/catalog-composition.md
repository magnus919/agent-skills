# Catalog handoffs and return contracts

Load a specialist for an active concern; do not load the whole catalog. Harness
engineering keeps ownership of the harness question and consumes bounded outputs.
A specialist's pass applies only to its stated evidence boundary.

| Active decision | Specialist | Provide | Consume and return to harness workflow |
|---|---|---|---|
| Domain/system architecture | [software-architecture](../../software-architecture/SKILL.md) | Drivers, constraints, candidate runtime boundaries | Accepted boundaries/fitness scenarios → tools and environment design |
| One reproducible defect | [systematic-debugging](../../systematic-debugging/SKILL.md) | Trace, expected/actual, revision, reproduction | Supported root cause → smallest intervention |
| Acceptance and phase contracts | [spec-driven-development](../../spec-driven-development/SKILL.md) | Intended product outcome and uncertainty | Testable spec/tasks → initializer and completion gate |
| Test strategy, weak assertions | [qa-methodology](../../qa-methodology/SKILL.md) | Risks, real checks, near misses | Oracles/challenge tests → verifier contract |
| Evidence-backed completion | [verification-methodology](../../verification-methodology/SKILL.md) | Candidate and explicit criteria | Per-criterion verdicts → task termination; missing evidence stays incomplete |
| Agent task comparisons, graders, traces | [agent-evals-and-observability](../../agent-evals-and-observability/SKILL.md) | Baseline/candidate, task population, decision | Eval/evidence plan → experiment; judge scores do not grant authority |
| Authority/trust boundaries | [secure-software-engineering](../../secure-software-engineering/SKILL.md) | Tools, identities, resources, adversarial paths | Enforceable controls → action executor, denial/replay tests |
| Business authorization | [ai-governance](../../ai-governance/SKILL.md) | Use case, owners, consequential decisions | Human authority contract → limits/escalation; no self-authorization |
| Long-term operating value | [ai-operating-economics](../../ai-operating-economics/SKILL.md) | Accepted outcomes, full costs, countermetrics | Adopt/constrain/retire decision → harness maintenance |
| Runtime latency/cost bottleneck | [performance-optimization](../../performance-optimization/SKILL.md) | Journey/stage measurements | Controlled experiment → context/tool/loop simplification |
| System restore/failure exercise | [resilience-and-recovery](../../resilience-and-recovery/SKILL.md) | Partial effects, recovery goals, dependencies | Exercise-backed restoration plan → checkpoint/replay design |
| Agent SDK implementation | [langgraph](../../langgraph/SKILL.md), [pydanticai](../../pydanticai/SKILL.md), [autogen](../../autogen/SKILL.md) | Framework choice and runtime contracts | SDK-specific implementation → verify abstract behavior unchanged |
| LangChain orchestration with a typed System One decision | [langchain](../../langchain/SKILL.md) owns LangChain Runnable/tool integration; [system-one](../../system-one/SKILL.md) owns Choice/Score/Noul semantics, model limits, and calibration | Task boundary, trusted state, finite candidate source, action/authority contract, acceptance oracle | LangChain node returns a versioned typed response to deterministic policy; System One reviews question/model fit; Harness Engineering measures actual task outcome and sends failures or regressions back to the owner of the failing boundary |
| Collection and query tooling | [telemetry](../../telemetry/SKILL.md), [grafana](../../grafana/SKILL.md) | Approved minimal signals and access | Operational queries/panels → runtime diagnosis |
| Browser journey implementation | [playwright](../../playwright/SKILL.md) | User journey, fixtures, accepted visible/state outcomes | Actual interaction evidence → acceptance record |
| Deploy/rollback pipeline design | [release-engineering](../../release-engineering/SKILL.md) | Versioned artifacts, relevant gates, recovery | Release plan → boundary checks; does not grant deploy permission |
| Operate evaluated agent | [agent-production-operations](../../agent-production-operations/SKILL.md) | Evaluation/readiness, authority, version | Staged control plan → operating owner; do not keep redesigning harness |
| Authorized PR-through-merge delivery | [verified-delivery](../../verified-delivery/SKILL.md) | Explicit delivery authority and candidate | Live gate/post-merge evidence → requested delivery boundary |
| Skill packaging/loading | [agent-skills](../../agent-skills/SKILL.md) | Coherent workflow and resources | Valid format/discovery → installation behavior |
| Human/agent documentation | [technical-documentation](../../technical-documentation/SKILL.md) | Reader jobs, source owners, working commands | Discoverable docs → fresh-session test |

## Example round trip

A checkout action fails after an apparently green unit suite. Harness engineering
frames the expected journey and trace. systematic-debugging identifies the first
failing API/storage contract. qa-methodology supplies a near-miss integration
case. The implementation specialist repairs the responsible layer.
verification-methodology returns criterion verdicts bound to the candidate. The
harness updates durable evidence and termination policy without claiming that an
isolated test proves deployment. Only an explicit delivery directive invokes
verified-delivery.

For a LangChain application that uses System One to select a candidate, the
harness first defines the real task outcome, finite candidate source, and
deterministic action boundary. System One reviews whether the trusted state and
typed question express the intended judgment and how that model is evaluated.
The LangChain skill implements the framework adapter and preserves the response
contract; it does not redefine model semantics. Harness Engineering then checks
freshness, policy gates, action effects, and the user outcome. Send model-level
misjudgments or calibration questions to System One; send adapter defects to
LangChain; send end-to-end failures back through harness diagnosis. See
[System One decision placement](system-one-decisions.md) and the
[round-trip examples](system-one-examples.md).

## Boundary conflicts

When specialists disagree, reconcile artifact revision, criteria, source fidelity,
and scope before aggregating verdicts. A security denial or missing required
acceptance cannot be outvoted by several positive model reviews. Broader activity
requires an owner decision, not a graph node creating new authority.
