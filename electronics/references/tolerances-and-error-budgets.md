# Tolerances and error budgets

## Define the claim first

Write the output quantity, operating interval, acceptance limit, and whether the limit is guaranteed, statistical, calibrated, or measured. A value such as “one percent accurate” is incomplete without temperature, supply, load, time, bandwidth, and confidence or coverage.

Partition error into:

- initial offset, gain, and reference error;
- component tolerance and matching;
- temperature coefficient and thermal gradients;
- supply sensitivity, loading, and leakage;
- noise, quantization, aliasing, and EMI;
- nonlinearity, hysteresis, repeatability, drift, aging, and self-heating;
- fixture, instrument, installation, and model uncertainty.

Label which terms calibration can remove. Calibration generally cannot remove random noise, changing hysteresis, future drift, an unmeasured installation shift, or an unbounded fault.

## Worst-case method

1. Express the output as a function of all bounded variables.
2. Define each variable's valid interval and correlation.
3. Evaluate nominal, all sign-relevant extrema, and temperature/supply corners.
4. Include loading and leakage in the same equation, not as a later footnote.
5. Compare the worst result with the requirement and record the controlling terms.
6. Use Monte Carlo only as a supplement to, never a replacement for, a bounded analysis.

For `y = f(x)`, the first-order estimate is `Δy ≈ Σ |∂f/∂xi| Δxi` when variables are small and smooth. This absolute-sum form is a conservative bounded estimate; statistical combinations require an explicit independence or covariance model. Use interval evaluation or direct corner enumeration when nonlinearities, saturation, clipping, or correlations matter.

## Original divider example

A monitor divides a 17.6 V rail by nominal resistors 68 kΩ and 10 kΩ. The ideal output is `17.6 × 10/(68+10) = 2.256 V`. With each resistor bounded at ±0.5%, the high output occurs with the lower upper resistor and higher lower resistor: `17.6 × 10.05/(67.66+10.05) = 2.276 V`; the low output occurs with the converse limits: `17.6 × 9.95/(68.34+9.95) = 2.236 V`. The resistor-only interval is therefore about ±0.9% around nominal, before monitor input leakage, reference error, temperature coefficient, noise, and rail measurement error. This is a bounded corner calculation; physical correlation may make some corners less likely or infeasible, while statistical confidence requires a separate model.

If the monitor input leakage is 80 nA and the Thevenin resistance is approximately `68 kΩ || 10 kΩ = 8.72 kΩ`, the added static error is about `0.70 mV` at the sense node. Whether that matters depends on ADC LSB, threshold margin, and the rail-to-output transfer. Recalculate at the actual leakage sign and temperature.

## Matching and calibration

Matched resistor networks may preserve ratios better than independent parts. State the matching specification, tracking temperature coefficient, and common substrate assumptions. Four equal-tolerance resistors in a difference amplifier can still create common-mode to differential conversion when ratios mismatch; use the exact topology's error expression.

For calibration, retain raw readings and fit residuals. Do not report the fitted curve without the reference values, instrument uncertainty, temperature, supply, sample count, and out-of-range behavior. Distinguish repeatability from reproducibility and accuracy from resolution.

## Evidence

- [TI Precision Analog Applications Seminar — Remote System Monitor Applications](https://www.ti.com/lit/pdf/slyp160) — opposite tolerance directions in divider examples; educational and historical.
- [TI SLVA450B, IQ vs Accuracy Tradeoff In Designing Resistor Divider Input To A Voltage Supervisor](https://www.ti.com/lit/an/slva450b/slva450b.pdf) — leakage, divider selection, and total accuracy; comparator/supervisor topology-specific.
- [TI regulator-divider report](https://www.ti.com/lit/an/slva423/slva423.pdf) — resistor tolerance plus regulator accuracy and environmental drift; use the exact regulator data.
- [TI matched difference amplifier](https://www.ti.com/lit/pdf/sboa582) — matching and CMRR; circuit assumptions apply.

## Error classes and correlations

| Class | Behavior | Treatment |
|---|---|---|
| Offset/bias | fixed or temperature dependent | calibrate only if stable |
| Gain/reference | multiplicative | calibrate span; include drift |
| Random noise | sample dependent | characterize bandwidth |
| Hysteresis | history dependent | measure both directions |
| Nonlinearity | signal dependent | inspect residuals |
| Aging/installation | time or mounting dependent | qualify and define recalibration |

For `Vout = Vref(1 + Rtop/Rbot)`, ratio accuracy can be good while reference drift dominates. Use partial derivatives to rank terms; sensitivity to `Vref` is `1 + Rtop/Rbot`. Do not use root-sum-square without independence evidence. Shared temperature, supply, substrate, or fixture can correlate errors; include covariance or bounded corners. Include instrument uncertainty, probe loading, fixture repeatability, gradients, and quantization before closing the budget.

## Output criteria

An error budget is decision-ready when every material term has a source, equation, interval or distribution, temperature/supply corner, correlation assumption, and verification method. Any missing term that could consume the margin remains `UNKNOWN` and blocks a confident pass.
## Systematic versus random

Systematic error shifts all units or all readings in one direction; random error varies between samples. A production average cannot prove a systematic offset is absent. Repeatability describes the same setup; reproducibility changes operator, fixture, or environment.

## Temperature and self-heating

Use the actual component temperature, not ambient alone. For a resistor, estimate P=V2/R or I2R, then apply its temperature coefficient over the measured temperature rise. For a sensor, excitation can change the measured quantity; model self-heating as part of the transfer function.

## Acceptance

Choose a guard band when measurement uncertainty is not negligible. If the requirement is plus or minus 1 unit and measurement uncertainty is plus or minus 0.4 unit, a reading of 0.8 unit cannot prove compliance without a defined decision rule.
