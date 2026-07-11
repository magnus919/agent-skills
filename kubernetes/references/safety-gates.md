# Safety gates

## Read-only operations

Context, version, discovery, get, describe, events, logs, auth checks, and rollout status are read-only in the Kubernetes API, although logs/exec can expose sensitive data. Bound output and redact values.

## Reversible mutations

Apply, scale, rollout restart, and non-destructive patches can still cause outage. Require:

- explicit context and namespace
- manifest or target scope
- diff/server dry-run
- field manager
- timeout and rollback/verification plan
- explicit `--yes` to enact through `k8s-cli`

## Destructive or high-risk mutations

Delete, drain, node cordon, finalizer removal, force-conflicts, RBAC broadening, admission changes, Secret changes, datastore restore, cluster reset, and upgrades require a human-confirmed scope. The CLI refuses these by default.

## Verification gate

After a mutation, verify:

1. command exit status
2. API object conditions
3. events and controller state
4. rollout/Pod readiness
5. Service/EndpointSlice or route
6. external health check when relevant

A successful command is not a successful operation until the relevant boundary is healthy.
