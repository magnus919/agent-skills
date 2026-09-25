# GLiNER2.5-Decide as a local decision classifier

Source checked 2026-09-24: [Fastino model card](https://huggingface.co/fastino/GLiNER2.5-Decide), [GLiNER2 code](https://github.com/fastino-ai/GLiNER2), and [fast-decisions dataset card](https://huggingface.co/datasets/fastino/fast-decisions). Recheck the card, code, license, and revisions before deployment.

For upstream classification training options and checkpoint-compatibility checks,
read `references/gliner25-decide-fine-tuning.md`.

## Fit and contract boundary

Fastino describes `GLiNER2.5-Decide` as an English, Apache-2.0, local classifier for operational labels. It accepts label sets at call time and can score several independent heads over one text in a single call. Single-label heads return one label string; multi-label heads return a list above a configured `cls_threshold`. Its card describes a 340M-parameter DeBERTa-v3-large encoder and CPU/GPU operation through `gliner2`. Verify the downloaded artifact size and tensor count for the selected revision before capacity planning.

Use it for bounded routing, intent, severity, or handoff classification when the application's trusted configuration owns the labels. It does not provide Jev Choice/Score/Noul semantics or a Jev response schema. An ordinal string label such as `"5"` is a class, not a calibrated Score probability. A `"yes"`/`"no"` head is a classification, not a Noul answer. Do not present its returned label as a probability, confidence, explanation, verified policy decision, or authorization.

## Local smoke test

In an isolated Python environment, install the upstream `gliner2` package and pin a tested package version and Hugging Face model commit for reproducibility. The model card's minimal API is:

```python
from gliner2 import AutoExtractor

model = AutoExtractor.from_pretrained("fastino/GLiNER2.5-Decide")
result = model.classify_text(
    "My subscription renewed after the service was down. Please refund it.",
    {
        "intent": ["refund_request", "technical_issue", "other"],
        "handoff": ["yes", "no"],
    },
)
print(result)  # e.g. {"intent": "refund_request", "handoff": "no"}
```

The comment illustrates the response shape, not an asserted model result. Load from an immutable local snapshot in a private deployment; verify the model and tokenizer revision, actual device, and a representative inference before declaring readiness. Keep the checkpoint resident, bound input length and concurrency, use private authenticated ingress, and exclude sensitive text from logs. Record latency including queue time and memory use under realistic traffic. Roll back to the previous pinned package and snapshot if quality or operations regress.

## Application adapter

Define each head and allowed label set in trusted configuration. Reject missing or extra heads, unexpected labels, wrong single/multi-label shapes, and duplicate multi-label values. Route malformed or unavailable results to the contract's review or fallback lane. For multi-label work, tune `cls_threshold` on held-out target data; it is a label-selection threshold, not an application-wide confidence guarantee. Keep eligibility, exact rules, action authority, and side effects in deterministic code.

If an application already uses Jev-shaped questions, write an explicit adapter with a distinct model identity and its own output type. Do not silently map classification labels to Choice distributions or claim Jev/Laya parity. Compare the incumbent and Fastino on the same frozen inputs and labels, including abstention or `other`, multilingual and out-of-domain cases, calibration only when comparable scores are actually available, and downstream policy outcomes. Fastino's card reports 60.2% average exact-match accuracy on its 17-domain `fast-decisions` suite versus 57.6% for JevK5 and 46.6% for Laya Router; those are vendor-reported results on that suite, not proof of superiority on your workload. The card directs multilingual inputs to `GLiNER2.5-multi-Decide`; validate that separate checkpoint before use.
