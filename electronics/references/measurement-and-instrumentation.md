# Measurement and instrumentation

Choose the instrument from the question being asked. A DMM establishes DC
voltage, resistance, continuity, diode behavior, and bounded current only when
connected correctly. A scope shows time behavior and ripple; a logic analyzer
decodes digital states but cannot establish analog voltage margin or power
integrity by itself.

## DMM discipline

Before touching the circuit, set function and range, verify the black lead is
in COM, and verify the red lead is in the voltage/ohms jack for voltage,
resistance, diode, and continuity. Current jacks are low impedance and are
intended for a series insertion across a deliberate circuit break. A voltage
measurement with the lead in a current jack can short the source through the
meter shunt. Confirm the current-input fuse rating and interrupt capacity from
the meter manual; a fuse is not permission to exceed the meter, lead, or source
rating. Prefer a clamp or shunt designed for the current when opening the path
is unsafe.

For resistance/continuity, remove power and discharge capacitors. For current,
predict the range and polarity, start on the highest range, connect in series,
and restore the lead to the voltage jack immediately afterward. Record whether
the reading is startup, steady-state, or a burst.

Source: Fluke, *ABCs of DMMs*:
https://media.fluke.com/ade6b718-4577-4b57-903b-b10600664c67_original%20file.pdf

Use a lead-position interlock in the procedure: announce “voltage” before
placing the tip, visually confirm COM plus V/Ω, and return the red lead to V/Ω
after every current measurement. If the meter's current fuse is open, a current
reading may silently become an open circuit; verify the instrument on a known
source or its self-test rather than assuming zero current. For low-side shunt
measurements, account for the shunt voltage drop and common-reference shift.

## Scope setup

A conventional benchtop scope has probe commons tied to protective earth and
all channel commons share that node. Connect the probe to the scope first,
then connect its ground to a known DUT reference before the tip. Never defeat
the protective earth or clip the common lead to a switching node. If neither
measurement point is safely at earth reference, use a correctly rated
differential or isolated probe and verify common-mode, differential, CAT, and
transient limits.

Select bandwidth and attenuation for the fastest edge and voltage range. Use a
short ground spring or coaxial fixture when edge shape matters. A long ground
lead adds inductance and can create ringing. Probe input capacitance is part of
the circuit: it can slow I2C rise time or change a marginal oscillator. Record
probe model, capacitance, attenuation, bandwidth limit, sample rate, coupling,
trigger, test point, and ground attachment.

Sources: Tektronix, *Floating Oscilloscope Measurements and Operator
Protection*: https://www.tek.com/en/documents/technical-brief/floating-oscilloscope-measurements-and-operator-protection
and *How Oscilloscope Probes Affect Your Measurement*:
https://www.tek.com/en/documents/application-note/how-oscilloscope-probes-affect-your-measurement
Keysight, *8 Tips for Better Scope Probings*:
https://www.keysight.com/us/en/assets/7018-01747/application-notes/5989-7894.pdf

### Repeatable capture

Use the same trigger point and timebase for a passing and failing capture.
Measure I2C rise time at the specified threshold interval, report overshoot and
low-level plateau separately, and annotate whether the probe was attached at
the controller or far end. For a rail transient, capture the rail and the event
trigger together; a DMM average cannot disprove a short brownout. State the
scope's vertical scale, offset, bandwidth limit, coupling, and sample/memory
settings so the result can be audited.

Treat displayed digits as estimates. Include probe tolerance, scope accuracy,
noise floor, trigger jitter, and repeatability when a limit decision depends on
small margins. If the margin is smaller than the combined uncertainty, classify
the result as inconclusive and change the measurement method or improve the
test point.

## Interpretation

Separate instrument evidence from circuit evidence. If attaching a second probe
changes the waveform, suspect loading and repeat with a lower-capacitance
attachment. If a DMM sees a stable rail but the scope shows droop during a
radio or load event, the transient is the relevant evidence. A decoded frame
does not prove VIH/VIL, rise time, ground integrity, or supply behavior.

## Validity, aliasing, and uncertainty

State the quantity and bandwidth needed to answer the question. A logic
analyzer sampling too slowly can miss a narrow glitch and still decode a clean
bus; a scope bandwidth limit can hide ringing. A DMM update rate can miss a
transient, and a continuity threshold can turn a high-value path into a beep.
Record range, resolution, input impedance, bandwidth, sample rate, filtering,
and trigger settings.

| Observation | False positive | False negative | Disambiguating test |
|---|---|---|---|
| continuity beep | threshold or parallel path | oxidized/high contact resistance | power-off ohms reading and lead subtraction |
| stable DMM rail | average hides droop | probe changes return | scope at load during event |
| clean decoded I2C | threshold/filter hides slow edge | sample misses glitch | analog SDA/SCL plus raw capture |
| zero current | open/blown current fuse | range overload | verify lead/jack/fuse and known source |
| probe improves circuit | probe adds pull/return path | probe masks intermittent fault | remove probe; alternate low-C attachment |

Continuity is a finite-resistance, low-current test. Zero displayed ohms is not
literal zero; an open-looking semiconductor, protection device, or capacitor
may be behaving normally. If a limit decision depends on a small margin, include
probe tolerance, scope accuracy, noise floor, trigger jitter, and repeatability.
If combined uncertainty overlaps the limit, classify the result inconclusive.

## Repeatable measurement sequence

1. Write the predicted signature and safety boundary.
2. Announce DMM function and visually verify COM plus V/ohms or current jack.
3. Connect scope ground/reference first where the instrument requires it.
4. Capture a disabled baseline and one controlled event.
5. Save raw data and settings; repeat once unchanged.
6. If surprising, test loading, aliasing, grounding, and range before modifying
   the circuit.
7. Classify confirmed, contradicted, or inconclusive and state why.

All probe commons on a conventional benchtop scope share earth/reference.
Never remove protective earth to obtain a floating measurement.
