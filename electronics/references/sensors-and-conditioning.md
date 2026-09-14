# Sensors and conditioning

## Classify the output

Before choosing an interface, identify passive resistance, analog voltage/current, binary threshold, pulse/frequency/PWM, serial stream, or register-based digital output. Confirm excitation, loading, common-mode, reference, bandwidth, response time, warm-up, supply dependence, and fault signaling. A module's advertised measurement range may not equal its conditioned output range.

## Signal-chain failure modes

Inspect for excessive divider loading, ADC acquisition current, insufficient excitation, input-protection leakage, common-mode violation, aliasing, ground return coupling, op-amp saturation recovery, sensor self-heating, cable pickup, connector leakage, condensation, and installation stress. Add source impedance and protection to the small-signal model. Check sensor output during power-up, disconnect, short, overrange, and saturated conditions.

For an ADC path, establish reference accuracy/noise, sample rate, anti-alias filter, settling, grounding, and digital coupling. Microchip [AN1007, Designing with the MCP3551 Delta-Sigma ADC](https://ww1.microchip.com/downloads/en/Appnotes/01007a.pdf) emphasizes measuring and inspecting actual samples for the MCP3551 high-resolution converter; nominal bit count does not establish system performance. Applicability: the cited MCP3551 evaluation workflow, with the exact ADC taking precedence.

## Calibration design

Define reference standard and traceability, fixture, number and placement of points, temperature and supply corners, warm-up, fit model, residual limit, storage format, validity flag, recalibration trigger, and out-of-range behavior. Retain raw data, fitted coefficients, residuals, instrument IDs, and operator or automated-run metadata.

Separate offset/span correction from nonlinearity, hysteresis, repeatability, drift, installation error, and random noise. A calibration curve cannot make a sensor safe outside its characterized range. Analog Devices' [MAX1464 compensation note](https://www.analog.com/en/resources/app-notes/max1464-signalconditioner-sensor-compensation-algorithm.html) demonstrates temperature compensation under an explicit constant-supply assumption; validate that assumption in the target product. Its [MAX14XX diagnostic note](https://www.analog.com/en/resources/design-notes/adding-diagnostic-capability-to-max14xx-low-cost-high-performance-signalconditioning-devices.html) illustrates retaining reference checks to detect drift. Applicability: those signal conditioners and procedures.

## Original calibration example

A bridge sensor is calibrated at 0, 40, and 80 input units at two temperatures. The output, with units declared, is fit to `y = a0 + a1x + a2T + a3xT`; each coefficient carries derived units and the valid fit rectangle is recorded. Before accepting it, verify fit residuals at held-out points, repeat one reference after thermal cycling, and test supply variation if excitation is not truly ratiometric. A 3-point fit can pass endpoints while leaving a bowed middle residual; report the residual envelope and repeatability, not only coefficients.

## Sensor-specific questions

| Family | Failure question |
|---|---|
| Resistive temperature | Is excitation causing self-heating, and is lead resistance included? |
| Thermocouple | Are cold-junction, polarity, shielding, and common-mode limits handled? |
| Accelerometer/gyro | Are bias, cross-axis sensitivity, vibration, saturation, and orientation conventions tested? |
| Current/voltage | Is isolation, burden/drop, common-mode, and fault energy valid? |
| Optical/gas | Are ambient spectrum, contamination, aging, and warm-up characterized? |
| GPS/radio | Are antenna, sky view, latency, fix validity, and privacy requirements explicit? |

## Conditioning table

| Output | Verify first | Failure |
|---|---|---|
| resistance | excitation, leads, self-heating | measurement changes sensor |
| voltage | source impedance, common-mode, range | loading or clipping |
| current | compliance, burden, isolation | loop cannot regulate |
| pulse/PWM | amplitude, timing, pull-up, missing state | capture/noise errors |
| serial/register | framing, scaling, validity, stale data | invalid data accepted |

Use an independent holdout or repeat; fitting and acceptance on the same points hides model error. Test increasing and decreasing stimulus, warm-up, and supply variation separately. Define safe behavior for invalid, stale, disconnected, saturated, and implausible readings. The final enclosure, cable routing, mounting torque, airflow, optical window, and thermal path are part of the sensor. Store timestamp, stimulus, raw code, engineering value, temperature, supply, fixture state, and validity flags; plot residual against each variable before choosing a more complex fit.

## Output criteria

An integration recommendation is complete when the output class, signal chain, legal input region, calibration model, fault behavior, installation assumptions, and measured acceptance criteria are recorded. Otherwise produce a bounded experiment and state what remains unknown.
## Uncertainty chain

Convert sensor datasheet terms into system output units: sensitivity, offset, gain, nonlinearity, hysteresis, repeatability, drift, ADC/reference error, noise, and installation error. Keep sign and correlation assumptions explicit. Report a residual envelope and confidence method.

## Failure investigation

When readings jump, compare raw output, supply, reference, temperature, timing, and physical stimulus. A firmware average can hide aliasing or intermittent saturation. Check stale digital registers and invalid flags before filtering. Disconnect and short the sensor input to distinguish sensor, wiring, conditioner, and ADC faults.

## Calibration rejection

Reject calibration when reference conditions are untraceable, raw data is discarded, points do not cover the operating range, or the fitted model is accepted only at training points.
