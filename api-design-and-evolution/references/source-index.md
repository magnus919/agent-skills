# Source Index

Versions, status, and URLs were checked against primary sources on 2026-07-13. Use a
source for its stated purpose; adoption depends on the applicable organization,
contract, and deployment. Recheck evolving specifications before relying on them.

| Source | Exact version/status | Primary URL | Decision use |
|---|---|---|---|
| OpenAPI Specification | 3.2.0, published specification | https://spec.openapis.org/oas/v3.2.0.html | HTTP API description; verify tool support before codegen or publication. |
| JSON Schema | 2020-12 specification release; corresponding IETF Internet-Drafts expired | https://json-schema.org/draft/2020-12/ | Schema semantics through the dialect selected by the contract format; do not present it as an IETF RFC. |
| HTTP Semantics | RFC 9110, Internet Standard (STD 97) | https://www.rfc-editor.org/rfc/rfc9110 | Method, conditional request, status, and representation semantics. |
| HTTP Caching | RFC 9111, Standards Track | https://www.rfc-editor.org/rfc/rfc9111 | Cache behavior and validator use. |
| Problem Details | RFC 9457, Proposed Standard | https://www.rfc-editor.org/rfc/rfc9457 | Optional HTTP problem representation. |
| Deprecation HTTP Field | RFC 9745, Proposed Standard | https://www.rfc-editor.org/rfc/rfc9745 | Deprecation response-field semantics. |
| Sunset HTTP Header | RFC 8594, Proposed Standard | https://www.rfc-editor.org/rfc/rfc8594 | Sunset communication semantics. |
| GraphQL | September 2025 edition, published specification | https://spec.graphql.org/September2025/ | GraphQL schema, execution, and deprecation guidance. |
| AsyncAPI | 3.0.0, published specification | https://www.asyncapi.com/docs/reference/specification/v3.0.0 | Event/message contract from the described application's perspective. |
| CloudEvents | 1.0.2 tagged specification; tag commit verified 2026-07-13 | https://github.com/cloudevents/spec/tree/v1.0.2 | Event envelope and context attributes, not delivery policy. |
| Semantic Versioning | 2.0.0, released | https://semver.org/spec/v2.0.0.html | Version labels only where public-API assumptions fit. |
| HTTP Message Signatures | RFC 9421, Proposed Standard | https://www.rfc-editor.org/rfc/rfc9421 | Optional integrity/signature building block. |
| Digest Fields | RFC 9530, Proposed Standard | https://www.rfc-editor.org/rfc/rfc9530 | Optional content-digest building block. |
| Idempotency-Key Header Field | `draft-ietf-httpapi-idempotency-key-header-07`, expired Internet-Draft | https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ | Convention requiring contract-specific semantics; not an RFC. |
| RateLimit Fields | `draft-ietf-httpapi-ratelimit-headers-11`, active Internet-Draft/work in progress as checked 2026-07-13 | https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/ | Evolving rate-limit field model; do not assign an RFC number or substitute fields from an older draft. |
