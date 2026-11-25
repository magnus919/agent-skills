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

## Prevent policy drift at capture

Record observations, one-off requests and proposed rules as such. Do not activate
a durable rule just because a conversation was summarized or a worker suggested
it. Give authorized rule changes a current source, owner, scope and review or
expiry trigger; link a superseded revision to its replacement. Keep historical
decisions searchable for audit but out of active policy retrieval by default.
On expiry or supersession, re-evaluate the authoritative baseline, refresh cached
derivatives, and test authorized and denied cases. Expiry never creates a grant.

## Maintenance decisions

Duplicate fact → remove duplicate after checking references. Conflicting rule →
resolve with owner, do not let the model vote. Stale fact → invalidate and refresh.
Never-used detail → move to on-demand reference. Recurring runtime mistake →
consider an executable invariant before adding another paragraph.

If ready work sits idle despite healthy workers and spare budget, distinguish
lack of capacity from a policy veto. Trace one blocked decision to the exact
rule, source, revision and scope. Compare against current authority and trace
derived copies in scheduler caches, generated instructions and session
summaries. If ownership or precedence remains ambiguous, escalate rather than
overriding the rule. Once the authorized owner confirms the disposition, keep
superseded guidance for audit but invalidate its operational copies. Verify
both sides in fresh and resumed executions: the authorized item becomes
eligible and a nearby prohibited action still fails its authorization check.
Do not actually execute the prohibited action as a test; exercise the denial
or a sandboxed equivalent.

### Worked example: retire a redundant rule during a release freeze

A team has spare build capacity and approved test-only work, but its scheduler
applies an obsolete ban on every repository write. The current release freeze
still forbids deployment. Trace each denial to its rule and enforcement point.
The workflow owner can retire the redundant scheduler rule only after confirming
its scope with the control owner. The release freeze remains in force at the
shared deployment boundary.

Record the old and new revisions, reason, affected caches or workers, the
protected effects, and how to restore the former revision. Preserve the old
rule in decision history. Refresh generated instructions and cached projections.
Re-evaluate queued jobs and resumed sessions against current effective policy
before dispatch or effect, as applicable.

Replay an approved test-only item through a fresh run and a resumed run. Next
exercise the denial for a direct release request, a pre-freeze queued release,
and a resumed worker holding the old policy. Observe denial at the effect
boundary using a dry run or an isolated fixture. Confirm the freeze and audit
receipt independently of the worker. A missing check or unexpected permission
holds the rollout and routes to the control owner for containment and restore
verification. Use [protected-control governance](../../ai-governance/references/protected-controls.md)
and [production control integrity](../../agent-production-operations/references/control-integrity.md)
for these decisions.

Yegge reported that simplifying Wheelhouse restored activity and removed a
freeze check. This fixture tests that failure mode using synthetic work and
release requests. [Wheelhouse interview, 08:13 onward](https://www.hackersandwizards.dev/podcast/steve-yegge/transcript/)

Use [templates/guardrail-promotion.md](../templates/guardrail-promotion.md). Harness
engineering owns making the rule reachable and enforceable; the architecture,
security, QA, or product owner owns the rule's domain correctness.
