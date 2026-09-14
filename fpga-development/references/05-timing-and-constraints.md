# Timing and constraints

Timing analysis is only as meaningful as the constraint model. Start with clocks, then I/O delays and exceptions, and prove that every relevant path is covered. Never silence negative slack as a cosmetic action.

## Constraint review

For each primary clock record period, waveform, jitter/uncertainty, source, and target registers. For generated clocks record the source object and multiplication/division/phase relationship. For external interfaces record board/device timing, input/output delay reference clocks, and setup/hold assumptions. For asynchronous domains record the CDC protocol and justified exception.

AMD’s current [UG903 timing-constraint guide](https://docs.amd.com/r/en-US/ug903-vivado-using-constraints/Timing-Constraints) identifies `create_clock`, `create_generated_clock`, input/output delays, clock groups, false paths, max/min delay, and multicycle paths as timing-related constraint classes. Its [exception priority guidance](https://docs.amd.com/r/en-US/ug903-vivado-using-constraints/Exceptions-Priority) explains that overlapping exceptions have precedence; this is a reason to review queries and scope, not to add broad exceptions.

Intel’s [Quartus Timing Analyzer guide](https://www.intel.com/content/www/us/en/docs/programmable/683068.html) is the corresponding vendor-specific reference. Use the exact edition for the target release.

## Report interpretation

Record worst setup and hold slack, endpoint/startpoint, clock pair, uncertainty, logic depth, routing delay, and whether the path is constrained. A positive result on one corner does not prove all corners or modes. Check unconstrained paths, missing clocks, ignored constraints, and exception counts before accepting a green summary.

Timing closure options include reducing logic depth, pipelining with latency changes, improving placement/resource inference, changing clock frequency only when the interface permits it, or correcting the constraint model. A false path is justified only by design semantics and a safe protocol.

## Hold, I/O, and multicycle proof

Define skew as capture-clock arrival minus launch-clock arrival; positive skew helps setup and hurts hold. A simplified setup slack is `Tperiod + skew - Tcq(max) - Tcomb(max) - Tsetup - Usetup`. A simplified hold slack is `Tcq(min) + Tcomb(min) - skew - Thold - Uhold`. Use the target tool's edge and uncertainty conventions for interpretation. Setup pass never implies hold pass.

External interfaces require both min and max input/output delays relative to the correct board clock edge, derived from the external device's timing, trace, package, and uncertainty. Record whether the interface is forwarded-clock, source-synchronous, or unrelated. For multicycle paths, document the altered setup capture edge and the paired hold adjustment according to the target tool guide. Retain exact exception queries and before/after path counts; traffic inactivity is not a false-path rationale.

Generated clocks need source object, ratio, phase, and waveform edges. A clock-like signal name is not a timing object. Review clock interaction, unconstrained min-delay, ignored constraints, and exception scope after every change.

## Failure gates

- unconstrained clocks or ports: no signoff;
- negative setup/hold slack: no signoff;
- unexplained timing exceptions or ignored constraints: no signoff;
- timing result without target corner/release metadata: inconclusive;
- “works on the bench” used to waive timing: reject.

## Worked setup calculation

For a same-clock path, a simplified setup budget is `Tperiod ≥ Tcq + Tlogic + Trouting + Tsetup + Tuncertainty`. If a 100 MHz clock has a 10 ns period, and measured worst-case terms are 0.8 ns, 7.4 ns, 0.9 ns, 0.5 ns, and 0.3 ns, the estimated slack is 0.1 ns before tool-specific modeling. This estimate explains a report; it is not a substitute for the signoff engine, corners, or hold analysis.

If a divided clock is produced by a PLL or counter, declare the generated relationship using the target tool’s documented mechanism. A name that looks like a clock does not make a clock object. For unrelated clocks, document the CDC circuit before choosing clock groups or false paths. An exception that removes analysis without safe transfer logic only removes evidence.

## Report excerpt interpretation

Capture the report fields, not just “timing failed”: startpoint, endpoint, launch/capture clocks, required time, arrival time, slack, logic delay, route delay, uncertainty, and constraint status. Then classify the cause:

| Finding | Likely next action |
|---|---|
| missing clock | correct clock definition and rerun |
| unconstrained I/O | obtain board/interface timing and add delays |
| negative setup slack | pipeline, reduce logic, improve placement, or revisit valid frequency |
| negative hold slack | inspect skew/min-delay strategy with vendor guidance |
| async crossing timed as synchronous | review CDC and clock relationship |

Acceptance artifacts are the constraint source, timing coverage summary, worst setup/hold paths, unconstrained-path report, exception report, tool/device/corner metadata, and closure rationale. Signoff requires a clean interpretation of warnings, not merely positive headline slack.
