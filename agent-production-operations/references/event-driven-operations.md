# Operate agents that sleep and wake

Load for agents resumed by callbacks, subscriptions, durable timers or queued
messages. Runtime design belongs to
[harness-engineering](../../harness-engineering/SKILL.md); this reference owns
production control decisions. The
[Infinity investigation](../../harness-engineering/references/infinity-sources.md)
(S4–S8, checked 2026-11-03) motivates these controls; they are recommendations,
not verified properties of an Infinity deployment.

## Define the operating population

Track persisted conversations, active completions, pending tool operations,
queued events and oldest-event age separately. A low idle footprint says little
about burst admission, model rate limits, tool saturation, or operator review
capacity. Define quotas per tenant, conversation, tool and event source. Bound
child fan-out and preserve a user-facing capacity reserve. Include storage,
queue/timer/callback, tool-server and human intervention costs alongside runtime
compute and model spend.

## Gate every wake-up

Authenticate the producer; bind tenant, thread, event and originating operation;
check retention/replay windows and current task revision before admitting content.
Resolve current grants and protected-control integrity before consequential work.
A grant remembered before sleep may be expired or revoked now. Quarantine
unmatched/stale events and reconcile their possible external effects; do not treat
synthetic assistant messages or matching IDs as authorization.

A stopped worker is not a disabled agent if a timer, tool or subscription can wake
it later. Disablement must revoke execution authority, gate admission, inventory
pending invocations/subscriptions/timers, and assign cleanup/reconciliation owners.
Retain incident evidence and required reconciliation access under an approved
operator identity. Route infrastructure changes to the platform/tool owner.

## Distinguish waiting from stalled

Define expected callback deadlines and pending-operation reconciliation. Observe
queue age, lost/duplicate callbacks, deferred-event age, unknown effects, redelivery
loops and dead-letter outcomes. The Infinity local adapter's deferred events can
be in memory; other embeddings can behave differently. Test process loss under
the deployed adapter before promising durable event handling.

A transport 200 is receipt, not successful execution. Likewise an advisory cancel
or synthetic interrupted result does not prove that a build, deployment or write
stopped. Fence stale publication, observe the external effect, and close each
pending operation with an explicit disposition. Do not replay an unknown-effect
mutation as though it failed.

## Release and recover

Canary under realistic event arrival and model/tool quotas, including a callback
burst after downtime. Verify rollback handles queued and in-flight work as well as
code/configuration. Escalate missing mandatory controls immediately; use existing
incident ownership for unknown effects or spoofed events. Record what was held,
rejected, reconciled and resumed. End when the tested operating envelope, current
authority, pending-effect disposition, evidence gaps and rollback owner are recorded.
A source review or synthetic capacity benchmark cannot authorize production.

## Release a coordinated-restore hold

Recovery must restore the logical agent deployment, including conversation and
runtime-state stores, configuration references, input replay position and pending
external operations. Inventory dedup records, subscriptions and pending human
choices, not just messages. Hold consequential dispatch on missing/incompatible
snapshot lineage; an operator must reconcile effects newer than the recovery
point before deciding what can resume. Preserve current revocation across restore.
The paired recovery manifest is an application control proposal, not a verified
Infinity facility. Use harness-engineering's
[restore drill](../../harness-engineering/references/context-and-state.md#restore-the-logical-deployment-not-only-its-transcript).

Distinguish stopped-session admission from authority enforcement. The inspected
Infinity local router checks existence/stopped state for event-style inputs, but
user text can create/resume threads, the stopped check defaults to admitting,
and store-check errors are processed fail-open. These lifecycle choices are not
a security revocation guarantee. Enforce current grants independently before
consequential dispatch, and test store failure and user-triggered resume under
a revoked grant. Source: [router](https://github.com/hydro-project/infinity/blob/1abc6fcff1f186124f924b56aa92c3a3684c90c5/crates/infinity-agent-core/src/system/local/router.rs).
