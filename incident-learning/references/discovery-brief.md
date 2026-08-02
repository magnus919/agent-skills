# Discovery Brief: Incident Learning

## Survey scope

This brief surveys adjacent skills in the agent-skills catalog to define the ownership boundaries of `incident-learning`. The goal is to own the conversion of operational incident evidence into verified, owned follow-up work — without duplicating incident command, postmortem facilitation, test design, eval implementation, product-outcome review, delivery planning, resilience exercise design, or production-readiness decisions.

## Skills surveyed

### site-reliability-engineering

**What SRE owns:** Incident command, on-call operations, SLO/SLI framework, error budget governance, blameless postmortems, monitoring and alerting, toil elimination, and product-focused reliability.

**Boundary:** SRE owns the live operational response to incidents — the incident command system, real-time alerting, postmortem facilitation, and postmortem document production. It does not own the post-postmortem learning pipeline: converting postmortem findings into verified, cross-domain follow-up work with closure evidence. SRE's postmortem process produces action items; incident-learning owns the structured record that separates evidence from inference, maps escaped-from gaps, assigns domain-specific follow-up work, and tracks each finding to verified closure.

**Routing decision:** Incident-learning routes live incident command, on-call operations, and postmortem facilitation to SRE. SRE's incident-command and postmortem references are the authoritative sources for incident response and postmortem production. Incident-learning owns the learning pipeline that consumes postmortem output and produces verified, owned improvements.

### qa-methodology

**What QA methodology owns:** Test strategy, regression testing, CI failure triage, test automation, quality gates and metrics, risk-based testing, exploratory testing, mutation-guided test hardening, agentic eval design, and SDET engineering.

**Boundary:** QA methodology owns the design and implementation of tests. Incident-learning owns the identification of test gaps from incident evidence and the mapping of those gaps to test follow-up work. When an incident reveals missing regression coverage, weak assertions, or untested failure paths, incident-learning records the gap and creates a test-domain follow-up item; QA methodology designs and implements the test that closes it. Incident-learning verifies closure — it confirms the test was added and catches the failure mode — but does not design the test itself.

**Routing decision:** Incident-learning routes test design and implementation to QA methodology. Incident-learning owns the gap identification, follow-up work mapping, and closure verification. QA methodology owns the test design and implementation that satisfies the follow-up work.

### verification-methodology

**What verification methodology owns:** Pass/fail assessment against explicit criteria using direct, source-faithful evidence, reproducible checks, and clear verdicts.

**Boundary:** Verification methodology owns the protocol for producing verification evidence — the method for checking whether a change satisfies its criteria. Incident-learning owns the closure standard that requires verification evidence and the closure record that holds it. Every incident-learning follow-up work item has a verification method field; verification-methodology provides the protocol for executing that verification and producing the evidence. Incident-learning does not re-derive the verification protocol; it consumes the verdict.

**Routing decision:** Incident-learning routes verification execution to verification-methodology. Incident-learning owns the closure standard (what constitutes verified closure) and the closure record; verification-methodology owns the verification protocol that produces the evidence.

### agent-evals-and-observability

**What agent evals and observability owns:** Evaluation design, dataset management, grader selection and calibration, trajectory review, regression analysis, release gates, production traces, and privacy-aware telemetry for AI agents.

**Boundary:** Agent evals and observability owns the design and operation of agent evaluation systems. Incident-learning owns the identification of eval gaps from agent incidents — missing eval cases, inadequate grader coverage, unobserved failure modes, dataset blind spots. When an agent incident reveals that an eval case would have caught the failure, incident-learning records the gap and creates an evals-domain follow-up item; agent-evals-and-observability designs and implements the eval. Incident-learning verifies closure: the eval case exists and catches the failure mode.

**Routing decision:** Incident-learning routes eval design and implementation to agent-evals-and-observability. Incident-learning owns the gap identification, follow-up work mapping, and closure verification. Agent-evals-and-observability owns the eval design and implementation.

### product-lifecycle-learning

**What product lifecycle learning owns:** Post-launch outcome review, evidence-backed assumption ledger, feature health assessment, continue/improve/harvest/pivot/pause/retire decisions, and retirement lifecycles with deprecation and migration.

**Boundary:** Product lifecycle learning owns the product-outcome learning loop — comparing intended outcomes against observed results and making lifecycle decisions. Incident-learning owns the incident-to-product-improvement pipeline. When an incident reveals a product assumption failure (a feature used differently than intended, a user need that was missed, a design choice that produced operational risk), incident-learning records the gap and creates a product-domain follow-up item; product-lifecycle-learning updates the assumption ledger and assesses feature health. The two skills meet at the product-domain follow-up: incident-learning identifies the product gap; product-lifecycle-learning owns the assumption-update and lifecycle decision.

**Routing decision:** Incident-learning routes product assumption updates and lifecycle decisions to product-lifecycle-learning. Incident-learning owns the incident-to-product-gap mapping; product-lifecycle-learning owns the assumption ledger and feature-health decisions.

### implementation-planning

**What implementation planning owns:** Delivery planning for approved requirements, work breakdown, dependency mapping, critical path, ownership, parallelism and sequencing, rollout strategy, rollback and recovery paths, and verification against the original requirement.

**Boundary:** Implementation planning owns the coordinated delivery of cross-domain, cross-team follow-up work. Incident-learning owns the follow-up work map — identifying what needs to be done and in which domain. When follow-up work spans multiple teams or repositories, incident-learning's follow-up work map feeds into implementation-planning's delivery plan. Implementation-planning sequences and coordinates the work; incident-learning tracks each item to verified closure.

**Routing decision:** Incident-learning routes cross-team, multi-repo follow-up coordination to implementation-planning. Incident-learning owns the follow-up work identification and closure tracking; implementation-planning owns the delivery coordination.

### resilience-and-recovery

**What resilience-and-recovery owns:** Resilience design, failure-mode analysis, graceful degradation, RTO/RPO decision records, restore testing, game days, failover drills, data integrity verification, and recovery communication.

**Boundary:** Resilience-and-recovery owns the pre-incident resilience design and exercise-evidence method. Incident-learning owns the post-incident and post-exercise learning pipeline. Exercise and DR test findings feed into incident-learning for cross-incident pattern analysis and verified follow-up closure. A game day that exposes a restore gap produces findings in resilience-and-recovery's follow-up work ledger; incident-learning consumes those findings, enriches them with the evidence/inference/uncertainty taxonomy, maps escaped-from gaps, and tracks closure with verification evidence.

**Routing decision:** Incident-learning consumes exercise and DR findings from resilience-and-recovery. Resilience-and-recovery owns the exercise design and finding capture; incident-learning owns the cross-incident pattern analysis and verified closure pipeline. The two skills are complementary: resilience-and-recovery produces exercise findings; incident-learning converts them into verified, domain-mapped improvements.

### production-readiness

**What production-readiness owns:** Minimum production evidence packet by risk class, go/no-go/defer/exception launch decisions, cross-domain evidence assembly with named sources or explicit missing-evidence outcomes.

**Boundary:** Production-readiness owns the launch decision — assembling cross-domain evidence and producing a go/no-go recommendation. Incident-learning owns the post-incident learning evidence that feeds into future launch decisions. When incident-learning findings reveal systemic gaps (a recurring escaped requirement, a pattern of monitoring gaps across services), those findings become evidence in the production-readiness packet for the next launch. Production-readiness consumes incident-learning records as one category of readiness evidence.

**Routing decision:** Incident-learning feeds evidence into production-readiness. Incident-learning owns the learning record production; production-readiness owns the launch decision that consumes those records as evidence.

### production-excellence bundle (not yet landed)

**What production-excellence will own:** Composing production-readiness, migration-engineering, resilience-and-recovery, capacity-and-cost-engineering, and incident-learning into a unified production evidence packet with go/no-go/defer/exception outcomes.

**Boundary:** Production-excellence will consume incident-learning records, causal ledgers, follow-up work maps, and closure records as input to cross-incident pattern analysis. Incident-learning produces the learning dimension of the production-excellence evidence packet.

**Routing decision:** Incident-learning feeds the production-excellence bundle. The learning records this skill produces are a required input to the production-excellence analysis and decision framework.

### agent-production-operations bundle (not yet landed)

**What agent-production-operations will own:** Operational management of AI agents in production — deployment, monitoring, governance, cost management, and operational learning specific to agent systems.

**Boundary:** Agent-production-operations will consume incident-learning records specific to agent incidents — agent authority failures, unexpected agent behaviors, eval gaps exposed in production — as input to agent-specific operational learning and governance decisions.

**Routing decision:** Incident-learning feeds the agent-production-operations bundle. Agent-incident learning records are a required input to agent-specific operational learning and governance.

## What incident-learning does NOT own

- **Incident command and live response**: owned by site-reliability-engineering. Incident-learning does not manage live incidents or run incident response.
- **Postmortem facilitation**: owned by site-reliability-engineering. Incident-learning consumes postmortem output; it does not produce postmortem documents or facilitate postmortem sessions.
- **Root-cause debugging**: owned by systematic-debugging. Incident-learning consumes debugging findings; it does not investigate failures.
- **Test design and implementation**: owned by qa-methodology. Incident-learning identifies test gaps; QA methodology designs and implements tests.
- **Eval design and implementation**: owned by agent-evals-and-observability. Incident-learning identifies eval gaps; agent-evals-and-observability designs evals.
- **Product assumption updates and lifecycle decisions**: owned by product-lifecycle-learning. Incident-learning identifies product gaps; product-lifecycle-learning updates assumptions and makes lifecycle decisions.
- **Cross-team delivery coordination**: owned by implementation-planning. Incident-learning identifies follow-up work; implementation-planning coordinates delivery.
- **Resilience exercise design**: owned by resilience-and-recovery. Incident-learning consumes exercise findings; resilience-and-recovery owns exercise design.
- **Launch decisions**: owned by production-readiness. Incident-learning feeds evidence into production-readiness; it does not make go/no-go calls.

## Summary

Incident-learning fills the gap between incident response (which SRE owns) and the implementation of follow-up work (which specialist skills own per domain). It is the pipeline that converts raw incident evidence into structured learning records with separated facts, hypotheses, and uncertainty; maps escaped-from gaps; assigns domain-specific follow-up work with ownership; and tracks every finding to verified closure — refusing to close on tickets alone. Its output feeds downstream decisions in resilience-and-recovery (cross-incident pattern analysis), production-readiness (launch evidence), production-excellence (unified evidence packet), and agent-production-operations (agent-specific operational learning).
