# Instructions, knowledge visibility, and executable invariants

## Make knowledge discoverable without inventing authority

A repository is often a convenient shared system of record for coding. It is not
a universal highest authority: user directives, organization policy, approved
external systems, and runtime rules may govern it. Establish precedence from the
actual host and source owners. A local preference must not override a binding
organizational or security constraint merely because it is more local.

For each consequential rule record: owner, scope, source, last reviewed revision,
reason, enforcement mechanism, and expiry/invalidation trigger. Separate accepted
requirements, design decisions, heuristics, temporary exceptions, and memories.
A meeting transcript is evidence of discussion, not necessarily an accepted rule.

## Build an entry map

Root: purpose, startup/readiness, acceptance/check routes, global authority and
constraints, state/resume pointer. Detail: domain rules close to the owning code,
architecture decisions with alternatives, test contracts, and operational docs.
Route by task condition. Check that links exist and point to the authoritative
version; include a conflict-resolution owner.

Example routing:

| Task | Load | Why |
|---|---|---|
| Change authentication middleware | Security/auth contract and middleware tests | Accepted boundary and negative cases |
| Modify retrieval indexing | Index format/version contract and recovery test | Prevent incompatible state |
| Diagnose a UI state failure | User journey, IPC/API contract, runtime evidence | Avoid isolated component-only reasoning |

Do not impose a universal 100-line limit. Measure what is needed to find and
obey the right rules, and use the smallest map that passes the discovery test.

## Promote feedback into the right mechanism

A repeated review finding can become a guardrail, but not every remark deserves
a permanent lint rule. Determine whether it is a reusable invariant, a scoped
exception, a one-off preference, or evidence of an upstream specification defect.

1. Capture the actual violation and why it harms the accepted behavior.
2. Name the domain owner and the authoritative rule; check for contradictory rules.
3. Choose the cheapest faithful mechanism: type constraint, parser/AST check,
   unit/contract/integration test, runtime validation, or documentation route.
4. Challenge it with a valid implementation, violating near miss, and omitted
   evidence. Text grep may detect a literal but miss aliases/comments/dynamic calls.
5. Give actionable failure feedback: WHAT violated, WHY consequential, WHERE
   observed, and a safe FIX direction. Avoid prescribing a single incidental shape.
6. Version the rule and measure false positives, coverage gaps, execution cost,
   and whether agents actually receive the result.
7. Keep exemptions scoped, owned, visible, and expiring. Retire stale rules with
   a rollback and a challenge test.

Example: renderer must not access filesystem directly. An import-name grep is a
cheap screen. An AST dependency rule plus a boundary integration test can observe
more of the actual property. Do not label grep output proof of process isolation.

## Maintenance decisions

Duplicate fact → remove duplicate after checking references. Conflicting rule →
resolve with owner, do not let the model vote. Stale fact → invalidate and refresh.
Never-used detail → move to on-demand reference. Recurring runtime mistake →
consider an executable invariant before adding another paragraph.

Use [templates/guardrail-promotion.md](../templates/guardrail-promotion.md). Harness
engineering owns making the rule reachable and enforceable; the architecture,
security, QA, or product owner owns the rule's domain correctness.
