# Discovery Brief — Production Readiness

## Survey scope

This brief surveys existing skills in the `magnus919/agent-skills` catalog as of
base commit `aa2f19b` (post wave 3) to establish ownership boundaries for the
production-readiness skill (#196). Every skill listed below exists in the
repository and is routed to by production-readiness via markdown links in
`SKILL.md`.

## Surveyed skills and ownership boundaries

### release-engineering

`release-engineering` owns the release pipeline: promotion stages, canary/ring
rollout, CI/CD gate configuration, versioning (SemVer), artifact management,
changelogs, SBOM/provenance, DORA metrics, and change-governance audit compliance.
It produces the *pipeline* gate answer (is the pipeline green?). Production-readiness
owns the *cross-domain evidence assembly* that feeds the launch decision (do we
have ownership, SLOs, security review, support runbooks, cost estimates assembled
and reviewed?). The two are complementary: release-engineering says the artifact
can be promoted; production-readiness says the evidence packet is complete enough
for a launch decision.

**Concrete boundary example:** When a team asks "is the CI pipeline green and are
the canary stages passing?", route to release-engineering. When they ask "do we
have the evidence packet ready for the launch-review board?", route to
production-readiness.

### site-reliability-engineering

`site-reliability-engineering` owns live-service health: SLO/SLI frameworks,
error-budget governance, incident command, blameless postmortems, on-call
rotations, monitoring and alerting design, toil elimination, and operational
maturity. It operates the *running* service. Production-readiness operates the
*pre-launch readiness boundary* — it asks whether SLOs are declared (and routes to
SRE for the SLO design itself), whether observability is instrumented (and routes
to SRE for the dashboard/alert design), whether runbooks exist (and routes to SRE
for the runbook content).

**Concrete boundary example:** When a team asks "what should our SLO be for this
service?" or "the error budget is burning, do we freeze features?", route to SRE.
When they ask "has the SLO been declared and linked in the readiness record before
launch?", route to production-readiness. Production-readiness checks *presence* of
the SLO evidence; SRE owns the SLO's *substance and live operation*.

### secure-software-engineering

Owns security requirements, threat modeling, secure defaults, authentication and
authorization design, untrusted-data handling, secrets management, dependency
evaluation, and security-sensitive code review. Production-readiness asks whether
a security review was completed and records its sign-off (or gap). It does not
perform the review itself.

### data-engineering

Owns database operations, ETL/ELT pipelines, data quality monitoring, schema
migration, and storage infrastructure. Production-readiness asks whether data
classification, retention/deletion policy, and migration test results exist. It
routes the actual data work to data-engineering.

### qa-methodology

Owns test strategy, regression testing, CI failure triage, test automation,
quality gates, risk-based testing, exploratory testing, and mutation-guided test
hardening. Production-readiness asks whether the QA sign-off exists for the
release candidate. It does not design the test plan.

### platform-engineering

Owns internal developer platforms, infrastructure-as-code, container
orchestration, service networking, secrets infrastructure, and observability
infrastructure. Production-readiness asks whether the platform dependencies
(quotas, networking, secrets access) are provisioned and tested. It does not
provision them.

### implementation-planning

Owns work breakdown, dependency mapping, critical-path analysis, ownership
assignment, sequencing, rollout strategy, and verification against requirements.
Production-readiness consumes the implementation plan's rollout and rollback
sections as evidence inputs. It does not create the plan.

### Others routed

- **spec-driven-development**: owns spec authoring and SDD phase gates.
  Production-readiness may reference the spec's acceptance criteria as outcome
  evidence.
- **verification-methodology**: owns verification verdicts against explicit
  criteria. Production-readiness routes boundary-verification questions there.
- **api-design-and-evolution**: owns API contracts and versioning.
  Production-readiness asks whether API compatibility is assessed for the
  release.
- **data-scientist**: owns statistical analysis and experimental design.
  Production-readiness routes questions about statistical validity of
  pre-launch experiments there.
- **production-excellence bundle** (future, wave 6): will compose
  production-readiness, migration-engineering, resilience-and-recovery,
  capacity-and-cost-engineering, and incident-learning into a full
  production-operations lifecycle. Production-readiness feeds its readiness
  record into that bundle's evidence packet. The bundle is referenced in prose
  only (not yet landed).

## What production-readiness does NOT own

- Release pipeline mechanics (release-engineering)
- Live-service SLO operations, incident response, on-call (SRE)
- Security implementation or threat modeling (secure-software-engineering)
- Data pipeline or schema migration engineering (data-engineering)
- Test strategy or QA gate design (qa-methodology)
- Platform infrastructure provisioning (platform-engineering)
- Implementation planning or work breakdown (implementation-planning)
- Spec authoring or SDD phase gates (spec-driven-development)
- Verification verdict mechanics (verification-methodology)
- API contract design (api-design-and-evolution)
- Statistical analysis (data-scientist)
- Full production-operations lifecycle orchestration (production-excellence bundle, future)

## Design rationale

Production-readiness fills the gap between "the pipeline is green" (release-engineering)
and "the service is healthy" (SRE). It is the structured evidence-assembly step that
happens before launch: collect the 11 evidence categories, scale by risk class, and
produce a decision with an accountable owner. Without it, teams either launch with
invisible gaps or duplicate readiness checks across every domain specialist.
