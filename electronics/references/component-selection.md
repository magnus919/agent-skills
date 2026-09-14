# Component selection

## Start with the job

Translate the request into an observable behavior before naming a part.

| Question | Required record |
|---|---|
| What crosses the boundary? | Voltage, current, force, temperature, light, sound, position, data, or energy |
| What are the corners? | Minimum, nominal, maximum, transients, fault states, temperature, supply |
| What must be guaranteed? | Accuracy, latency, ripple, lifetime, noise, efficiency, safety, availability |
| What constrains implementation? | Package, assembly, PCB area, isolation, firmware, cost, sourcing |

“Use a transistor” is not a requirement. Identify switching versus amplification, high-side versus low-side, linear versus switched operation, and whether the device must fail open, fail safe, or remain isolated.

## Evidence ladder

1. Identify the exact ordering code, package, revision, qualification, and lifecycle status.
2. Retrieve the current manufacturer datasheet and applicable application note.
3. Separate absolute maximum, recommended operation, guaranteed electrical characteristics, typical curves, and marketing claims.
4. Read pinout, truth tables, timing, startup, shutdown, thermal, layout, and errata sections.
5. Check the actual schematic, load, source impedance, cable, connector, board, and software assumptions.
6. Mark every unverified value `UNKNOWN`; do not fill gaps with a family-level typical.

Distributor pages and breakout-board labels are discovery aids. They do not establish pin compatibility, current rating, thermal performance, or safe operating area.

## Requirements matrix

For each candidate, maintain one row per requirement and one column for evidence, corner, calculated result, margin, and verification method. Reject a candidate when a required value is unavailable, out of range, or only typical where a guarantee is required. Record the controlling corner rather than only a nominal pass.

Useful screening columns include:

- input/output range and polarity;
- DC, RMS, peak, surge, and inrush current;
- frequency, edge rate, duty cycle, and timing tolerance;
- common-mode range, input/output impedance, leakage, and loading;
- efficiency, dissipation, junction-to-ambient or board thermal path;
- protection thresholds and fault energy;
- package, pinout, exposed pad, creepage, clearance, and assembly limits;
- calibration, drift, production test, and field diagnostics;
- supply chain, alternates, firmware/driver maturity, and end-of-life risk.

## Original worked example: low-side actuator switch

Suppose a 12 V actuator is specified by the system owner as 0.42 A steady state, 0.9 A for 120 ms at cold start, and 18 V maximum supply during charging. The controller output is 3.0 V with 4 mA available. A candidate MOSFET is considered.

The selection cannot use only the nominal current and `RDS(on)` headline. Check gate voltage at 3.0 V, drain voltage including turn-off overshoot, pulse SOA during startup, body-diode direction, avalanche or clamp path, and package thermal resistance. If a measured drain overshoot is 26 V, a 30 V absolute maximum is not a credible margin; add a defined clamp and remeasure. If the candidate's guaranteed `RDS(on)` at the available gate voltage is 180 mΩ, steady-state loss is approximately `0.42^2 × 0.18 = 32 mW`, while the 0.9 A pulse is `0.9^2 × 0.18 = 146 mW` before temperature dependence. Those calculations are screening only; verify hot resistance and pulse thermal impedance in the exact package and layout.

The output should name the driver, clamp, gate pulldown, supply path, fault response, measurement points, and the evidence still missing.

## Role screening

| Role | First constraints | False shortcut |
|---|---|---|
| Power switch | gate drive, SOA, loss, surge, fault energy | nominal current |
| Regulator | input transients, load steps, stability, heat | output voltage only |
| Op amp | common-mode, noise gain, load, stability | offset alone |
| Comparator | thresholds, hysteresis, output, delay | op amp substitution |
| Sensor | output class, excitation, installation, drift | module range as accuracy |
| Protection | waveform, repetition, clamp, failure mode | package size |

Record whether each interface is voltage-mode, current-mode, open-drain, push-pull, differential, isolated, or bidirectional. Include startup contention and unpowered behavior. Treat a second source as a new candidate: redo thermal, timing, protection, and calibration checks. Return requirement, candidate, evidence, controlling corner, margin, verification, and unknowns.

## Routing

Route to the exact component datasheet for numeric limits. Route to `power-thermal-and-protection.md` for energy, heat, SOA, and fault design. Route to `tolerances-and-error-budgets.md` for accuracy. Route to `analog-and-digital-building-blocks.md` for feedback, thresholds, and ADC interfaces. Route to `sensors-and-conditioning.md` for transducers and calibration. For ESP32 board, pin, firmware, flashing, or recovery choices, route to `esp32-development`.

## Stop criteria

Selection is complete when one candidate satisfies every recorded corner with an evidence-backed margin, rejected options have reasons, the schematic and layout constraints are represented, and a bench or production verification plan exists. Otherwise return a bounded shortlist and explicit unknowns.

## Primary sources

- [TI Precision Analog Applications Seminar — Remote System Monitor Applications](https://www.ti.com/lit/pdf/slyp160) — bridge/divider and sensor-interface examples; a 2005 instructional seminar, not a component guarantee.
- [TI regulator divider accuracy](https://www.ti.com/lit/an/slva423/slva423.pdf) — feedback-divider error and environmental contributors; apply to the described regulator topology.
- [TI difference-amplifier matching](https://www.ti.com/lit/pdf/sboa582) — ratio matching and CMRR; assumptions are circuit-specific.
## Rejection reasoning

Reject a part when a required limit is typical only, when the test condition differs from the product corner, when the thermal path is unspecified, when an alternate changes pin or startup behavior, or when protection depends on an unverified waveform. State the evidence and the smallest next measurement.

## Candidate experiment

For an uncertain actuator, use a current-limited supply and a substitute load with measured resistance and inductance. Capture gate, switch, load, and supply simultaneously. Sweep cold-start, stall, reversal, disconnect, and brownout. Retain waveforms and temperature, then update the candidate matrix.

## Datasheet extraction

Copy no values without units, conditions, min/typ/max status, and temperature. Record footnotes, test circuit, package variant, and revision. A value from a graph is an estimate and needs margin or measurement.
