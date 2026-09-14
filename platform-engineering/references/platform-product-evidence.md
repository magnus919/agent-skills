# Platform product evidence

Use this reference when deciding whether to start or expand an internal platform, shaping its first valuable slice, or reviewing whether it creates measurable value.

## Applicability and intake

Frame the opportunity before selecting tools:

1. Name the strategic software outcome and the internal teams who need it. If custom software is not material to the organization’s success, record why a platform still has a credible efficiency, security, or governance return.
2. Gather evidence of friction: queue time, repeated manual work, failure/rework, cognitive load, incident recovery, or duplicated cloud and staffing cost. Separate observed measurements from stakeholder assertions.
3. Identify the highest-frequency workflow and its grain (for example, “new service to first production deployment”). Define the minimum valuable slice, early adopters, dependencies, and an explicit escape hatch.
4. Name a technical product owner and the platform domain owners. Each owner needs a backlog, decision rights, customer feedback channel, service interface, and response responsibility.
5. State adoption, time-to-value, reliability, security, and cost hypotheses with a baseline, target, measurement window, and stop/escalation rule. Do not claim success from delivery of platform components alone.

Stop or reshape the investment when the internal-user population is too small, the workflow is not strategically important, the measured friction is trivial, or early adopters do not use the slice after a reasonable enablement pass. Preserve the evidence and the reason; a stopped platform experiment is a valid outcome.

## Outcome and self-service contracts

For every dependency owned by another team, capture either a self-service API or a testable outcome contract. A contract should state:

| Field | Required question |
|---|---|
| Consumer and owner | Who invokes it, who maintains it, and who responds to failure? |
| Outcome | What observable result is guaranteed? |
| Inputs and authorization | Which fields, identities, scopes, and quotas are accepted? |
| Idempotency and lifecycle | What happens on retry, duplicate request, update, and deletion? |
| Evidence | What audit, policy, cost, and status record is retained? |
| SLO and failure | What latency/availability target applies, and how is an actionable failure returned? |
| Escape hatch | What can a consumer do when the contract does not fit, and who reviews it? |

Prefer an API-first interface with a documented request/response shape. A portal or CLI may sit on top, but the interface must remain automatable and independently testable. Keep generated infrastructure and policy decisions in version control where practical.

## Adoption and value review

Review at a fixed interval using a small evidence set: active and repeat users, completion rate, time-to-first-use, lead time through the target workflow, support tickets or handoffs removed, failure/rework rate, incident recovery effect, developer sentiment/cognitive-load signal, security-policy coverage, and platform cost per consumer or workflow. Compare actuals to the original baseline and value model; revise the roadmap when the evidence disagrees.

Treat adoption as a product problem. Sample non-users, observe where they leave the path, fix the highest-friction step, and measure again. Do not force adoption by removing the escape hatch or by converting unresolved usability problems into policy violations.

## Domain and event boundaries

Keep platform domains independently accountable for their APIs and backlogs. Use events for cross-cutting adapters such as issue tracking, CI hooks, observability, configuration inventory, and audit collection. Define event schema, producer/consumer ownership, delivery semantics, replay behavior, and failure visibility before adding an adapter. Tool-specific cluster, IaC, proxy, or telemetry operations belong to their named tool skills.
