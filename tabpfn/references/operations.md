# Local installation, terms and artifact boundaries

## Pin before installing

Inventory Python/OS/accelerator and package metadata with the helper. Resolve a
package version with the selected checkpoint generation in a new environment.
Record the exact requirements/lock and official recipe revision. Do not globally
upgrade Torch or install into another project. The repository currently documents
Python 3.10+ and accelerator-specific behavior; verify compatibility with the
installed release and tiny operation rather than only an import.

Code and weights have separate terms. The inspected README describes Apache-2.0
repository code, separate non-commercial terms for later model generations, and
a different attribution-bearing prior license for v2 weights. The model page and
release-specific license files are authoritative for the selected artifact; any
apparent documentation conflict needs resolution before use. A non-commercial
checkpoint must not silently become a commercial/production offering. Record
approved scope and actual terms; do not automatically accept agreements for a user.

## Authentication and network

First-use model acquisition can invoke browser login/license acceptance and cache
a token. Headless token variables are authentication, not permission to accept
terms. Never write tokens into a script, config committed to Git, logs or reports.
Use the approved cache and explicit model file. Hosted `tabpfn_client` is a different
data-transfer boundary from the local package; local installation does not make
hosted calls private or offline. Check telemetry/weight fetching behavior in the
installed code and test egress policy before claiming offline operation. A local
checkpoint path and Hugging Face offline variable alone do not prove no networking.
The privacy page failed extraction in this investigation; no telemetry guarantee
is inferred from that omission.

## Explicit local recipe shape

After authorizing setup, pin a local trusted checkpoint and use the matched API:

```python
from tabpfn import TabPFNClassifier
model = TabPFNClassifier(model_path=approved_local_checkpoint, device="cuda")
model.fit(train_features, train_labels)
probabilities = model.predict_proba(test_features)
```

This is the documented API shape, not a executed recipe or promise all checkpoint
releases accept identical parameters. Inspect the installed signature and exact
checkpoint contract, supply real immutable paths and preserve the labeled context.
For regression use the version-matched regressor/output interface. Avoid silently
switching a GPU-only task to CPU or hosted inference. Do not deserialize untrusted
pickle/checkpoint/estimator files; assess the serialization format and source.

## Artifact and restart contract

Save checkpoint identity, package/env versions, schema/column order, category/text
processing, labeled train-context hash/location, class mapping, ensemble/seed/
subsampling configuration and calibration object. An estimator pickle alone is
neither a portable deployment bundle nor proof of exact train-context recovery.
Include privacy/storage/retention decisions for labeled data. Load in a fresh
process with compatible versions and compare fixed input predictions and output
class order, then task metrics. Separate numeric tolerances from calibrated
policy acceptance. Pin derived weights if fine-tuned; do not relabel them as the
original checkpoint.

For serving, budget reloading/caching costs and concurrency; document whether each
worker replicates context/model state. Preserve an accepted bundle/config for
rollback. Operations are complete only when actual requested load/predict/reload
and policy tests run. Prepared code and inventory exit zero are not completion.
