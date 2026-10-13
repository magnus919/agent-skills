# Reward and verifier contract

Revision/date/owner:
Experiment hypothesis and failure hypothesis:

## Independent task truth

- Input/output and parser contract; how ambiguous/extra verdicts are handled:
- Trusted reference or human/domain labels with evidence pointers:
- Gold solution must pass; broken starting solution must fail:
- Training reward tests; development tests; sealed final acceptance tests:
- Source/task families, known test gaps and pretraining contamination limits:
- Verifier code/suite/reference/environment hashes:

## Incentives

| Component | Observable property | Range/weight | Failure behavior |
|---|---|---|---|
| Task correctness | Trusted execution/reference outcome | | |
| Format | Parsed required shape | | |
| Style/length | Independently defined constraint | | |
| Operational failure | Timeout/infra/termination | | |

- Prove correct outputs outrank plausible wrong/style-only outputs:
- Check constant predictions and imbalanced class contribution:
- Penalizing length/lint must not reward empty or incomplete programs:
- Finite score bounds; parser failures; no hidden test/answer access:
- Timeout is not task truth; infrastructure abort/requeue policy and retry budget:
- Normalization/grouping/loss configuration pinned separately from reward code:

## Challenge receipts

Use the schema in `references/local-rlvr.md` and the synthetic
`templates/verifier-receipts.json` demonstration. Include all six categories:
correct, incorrect, malformed, adversarial, timeout and infrastructure_error.
Replace every synthetic pointer/hash with actual independent evidence before use.

Record each observed status/reward, expected correctness and label provenance.
Audit with `scripts/specialization_audit.py rewards` from the skill root. The
helper reads receipts only; it does not execute or validate their provenance.

## Runtime boundary

- Writable workspace versus read-only evaluator/hidden tests:
- No credentials, privileged sockets or unrelated host paths:
- Verified network, process/capability and filesystem policy:
- CPU/RAM/PID/time/output limits; terminated child-process cleanup:
- Actual negative capability tests and run-owned cleanup evidence:
- Generated tests accepted by reference and rejected by credible near misses:

## Monitor and stop

Reward components/std, zero-variance groups, pass rate, invalid/timeout/infra rate,
KL/entropy/clipping, output length, independent hidden correctness and regressions:

Stop thresholds and fixed spend budget:
Three-pass escalation record:
Decision: use / repair / reject / unresolved. No claim of general verifier quality
from challenge fixture coverage alone.
