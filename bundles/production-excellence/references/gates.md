# Gate and Exception Model

The production-excellence gate model defines five discrete outcomes for every
production change. Each outcome requires specific conditions and evidence;
no outcome is reachable on a bare checklist.

## Guiding principles

- **Service ownership**: every gate decision names the service owner accountable
  for the outcome.
- **Risk**: the risk class (Low / Standard / High per
  [production-readiness](../../production-readiness/SKILL.md)) determines which
  evidence domains are required and which gates are applicable.
- **Evidence**: no gate passes without evidence from the production evidence
  packet ([evidence-packet.md](evidence-packet.md)). A missing-evidence gap is
  acceptable only when the risk class permits it and the gap is explicitly
  recorded with an owner and due date.
- **Verification**: evidence must be verified at the declared boundary (component,
  integration, end-to-end, or production per
  [verification-methodology](../../verification-methodology/SKILL.md)). An
  unverified claim does not satisfy an evidence requirement.

## Outcomes

### Go

**Meaning**: the change is authorized to proceed to production.

**Conditions**:

- All evidence domains required for the risk class are sourced (not gapped).
- The readiness decision from [production-readiness](../../production-readiness/SKILL.md)
  is "Go."
- Migration evidence (if applicable) confirms a verified recovery path.
- Resilience evidence (if required by risk class) includes a recent exercise result.
- Capacity and cost model (if required) shows the change is within budget and
  capacity constraints, with explicit assumptions.
- Incident-learning review (if applicable) confirms no unclosed follow-up items
  relevant to this change.
- Security review (if trust-boundary change) is complete.
- Release plan is documented and approved.
- QA verification evidence is present.

**Evidence required**: the complete production evidence packet with all domains
sourced or explicitly marked not-applicable.

**Accountable owner**: the service owner, who signs off on the Go decision.

### No-go

**Meaning**: the change is blocked and must not proceed.

**Conditions** (any one is sufficient):

- A required evidence domain has a blocking gap (e.g., no restore test for a
  High-risk launch, no security review for a trust-boundary change).
- The readiness decision is "No-go."
- A migration has no verified recovery path and the step is irreversible.
- An incident-learning review reveals an unclosed follow-up item that would be
  exacerbated by this change.
- A cost/SLO conflict cannot be resolved (the change would violate an SLO, and
  no budget increase or SLO relaxation is authorized).
- A dependency outage assessment shows the change would create an unacceptable
  blast radius.

**Evidence required**: the gap or condition that triggered the No-go, recorded
with the specific domain, the missing evidence, and the accountable owner who
can resolve it.

**Accountable owner**: the service owner records the No-go; the owner of the
blocking gap is named as the resolver.

### Defer

**Meaning**: the change is postponed to a later date with explicit conditions
for re-evaluation.

**Conditions**:

- The change is not blocked permanently (it is not a No-go), but:
  - A required evidence domain has a non-blocking gap with a committed due date.
  - A dependency (e.g., an upstream service's readiness, a platform capability)
    is not yet available but has a committed delivery date.
  - A cost/SLO conflict requires a budget or SLO decision that is in progress
    but not yet authorized.
  - The risk window (e.g., a holiday freeze, a peak-traffic period) makes the
    current timing unsuitable.

**Evidence required**: the deferral reason, the condition for re-evaluation, the
committed date or trigger event, and the owner responsible for meeting the
condition.

**Accountable owner**: the service owner records the Defer; the owner of the
deferral condition is named with the committed resolution date.

### Exception

**Meaning**: the change proceeds despite a gap, under an explicit waiver with
named approval authority.

**Conditions**:

- A required evidence domain has a gap that would normally produce a No-go, but:
  - An explicit human authority (not the service owner, not the agent) approves
    the exception.
  - The exception is time-bounded (an expiration date or post-launch condition).
  - The exception is risk-bounded (what specifically is waived, and what is not).
  - The exception is recorded with the approving authority's name and the date
    of approval.
- The exception does not waive security review for trust-boundary changes
  (a hard constraint — see Escalation).

**Evidence required**: the exception record with the waived domain, the
approving authority, the approval date, the expiration or post-launch
condition, and the accountable service owner.

**Accountable owner**: the approving authority (the human who granted the
exception). The service owner records the exception and tracks the post-launch
condition.

### Escalation

**Meaning**: the decision cannot be made within the bundle's authority and must
be escalated to a higher decision body.

**Conditions** (any one is sufficient):

- A security review for a trust-boundary change cannot be completed and no
  exception is authorized (security is a hard constraint — never waived without
  a security authority).
- Two or more gate outcomes are in irreconcilable conflict (e.g., the readiness
  review says Go but the capacity model shows an SLO violation with no
  authorized budget increase).
- The service owner and the readiness reviewer disagree on the outcome and
  neither has the authority to resolve the disagreement.
- A cross-team dependency blocks the change and the dependency owner is not
  accountable to the service owner (organizational escalation).
- The change crosses a regulatory or compliance boundary and the bundle lacks
  the domain expertise to assess it.

**Evidence required**: the escalation record with the specific conflict or gap,
the parties involved, the decision body being escalated to, and the accountable
owner who initiated the escalation.

**Accountable owner**: the initiator of the escalation (service owner or
readiness reviewer). The escalation itself names the target decision body.

## Gate applicability by risk class

| Outcome | Low risk | Standard risk | High risk |
|---|---|---|---|
| **Go** | Lightweight: readiness + release + QA evidence sufficient | All applicable domains sourced | All domains sourced; no gaps permitted |
| **No-go** | Blocking gap in any required domain | Blocking gap; irreversible migration without recovery; unresolved incident | Any gap in any domain; no exceptions for High risk without escalation |
| **Defer** | Non-blocking gap with due date | Dependency or timing constraint | Only timing constraints (e.g., freeze window); no evidence gaps deferrable |
| **Exception** | Service owner may self-approve with recorded rationale | Explicit human authority required; time-bounded | Escalation required (High-risk exceptions are escalated, not granted locally) |
| **Escalation** | Security hard-constraint, cross-team authority gap, regulatory boundary | Same as Low, plus irreconcilable gate conflict | Same as Standard; any High-risk exception is escalated |

## Post-gate: operational handoff

After a gate outcome is reached, the operational handoff record
([handoff-record.md](handoff-record.md)) is populated. For Go and Exception
outcomes, the handoff includes the launch evidence and the post-launch learning
path. For No-go, Defer, and Escalation outcomes, the handoff records the
blocking condition and the follow-up path.
