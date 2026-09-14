# RTL module contract and review

## Intent

- Module and purpose:
- Invariants:
- Clock/reset ownership:
- Input legal domain and illegal-input behavior:

## Interface

| Signal | Width/signedness | Clock domain | Meaning | Stability/handshake |
|---|---|---|---|---|
| | | | | |

- Latency:
- Throughput:
- Backpressure / loss policy:
- Overflow, saturation, rounding, and truncation policy:
- Fixed-point format, binary point, intermediate ranges, explicit casts:

## Synthesis hypothesis

- Expected LUT/FF/BRAM/DSP/PLL resources:
- Expected inferred structure:
- Simulation-only constructs excluded:
- Vendor-specific constructs and portability boundary:
- Parameter legality checks:

## Evidence and disposition

- Lint command/version/result:
- Elaboration command/version/result:
- Synthesis warnings and disposition:
- Resource report:
- Changes required before simulation or implementation:

## Review instructions

For each arithmetic expression record operand widths before evaluation, result width, cast point, rounding, and overflow policy. For each process record sensitivity/clock, reset behavior, assignment style, and driver owner. Compare the hypothesis with elaboration and synthesis reports. Treat a changed latency or inferred memory shape as an interface change.

## Example decision

`HOLD`: synthesis infers a latch for `data_valid`, while the contract requires a one-cycle registered pulse. Add complete combinational assignments or redesign the register boundary, then rerun lint and synthesis.
