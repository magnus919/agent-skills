# Timing and constraints review

## Constraint inventory

| Object | Constraint | Source evidence | Scope | Verified by report |
|---|---|---|---|---|
| primary clock | | | | |
| generated clock | | | | |
| input/output delay | | | | |
| input/output min/max | | external timing source | | |
| asynchronous groups | | | | |

## Results

- Tool/release/device/corner/mode:
- Worst setup slack and path:
- Worst hold slack and path:
- Unconstrained paths:
- Missing/ignored/overlapping constraints:
- Exception endpoint queries and before/after path counts:
- Generated-clock source, edges, phase, and waveform:
- Clock interaction and CDC report:

## Closure decision

- Root cause of worst path:
- Chosen change and expected tradeoff:
- Before/after artifacts:
- Exceptions justified by design semantics:
- Multicycle setup and paired hold semantics verified against target guide:
- Decision: PASS / FAIL / INCONCLUSIVE
- Signoff owner/date:

## Review instructions

Check clock definitions before reading slack. Record setup and hold separately, then inspect unconstrained paths, ignored constraints, and exception scope. Every exception must point to a protocol or nonfunctional path and have a review owner. Use the target vendor’s current guide for syntax and precedence.

## Example decision

`HOLD`: headline setup slack is positive, but 14 ports are unconstrained and a generated PLL clock is absent from the clock report. Correct the constraint model and rerun all reports.
