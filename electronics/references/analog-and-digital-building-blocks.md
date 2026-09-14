# Analog and digital building blocks

## Input and output legality

For an op amp, comparator, reference, logic IC, timer, or converter, check input common-mode range, differential input limit, bias/leakage, output swing at the real load, output current, supply headroom, startup state, overload recovery, timing, noise, and temperature guarantees. “Rail-to-rail” describes a region or condition, not an exact rail voltage at arbitrary current and frequency.

A comparator and op amp may share a schematic symbol but differ in output topology, input protection, propagation behavior, recovery, and stability. Select by required threshold behavior and output interface, not symbol.

## Feedback and stability

Identify the feedback factor, noise gain, source impedance, input capacitance, output capacitance, cable, ADC sample capacitor, protection network, and load. Simulate the actual network, then test a populated board with step response, load transients, and supply corners. TI's [stability theory note](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/14/SBOA626_2D00_stability_2D00_9_2D00_16_2D00_2025.pdf) and [capacitive-load article](https://www.ti.com/document-viewer/lit/html/SSZT999) document ringing, long settling, and oscillation from added poles and phase-margin loss. Applicability: TI amplifier methods; use the exact amplifier stability specification.

An isolation resistor can decouple an op-amp output from capacitance, but it also creates an RC pole with the load and may change settling, current limit, and filter response. Record its value, load range, capacitor bias dependence, and worst-case step response. Do not “fix” oscillation by adding arbitrary capacitance to a feedback node.

## Threshold design

Define rising and falling thresholds, reference source and tolerance, noise band, hysteresis, propagation delay, pull-up/pull-down, output load, and supply-ramp behavior. TI's [comparators with hysteresis](https://www.ti.com/lit/an/snoa654a/snoa654a.pdf) explains the risk of a slowly changing input lingering in a high-gain transition region. Hysteresis, filtering, and firmware debounce solve different problems.

### Original threshold example

A 0–3.3 V sensor should assert at 2.10 V and deassert at 1.95 V. The 150 mV gap is a system requirement, not automatically a resistor value. Allocate reference error, divider tolerance, input offset, input noise, and temperature drift first. If their worst-case sum consumes 120 mV, only 30 mV remains for switching uncertainty; redesign the reference or thresholds before implementing positive feedback. Verify both transitions with a slow ramp and injected noise, plus power-up and sensor-disconnect tests.

## ADC and digital boundaries

Check source impedance against acquisition time, anti-alias filter loading, reference drive and decoupling, grounding, return currents, clock coupling, code width, missing codes, and sample timing. Microchip [AN688](https://www.microchip.com/en-us/application-notes/an688) states that ADC layout depends on the complete system and environment. Analog Devices [MT-031](https://www.analog.com/MT-031) covers mixed-signal grounding, routing, and decoupling. These are general guidance; the converter's datasheet and evaluation board take precedence.

For logic, verify VIH/VIL at the receiver's supply and temperature, VOH/VOL at the actual load, edge rate, pull resistor current, boot-state contention, and level translation. A nominal “3.3 V logic” label does not prove compatibility across families.

## Failure signatures

| Observation | Candidate causes | Check |
|---|---|---|
| ringing after edges | phase margin, cable/load capacitance | isolate load; measure step |
| threshold chatter | hysteresis, noise, reference coupling | slow ramp with injected noise |
| codes wrong only with firmware | digital return or sampling coupling | quiet-clock capture |
| output misses rail | load current or topology | sweep load and inspect limits |
| slow overload recovery | saturation or protection conduction | measure recovery |

An inverting stage with `Rin=12 kΩ` and `Rf=180 kΩ` has ideal gain `-15`. A forgotten 3 kΩ source resistance changes it to `-12`, before tolerance, bias, and finite open-loop effects. Redraw source impedance and recompute noise gain, bandwidth, and stability. For counters, shift registers, timers, and displays, record clock tolerance, setup/hold, propagation delay, reset release, metastability exposure, output enable, and power-up state; validate voltage and temperature corners.

## Verification output

Return a legal operating region, worst-case threshold or gain, stability evidence, interface timing, measurement setup, and any unknowns. A simulation that omits package, cable, ADC sampling, or load capacitance is a hypothesis, not proof.
## Noise gain and settling

For an op amp, noise gain is determined by the feedback network even when signal gain is different. Use noise gain for stability, input voltage-noise contribution, and bandwidth. Check settling to the required error band after a full-scale step; a small-signal bandwidth number does not prove settling.

## Comparator rejection

Reject a comparator topology when its input range, output pull-up, propagation delay, or hysteresis is unspecified at the real supply. Test a slow ramp, noisy ramp, fast overdrive, input disconnect, and supply ramp. Record both threshold directions and output state when unpowered.

## Digital evidence

A logic analyzer can miss analog ringing and marginal VIH/VIL. Pair protocol decoding with oscilloscope voltage at the receiver pin and current in the return path.
