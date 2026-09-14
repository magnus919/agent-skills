# Target and interface contracts

An FPGA recommendation starts with a target contract, not a board archetype. Record the exact board name, revision, FPGA ordering code, package, speed grade, configuration method, oscillator part and measured/declared frequency, power rails, I/O bank voltages, and attached devices. A USB descriptor identifies a bridge; it does not prove the FPGA part or pin wiring.

## Contract fields

- **Identity:** board revision, device/package/speed grade, silicon date if relevant, toolchain release, HDL dialect and top module.
- **Clock:** source oscillator, frequency evidence, duty-cycle assumption, reset/lock behavior, generated clocks, and clock-domain relationships.
- **I/O:** logical port, electrical standard, direction, pin, bank, pull configuration, drive/slew constraints, polarity, and external load.
- **Programming:** transport, bitstream format, configuration mode, offset/device selection, expected reset behavior, and recovery path.
- **Boundary behavior:** timing, latency, throughput, reset state, legal transactions, overflow/backpressure, and observable acceptance evidence.

Never fill missing values with “typical.” Mark them `UNKNOWN`, identify the artifact that would resolve them, and stop before pin assignment or programming when the unknown could damage hardware.

## Interface example

For a sensor bridge, define `sample_clk`, `sample_valid`, `sample_data[11:0]`, and `sample_ready` with exact clock ownership. State whether `sample_data` remains stable while `valid && !ready`, what happens on reset, whether samples may be dropped, and whether the receiver may pause. A waveform that shows one happy transfer is insufficient; test stall, reset during transfer, and maximum-rate traffic.

## Evidence gate

Before implementation, attach the schematic/pinout and device datasheet pages supporting each pin, voltage, clock, and electrical claim. Before release, retain the resolved contract, source revision, constraints, tool versions, and observed boundary result. If the contract changes, invalidate dependent timing and hardware evidence.

Primary anchors: [nextpnr constraints](https://github.com/YosysHQ/nextpnr/blob/main/docs/constraints.md) demonstrates architecture-specific I/O and clock constraints; [nextpnr iCE40 constraints](https://github.com/YosysHQ/nextpnr/blob/main/docs/ice40.md) explicitly identifies its PCF frequency syntax as a non-standard extension. Use these as examples of tool scope, never as universal pin rules.

## Failure gates

- Missing board revision or pin evidence: no programming.
- Unresolved clock frequency or generated-clock relationship: no timing signoff.
- Unstated reset polarity or release behavior: no hardware acceptance.
- Interface without backpressure/loss semantics: no throughput claim.
- Constraint file that leaves ports or clocks unconstrained: implementation is incomplete.

## Worked scenario: sensor-to-FPGA interface

Suppose a board label says “12-bit sensor header” and a project request says “sample at 2 MSPS.” Neither statement identifies the FPGA pins, bank voltage, clock source, sensor signaling standard, or whether 2 MSPS means conversion rate or accepted transfer rate. The correct first decision is `UNKNOWN`, followed by requests for the board schematic, sensor datasheet, FPGA package pinout, and clock source.

Once those artifacts are present, write the contract as a boundary sequence. The sensor drives `data[11:0]` and `valid`; the FPGA samples on `sample_clk`; the FPGA must acknowledge with `ready` or the sensor must guarantee a fixed hold interval. Define whether a sample is lost when the consumer stalls. Define reset values and whether the first post-reset sample is valid. Define input delay relative to the declared clock rather than assuming the data changes at an ideal edge.

| Question | Evidence | Decision if absent |
|---|---|---|
| Which physical pin carries `data[0]`? | Board schematic and package pinout | Stop pin assignment |
| What voltage standard applies? | Bank rail and device electrical table | Stop power-up |
| What clock samples the bus? | Sensor timing diagram and oscillator evidence | Stop timing constraints |
| Can the producer stall? | Interface protocol or sensor datasheet | Define capture buffer or loss policy |
| What does reset do to `valid`? | Device/protocol reset specification | Hold receiver disabled |

## Interface review procedure

1. Draw producer, receiver, clocks, reset, and physical boundary.
2. Label every signal with owner, domain, polarity, width, and stability rule.
3. Identify whether each boundary is synchronous, asynchronous, or analog/electrical.
4. Translate the timing diagram into executable checks.
5. Map logical ports to pins only after the target contract is complete.
6. Review the contract with the board artifact and implementation report together.

Acceptance artifacts are the signed target worksheet, annotated schematic excerpt, pin/bank table, clock inventory, interface timing diagram, open-unknowns list, and reviewer decision. A successful synthesis with an unresolved bank voltage remains a failed target contract.
