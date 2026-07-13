# Contract And Representation Semantics

Define domain vocabulary before transport names. State the authoritative schema and
owner, identifier scope, mutability, lifecycle, and invariants for every exposed
representation. A mapping layer must not quietly become the authority.

## Representation Questions

- Does absence mean unknown, inapplicable, withheld, or an omitted default? Is `null`
  distinct from absence in requests and responses?
- Are defaults applied by the server, client, transport, or generated SDK? Can a
  future default change behavior?
- Are enum and union values open or closed for each consumer? Specify unknown-value
  handling rather than assuming an added value is safe.
- Define time zone/offset, precision, clock meaning, duration format, units, rounding,
  locale, currency, and identifier comparison rules where relevant.
- State which fields are stable identifiers, opaque tokens, display values, or
  derived/cached views.

## HTTP Contract Semantics

For REST/HTTP, make the protocol behavior part of the domain contract:

- Choose a method from its RFC 9110 semantics, not a CRUD-name chart. `GET` and `HEAD` are safe; `PUT`, `DELETE`, and safe methods are idempotent in intended effect, but responses and incidental logging can differ. `POST` and `PATCH` can be made retryable only through an explicit application contract.
- Define the success, redirection, client-error, and server-error statuses that consumers act on. `202 Accepted` means processing was accepted, not completed; give a status/result mechanism when completion is asynchronous. `204 No Content` carries no response content. Do not wrap every outcome in `200 OK` and an application flag.
- State request and response media types, character/serialization rules, content negotiation, language where applicable, and `Vary` behavior. A new representation or default can change caches and generated clients.
- Define cacheability, freshness, validators such as `ETag` or `Last-Modified`, conditional requests, and invalidation for reads where caching matters. Do not use an ETag as a write precondition unless its representation and validator semantics support that contract.
- Keep resource identifiers stable and opaque where consumers should not infer structure. URI naming is a consistency decision, not a universal plural-noun rule; avoid exposing storage topology as domain authority.

## Collections

Document filter grammar, supported fields/operators, escaping, case/locale behavior,
sort keys and directions, ties, default ordering, search consistency, sparse-field
semantics, and resource-cost constraints. Reject or constrain inputs by the published
contract; do not claim a universal maximum.

For pagination, choose offset, keyset, cursor, or another model based on data shape
and consumer need. A cursor is not inherently snapshot-stable or idempotent. State:

- sort keys and deterministic tie breaking;
- whether the token is opaque and integrity protected;
- direction, page-size interaction, expiry, and resume behavior;
- behavior when records change or disappear between pages; and
- expected duplicate, skipped-item, or snapshot guarantees, if any.

Keyset pagination can use any stable ordered key or tuple; it is not limited to
sequential IDs. Provide contract examples and negative examples for invalid filters,
expired cursors, and incompatible combinations.

## Contract Formats And Tooling

Use OpenAPI 3.2.0 for HTTP contracts when its feature set and the chosen toolchain support it. Its JSON Schema dialect is defined by the selected OAS version; do not assume a generator, validator, gateway, or documentation renderer supports every 3.2 feature. Pin the tool versions, validate generated server/client behavior, and use a compatible subset or another published contract version when needed.

A useful OpenAPI contract includes operation identity and ownership; parameters and serialization; request and response media types; every consumer-relevant status; schemas with required/null/default/read-only/write-only semantics; security requirements; reusable components; and validated positive and negative examples. Add callbacks, webhooks, links, streaming content, or external references only when the selected OAS version and deployed tools preserve their meaning. Linting proves rules, not domain correctness. Resolve references from the actual entry document, and test that examples and generated artifacts conform to the same dialect.

Code generators can turn optionality, unions, enums, defaults, integer widths, dates, and polymorphism into stricter language models than the wire schema suggests. Generate representative clients in CI or treat them as explicit consumers in compatibility review.

For GraphQL, express field ownership, nullability, pagination, mutation payloads, errors, query-cost controls, and deprecation in the schema. For RPC, make commands, input/output messages, deadlines, and application errors explicit. Generated code is a consumer with its own strictness and upgrade behavior.
