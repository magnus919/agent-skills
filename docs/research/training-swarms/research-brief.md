# What Training Swarms contributes to multi-agent coordination

**Research question.** Which findings from Hugging Face’s *Training Swarms* and the research it cites would improve the existing skill?

**Scope.** Source review and catalog comparison, 2026-11-28. See the [research log](research-log.md) for source-level evidence, access dates and exclusions.

## Recommendation

Make the coordination experiment distinguish **information that must be combined** from **work that independent agents can each complete**. The skill already asks for a single-agent or sequential baseline, matched resources and accepted integrated outcomes. The addition is to make an independent team baseline and a communication control explicit wherever a claimed improvement could come from getting more tries. On work that requires combining private facts, use the no-sharing condition to check whether the information is necessary, and use a simple authorized collector or fixed handoff as the practical baseline. [Hugging Face experiment](https://huggingface.co/blog/training-swarms#our-first-experiment-four-agents-ordering-numbers) · [s³, §4–5](https://arxiv.org/html/2611.08615v1)

| Priority | Improvement | Fit with the catalog |
| --- | --- | --- |
| 1 | **Isolate the value of communication.** On solo-solvable tasks, compare a strong single agent, independent attempts and the communicating team. Fix the eligible search surface, task roster, model and resource allowance. Count selection and integration. Where useful, remove sharing from the same harness to measure dependence on that channel. | [Evaluation](../../../multi-agent-coordination/references/evaluation.md) and its [experiment template](../../../multi-agent-coordination/templates/coordination-experiment.md). Put the short task-class decision in [decomposition and topology](../../../multi-agent-coordination/references/decomposition-and-topology.md). |
| 2 | **Compare what changed after sharing.** For aggregation, check distinct-source coverage, delivery, use and correct synthesis. For exploration, check a selected or redirected branch, verified intermediate progress, and avoidable overlap. Preserve useful replication and shared prerequisites. For either, measure total cost and recipient overhead alongside final acceptance. | The [message contract](../../../multi-agent-coordination/references/communication-and-context.md) already distinguishes delivery from adoption. Add concrete diagnostic measurements to the evaluation reference and template. |
| 3 | **Score the integrated outcome and test isolation.** Use one accepted outcome per task, track component defects and conduct independently, and check the independent arm’s actual resource isolation with a benign challenge. | Keep the [existing authority split](../../../multi-agent-coordination/references/authority-and-recovery.md). Coordination defines the experimental obligation. Harness and evaluation owners implement and verify enforcement. |

## What the results establish

Hugging Face reports 26/32 held-out solves after 75 updates. The 37.4% generated-token decrease compares training windows, and held-out token-efficiency measurements were unavailable. Broadcasts increased while generation fell. That makes message count a poor proxy for cost. Since the private numbers were withheld from solo agents, this setup cannot answer whether communication beats a strong single agent given the same usable information or an independent team on a solo-solvable task. [Hugging Face results and comparison limits](https://huggingface.co/blog/training-swarms#our-results)

The cited s³ preprint supplies a more discriminating experiment. At four agents, the communication-disabled exploration arm lost 19 percentage points, while the difference versus solo-trained best-of-four did not survive multiple-comparison correction. At six agents, the communicating team beat best-of-six by about seven points after correction. The paper covers two synthetic tasks, small shared-policy models and one training run per condition. Those results justify designing the controls and reporting the arms separately. They provide no dependable team-size or effect-size target for the catalog. [s³, §5 and §7](https://arxiv.org/html/2611.08615v1)

The paper’s cited test-time communication study supplies a useful check with model weights held fixed. Sharing checkable intermediate progress helped on selected search tasks given sufficient per-agent resources. The benefit disappeared in lower-budget conditions, and communicating pairs trailed independent pass@2 in its limited Terminal-Bench comparison. Anthropic’s cases independently illustrate scope confounding and how visible collaboration can coexist with weak integration. A useful hypothesis is that communication pays when peers can act on fresh, verified information early enough to change their work. [Park et al., §3–4](https://arxiv.org/html/2609.21032) · [Anthropic’s multi-agent experiments](https://www.anthropic.com/research/multiagent-systems)

Confidence is high in the experimental-design recommendation, moderate in the proposed diagnostics as useful mechanism checks, and low in any expected gain for heterogeneous production teams. The paper’s shared reward motivates task-level scoring, with a guard against proxy incentives such as rewarding messages or workers spawned. Kimi's orchestrator-only training shows why a catalog experiment should record which policy, prompt or routing layer changed. Reinforcement learning is optional research background for this skill. [s³ reward ablations](https://arxiv.org/html/2611.08615v1) · [Kimi K2.5](https://www.kimi.com/en/blog/kimi-k2-5#2-agent-swarm)

## Open questions

- On a representative task, does sharing improve acceptance over independent attempts after charging recipient context, selector, integration and review?
- Can an authorized deterministic collector handle the private-information fixture within the required scope and latency?
- At what per-agent allowance does the communicating configuration stop paying for itself, and which gains survive new tasks or heterogeneous workers?

The [catalog application](catalog-application.md) records the experiment design and the challenges for the two added eval cases. The [research log](research-log.md) preserves source claims, caveats and exclusions. This assessment did not run the published benchmarks or measure an effect on the local skill.
