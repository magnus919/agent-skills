# Development and architecture

## Authoring surface

Eve discovers conventional files below `agent/` and compiles a manifest for the runtime. The files are the agent’s operational surface:

| Path | Responsibility |
|---|---|
| `instructions.md` | Always-on system instructions |
| `agent.ts` | Model and runtime configuration |
| `tools/*.ts` | Typed model-callable actions; filename becomes tool name |
| `skills/` | Larger on-demand procedures and reference material |
| `subagents/` | Child agents with fresh state and their own configuration |
| `channels/` | HTTP, Slack, and other platform entry points |
| `connections/` | Typed external integrations and credential mediation |
| `sandbox/` | Isolated filesystem and command-execution configuration |
| `instrumentation.ts` | OpenTelemetry setup run at server startup |
| `schedules/` | Recurring work |

Keep a capability in the smallest suitable boundary. A one-off action belongs in a tool. A reusable procedure belongs in a skill. Work with a fresh conversation, a narrower tool set, or potentially noisy intermediate state belongs in a subagent.

## Sessions and durability

A session is a durable conversation or task. Each message or external event creates a turn. On Vercel, Workflows persists an event log and replays it to reconstruct state across cold starts, deploys, and pauses.

Do not infer application-level correctness from framework durability. External side effects must still be idempotent or guarded by a durable approval/receipt boundary. Decide what an interrupted tool call means before the agent can execute it twice.

## Models and credentials

A string `model` ID is AI-Gateway-routed. On Vercel, project OIDC can authenticate this path. Outside Vercel, use `AI_GATEWAY_API_KEY` if Gateway routing is desired.

To avoid Gateway routing, install an AI SDK provider package and pass its model object, then use the provider’s normal environment credential. Keep that credential in the host environment or a secret manager, never in an agent file.

## Tools, connections, and sandboxes

A tool should make its input and side effects precise. Validate schema input at the tool boundary. Treat free-form shell, file mutation, outbound network access, and credential-bearing integrations as separate high-risk capabilities.

Connections keep provider configuration and credentials outside prompts and generic tool implementation. Sandboxes constrain locally generated commands, but they do not repair an over-broad network policy or a secret injected into the sandbox. Choose the sandbox backend and policy before exposing tools that can execute commands.

## Observability

Vercel Agent Runs supplies a managed session and turn view. For portability, configure `agent/instrumentation.ts` to export AI SDK OpenTelemetry spans to the organization’s chosen backend.

Trace capture can include message input, model output, tool arguments, and tool results. Use `recordInputs` and `recordOutputs` deliberately. Sensitive-data minimization is a configuration and policy decision, not an observability afterthought.
