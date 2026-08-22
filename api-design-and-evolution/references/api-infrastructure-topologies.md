# API Infrastructure Topologies

Use this reference when an API decision depends on where traffic enters, crosses, or
leaves a system. Topology supports a contract; it does not define the domain agreement.
Describe the actual path, the responsibility at each hop, and the failure behavior
consumers can observe.

## Traffic Directions

- **North-south:** traffic between clients or external networks and a service estate.
  Common concerns include public admission, identity handoff, rate/resource controls,
  external routing, protocol translation, and partner-facing observability.
- **East-west:** traffic among services, jobs, brokers, and internal control planes.
  Common concerns include service identity, discovery, retries and deadlines, locality,
  load balancing, encryption, dependency policy, and partial-failure containment.
- **Ingress and egress:** name the boundary explicitly. An ingress proxy may admit
  traffic into a cluster or domain; an egress control may govern calls leaving it. Do
  not infer either responsibility from the word "gateway."

## Gateway Versus Service Mesh

Use a gateway or ingress proxy for boundary-facing concerns such as listener and host
routing, external authentication integration, protocol adaptation, public throttling,
request-size limits, cross-origin behavior, and consumer-visible access policy. Keep
domain authorization and contract semantics in the service unless the gateway is an
explicitly governed policy decision point.

Use a service mesh for service-to-service transport concerns such as service identity,
encryption between workloads, discovery, load balancing, traffic shifting, retries,
timeouts, and telemetry propagation. A mesh does not make an unsafe retry safe, prove
business authorization, or define an event's delivery guarantee.

These are tendencies, not mandatory product boundaries. A deployment may combine
functions, use no mesh, or place a control in another proxy. Record who owns each
policy and what happens when the enforcement component is unavailable.

## Map The Request Path

For each important flow, draw or tabulate:

1. caller and trust context;
2. DNS or discovery and route selection;
3. ingress/gateway hops and transformations;
4. mesh sidecars, gateways, or direct service links;
5. service authorization and contract enforcement;
6. downstream calls, queues, or data stores;
7. response, event, or callback path;
8. telemetry and correlation propagation at every boundary.

For each hop record protocol, timeout/deadline, retry owner, load-balancing scope,
buffering, size limit, identity propagation, policy decision, and whether the hop can
duplicate, reorder, delay, or drop work. Never add retries at multiple layers without
an explicit retry budget and operation safety assessment.

## Place Policy Deliberately

Classify a policy as edge, transport, service, or domain policy. Edge policy can
protect a public boundary but may lack domain context. Transport policy can constrain
who may connect and how traffic behaves but cannot replace object/action authorization.
Service policy can enforce resource and operation rules with domain context. Domain
policy decides business invariants and state transitions. Duplicate enforcement only
when the different layers have distinct purposes and failure behavior.

For each policy state the decision owner, source of truth, update path, audit evidence,
fail-open or fail-closed behavior, and stale-policy risk. Route threat modeling and
abuse resistance to `secure-software-engineering`.

## Observability And Failure Boundaries

Define signals at the consumer-visible boundary and at internal hops: request outcome,
latency, saturation, retries, timeouts, rejected policy decisions, route changes, and
correlation/trace continuity. Attribute failures to the narrowest known boundary and
preserve enough context to distinguish an edge rejection, proxy failure, mesh failure,
service failure, dependency failure, and ambiguous completion.

Health checks must reflect the promise they make. A process-level success signal does
not prove that a dependency or route is usable. Document which failures are retried,
which are surfaced, which may have caused work despite an error, and how a consumer
reconciles uncertain outcomes. Coordinate SLO and incident operations with
`site-reliability-engineering`; do not create platform runbooks here.

## Topology Change

Before moving a route, adding a proxy, or introducing a mesh, compare the old and new
paths for contract-visible changes: headers, status mapping, timeout, retry, ordering,
source identity, body limits, caching, streaming support, and telemetry. Use a staged
coexistence path where feasible. Prove the deployed boundary, rollback or pause trigger,
and recovery of in-flight or ambiguously completed work. A topology migration does not
authorize a contract change without the compatibility workflow.

## Topology Exit Check

Stop when traffic direction and paths are explicit, each concern has an owner, policy
placement and unavailable-component behavior are documented, observability crosses the
relevant boundaries, failure and retry multiplication are bounded, and any contract
impact has a separate compatibility assessment.
