# Data Architecture Design Session

Use this worksheet to facilitate a decision session. Capture evidence and unresolved assumptions rather than filling gaps with consensus.

## Session Brief

- **Decision or problem:**
- **Business outcome and cost of inaction:**
- **Decision owner:**
- **Participants:** business, domain producers, consumers, data, platform, security, compliance
- **Date and decision deadline:**
- **Non-negotiable constraints:**
- **Evidence gaps:**

## Current State

### Flows and Ownership

- Sources and systems of record:
- Current transformations and storage:
- Operational consumers:
- Analytical, ML, and reporting consumers:
- Data owners and support paths:
- Current quality, freshness, availability, and incident evidence:

### Workloads

| Consumer/use case | Data needed | Access mode | Freshness/latency | Quality or recovery need |
|---|---|---|---|---|
| | | | | |

## Candidate Shapes

| Candidate | Problem it solves | New obligations | Key risks | Evidence needed |
|---|---|---|---|---|
| Centralized | | | | |
| Hybrid | | | | |
| Fabric capabilities | | | | |
| Mesh/domain products | | | | |
| Event-driven product | | | | |

Name what remains centralized and what becomes locally owned. For event-driven candidates, record replay, ordering, late data, compatibility, and consumer recovery decisions.

## Decision Record

- **Chosen shape and scope:**
- **Why it fits the evidence:**
- **Rejected alternatives and conditions that would change the decision:**
- **Ownership and decision rights:**
- **Product quality and service expectations:**
- **Governance checks and escalation path:**
- **Interface-contract handoff:** `api-design-and-evolution`
- **Implementation handoff:** `data-engineering`
- **Platform-operations handoff:** `platform-engineering`

## Experiments and Transition

| Hypothesis | Smallest experiment | Owner | Exit evidence | Reversible action |
|---|---|---|---|---|
| | | | | |

- **Phase 1 foundation:**
- **Phase 2 pilot:**
- **Phase 3 expansion or stop condition:**
- **Metrics:** consumer adoption, quality/freshness, incident recovery, delivery time, cost, and team load

## Open Risks

- Assumption that needs validation:
- Cross-domain dependency:
- Security, privacy, or compliance concern:
- Cost or capacity concern:
- Failure and recovery concern:
- Reason to keep the current architecture for now:
