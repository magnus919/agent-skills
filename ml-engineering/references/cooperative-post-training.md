# Choose which policy to train in a multi-agent system

Start with observed failures on checked tasks. Compare a fixed-policy prompt or
harness change before budgeting training. Use the [specialization study](../templates/specialization-study.md)
to freeze the comparison and the [coordination experiment](../../multi-agent-coordination/templates/coordination-experiment.md)
to test whether sharing improves accepted outcomes under the serving budget.

| Observed failure | Candidate intervention | Control that tests the hypothesis |
| --- | --- | --- |
| Workers can execute suitable assignments, but decomposition, dispatch, or synthesis fails | Train the orchestrator. Pin worker policies and interfaces across the baseline and candidate. | Fixed orchestrator with the same workers, tools, and task information. Consider a prompt or harness repair with the same worker policies. |
| Workers must learn when to share, read, or act on peer findings | Train a common worker policy with separate context for each logical agent. Use a team reward where useful contributions primarily benefit peers. | Evaluate the starting checkpoint with the same messaging interface. Compare team versus individual reward with comparable rollout budgets if the incentive is the hypothesis. |

For a shared policy, define the team episode, the independently verifiable
accepted outcome, and which generated actions receive the learning signal. A team
reward can reinforce useful contributions from agents whose own answer was wrong.
It leaves individual credit unresolved. Inspect traces for missing contributions,
unused evidence, and redundant work. If success earns an efficiency bonus,
preserve the ordering that a valid success outranks an early failure. Keep
access and conduct requirements as independent acceptance constraints.

## Compare training and serving separately

- Freeze the task splits, verifier, policy and harness revisions, and checkpoint
  selection before inspecting held-out outcomes. Record updates, rollout count
  and unit (individual or team episode), generated tokens, and training compute.
- On the same held-out tasks, compare accepted outcomes at matched serving
  allowances. For solo-solvable tasks, include independent best-of-N with a
  deployable selector where feasible. For distributed facts, compare with an
  authorized collector. Label same-checkpoint channel ablations separately from
  controls that were trained independently.
- Report actual serving use including failures, received context and selection
  overhead. If claiming speed or savings, measure end-to-end elapsed time and cost
  as well as generated tokens. Keep learning curves and held-out measurements distinct.

## Evidence and transfer limits

[Kimi K2.5 §3](https://arxiv.org/html/2602.02276v1#S3) describes a trainable
orchestrator with frozen workers. [s³ §§3–5](https://arxiv.org/html/2611.08615v1#S3)
trains one shared worker policy from team episodes. In its private-fact task,
individual rewards discourage sharing. On its solo-solvable exploration task,
the individual-reward control performs comparably to the team-reward arm.
These studies illustrate different training targets and do not rank them
head-to-head. Hugging Face's [worked aggregation example](https://huggingface.co/blog/training-swarms#our-results)
reports held-out success, but its 37.4% reduction in generated tokens comes from
training windows. Measure held-out efficiency on the intended workload.
