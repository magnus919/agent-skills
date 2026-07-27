# Troubleshooting

Load this reference when a planned path is degraded, unavailable, unacknowledged, or behaving differently from the approved plan.

## Bound The Diagnosis

State the communication pair, operational need, expected current tier, observed symptom, time first observed, and evidence source. Separate an unconfirmed report from a directly observed failure.

Do not provide equipment commands, frequencies, channel changes, credential workarounds, or regulatory advice unless they come from the user's authorized local procedure.

## Diagnostic Sequence

1. **Confirm the plan state.** Which tier should both endpoints be using, and what trigger or decision established that state?
2. **Confirm alignment.** Are sender and receiver using the same approved procedure, and can each detect or acknowledge the other?
3. **Check endpoint readiness.** Record only authorized checks of power, equipment readiness, trained staffing, addressing, and local environment.
4. **Check path dependencies.** Determine whether device, power, provider, network, site, gateway, relay, authentication, staffing, or transport dependencies are degraded.
5. **Check fallback independence.** Determine whether the proposed next tier shares the observed or suspected failure domain.
6. **Apply transition criteria.** If the current tier meets its abandonment criterion, present the evidence to the named authority or follow the already authorized procedure.
7. **Recover or hand off.** Record the selected tier, acknowledgment, unresolved uncertainty, and ownership of restoration work.
8. **Preserve the decision.** Use `templates/troubleshooting-decision-log.md` and create a corrective action when the plan or readiness evidence was inadequate.

## Stop Conditions

Stop troubleshooting and hand off when:

- an action would exceed the user's authority or applicable procedure;
- immediate danger requires emergency services or incident leadership;
- the next check would be destructive or irreversible;
- further diagnosis is not narrowing the cause and the local procedure calls for escalation or qualified handoff;
- no approved path remains;
- evidence conflicts and the conflict affects safe operation.

Do not label a path restored until both endpoints complete the plan's verification method. A locally successful device check is not end-to-end communication evidence.
