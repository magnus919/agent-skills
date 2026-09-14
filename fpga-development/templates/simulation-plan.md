# Self-checking simulation plan

## Provenance

- DUT/top and source revision:
- Simulator/version/command:
- Defines, packages, libraries:
- Seed policy:
- Retained log/waveform paths:

## Stimulus matrix

| Case | Stimulus | Expected invariant/result | Evidence |
|---|---|---|---|
| reset at start | | | |
| boundary values | | | |
| illegal input | | | |
| stall/backpressure | | | |
| reset during traffic | | | |

## Checks

- Immediate/concurrent assertions:
- Reference model:
- Acceptance-count, ordering, payload-stability, occupancy, and reset-epoch invariants:
- First-failure diagnostic fields:
- Required nonzero exit behavior:
- Negative control: injected defect and expected failure:

## Coverage and conclusion

- Coverage types and denominator:
- Exclusions with rationale:
- Uncovered behavior:
- Result: PASS / FAIL / INCONCLUSIVE
- Why the result does or does not establish synthesis or hardware behavior:

## Review instructions

The checker must be capable of failing independently of the DUT’s internal signals. Include at least one boundary case and one stalled or reset-interrupted case. Run a seeded mutation and retain its failing log. Record coverage exclusions with a reason tied to the contract; never use a percentage as a substitute for missing properties.

## Example decision

`INCONCLUSIVE`: all directed tests pass, but the mutation that removes FIFO-full protection also passes. Add a producer-overrun test and an assertion before accepting the suite.
