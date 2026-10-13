# Model, context and capacity decisions

TabPFN is a prior-data fitted network: pretraining uses synthetic datasets to
learn prediction conditional on labeled examples. At application time the training
rows/labels are input context. Distinguish this from pretrained text weights, a
nearest-neighbor embedding index, and a conventional estimator that discards raw
training examples after optimizing parameters. Weight fine-tuning is optional and
separate from the sklearn `fit` interface.

## Applicability and versioned constraints

Start with row count, feature count/types, target cardinality, missingness,
class imbalance, independence/time structure and prediction throughput. Evaluate
a linear/tree baseline with equal feature information and tuning time. Do not
infer causal structure from the synthetic structural-causal priors used in pretraining.
Good predictions neither identify causes nor validate medical/financial decisions.

The dated official models page distinguishes v2, later generations, local/hosted,
Plus/Thinking/Fast surfaces and class/text/row/column constraints. Current README
names v3.5 as default and a separate Fast checkpoint, while older APIs used separate
classifier/regressor weights. A version alias is not an immutable file/revision.
Pin package and weight revision, SHA-256, inference configuration and class order.
Check current docs at execution; never turn this dated guide into a latest-model
promise. Row and feature maxima trade off and cannot be assumed simultaneously
feasible. CPU guard overrides are not performance/capacity evidence.

Labeled-context size affects latency, memory and behavior. Record context retention
and per-estimator subsampling; subsampling or ensembling changes both cost and
quality, not only an OOM workaround. Identify rare classes lost by sampling.
Test maximum representative shapes, not one short row. Leave explicit device/RAM
reserve and monitor full process lifetime including initialization and caching.

## Distinct alternatives

TabICL/TabICLv2 are separate tabular foundation-model implementations using
in-context prediction, their own pretraining/architectural choices and sklearn-style
interfaces. Author benchmark claims motivate a matched comparison; they do not
establish parity with TabPFN or operational support through this skill. Evaluate
licenses/checkpoints, calibration, context size, fit/predict caching, ensembles,
feature transforms and compute on each implementation's own contract.

Tree baselines remain valuable; older tabular results and newer foundation-model
leaderboards concern different datasets/protocols. Use chronological/group tests
when deployment violates IID. A benchmark winner does not establish superiority
on fraud with delayed labels and interventions. Training labels in an inference
context do not make final-test labels permissible.

## Forecasting boundary

The inspected From Tables to Time paper maps forecasting to tabular regression
with temporal featurization. This is a distinct route, not evidence every TabPFN
checkpoint is a sequence model. Ensure lag/calendar/covariate features existed
at the forecast origin and compare rolling origins, horizons and a seasonal naive
baseline. Route sequence/forecasting design to ML Engineering and data-scientist.

## Selection record

Record objective/output, supported inputs, exact model/package, commercial/local
scope, context preparation, class map, measured cold/warm/complete-batch timings,
peak VRAM/RAM, quality by segment and rejection conditions. Document what is
vendor-reported, observed, unsupported or unknown. Do not use an advertised
million-row ceiling as a promise about a 16GB shared GPU.
