# Digital Twin: implementation

## Build order

### 1. Frame one decision

Record original, owner, authoritative sources, decision, outcome, latency/fidelity target, excluded conditions, privacy class, allowed response, forbidden actions, fallback, stop authority, and simpler alternatives. Start with `observe` and `recommend`, not merge or deploy authority.

### 2. Capture identity and events

Use stable IDs, aliases, revisions, and content-addressed artifact references. Wrap source events in a standard envelope such as CloudEvents. Add represented-entity ID, source sequence, event/observation/ingestion times, schema version, tenant, sensitivity, payload digest, signature/attestation, trace context, and connector version.

Assume duplicates, delay, reordering, clock skew, source silence, and out-of-band changes. Deduplicate by source plus event ID, make projections idempotent, quarantine invalid events, expose loss/reordering metrics, and retain raw envelopes.

### 3. Build temporal state and provenance

Keep three distinct layers:

- immutable evidence: received events and artifact digests;
- claims: source-specific assertions, contradictions, confidence, and quality;
- projections: disposable current and historical views.

Prefer bitemporal records: when a fact was valid in the original, and when the twin learned/recorded it. Every state field and edge must resolve to source events, transformations, schema, authority, confidence, and freshness. Use W3C PROV where provenance needs portable entity/activity/agent semantics. Use OpenLineage for compatible pipeline/data lineage, not as a complete software-factory ontology.

### 4. Define a small semantic core

Start with Product, Repository, Revision, Requirement, Change, Build, Artifact, Dependency, Service, Deployment, Environment, RuntimeObservation, Incident, Person, Agent, Policy, Model, Scenario, Decision, and Action. Relationships have direction, identity, provenance, confidence, validity, and owner.

Use JSON-LD/RDF if cross-system semantic portability matters. Use SHACL or equivalent validation to reject dangling identities, invalid edge directions, missing provenance, incompatible units, and unversioned model references. Keep ontology versions immutable and test export/import round trips.

Interoperability standards have different jobs:

- **DTDL:** interfaces, properties, relationships, components, telemetry, commands, schemas, and semantic annotations. Treat service-specific behavior as non-portable until tested.
- **AAS / OPC UA:** industrial asset representations, information models, services, security, historical access, and companion models at industrial boundaries.
- **FMI:** model exchange, co-simulation, scheduled execution, events, clocks, and communication points. It does not prove semantic correctness.
- **CloudEvents / PROV / OpenLineage / SPDX:** event, provenance, lineage, and supply-chain contracts. Combine them; do not treat them as substitutes.

### 5. Register models and scenarios

Each model release records digest/version, intended use, owner, domain, assumptions, limits, prohibited uses, training/calibration references, code/dependencies, parameters, solver/runtime, random seed policy, input/output schema and units, verification/validation/uncertainty results, scenario suite, approval, expiry/review date, and rollback target.

Each scenario pins input snapshot, model and adapter digests, scenario configuration, seed, clock policy, network/data fixtures, resource limits, outputs, uncertainty, and teardown attestation. Run untrusted code and agents in isolated, short-lived environments with denied-by-default network and credentials.

Useful adapters include repository build/test environments, API emulators, recorded traffic/state replay, queueing/discrete-event models, policy and infrastructure-plan sandboxes, FMI importers, and learned surrogates. Learned world models are for exploration, not the sole release oracle.

### 6. Version and migrate explicitly

Version event schemas, vocabularies, validation shapes, connectors, projections, source mappings, policies, models, adapters, scenarios, prompts/tools, deployments, and compositions independently. Lock them in a release manifest. For changes, dual-read or parallel-project, replay historical evidence, compare outputs, canary consumers, advance an explicit alias, and preserve rollback. Never silently reinterpret old evidence.

### 7. Deploy as replaceable services

Separate event gateway, immutable log/object store, state projector, semantic/provenance service, model registry, scenario orchestrator, policy gateway, query API, and evaluation/observability service. Package adapters with pinned digests. Keep canonical IDs and contracts provider-neutral. Export events, artifacts, temporal state, schemas/shapes, provenance, SBOMs, model/scenario manifests, evaluation reports, and lockfiles.

Portability requires conformance tests on a second runtime/store: event replay, semantic round trip, model loading, deterministic scenarios, policy behavior, and restoration from export.

## Templates and scripts

Use `templates/twin-manifest.yaml`, `templates/evaluation-plan.md`, and `templates/release-evidence.md` for recurring artifacts. No runtime script is bundled: tool choices and storage/runtime behavior vary too widely, while contract validation is best implemented by the adopting system.

## Sources

- CloudEvents 1.0.2: https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md
- W3C PROV-O: https://www.w3.org/TR/prov-o/
- W3C RDF 1.1: https://www.w3.org/TR/rdf11-concepts/
- W3C JSON-LD 1.1: https://www.w3.org/TR/json-ld11/
- W3C SHACL: https://www.w3.org/TR/shacl/
- OpenLineage object model: https://openlineage.io/docs/spec/object-model/
- SPDX overview: https://spdx.dev/learn/overview/
- DTDL: https://azure.github.io/opendigitaltwins-dtdl/DTDL/v4/DTDL.v4.html
- IDTA AAS specifications: https://industrialdigitaltwin.org/en/content-hub/aasspecifications
- FMI 3.0: https://www.fmi-standard.org/docs/3.0/
- NASA-STD-7009 model/simulation credibility: https://standards.nasa.gov/standard/NASA/NASA-STD-7009
