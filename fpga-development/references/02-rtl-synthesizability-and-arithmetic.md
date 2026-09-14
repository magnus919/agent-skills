# RTL synthesizability and arithmetic

RTL is a concurrent hardware description. Ask what gates, registers, memories, and clock enables a construct implies, then verify that interpretation in the selected synthesis tool. Simulation convenience does not make a construct implementable.

## Design rules

- Give every combinational output a value on every path; otherwise an inferred latch may be intentional or a defect.
- Use one clocking process per register set and make reset polarity and release explicit.
- Treat nonblocking assignments as state updates sampled together; do not rely on statement order to model a pipeline.
- Keep one signal's driver ownership unambiguous.
- Bound loops and arrays so elaboration has finite hardware cost.
- Mark file I/O, delays, testbench tasks, and scoreboards as simulation-only unless the target flow documents an implementation mapping.
- Parameterize widths and limits, then assert legal parameter ranges at elaboration.

## Arithmetic contract

For an unsigned `W`-bit sum, allocate at least `W+1` bits when overflow must be represented. For signed two's-complement addition, allocate a guard bit or define wrap/saturate behavior. Multiplication of widths `A` and `B` can require `A+B` result bits. Division by a constant may infer expensive logic; division by a power of two is a shift only when signedness and rounding semantics are specified.

Example: an 8-bit ADC value scaled by 3 should use an explicitly widened intermediate, then define whether the 10-bit result is clipped to 255, wrapped, or exposed at full width. A passing test at nominal values does not establish behavior at 0, maximum, or values that overflow.

## Evidence

Review lint, elaboration, synthesis warnings, inferred-resource reports, and post-synthesis widths. Compare intended latency and resource class with reports. A warning that changes signedness, truncation, latch inference, or clock/reset interpretation is a release blocker until disposition is recorded.

The language authority is [IEEE 1800-2023](https://ieeexplore.ieee.org/document/10458102), whose scope includes RTL, gate-level descriptions, testbenches, assertions, coverage, and constrained-random constructs. Tool support is a separate claim: record exact parser, version, and switches.

## Fixed-point semantic proof

For signed QI.F and QJ.G operands, a product needs at least I+J integer capacity and F+G fractional bits before rescaling. Addition requires aligned binary points and a range-derived guard bit. Arithmetic right shift rounds negative values toward negative infinity; for example, stored -3 with two fractional bits represents -0.75, and shifting right one bit gives stored -2 (-0.5), while truncation toward zero would give stored -1 (-0.25). Record all casts, expression widths before evaluation, and binary-point movement because assignment width cannot repair an already-truncated expression.

Original test: a signed Q4.4 value multiplied by a signed Q2.6 coefficient produces a result with ten fractional bits before conversion. Test both signs, negative half-LSB and tie values, signed minimum and maximum, and the first overflowing product under the chosen nearest/truncate/saturate policy. Compare against a software integer reference model and inspect post-synthesis widths.

## Failure gates

- implicit truncation or signed conversion: blocked until tested and documented;
- inferred latch in a clocked datapath: blocked unless deliberately designed;
- arithmetic latency omitted from the interface contract: blocked;
- synthesis report differs materially from the resource/latency hypothesis: investigate before timing work;
- simulation-only behavior used as hardware behavior: reject.

## Worked scenario: fixed-point scaling

An unsigned 11-bit ADC produces raw codes 0 through 2047. Suppose a stated calibration maps 1024 counts to 1000 mV. A nearest-rounded millivolt estimate can be `mV = (x*1000 + 512) >> 10`; the product plus rounding constant needs 21 bits because its maximum is 2,047,512. If centivolts are required, define a second conversion, such as nearest `cV = (mV + 5) / 10`, and state whether integer division truncates or rounds. If the output is 8 bits, define behavior above 255. These widths and units are assumptions for the example, not a device calibration guarantee.

| Choice | Benefit | Cost / proof required |
|---|---|---|
| Wrap on overflow | Small logic | Dangerous unless protocol permits modulo values |
| Saturate | Safe bounded output | Comparator and boundary tests |
| Round-to-nearest | Lower bias | Extra guard bits and tie rule |
| Truncate | Simple, deterministic | Quantization bias; document it |
| Pipeline multiply/divide | Timing closure | Latency contract and valid alignment |

For a signed signal, sign-extend before widening. Concatenating a zero onto a negative signed value changes its interpretation. Every cast should state the intended domain and width. Test zero, maximum positive, negative minimum, just-under/over rounding boundaries, and overflow.

## Failure investigation

When simulation and hardware differ, inspect in this order: elaborated widths and signedness; synthesis warnings; inferred latch/register/memory; reset and initial state; clock enable semantics; resource inference; then post-route timing. Compare the RTL expression tree with the synthesis report. A warning about truncation is not harmless because it may alter only rare boundary values.

Acceptance artifacts include a width table, arithmetic examples with expected values, lint/elaboration logs, synthesis inference report, latency diagram, and tests demonstrating the chosen overflow and rounding policy. Do not accept a numerical result solely because a nominal decimal example matches.
