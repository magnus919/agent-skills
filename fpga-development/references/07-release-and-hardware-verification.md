# Release and hardware verification

Release is a chain of identity and observation. Separate “RTL simulated,” “synthesized,” “placed and routed,” “bitstream generated,” “programmed,” and “behavior observed.” Each boundary needs its own evidence.

## Release record

Retain repository revision, top/defines, HDL and constraint manifests, target device/package, tool versions, commands or project archive, warnings, utilization, timing/CDC reports, bitstream hash, programming log, and known limitations. Ensure a clean rebuild or explain every generated input. Store the recovery image and the documented path back to a known-good configuration.

## Hardware test order

1. Confirm board identity, power, programming transport, and safe current/voltage conditions.
2. Program a minimal identity design and verify reset/clock indication.
3. Test one output and one input against the schematic, including polarity.
4. Add interface traffic with a known pattern or loopback.
5. Repeat reset, reprogram, and power-cycle tests.
6. Capture measured observations, instrument settings, environmental conditions, and failure traces.

Do not claim SerDes, DDR, differential I/O, or high-speed correctness from a static LED result. Those require exact electrical/protocol documentation and suitable measurement or validated IP evidence.

## Failure gates

- bitstream hash does not match the reviewed build: reject;
- programming target or mode is ambiguous: stop;
- hardware result differs from simulation with no captured trace: diagnose, do not patch blindly;
- timing/CDC warnings unresolved: no release;
- recovery path not tested or image not retained: no deployment.

## Worked traceability scenario

A bitstream is rebuilt after changing a pin constraint. The source commit is unchanged, so a superficial review may reuse old hardware evidence. The release record must instead link the new constraint hash, target package, tool release, bitstream hash, programming log, and pin-level observation. Because the physical boundary changed, the previous observation is invalid until repeated.

Use a traceability chain:

`requirement → interface contract → RTL revision → simulation evidence → constraint revision → implementation reports → bitstream hash → programmed target → measured observation`.

Every link has an owner and timestamp. Generated IP and tool databases belong in the manifest or are referenced by immutable version. A release candidate with an untracked generated file is not reproducible.

## Failure investigation

When hardware disagrees with simulation, capture the exact programmed hash and board identity first. Verify reset/clock indication, pin polarity, bank voltage, and programming mode. Compare observed timing with the contract. Then inspect timing/CDC reports and add an internal observable or external logic-analyzer capture. Do not change RTL before preserving the failing artifact.

| Boundary | Minimum evidence |
|---|---|
| RTL → simulation | self-checking log, waveform, tool/version |
| RTL → implementation | synthesis warnings, utilization, netlist/report |
| implementation → bitstream | timing/CDC signoff, build manifest, hash |
| bitstream → target | target ID, programming log, reset result |
| target → behavior | measured signal, setup, expected/observed result |

Acceptance requires the completed traceability chain, known-good recovery image, repeated reset/reprogram/power-cycle results, and an explicit list of residual unknowns. A successful LED blink is evidence for that LED path only.
