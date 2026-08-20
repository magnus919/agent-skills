# Model Validation Plan

## Intended Use

- Model/version:
- Population and decision boundary:
- Forecast or outcome horizon:
- Deployment cadence:
- Information available at scoring time:

## Evaluation Design

- Split type: [grouped / blocked / rolling / nested / other]
- Training window:
- Validation window:
- Test window:
- Gap or embargo:
- Unit and group leakage checks:
- Refit and tuning policy:

## Metrics

- Point prediction:
- Probabilistic score:
- Calibration:
- Ranking/discrimination:
- Tail or aggregate-loss metric:
- Segment stability:
- Business decision metric:

## Robustness and Sensitivity

- Alternative outcome definitions:
- Alternative distributions/links:
- Missing-data sensitivity:
- Tail and stress scenarios:
- Regime or period sensitivity:
- Parameter/model-form uncertainty:

## Release Gate

- [ ] Data and feature provenance verified
- [ ] Evaluation partition is leakage-safe
- [ ] Diagnostics reviewed
- [ ] Uncertainty reported
- [ ] Limitations and intended-use restrictions documented
- [ ] Independent review completed
- [ ] Monitoring and rollback triggers assigned
