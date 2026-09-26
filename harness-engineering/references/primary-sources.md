# Primary-source index and claim boundaries

Checked 2026-09-26 during the deeper source review. Prefer these first-party
sources for the ideas below; recheck product/version semantics when implementing.
The course is a useful synthesis, not authority over every runtime.

| Source | Supported use | Do not infer |
|---|---|---|
| [OpenAI harness engineering](https://openai.com/index/harness-engineering/) | Case study of repository knowledge, executable invariants and feedback | All Codex use has identical worktrees/telemetry, or reported output size proves productivity |
| [Anthropic effective long-running harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Initializer/coding phases, incremental work and structured handoffs | JSON alone enforces transition integrity or one filename is mandatory |
| [Anthropic application harness design](https://www.anthropic.com/engineering/harness-design-long-running-apps) | Model-dependent context strategy, contracts, evaluator feedback | Separate evaluator guarantees truth; very different time/cost runs prove isolated causal effect |
| [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | JIT retrieval, compaction, notes, isolation tradeoffs | Universal context threshold or all claims about any vendor's internal implementation |
| [Anthropic tool engineering](https://www.anthropic.com/engineering/writing-tools-for-agents) | Clear affordances, bounded useful results, realistic task evaluation | Successful API call proves user outcome or toy tasks establish field quality |
| [Claude Code hooks](https://code.claude.com/docs/en/hooks) | Event-specific hook control and stop-loop protections | Universal hook schema/failure policy for other hosts |

## How to use evidence

Identify whether the source is a reported observation, public API contract,
implementation snapshot, or community interpretation. Pin code/version when
relying on internals. A supported design idea can be portable while the vendor's
exact event names, memory caps, command names, and precedence are not.

The application-harness article explicitly notes that model changes allowed
removing context resets from a prior design and that evaluator separation alone
did not eliminate leniency. This supports measured simplification and qualified
review evidence, not unconditional reset or independent-agent rules.

The hooks reference documents repeated-stop protection and an active-hook input.
For an adapter, test reentrancy and the installed runtime's exact stop behavior;
do not treat an example stop hook as a release gate.

No provider benchmarks, anonymous course anecdotes, generated rubric scores, or
community percentages are imported as evidence that this skill improves tasks.
Use the source coverage map and inventory for extraction provenance, then execute
representative tasks to establish effectiveness.
