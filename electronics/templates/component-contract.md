# Component contract

## 1. Job and envelope

- Function and observable behavior:
- Component family and why:
- Input/output quantities and units:
- Minimum / nominal / maximum / transient / fault:
- Supply rails, frequency, duty cycle, ambient, enclosure, lifetime:
- Acceptance criteria:

## 2. Identity and evidence

- Manufacturer and exact ordering code/package/revision:
- Datasheet and application-note URLs:
- Schematic, pinout, exposed pad, polarity, assembly constraints:
- Guaranteed values versus typical curves:
- Board/SoC schematic and firmware assumptions, if attached:
- Unknowns and evidence owner:

## 3. Margins and calculations

| Requirement | Equation/assumption | Corner | Result | Margin | Evidence |
|---|---|---|---|---|---|
| | | | | | |

- Tolerance, drift, noise, leakage, loading:
- Dissipation, thermal path, SOA/transient:
- Protection energy and clamp limits:
- Guaranteed / estimated / measured classification:
- Controlling corner and model-validity range:
- Observed fact:
- Inference supported by the fact:

### Completed example

| Requirement | Equation/assumption | Corner | Result | Margin | Evidence |
|---|---|---|---|---|---|
| actuator conduction | `P=I²R`, hot guaranteed `RDS(on)` | 0.42 A steady, hot | 32 mW | below thermal budget | datasheet condition + measured rail |

The example is screening evidence only; startup linear-mode SOA and clamp
waveforms remain separate requirements.

## 4. Interface and failure contract

- Logic thresholds, impedance, timing, power-up/down:
- Driver, pull resistor, clamp, flyback, snubber, fuse/current limit:
- Ground/isolation, creepage/clearance:
- Open, short, reversed, disconnected, brownout behavior:

## 5. Verification

- Instruments, fixtures, raw-data location:
- Normal, corner, reset/power-cycle, and fault tests:
- Temperature/supply/load corners:
- Calibration and diagnostic checks:
- Pass/fail evidence and unresolved risks:
