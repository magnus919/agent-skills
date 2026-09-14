# Power, thermal, and protection

## Energy map

Before choosing a device, draw current paths for normal operation, startup, shutdown, reversal, disconnect, short circuit, wrong polarity, and communication loss. Record source impedance and stored energy in inductors, capacitors, batteries, cables, and rotating loads.

For a switch, estimate `Pcond = I²R` when conduction is resistive. Use `Psw ≈ 0.5 V I (tr+tf) fs` only as a screening model when a roughly linear voltage/current overlap is justified; for release, integrate measured or datasheet waveforms and add duty, gate-drive, diode, reverse-recovery, quiescent, and regulator losses. Do not use these simplified equations through saturation, current limiting, or an unknown waveform.

For thermal screening, use `Tj = Ta + P × θJA` only when the board, airflow, copper, and steady-state conditions match the specified thermal resistance. Otherwise use the package's junction-to-board/case path and transient thermal impedance. Verify temperature with a calibrated method and identify the hottest location.

## SOA and linear operation

A MOSFET selected for low on-resistance may be unsuitable while it is partly enhanced. Startup ramps, e-fuses, current limiting, motor stalls, slow gates, and avalanche events can place it in linear mode. Check the exact SOA for voltage, current, pulse duration, case temperature, gate condition, duty cycle, and mounting. Infineon's [linear-mode/SOA note](https://www.infineon.com/assets/row/public/documents/24/42/infineon-applicationnote-linear-mode-operation-safe-operation-diagram-mosfets-applicationnotes-en.pdf?fileId=db3a30433e30e4bf013e3646e9381200) explains why the published SOA curve is conditional and why transient thermal impedance and thermal instability matter. Applicability: the cited MOSFET guidance; exact part data controls.

## Protection selection

Match protection to the fault waveform:

| Threat | Candidate action | Required proof |
|---|---|---|
| Inductive turn-off | Flyback diode, TVS, active clamp, snubber | Peak voltage, decay time, repetition heat |
| Overcurrent/short | Fuse, current limit, foldback, e-fuse | Trip delay, I²t, restart and fault energy |
| Reverse supply | Series FET/diode, ideal-diode controller | Drop, reverse current, startup behavior |
| Surge/ESD | TVS, filtering, shielding, layout | Source waveform, clamp voltage, pulse rating |
| Thermal runaway | Derating, sensor, shutdown, foldback | Hot-case behavior and restart policy |
| Cross-domain fault | Isolation, creepage, current limiting | Withstand, leakage, fault containment |

Protection must survive the source, not merely the nominal load. Check TVS standoff and clamp values at the actual current, diode reverse recovery, capacitor ESR, fuse interrupt rating, and repeated-fault thermal accumulation.

## Original thermal example

A 24 V load draws 0.65 A and a high-side switch has a guaranteed hot resistance of 120 mΩ. Conduction loss is `0.65² × 0.12 = 50.7 mW`. A 2 A, 20 ms startup pulse gives `0.48 W` during the pulse only if the switch remains in the ohmic region; linear-mode intervals require `VDS × IDS` from the waveform and SOA. If the board path were independently verified as 70 °C/W steady state and ambient is 45 °C, the steady junction rise is `0.0507 × 70 = 3.55 °C`, giving an estimated junction temperature of `48.55 °C` absolute, only when the package thermal model applies. If an overload lasts 400 ms at 2 A, the ohmic screening energy is `0.48 × 0.4 = 0.192 J`; pulse SOA and transient thermal impedance decide survival.

## Thermal review

| Question | Evidence |
|---|---|
| Is loss conduction, switching, magnetic, gate, or quiescent? | waveform and calculation |
| Is the rating steady or transient? | thermal model and pulse duration |
| What is the hottest junction? | thermal path plus measurement |
| Does heat change resistance or current? | hot characteristics |
| What repeats the pulse? | duty cycle and fault cycling |

For inductive loads, record inductance or measured stored energy, current at turn-off, clamp location, clamp voltage, and decay requirement. A diode lowers voltage but may slow release; a TVS or active clamp trades voltage for loss. Measure load terminals and switch pins because wiring inductance can hide local spikes. Keep high-di/dt loops small and protection current out of sensitive returns; a schematic symbol does not prove placement, parasitics, or pulse rating.

## MCU boundary

An MCU GPIO is a control signal. It is not a power supply for motors, relays, solenoids, servos, high-current LEDs, or large capacitive loads. Specify the external driver, gate/base current, supply, ground or isolation, clamp path, power-up default, and reset behavior. Test with a current-limited supply, oscilloscope at the device pins, thermal measurement, and repeated fault cycles.

## Exit evidence

Require a measured normal waveform, startup and shutdown waveform, peak clamp voltage, current and temperature at controlling corners, and a demonstrated recovery path for each fault. If the fault waveform is unknown, the protection result is incomplete.

## Sources

- [Infineon MOSFET linear mode and SOA](https://www.infineon.com/assets/row/public/documents/24/42/infineon-applicationnote-linear-mode-operation-safe-operation-diagram-mosfets-applicationnotes-en.pdf?fileId=db3a30433e30e4bf013e3646e9381200) — conditional SOA and thermal analysis.
- [TI technical-document index](https://www.ti.com/technical-documents/techdoc/results?docCategoryId=1&familyId=64&litCount=all&rootFamilyId=64) — manufacturer application notes for transient thermal impedance and SOA; select the exact device family.
## MOSFET gate and resistance

Threshold voltage is the onset of a small specified drain current, not the voltage that guarantees low resistance. Use the RDS(on) specification at the actual gate voltage and temperature. Check gate-charge, driver source/sink current, Miller plateau, turn-on/off time, and false turn-on from dV/dt. A slow or floating gate can spend damaging time in linear mode.

## Protection rejection

Reject a clamp that has no source waveform, a fuse with no interrupt rating, or a diode whose reverse-recovery and repetition loss are unknown. Test a shorted switch, open clamp, stuck enable, reversed supply, and repeated restart. Thermal shutdown behavior is not a complete fault strategy unless restart and energy limits are specified.

## Verification

Measure at the silicon pins, not only at the bench supply. Use a probe and ground connection that do not create the spike being measured. Correlate electrical waveform, current, case temperature, and reset/log evidence.
