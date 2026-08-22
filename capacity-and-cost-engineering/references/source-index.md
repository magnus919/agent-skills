# Source Index

This skill is an original, task-centered synthesis. Public sources inform
terminology and decision pressures; they are not copied as instructional text.

| Source | Use in this skill | URL |
|---|---|---|
| Google SRE resources | Capacity, overload, service behavior, and evidence-oriented reliability framing | https://sre.google/sre-book/table-of-contents/ |
| OpenSLO specification | Portable vocabulary for connecting service objectives to evidence; SLO ownership remains with SRE | https://github.com/OpenSLO/OpenSLO |
| OpenTelemetry semantic conventions | Tenant-aware measurement vocabulary and observability handoff; implementation remains with platform/telemetry owners | https://opentelemetry.io/docs/specs/semconv/ |
| FinOps Framework | Shared-cost allocation, unit economics, and accountability vocabulary; financial outcomes remain with financial-modeling | https://www.finops.org/framework/ |
| Kubernetes resource management documentation | Resource requests, limits, and scheduling concepts as implementation context; platform-engineering owns configuration | https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ |
| RFC 6585 | HTTP status vocabulary for rate-limit and overload responses; API contract details remain with api-design-and-evolution | https://www.rfc-editor.org/rfc/rfc6585 |

## Ownership and transformation boundary

- End-to-end tenant semantics, control/application planes, lifecycle, and
  placement architecture belong to `multi-tenant-saas-architecture`.
- Threat controls and tenant isolation evidence belong to
  `secure-software-engineering`.
- Financial statements, pricing, margin, and SaaS outcomes belong to
  `financial-modeling`.
- Infrastructure and telemetry implementation belong to
  `platform-engineering`; SLOs and live operations belong to
  `site-reliability-engineering`.
- The supplied private comparison report informed the gap framing only. No
  purchased ebook is a source file for this skill, and no protected prose,
  table, diagram, example, taxonomy, or chapter structure is reproduced.

## Review rule

If a future edit resembles a source's distinctive expression or presentation,
rewrite it from the issue requirements, public sources, and repository ownership
boundaries before publication.
