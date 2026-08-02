# Causal/Evidence Ledger

Track each causal claim from the incident learning record with its supporting evidence, confidence, alternatives, and disposition. This ledger is the evidentiary backbone of the learning record — it ensures every causal statement is traceable to observed facts and that alternative explanations are not silently discarded.

## Ledger

| Claim ID | Causal claim | Source (learning record hypothesis #) | Supporting evidence (fact #s) | Confidence | Alternative explanations considered | Evidence against alternatives | Disposition | Disposition date |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |
| | | | | | | | | |

## Field definitions

| Field | Description |
|---|---|
| **Claim ID** | Unique identifier for this causal claim |
| **Causal claim** | The causal statement — what is claimed to have caused what |
| **Source** | Link to the hypothesis in the incident learning record |
| **Supporting evidence** | Observed facts (by fact #) that support this claim |
| **Confidence** | High / Medium / Low, with brief justification |
| **Alternative explanations considered** | Competing causal hypotheses that were evaluated |
| **Evidence against alternatives** | Why the alternatives were ruled out or downgraded |
| **Disposition** | Accepted / Rejected / Unresolved / Superseded by (claim ID) |
| **Disposition date** | When the disposition was determined |

## Disposition rules

- **Accepted**: The causal claim is the best-supported explanation. Supporting evidence is strong; alternatives are ruled out or significantly less consistent.
- **Rejected**: The causal claim is inconsistent with the evidence. An alternative explanation is better supported.
- **Unresolved**: Evidence is insufficient to accept or reject. This becomes an unresolved uncertainty in the learning record and drives investigation follow-up work.
- **Superseded by**: A later analysis produced a better causal claim that replaces this one. Reference the superseding claim ID.

## Confidence calibration

| Confidence | Evidence standard |
|---|---|
| **High** | Multiple independent evidence sources; alternatives tested and ruled out; causal mechanism well-understood and reproducible. |
| **Medium** | Some evidence supports the claim; alternatives are plausible but less consistent with the evidence; causal mechanism is understood but not fully validated. |
| **Low** | Claim is consistent with evidence but not strongly supported; alternatives are equally or nearly equally plausible; causal mechanism is speculative. |

## Ledger integrity rules

1. Every causal claim in the learning record must appear in the ledger.
2. Every accepted claim must have at least one supporting evidence reference (fact #) and at least one alternative explanation that was considered.
3. No claim may be accepted with "low" confidence without explicit justification for why the best-available explanation is sufficient for follow-up work despite low confidence.
4. Rejected claims remain in the ledger — they are not deleted. The rejection reason is recorded.
5. Unresolved claims must have a linked investigation follow-up item in the follow-up work map.
