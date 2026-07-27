# Coordination And Authorized Operation

Load this reference when assigning ownership, aligning participants, defining transitions, or supporting an authorized activation or handoff.

## Decision Rights

Separate these responsibilities even when one person holds several:

| Responsibility | Required decision |
|---|---|
| Plan owner | Maintains the plan and convenes review. |
| Path owner | Maintains readiness evidence for one method. |
| Decision authority | Approves the plan and consequential exceptions. |
| Activation authority | Authorizes moving or activating under the local procedure. |
| Sender and receiver | Monitor, acknowledge, and follow the same current-tier procedure. |
| Exercise controller | Keeps a test inside its approved scope and stop conditions. |

Missing decision or activation authority is a blocking unknown for operation, not an invitation to infer authority.

## Endpoint Alignment

Before approving a path, confirm both ends agree on:

- who initiates and who acknowledges;
- what each participant monitors;
- contact and addressing procedure;
- check-in interval or event, if locally required;
- observable failure or degradation criteria;
- transition announcement and acknowledgment;
- fallback if the transition itself cannot be coordinated;
- recovery, return-to-primary, or handoff authority.

The plan-local procedure decides whether participants monitor multiple paths concurrently. Do not invent a monitoring burden that local staffing cannot sustain.

## Activation Sequence

Read-only planning may proceed without a mutation gate. Before a real transmission, activation, or live-system test:

1. Confirm the exact target system or path.
2. Confirm scope, participants, time window, and possible collateral effects.
3. Confirm how to stop and restore the prior state.
4. Confirm the named activation authority and applicable procedure permit the action.
5. Record the approved trigger evidence.
6. Execute only the approved action.
7. Record acknowledgment, outcome, and any handoff.

If any confirmation is missing, stop at recommendation or drafting.

## Transition And Recovery

Move tiers only when the approved observable criterion is met or the named authority directs an allowed exception. Record what failed, what evidence confirmed it, who decided, which path became current, and how participants were aligned.

Returning to a preferred path also needs a plan-local recovery criterion and decision authority. Availability alone does not prove stability or justify an uncoordinated return.
