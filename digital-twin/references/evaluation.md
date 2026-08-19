# Digital Twin: evaluation and health

## Evaluate five independent planes

Never collapse these into one health score:

1. **Represented-system health:** Is the software, process, asset, or service itself healthy?
2. **Synchronization/data health:** Is state timely, complete, authentic, ordered, and traceable?
3. **Model credibility:** Is the model verified, validated, calibrated, and appropriately uncertain for its declared use?
4. **Platform health:** Is the twin service correct, available, observable, secure, and performant?
5. **Agent/action quality:** Does the agent use the twin correctly, safely, and within authority?

A sick asset with an accurate twin is not a sick twin. A healthy system with large residuals suggests a sick model. A correct twin followed by an unsafe action is an agent or authority failure.

## Evaluation contract

Freeze represented entity, authoritative truth, intended decision, descriptive/predictive/prescriptive/closed-loop mode, permitted tools/actions, domain, versions, quantities of interest, tolerances, false-positive/false-negative/stale-answer costs, assumptions, limits, fallback, stop authority, and owner.

Use risk-scaled evidence. A visualization twin and an autonomous actuator twin do not require the same burden of proof.

## Synchronization and data metrics

- update latency: twin apply time minus source event time, by source and mode;
- state age and decision-boundary freshness;
- clock skew and timestamp quality;
- state disagreement against independently captured checkpoints;
- missing, duplicate, late, and out-of-order rates;
- field completeness, schema/range/unit validity, and cross-source consistency;
- provenance, integrity, and authenticity coverage;
- replay determinism and reconciliation success.

Replay golden traces while injecting loss, duplication, reordering, delay, source silence, clock skew, timestamp rollback, schema/unit changes, corruption, spoof/replay, and conflicting sources. Verify quality flags, uncertainty inflation, abstention, recovery, and no duplicate side effects.

## Verification, validation, and uncertainty

**Verification** asks whether the implementation correctly executes its model: unit/property tests, analytic or manufactured solutions, convergence, invariant checks, differential tests, metamorphic tests, interface contracts, and frozen-run reproducibility.

**Validation** asks whether the model represents the original well enough for the declared use: held-out paired data, normal/boundary/rare/OOD slices, mode and horizon stratification, predicted-versus-observed transitions, and independent runtime/control-plane evidence.

Maintain an uncertainty budget for inputs, parameters, initial/boundary conditions, numerical error, model-form discrepancy, surrogate error, synchronization age, and distribution shift. Evaluate coverage and sharpness of intervals, Brier/log/CRPS or equivalent proper scores, reliability, and critical-slice behavior. If uncertainty exceeds the actionability limit, downgrade to advisory or abstain.

## Software-twin metrics

Measure inventory coverage and stale/phantom components; dependency-edge precision/recall; configuration and semantic drift; runtime revision/replica/flag/queue/capacity match; event-sequence conformance; query correctness and stale/unknown rate; predicted versus observed canary blast radius; intended-action success; duplicate/partial/unreconciled effects; and event-to-state lag.

Never let the twin grade itself. Use independent snapshots, incident replays, shadow changes, bounded canaries, and post-action reconciliation.

## Agent evaluation

Define a task contract: inputs, allowed tools, expected outcome, prohibited outcomes, and evidence. Define a trajectory contract: tool choice/arguments, authorization, grounding, state transitions, recovery, stopping/escalation, and side effects.

Measure environment-verified success, decision regret, grounded-claim precision, correct twin queries, use of freshness/provenance/uncertainty, abstention/escalation, unauthorized actions, idempotency, rollback/recovery, loops/retries/timeouts, latency/cost, and reviewer disagreement. Unauthorized or unreconciled harmful effects are hard failures.

## SLOs and drift

Define good events over eligible events and document denominator, exclusions, delayed labels, sampling, missing-data behavior, slices, owner, and alert delay. Keep separate error budgets for synchronization, model credibility, platform reliability, and agent behavior.

Monitor source/schema, data, topology/state, model, simulator, policy/agent, and platform drift separately. Alert on persistence plus decision impact, not a p-value alone. A drift signal should lead to annotation, abstention, shadow, restricted authority, recalibration, rollback, or retirement.

## Chaos and stop gates

Exercise source silence, bias, corruption, spoof/replay, loss, duplication, reordering, skew, schema changes, conflicting sources, partitions, model timeout, bad parameters, OOD shift, tool denial, stale results, partial side effects, and feedback interruption. Each experiment needs a steady-state hypothesis, bounded scope, blast-radius limit, abort condition, safe fallback, and verified rollback.

Immediately stop actuation for unauthorized action, integrity failure, critical freshness breach, OOD input without approved behavior, invariant failure, missing provenance/version/policy, unavailable audit telemetry, or material predicted/observed divergence. Missing evidence is `hold`, not pass.

## Sources

- NISTIR 8356: https://csrc.nist.gov/pubs/ir/8356/final
- NIST Digital Twins for Advanced Manufacturing: https://www.nist.gov/programs-projects/digital-twins-advanced-manufacturing
- NASA-STD-7009: https://standards.nasa.gov/standard/NASA/NASA-STD-7009
- ASME VVUQ: https://www.asme.org/codes-standards/publications-information/verification-validation-uncertainty
- ISO/IEC 25024: https://www.iso.org/standard/35749.html
- Google SRE SLOs: https://sre.google/workbook/implementing-slos/
- Principles of Chaos Engineering: https://principlesofchaos.org/
- OpenTelemetry agent observability: https://opentelemetry.io/blog/2025/ai-agent-observability/
- Gneiting and Raftery, proper scoring rules: https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf
