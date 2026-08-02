# Discovery Brief: Resilience and Recovery

## Survey scope

This brief surveys adjacent skills in the agent-skills catalog to define the ownership boundaries of `resilience-and-recovery`. The goal is to own resilience design, exercise evidence, and recovery verification — without duplicating incident command, infrastructure implementation, backup operations, security incident response, release mechanics, or post-incident learning.

## Skills surveyed

### site-reliability-engineering

**What SRE owns:** Incident command, on-call operations, SLO/SLI framework, error budget governance, blameless postmortems, monitoring and alerting, toil elimination, and product-focused reliability.

**Boundary:** SRE owns the live operational response to incidents — the incident command system, real-time alerting, and post-incident postmortem process. It does not own the pre-incident resilience design method, the exercise-evidence standard, or the recovery-plan template. SRE's postmortem process produces follow-up actions; resilience-and-recovery's exercise method produces follow-up work from game days and restore tests.

**Routing decision:** Resilience-and-recovery routes live incident command and on-call operations to SRE. SRE's postmortem and incident-command references are the authoritative sources for incident response. Resilience-and-recovery owns the resilience plan, exercise design, and recovery verification — the work that happens before and between incidents.

### platform-engineering

**What platform engineering owns:** Infrastructure as code, CI/CD pipeline implementation, container orchestration, service networking, secret management, and cloud architecture. It builds and operates the delivery platform.

**Boundary:** Platform engineering owns the implementation of infrastructure that satisfies resilience requirements. Resilience-and-recovery owns the resilience requirements themselves: what the infrastructure must withstand, how recovery must behave, and how that behavior is verified through exercises. Platform engineering implements the circuit breaker; resilience-and-recovery defines the degradation path and verifies it in a game day.

**Routing decision:** Resilience-and-recovery routes infrastructure implementation to platform-engineering. Platform engineering's IaC patterns and service-networking references are the authoritative sources for implementation. Resilience-and-recovery owns the requirements, the exercise design, and the evidence standard.

### data-engineering

**What data engineering owns:** Backup strategy implementation, WAL archiving, snapshot management, database migration patterns, data quality monitoring, and storage infrastructure. It operates the data stores.

**Boundary:** Data engineering owns the backup implementation — the mechanics of taking backups, managing WAL archives, and scheduling snapshots. Resilience-and-recovery owns the restore-testing evidence and data-integrity verification protocol: proving that backups can actually be restored within the RTO, and that restored data is correct and consistent. A backup that passes data engineering's integrity check is necessary but not sufficient; resilience-and-recovery requires a full end-to-end restore exercise with application-level validation.

**Routing decision:** Resilience-and-recovery routes backup implementation and pipeline operations to data-engineering. Data engineering's backup-and-recovery reference is the authoritative source for backup mechanics. Resilience-and-recovery owns the restore exercise, the data-integrity verification after restore, and the RTO/RPO decision record that the backup strategy must satisfy.

### secure-software-engineering

**What secure-software-engineering owns:** Security requirements, threat modeling, secure design, authentication and authorization, input validation, secrets lifecycle, dependency supply chain, and secure code review. It builds security into decisions before defects reach production.

**Boundary:** Secure-software-engineering owns the security posture of the system — preventing and containing security incidents. Resilience-and-recovery owns the resilience dimension of security incidents: ensuring that recovery capability survives a security event. If a system is compromised, can it be restored from a known-good backup? Is the backup air-gapped or immutable? Has the restore been tested? These are resilience questions that security engineering surfaces but does not own.

**Routing decision:** Resilience-and-recovery routes security incident containment and forensics to secure-software-engineering. Secure-software-engineering's threat-modeling and incident-learning references are the authoritative sources for security posture. Resilience-and-recovery owns the recovery-from-security-event path: the restore procedure, the data-integrity verification after a security restore, and the exercise that proves it.

### release-engineering

**What release-engineering owns:** Release process design, CD pipeline architecture, progressive delivery, feature flags, versioning and artifacts, readiness gates, rollback and recovery planning, change governance, and DORA metrics.

**Boundary:** Release-engineering owns the release mechanics — how code moves from commit to production, how rollbacks are executed, and how progressive delivery manages risk. Resilience-and-recovery owns the resilience verification of those mechanics: does the rollback actually work under failure conditions? Has the failover been exercised? The release engineer designs the rollback runbook; resilience-and-recovery designs the game day that tests it.

**Routing decision:** Resilience-and-recovery routes release rollout, progressive delivery, and rollback mechanics to release-engineering. Release-engineering's rollback-planning and progressive-delivery references are the authoritative sources for release mechanics. Resilience-and-recovery owns the exercise that verifies those mechanics and the evidence that results.

### incident-learning (wave 5, not yet landed)

**What incident-learning will own:** Separation of observed facts from causal hypotheses and contributing conditions; mapping follow-up work across code, tests, skills, operations, product, and governance; closure defined as verification that the intended change occurred. It is the pipeline that converts incident findings into verified, owned follow-up work.

**Boundary:** Incident-learning will own the post-incident learning pipeline — taking an incident or near-miss and producing verified, owned follow-up work with closure evidence. Resilience-and-recovery feeds exercise and DR test findings into that pipeline. A game day that exposes a restore gap produces findings; incident-learning tracks those findings to verified closure.

**Routing decision:** Resilience-and-recovery routes exercise and DR findings to incident-learning for cross-incident pattern analysis and verified follow-up closure. Resilience-and-recovery owns the exercise design and the finding capture; incident-learning owns the verified closure pipeline.

### production-excellence bundle (wave 6, not yet landed)

**What production-excellence will own:** Composing production-readiness, migration-engineering, resilience-and-recovery, capacity-and-cost-engineering, and incident-learning into a unified production evidence packet with go/no-go/defer/exception outcomes.

**Boundary:** Production-excellence will consume resilience evidence — exercise results, RTO/RPO decision records, follow-up work ledgers — as input to production readiness decisions. Resilience-and-recovery produces the resilience dimension of that evidence packet.

**Routing decision:** Resilience-and-recovery feeds the production-excellence bundle. The resilience evidence this skill produces (exercise results, decision records, follow-up ledgers) is a required input to the production-excellence go/no-go/defer/exception decision.

## What resilience-and-recovery does NOT own

- **Incident command**: owned by SRE. Resilience-and-recovery does not manage live incidents or run incident response.
- **Infrastructure implementation**: owned by platform engineering. Resilience-and-recovery does not write Terraform, configure Kubernetes, or build CI/CD pipelines.
- **Backup mechanics**: owned by data engineering. Resilience-and-recovery does not implement backup schedules, WAL archiving, or snapshot management.
- **Security incident containment**: owned by secure-software-engineering. Resilience-and-recovery does not contain threats or perform forensics.
- **Release mechanics**: owned by release-engineering. Resilience-and-recovery does not design release pipelines or progressive-delivery strategies.
- **Post-incident learning pipeline**: owned by incident-learning (wave 5). Resilience-and-recovery feeds findings into that pipeline but does not own the verified-closure process.
- **Production readiness decisions**: owned by the production-excellence bundle (wave 6). Resilience-and-recovery provides resilience evidence as input but does not make the go/no-go call.

## Summary

Resilience-and-recovery fills a gap between design-time resilience planning (which SRE, platform, data, security, and release engineering each touch from their own angle) and verified recovery capability. It is the method for designing resilience, exercising it, and proving it — producing evidence that feeds downstream decisions in incident-learning and production-excellence.
