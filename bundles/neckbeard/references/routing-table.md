# Routing Table — Conditional Applicability Matrix

neckbeard owns the **cross-stage contracts**: the change contract, the evidence
ledger, the stop/escalation rules, and the evaluation protocol. It does **not**
own domain method. When a stage has a specialist skill, load it and follow it
instead of re-deriving its method here.

This matrix prevents the omnibus bundle from swallowing the specialist catalog.
Each row carries a concrete **applicability signal** (an observable,
file-system- or artifact-based criterion) and a concrete **skip rule** (its
observable complement). Evaluate every row against the change surface; record
each skip with its reason in the delivery packet
([delivery-packet.md](delivery-packet.md), group (e)). Silent omission is
prohibited.

## Routing matrix

| Catalog skill | Applicability signal | Skip when | neckbeard provides |
|---|---|---|---|
| `product-discovery` | Change request text lacks testable acceptance criteria, no `SPEC.md` or requirements artifact accompanies it, or scope is contested among stakeholders | Scope is fully specified in the change request with testable acceptance criteria and no stakeholder ambiguity | Contract, ledger |
| `product-methodology` | Multiple competing requirements documents, backlog items, or priority-conflicting issues reference the same feature area; sequencing or prioritization decisions must be recorded | Requirements are singular and uncontested; no backlog, roadmap, or prioritization document needs updating | Contract, ledger |
| `product-design-and-ux` | Change creates or modifies view templates, component files, route definitions, interaction flows, information architecture, or UI-state logic | No view template, component, route definition, interaction flow, information-architecture artifact, or UI-state logic is created or modified | Contract, ledger |
| `spec-driven-development` | Work requires a formal specification with phase gates, acceptance-criteria mapping, and structured decomposition (`SPEC.md`, `TASK-PLAN.md`) | Change is a single-surface fix fully described by the change contract; no separate `SPEC.md` or phased decomposition is needed | Contract, ledger, stop rules |
| `software-architecture-analysis` | Change modifies or requires understanding of module boundaries, service dependencies (`go.mod`, `package.json` dependency graph, import graphs), cross-service contracts, or system-level structure | Change is confined to a single function or module with no cross-component dependency, service boundary, or system-level structure change | Ledger, assumptions list |
| `c4-diagramming` | Architecture change spans multiple containers or services and the design record requires system context, container, component, or code-level diagrams for review | Change fits within a single container or service; no multi-system diagram is needed for the design record | Ledger |
| `adr-authoring` | A consequential, hard-to-reverse technical decision (storage engine, framework, protocol choice) must be recorded in a decision record with context, alternatives, and consequences | No consequential decision beyond what the change contract already captures is required; no decision-record file is needed | Decision-record template, ledger |
| `api-design-and-evolution` | Change modifies or creates a public API surface: OpenAPI/AsyncAPI specs, protobuf/gRPC definitions, REST endpoints, GraphQL schema, webhook contracts, or SDK interface | No public API surface, interface contract, or protocol definition is created or modified | Contract, ledger, boundary verification |
| `systematic-debugging` | Change request reports a bug, failure, or regression; error logs, stack traces, or reproduction steps accompany it; root-cause analysis is needed before a fix can be designed | Change is not a bug fix; no error log, stack trace, or reproduction evidence accompanies the request; the desired behavior is already known | Contract, ledger, boundary verification |
| `secure-software-engineering` | Change touches auth modules, middleware handling untrusted input, secrets-management files, cryptographic operations, or code that crosses a trust boundary (e.g., `auth/`, `middleware/`, `crypto/`, input-validation handlers) | No auth module, untrusted-input handler, secrets file, crypto operation, or trust-boundary-crossing code is in the change surface | Contract, ledger, trust-boundary checks |
| `security-audit-methodology` | A security audit artifact (`SECURITY-AUDIT.md`, threat model, STRIDE analysis) is requested, or the change touches auth/crypto/trust-boundary files and a post-build vulnerability review is required | No security audit artifact is requested and the change surface does not include auth, crypto, or trust-boundary files requiring post-build review | Ledger |
| `web-accessibility` | Change modifies user-facing markup, styles, ARIA attributes, keyboard/focus contracts, or error-recovery UI; WCAG conformance is in scope | No user-facing markup, style, ARIA attribute, keyboard/focus contract, or error-recovery UI is created or modified | Ledger, non-negotiable confirmation |
| `qa-methodology` | A `VERIFICATION-PLAN.md` or test-strategy artifact is required, CI quality-gate configuration is modified, or independent verification-plan ownership is needed before implementation | Change requires no `VERIFICATION-PLAN.md`, no CI quality-gate modification, and no independent test-strategy artifact beyond the implementer's own focused tests | Ledger, boundary verification |
| `technical-documentation` | Change creates or modifies user-facing docs, README, API reference, guides, or inline documentation intended for consumers | No user-facing documentation, README, API reference, or guide is created or modified | Ledger |
| `verification-methodology` | A `VERIFICATION.md` verdict artifact with layered evidence (PASS/FAIL/BLOCKED/NOT-APPLICABLE) is required at the delivery boundary | Verification is a single focused test run that does not produce a `VERIFICATION.md` artifact or need the structured verdict protocol | Ledger, boundary rules |
| `release-engineering` | Change modifies version files, changelogs, release configuration, pipeline promotion rules, rollout strategy, or rollback procedures | No version file, changelog, release configuration, pipeline promotion rule, rollout strategy, or rollback procedure is created or modified | Contract, ledger, rollback evidence |
| `site-reliability-engineering` | Change modifies SLO/SLI definitions, incident response runbooks, operational recovery procedures, monitoring dashboards, or alerting configuration files | No SLO/SLI definition, incident runbook, operational recovery procedure, monitoring dashboard, or alerting configuration file is created or modified | Contract, ledger, rollback evidence |
| `platform-engineering` | Change modifies infrastructure-as-code, deployment pipelines, container/orchestration configuration, or platform-level provisioning files | No infrastructure-as-code, deployment pipeline, container/orchestration configuration, or platform provisioning file is modified | Contract, ledger |
| `programming-principles` | Change is primarily a refactoring (files renamed/moved/split without behavior change), code-review request, or quality assessment; diff touches many files with structural reorganization | Change is greenfield implementation or a targeted bug fix; no structural reorganization, review request, or quality assessment is the primary objective | Contract, ledger, boundary verification |
| `backend-engineering` | Change modifies server-side logic, service architecture (clean/hexagonal/layered), database access patterns, API implementation code, middleware, or service-to-service integration | No server-side logic, service architecture, database access pattern, API implementation, middleware, or integration code is modified | Contract, ledger |
| `frontend-engineering` | Change modifies client-side application code, component hierarchy, state management, browser APIs, or UI rendering logic | No client-side application code, component, state management, browser API, or UI rendering logic is modified | Contract, ledger |
| `cli-builder` | Change creates or modifies a command-line interface: argument parsing, flag design, subcommands, `--json` output, `--dry-run` preview, or exit-code contracts | No CLI argument parsing, flag, subcommand, or CLI output contract is created or modified | Contract, ledger |
| `data-engineering` | Change modifies database schemas, migration files (`migrations/`, `*.sql`), ETL/ELT pipelines, data quality checks, or analytical SQL | No schema, migration file, ETL/ELT pipeline, data quality check, or analytical SQL is created or modified | Contract, ledger |
| `data-architect` | Change requires a data-model design artifact, storage-platform evaluation, data-governance definition (ownership, lineage, cataloging), or cross-system data-flow diagram before implementation | No data-model artifact, storage-platform evaluation, data-governance definition, or cross-system data-flow design is required; schema changes are mechanical | Contract, ledger |
| `agent-evals-and-observability` | Change modifies AI/agent behavior: eval definitions, agent task contracts, grader bindings, trajectory fixtures, prompt templates, or agent observability/telemetry | No agent eval, task contract, grader, trajectory fixture, prompt template, or agent telemetry is created or modified | Contract, ledger |
| `opensource-contributions` | **Conditional — public/OSS repos only.** Repository remote is public, an open-source license is present, and a `CONTRIBUTING.md` or equivalent contribution governance file exists (verify via repo remote or `gh api`); contribution norms, agent disclosure, or fork etiquette apply | Repository is private or enterprise-internal (non-public remote, no open-source license); record skip as "non-public repository." Also skip when no contribution-norm question arises even in a public repo | Contract, ledger |

## Change-surface coverage

Every mandated change surface maps to at least one row above. When a change
request touches one of these surfaces, the corresponding row's applicability
signal triggers:

| Change surface | Routing row(s) |
|---|---|
| Ambiguous scope | `product-discovery`, `product-methodology` |
| User-facing behavior | `product-design-and-ux`, `frontend-engineering`, `web-accessibility` |
| Architecture | `software-architecture-analysis`, `c4-diagramming`, `adr-authoring` |
| API/interface | `api-design-and-evolution` |
| Data (schema/migration) | `data-engineering`, `data-architect` |
| Implementation domain | `backend-engineering`, `frontend-engineering`, `cli-builder` |
| Security | `secure-software-engineering`, `security-audit-methodology` |
| AI/agent behavior | `agent-evals-and-observability` |
| Documentation | `technical-documentation` |
| Operational | `site-reliability-engineering`, `platform-engineering`, `release-engineering` |

Additional rows serve cross-cutting stages: `spec-driven-development`
(specification and decomposition), `systematic-debugging` (root-cause analysis),
`qa-methodology` (test strategy and verification planning),
`verification-methodology` (structured verdicts), and `programming-principles`
(implementation quality review).

## Multi-row composition

When several applicability signals trigger for one change (e.g., backend +
API + schema/migration), specialists **compose by stage**:

- **One lead per stage.** Each stage has exactly one lead specialist. No two
  rows own the same stage simultaneously.
- **Record per-stage leads.** The delivery packet group (e) records each
  selected skill with its stage lead — for example,
  "`backend-engineering` (lead: implementation),
  `api-design-and-evolution` (lead: contract design),
  `data-engineering` (lead: migration)."
- **Skipped rows still recorded.** Every row whose signal did not trigger is
  listed with its skip-rule reason, per the skip-transparency rule above.

## No-specialist-needed fallback

When **no** row's applicability signal triggers, work proceeds on the neckbeard
spine using the minimal stage methods in [stages.md](stages.md). The delivery
packet records: **"no specialist selected — no applicability signal triggered."**
This is a legitimate routing decision — not a silent omission and not a
fabricated skip reason.

## "Use the existing skill instead" conditions

Route entirely to a specialist — do **not** run the neckbeard spine — when:

- The task is a pure documentation job with no delivery-boundary risk →
  `technical-documentation`.
- The task is a self-contained debugging request and the user only wants the root
  cause and fix → `systematic-debugging` (neckbeard's ledger is still worth
  appending if the fix is non-trivial).
- The task is a formal spec authoring exercise → `spec-driven-development`.

## When no specialist is installed

neckbeard's [stages.md](stages.md) gives a minimal fallback method per stage.
Use it, but record in the ledger that the specialist skill was absent, so a
reviewer knows the method was the fallback rather than the full specialist.

## What neckbeard never does

- It does not re-implement a specialist's internal method.
- It does not override a repository's own contribution rules, review process, or
  human accountability.
- It does not automate privileged, destructive, deployment, or merge actions
  beyond the host agent's existing authority and confirmation controls.
- It does not treat a benchmark win as proof of production effectiveness.
