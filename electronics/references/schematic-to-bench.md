# Schematic to bench review

Turn the design into a reviewable physical plan before applying power.

## Review record

For each net record:

| Field | Required content |
|---|---|
| Net and return | signal name, source, destination, explicit return path |
| Pin identity | exact component reference, pin number, package/board revision |
| State | power-off, reset, idle, active, fault level and polarity |
| Limits | voltage, current, power, timing, absolute maximum and operating range |
| Test point | probe/meter access, reference node, expected measurement |

Read the exact schematic, board drawing, module documentation, and datasheet.
The silkscreen or a familiar breakout is evidence of placement, not of pin
function, voltage tolerance, pull-ups, or address straps. Mark every unknown.

## Electrical reasoning

Calculate each intentional load. For a resistor-fed LED, evaluate the range
`I = (Vsupply - Vf) / R` across supply, forward-voltage, and resistor tolerance;
then check the LED, resistor dissipation, and source/driver current limits. A
GPIO is a control output, not a power supply. For an inductive load specify
driver rating, flyback path, external supply, shared reference or isolation,
and reset-time state. For analog inputs include source impedance, scaling,
fault voltage, ADC range, reference/calibration, and filter corner.

For mixed voltages, identify direction and topology. A bidirectional open-drain
bus needs a translator that preserves release/high-impedance behavior; a
push-pull signal may need a different level shifter. Do not infer tolerance from
the board's supply label.

## First-power gate

With power removed, inspect orientation, rails, bridges, connector keying, and
unpopulated options. Check intended continuity and absence of rail-to-rail or
rail-to-signal shorts. Define a current limit and a stop condition before
powering. Apply power with the load disabled where possible; measure rail
voltage and current, reset state, and temperature. Add one signal group or
peripheral at a time.

The review is complete when a second engineer can wire or probe from the record,
every numeric choice has a source or calculation, and unresolved facts are
visible rather than hidden in assumptions.

Sources: component datasheet and board schematic are controlling sources.
For I2C electrical constraints use NXP UM10204 sections 3 and 7:
https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/nxp-designs/931/1/UM10204.pdf

## Worked review and stage gates

For a 3.3 V GPIO driving an LED through 680 ohms, record GPIO4 → resistor →
anode, cathode → ground, active-high, reset-off, and the LED datasheet's Vf
range. At Vf=2.0 V, nominal current is `(3.3-2.0)/680 = 1.9 mA`; recalculate
the extremes, resistor power (`I²R`), and GPIO limits. A continuity beep does
not prove this load calculation, reset state, or driver safety.

| Gate | Required evidence | Stop condition |
|---|---|---|
| documentation | exact schematic/BOM/board/component revisions | pin, rail, polarity unknown |
| unpowered | visual, continuity, rail-short record | unexpected conductive path |
| first power | current limit, rail/current/reset/temperature | rail collapse or excess current |
| signal | defined idle/active test-point readings | unexplained level or polarity |
| integration | identity/readback and bounded timeout | scan-only or hanging driver |
| release | reset/power-cycle and acceptance record | open electrical limit |

Do not treat success at one gate as evidence for the next: a stable rail does
not prove correct signaling, and a functional demo does not prove recovery.
