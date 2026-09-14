# Simulation and verification evidence

Treat simulation as an executable contract. A self-checking testbench must fail with a nonzero result when the design violates an invariant; “the waveform looked right” is an observation, not a gate.

## Minimum structure

1. Drive reset and clocks deterministically.
2. Generate legal, boundary, illegal, stalled, reordered, and reset-interrupted transactions.
3. Check outputs against a small reference model or temporal invariants.
4. Report the first failing transaction with time, inputs, expected, actual, and seed.
5. Retain source hash, simulator version, command, log, waveform, seed, and coverage output.

Use assertions for properties such as “valid data remains stable until accepted,” “a FIFO never reads empty,” or “a request eventually receives a response under stated fairness.” Add a negative control by mutating a known line and proving the test fails.

## Tool applicability

[Verilator’s command reference](https://verilator.org/guide/latest/exe_verilator.html) documents lint-only mode, timing switches, tracing, assertions, and coverage options. Its [simulation guide](https://verilator.org/guide/latest/simulating.html) describes line, toggle, expression, FSM, user, property, and covergroup coverage. These are applicable when the installed Verilator version supports the selected constructs; they do not replace an event-driven simulator or vendor primitive model.

[YosysHQ formal tools](https://yosyshq.readthedocs.io/en/latest/tools.html) distinguish SBY safety/liveness/reachability flows, EQY equivalence, and MCY mutation coverage. Use formal when properties can be stated and the supported HDL subset is known; record bounds, assumptions, solver, and proof status.

## Interpretation

Coverage is a gap-finding signal. High line coverage can coexist with untested protocol ordering, reset release, overflow, CDC, or illegal input behavior. A passing bounded proof is conditional on assumptions and depth. A waveform is useful evidence only when the stimulus and expected property are retained.

## Protocol invariants and mutation depth

For ready/valid, acceptance is exactly `valid && ready` at the active edge. Assert stalled payload and sideband stability, acceptance-count conservation, ordering, and the specified reset discard or drain policy. Cover simultaneous enqueue/dequeue, empty/full boundaries, reset during traffic, and absence of combinational ready/valid loops. Liveness requires an explicit fairness assumption or a finite response bound.

Functional coverage should cross reset phase, backpressure, occupancy boundary, simultaneous operations, and illegal-input policy. Retain the denominator and exclusion rationale. Map each deliberate mutation to the property or checker expected to fail; a surviving mutation is missing evidence, even when directed tests pass.

## Failure gates

- testbench exits zero despite an injected defect: verification gate fails;
- no deterministic seed or source/tool provenance: result is non-reproducible;
- coverage denominator or exclusions unexplained: coverage claim is inconclusive;
- unresolved assertion or X/unknown behavior: blocked;
- simulation pass with synthesis warnings affecting behavior: blocked pending synthesis review.

## Worked scenario: ready/valid pipeline

For a one-stage pipeline, the property is not merely “output eventually equals input.” When `valid` is high and `ready` is low, the output payload and `valid` must remain stable. When both are high, one transaction is accepted. A scoreboard therefore updates on accepted transactions, not on every clock. Drive independent producer and consumer stalls, reset between transactions, and back-to-back transfers.

| Stimulus | Checker question | Retained evidence |
|---|---|---|
| producer stalls | Is output unchanged while waiting? | Assertion failure time and payload |
| consumer stalls | Is data held without duplication? | Waveform and scoreboard trace |
| reset during transfer | Are partial items discarded as specified? | Reset-segmented log |
| maximum throughput | Is one item accepted per cycle? | Count comparison |
| malformed input | Is rejection or error response deterministic? | Error assertion |

## Mutation and coverage procedure

Choose one deliberate mutation: invert a ready condition, remove a reset assignment, change a boundary comparison, or drop a FIFO full check. Run the same test command and require a nonzero failure. If the mutation survives, add a stimulus or property before declaring the test suite adequate.

Coverage must name its denominator and exclusions. Line coverage can miss a protocol sequence; toggle coverage can miss a legal transaction; FSM coverage can miss data-dependent arithmetic. Use directed cases for contractual boundaries and constrained random only when the generator and seed are retained. A coverage percentage without the report, tool version, and exclusion rationale is inconclusive.

Acceptance artifacts are the test plan, self-checking harness, deterministic command, source hash, log, waveform, assertion report, coverage report, mutation result, and a concise interpretation. A passing test with a silent checker is a failed verification gate.
