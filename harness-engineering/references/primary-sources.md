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

## Tool discovery and large results

Checked 2026-10-04. These sources support implementation mechanisms and protocol
shapes; they do not establish that the same approach improves another runtime.

| Source | Supported use | Do not infer |
|---|---|---|
| [Anthropic tool search](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) | On-demand matching/loading for large tool catalogs; returned tool definitions and empty-match behavior | A need for dynamic search in a small stable catalog, or reliable task matching without task-based evaluation |
| [Anthropic programmatic tool calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling) | Product-specific flow that calls tools from code and filters/processes intermediate results before the model receives final output | That all code execution environments can call MCP tools, or that benchmarks establish this harness's behavioral uplift |
| [Anthropic code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) | Vendor design example for calling MCP tools through code and keeping intermediate results out of model context | A universal implementation recipe; code-mediated calls still require sandboxing, resource limits, authorization and failure handling |
| [Anthropic MCP connector](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector) | One product-specific integration path for remote MCP tool calls and per-tool configuration | Full MCP feature support, local stdio support, or cross-provider semantics |
| [MCP tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) | Tool listing and pagination, input/output schemas, structured content, resource links, and annotations | Runtime authorization, durable artifact retention, cross-source identity resolution, or task dependency planning |
| [MCP resources](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) | Resource reads, resource templates, and resource-link metadata | That every client displays, persists, authorizes, or can recover every resource link identically |
| [MCP security best practices](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) | Security considerations for MCP implementations | That a model-facing description enforces the corresponding boundary |

The conference mockup bug-fix demonstration and stated product experiences are
orientation for these questions only. Vendor-reported early comparisons are not
treated as independently validated efficacy evidence. Keep task selection,
authorization, identity semantics, result completeness, and retention grounded in
the target system's real contracts and tests.
