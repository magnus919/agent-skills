# Clocks, reset, and clock-domain crossing

Clocking is part of function. List every clock, source, frequency, phase relationship, duty-cycle assumption, generated-clock mechanism, and reset relationship before reviewing CDC.

## Reset

Choose synchronous or asynchronous assertion deliberately. Make deassertion safe for each clock domain, document what state is valid after release, and account for PLL/MMCM lock before enabling dependent logic. Test reset at time zero, during idle, during a transaction, and after clock loss or re-lock where applicable. Do not use an unqualified asynchronous input as a synchronous control.

## CDC selection

- A single level crossing: destination-domain synchronizer, with attributes and MTBF assumptions sourced for the device.
- A pulse: toggle/handshake or pulse stretcher according to rate and loss semantics; a two-flop level synchronizer alone can miss a narrow pulse.
- A multi-bit value: handshake with stable data, Gray-coded counter, or dual-clock FIFO; do not synchronize bits independently and assume atomicity.
- A stream: dual-clock FIFO with explicit full/empty semantics, reset coordination, and overflow/underflow policy.

Maintain a CDC inventory: source/destination clock, signal kind, protocol, synchronizer/FIFO, allowed loss/duplication, reset interaction, timing exception, and verification evidence.

## Constraints and review

AMD [UG949 CDC guidance](https://docs.amd.com/r/en-US/ug949-vivado-design-methodology/Constraining-Asynchronous-Clock-Groups-and-Clock-Domain-Crossings) says asynchronous paths require proper synchronization and should not be treated as ordinary default-timed paths. A timing exception cannot make an unsafe crossing safe. AMD [UG903](https://docs.amd.com/r/en-US/ug903-vivado-using-constraints/Timing-Constraints) documents clock groups, false paths, generated clocks, input/output delays, and multicycle paths.

## Gray-pointer and reset-release proof

A dual-clock FIFO must prove that its Gray encoder changes one bit per pointer increment, that pointer width and extra wrap bit are correct, and that full/empty comparisons use the delayed synchronized pointer conservatively. Independently synchronized binary bits are not coherent. The property can be expressed as one-hot-or-zero difference between successive Gray values when the pointer advances by at most one; cover wrap and reset boundaries.

A Gray bus still needs a device-specific max-delay or bus-skew constraint so destination sampling cannot observe multiple physical transitions. Derive the allowed skew from the fastest source clock and sampling uncertainty, apply the target vendor's documented syntax, and inspect every bit's post-route endpoint report. A false path without skew evidence only removes analysis. Record synchronizer depth, MTBF assumptions, pointer reset values, and reset coordination.

Use per-domain reset synchronizers, commonly asynchronous assertion with synchronous release, with vendor attributes and recovery/removal evidence. Hold valid/ready, FIFO enables, and synchronized flags inactive until local release and remote-reset knowledge are valid. Test reset during outstanding requests, differing pointers, backpressure, and PLL unlock or clock absence. Reset reconvergence is a protocol event, not merely a register initialization.

## Failure gates

- CDC crossing has no identified protocol: blocked;
- asynchronous reset deassertion is not domain-safe: blocked;
- multi-bit bus lacks atomicity proof: blocked;
- waiver/false path lacks design rationale and report evidence: blocked;
- CDC report is unavailable or generated with a different target/tool release: inconclusive.

## Worked scenario: pulse and stream crossing

A 100 MHz producer emits a one-cycle event to a 25 MHz consumer and also sends a 16-bit stream. A two-flop synchronizer on the pulse can miss it because the destination samples only every 40 ns. Use a toggle or request/acknowledge protocol for an event, and a dual-clock FIFO for the stream. State whether the producer may queue multiple events and what happens when the FIFO is full.

For a FIFO, calculate backlog from rates rather than intuition. If the producer can write 100 million words/s and the consumer drains 25 million words/s for a burst of `B` seconds, required depth is at least `75,000,000 × B` words plus reset and margin policy. If the producer is allowed to stall, `full` must feed back before overflow. If it is not allowed to stall, dropping, overwrite, or upstream buffering must be contractual.

| Crossing | Suitable mechanism | Common failed shortcut |
|---|---|---|
| stable level | destination synchronizer | sampling raw asynchronous level |
| isolated event | toggle/handshake | one-cycle pulse synchronizer |
| occasional multi-bit word | handshake plus stable holding register | one synchronizer per bit |
| sustained stream | dual-clock FIFO | unsynchronized counter/data bus |

## Reset reconvergence review

Resetting two domains independently can release related logic on different cycles. Identify reset assertion, deassertion, and state validity in each domain. Do not let a destination consume a synchronized flag until its own reset release is complete. Test reset while a request is outstanding, while FIFO pointers differ, and while a PLL is unlocked.

Acceptance artifacts are the clock graph, CDC table, rate/backlog calculation, reset sequence diagram, CDC report, assertions for stability/full/empty, and tests of event bursts and reset interruptions. A waived CDC path without a protocol proof is a failure.
