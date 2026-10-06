# External Agent Handoff

Use with `ai-interaction-contract.md` and `task-flow-state-model.md` when the human delegates from an agent surface outside the product. Link each consequential field to approved evidence, a verified product capability, or an explicit unresolved decision. Do not fill unknowns with assumed integration behavior.

## Outcome and participants

- Human outcome and observable product-side completion evidence:
- Human goal owner and decision owner:
- Product account / organization / workspace:
- External agent host or client (verified name/version or unknown):
- Agent or integration principal authenticated to the product:
- Start surface and return surface(s):
- Supported connection or invocation path and evidence:
- Unverified identity or integration assumptions:

## Delegated authority

| Product target | Read / write / send / commit operation | Acting principal | Authority source | Scope boundary | Duration / revoke / re-check | Human decision required |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

Record which user-facing request is only intent and what the product accepts as authorization. Recheck authority after meaningful delay, target change, or permission change. Identify any operation that cannot be limited or revoked before allowing it.

## Cross-app flow and evidence

| Stage and surface | Actor | User-visible status | Context / data crossing boundary | Product-side evidence | Next action and return path |
|---|---|---|---|---|---|
| Delegate | Human in external agent host |  |  |  |  |
| Authenticate / connect |  |  |  |  |  |
| Preview or request input |  |  |  |  |  |
| Product action / commit |  |  |  |  |  |
| Reconcile and return |  |  |  |  |  |
| Inspect intended outcome | Human in product or agent host |  |  |  |  |

- Stable operation/task reference and freshness:
- Product object(s) and confirmed state:
- What the agent can report versus what the product can verify:
- Context the human may inspect, correct, or remove:
- Context intentionally not transferred and why:

## Human intervention and recovery

| Event | Where the person can act | Request/acknowledgment semantics | In-flight or completed effects | Preserved context | Safe next step |
|---|---|---|---|---|---|
| Correct scope or input |  |  |  |  |  |
| Pause or cancel |  |  |  |  |  |
| Revoke access / disconnect |  |  |  |  |  |
| Agent host closes / connection drops |  |  |  |  |  |
| Partial or unknown result |  |  |  |  |  |
| Resume / retry |  |  |  |  |  |
| Permission or ownership changes |  |  |  |  |  |
| Reference expires |  |  |  |  |  |

- Is cancellation confirmed by the product, or only requested?
- Which completed effects require compensation rather than cancellation?
- What prevents a retry from duplicating an effect, or what warning is shown?
- How can the person continue manually?
- Who owns unresolved protocol, security, support, or retention decisions?

## Acceptance evidence

| Scenario | Expected observable behavior | Evidence source / owner | Result or unresolved limitation |
|---|---|---|---|
| Correct human and integration principal; intended target |  |  |  |
| Agent identity differs from human account or is unavailable |  |  |  |
| Requested operation exceeds granted scope |  |  |  |
| Scope/target changes before commit |  |  |  |
| App switch, reconnect, or stale agent status |  |  |  |
| Cancel races with an external side effect |  |  |  |
| Partial completion followed by retry |  |  |  |
| Access revoked or task reference expires |  |  |  |

Do not mark the handoff complete until the intended user outcome has product-side evidence or the remaining owner and verification gate are explicit.
