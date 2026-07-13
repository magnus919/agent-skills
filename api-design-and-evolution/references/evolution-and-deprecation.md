# Compatibility, Versioning, And Deprecation

Compatibility is a consumer property. Assess each known consumer separately,
including strict decoders, generated SDKs, exhaustive switches, signatures, caches,
query-cost limits, quotas, operational automation, and undocumented behavior.

An optional field, enum value, method, changed default, or new endpoint can be
compatible for one consumer and breaking for another. Record evidence and assumptions;
do not use a universal safe-change table. Prefer additive evolution only after testing
the consumer/tooling assumptions that make it safe.

Versioning may be in place, media type/header, schema, topic, package, or a new
interface. Each changes discovery, routing, caching, generated code, and coexistence
cost differently. No explicit version can be appropriate for disciplined additive
evolution. SemVer 2.0.0 applies only when its public-API assumptions fit the artifact;
it does not settle HTTP or event compatibility by itself.

Deprecation is a lifecycle: inventory the affected surface and consumers; assign an
owner; publish a replacement and migration support; collect telemetry; communicate;
define evidence-based sunset criteria; run rollout; preserve rollback; and retire only
when the criteria are met. Do not invent a standard window, threshold, or removal date.

RFC 9745 defines the HTTP `Deprecation` response header; RFC 8594 defines `Sunset`.
Headers and an OpenAPI/GraphQL deprecation annotation communicate status but do not
replace the lifecycle. State the successor, impact, migration path, support channel,
and whether removal remains conditional. For semantic changes, run old and new
meanings in parallel where feasible and validate results before cutover.
