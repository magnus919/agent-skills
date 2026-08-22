# Model Families

Choose a family from the outcome support and data-generating structure, not from the
algorithm currently in fashion. A candidate is not validated merely because it converges.

| Structure | Candidate families | Questions and checks |
|---|---|---|
| Continuous, approximately symmetric | Linear regression, transformed regression, robust regression | Linearity, variance, leverage, residual dependence, transformation interpretation |
| Binary or categorical | Logistic/probit, multinomial/ordinal models | Class prevalence, separation, link fit, calibration, threshold costs |
| Counts | Poisson, negative binomial, quasi-likelihood, hurdle/zero-inflated models | Exposure offset, overdispersion, structural zeros, integer support, dependence |
| Positive skewed amounts | Gamma/log-link, lognormal, inverse Gaussian, robust or quantile models | Positive support, retransformation, tail fit, heteroscedasticity, aggregate implications |
| Zero plus positive amount | Two-part/hurdle, frequency-severity, Tobit only when censoring assumptions fit | Zero mechanism, conditional severity, exposure, dependence between parts |
| Proportion or bounded outcome | Binomial/beta-type models, fractional response | Denominator, boundary masses, dependence, calibration |
| Event time | Survival, accelerated-failure-time, proportional-hazards, recurrent-event models | Censoring, truncation, competing risks, time-varying covariates, proportionality |
| Repeated or clustered | Fixed/random effects, mixed models, GEE, hierarchical models | Cluster definition, within-cluster correlation, missingness, transportability |
| Ordered time | Dynamic regression, ARIMA/state-space, exponential smoothing, volatility models | Information cutoff, stationarity, seasonality, interventions, rolling validation |
| Extreme or tail-focused | Quantile, generalized Pareto/extreme-value, tail-adjusted GLM, scenario analysis | Threshold choice, tail dependence, sparse data, extrapolation uncertainty |

## Generalized linear model checklist

Specify the response distribution, link, linear predictor, exposure offset, estimation
method, and interpretation scale. Check whether the variance function matches the data,
whether the link is plausible, whether overdispersion or zero inflation remains, and
whether residuals are independent enough for the intended inference. For an insurance
rate, distinguish a frequency offset from a severity weight. A convenient transformation
is not an offset.

## Common traps

- Poisson does not become appropriate merely because the target is called a “count.”
- Negative binomial handles overdispersion, not arbitrary dependence or zero mechanisms.
- A log-transformed response is not automatically equivalent to a log-link model for the
  original conditional mean; retransformation and target interpretation matter.
- Tobit is a censored-outcome model, not a generic answer for any target with zeros.
- A random effect is not a magic correction for omitted-variable bias or leakage.
- A survival model needs an event origin and censoring story, not only a duration column.
- Extreme-value extrapolation is fragile when the tail threshold or data-generating regime
  is uncertain. Show sensitivity rather than one authoritative tail number.

## Model comparison

Compare candidates on a predeclared, decision-relevant evaluation design. Include a simple
baseline and a transparent benchmark. Compare both performance and failure behavior:
calibration, tail loss, segment stability, operational cost, interpretability, data needs,
and monitoring burden. Complexity must earn its place with evidence.
