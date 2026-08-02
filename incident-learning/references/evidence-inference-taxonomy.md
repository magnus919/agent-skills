# Evidence, Inference, and Uncertainty Taxonomy

Every incident learning record separates three categories. Conflating them produces false confidence and misdirected follow-up work. This reference defines each category, provides classification rules, and gives examples of correct and incorrect classification.

## The three categories

### Category 1: Observed facts (evidence)

**Definition:** What happened — claims backed by telemetry, logs, direct observation, or reproducible measurement. An observed fact is independently verifiable: a second observer with access to the same data would reach the same conclusion.

**Required attributes:**
- Source: where the observation came from (dashboard, log line, alert, witness statement, metric)
- Timestamp or time range: when it was observed
- Measurement: the concrete value or event (not an interpretation)

**Examples:**
- "The payment-service error rate exceeded 5% between 14:03 and 14:17 UTC on 2025-08-12. Source: payment-service dashboard, HTTP 5xx metric."
- "The database connection pool reached its maximum of 100 connections at 14:04:22 UTC. Source: db-pool-metrics, connection-count gauge."
- "The deployment of version v2.4.1 completed at 13:58 UTC. Source: CI/CD pipeline log, deploy step."

**Non-examples (these are inference, not facts):**
- "The deployment caused the error rate spike." (Causal inference — deployment preceded the spike, but causation is not observed)
- "The database was overwhelmed." (Interpretation — the pool maxed out, but "overwhelmed" is a judgment)
- "The team was not monitoring the right dashboard." (Inference about attention, not an observed event)

### Category 2: Causal hypotheses (inference)

**Definition:** Explanations of why something happened. A causal hypothesis connects observed facts into a causal narrative. It is an inference — it may be correct, partially correct, or incorrect. Every causal hypothesis must be labeled with a confidence level and at least one alternative explanation.

**Required attributes:**
- Hypothesis statement: the proposed causal explanation
- Supporting evidence: which observed facts support this hypothesis
- Confidence level: high / medium / low, with brief justification
- Alternative explanations: at least one competing hypothesis that could also explain the observed facts
- Testability: how this hypothesis could be validated or invalidated

**Confidence levels:**
- **High**: supported by multiple independent evidence sources; alternative explanations have been tested and ruled out; the causal mechanism is well-understood.
- **Medium**: supported by some evidence; alternative explanations are plausible but less consistent with the evidence; the causal mechanism is understood but not fully validated.
- **Low**: consistent with the evidence but not strongly supported; alternative explanations are equally plausible; the causal mechanism is speculative.

**Examples:**
- "Hypothesis: The v2.4.1 deployment introduced a connection-pool misconfiguration that caused connections to not be released after use. Confidence: medium. Supporting evidence: the pool exhaustion began within 5 minutes of the deployment completing; the deployment diff included a connection-pool configuration change. Alternative: a traffic spike coincident with the deployment overwhelmed the pool at its previous capacity. Testability: reproduce the deployment with the previous pool configuration and observe connection behavior."
- "Hypothesis: The alert did not fire because the alert rule had a 10-minute sustained threshold and the error burst lasted 8 minutes. Confidence: high. Supporting evidence: alert rule definition specifies 10-minute window; error duration measured at 8 minutes. Alternative: the alerting pipeline was down during the incident window. Testability: check alerting pipeline availability logs for the incident window."

**Non-examples:**
- "The deployment was the root cause." (No confidence level, no alternatives, no supporting evidence)
- "Someone made a mistake." (Blame language, not a causal hypothesis)
- "The system is fragile." (Vague, untestable, no mechanism)

### Category 3: Unresolved uncertainty

**Definition:** What remains unknown — open questions, competing hypotheses that could not be resolved, missing data, and conditions that cannot be determined from available evidence. Unresolved uncertainty is not a failure of analysis; it is a structural part of the learning record that drives investigation follow-up work.

**Required attributes:**
- Question or uncertainty statement
- Why it matters: what decision or follow-up work depends on resolving it
- What would resolve it: what data, observation, or experiment would answer the question
- Status: open / investigation in progress / cannot be resolved with available data

**Examples:**
- "Uncertainty: We do not know whether the connection-pool exhaustion also affected other services that share the same database cluster. Why it matters: if other services were affected, the incident scope is larger than documented. What would resolve it: connection-pool metrics for all services sharing the cluster during the incident window."
- "Uncertainty: Competing hypotheses — the error rate spike could be from the deployment OR from a coincident upstream traffic pattern change. Both are consistent with the observed facts. Why it matters: the follow-up work is different (rollback vs. rate limiting). What would resolve it: reproduce the deployment in a staging environment with the same traffic pattern; observe whether the pool exhaustion reproduces."
- "Uncertainty: The exact sequence of 14:03:00–14:03:30 is missing from our logs due to a log-buffer overflow during the incident. Why it matters: the initial trigger event may be in the gap. What would resolve it: cannot be resolved — the data is permanently lost. Mitigation: improve log-buffer sizing to prevent gap in future incidents."

**Non-examples:**
- "We're not sure what happened." (Too vague — what specifically is uncertain?)
- "Maybe it was a network issue." (This is a hypothesis, not an uncertainty statement — include it in Category 2)

## Classification rules

1. **If it can be independently verified from a named source, it belongs in observed facts.** If there is no source, it is not an observed fact.
2. **If it explains why something happened, it belongs in causal hypotheses.** Even if you are confident, an explanation is an inference — label it with confidence and alternatives.
3. **If it is a question you cannot answer from available evidence, it belongs in unresolved uncertainty.** The fact that you cannot answer it is itself a finding.
4. **A statement that begins with "the team thinks," "we believe," "it seems," or "probably" is a hypothesis (Category 2), not a fact (Category 1).** Rephrase it as a hypothesis with confidence and alternatives.
5. **A postmortem timeline event (what happened at time T) is an observed fact if it has a source; a postmortem "why" or "root cause" is a hypothesis (Category 2).** Timelines document facts; root causes are inferences.
6. **Blame statements ("who caused this") do not belong in any category.** They are not facts (no source for fault), not useful hypotheses (no causal mechanism), and not uncertainty (they are assertions). Exclude them.

## Common classification errors

| Statement | Incorrect classification | Correct classification | Reason |
|---|---|---|---|
| "The deployment broke production." | Observed fact | Causal hypothesis (low confidence without supporting evidence) | Causation is inferred, not observed; the deployment and the breakage are temporally correlated |
| "The database was under-provisioned." | Observed fact | Causal hypothesis | "Under-provisioned" is a judgment about capacity relative to demand; the observed fact is "connection pool maxed at 100 connections" |
| "We don't know what caused it." | Causal hypothesis | Unresolved uncertainty | This is a statement about the state of knowledge, not an explanation |
| "The on-call responded in 4 minutes." | Causal hypothesis | Observed fact (if sourced: pager log, timestamp) | If sourced, this is a verifiable event |
| "The system wasn't designed for this load." | Observed fact | Causal hypothesis | "Designed for" is an inference about intent and capacity; the observed fact is the load exceeded capacity at a specific threshold |

## Using this taxonomy in the learning record

The incident-learning record template requires these three sections. When completing the record:

1. Start with observed facts. List every verifiable event with its source. Do not explain; do not interpret. If you cannot name a source, move the statement to hypotheses or uncertainty.
2. For each causal hypothesis, identify which observed facts it explains. State confidence and at least one alternative. A hypothesis that explains no facts is speculation; either find supporting evidence or downgrade to uncertainty.
3. For each unresolved question, state why it matters and what would resolve it. An uncertainty that changes no decision can be noted but does not require follow-up work. An uncertainty that would change a follow-up work domain, owner, or approach requires an investigation follow-up item.
