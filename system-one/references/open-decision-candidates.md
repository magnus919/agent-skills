# Open decision-model candidates

Checked 2026-09-27. This is a source-based screening note, not a ranking or
endorsement. These projects implement related decision readouts; they do not
establish compatibility, calibration, or quality parity with TypeSafe Jev.
Pin the model and serving revisions used in an actual comparison. Revision
hashes below came from GitHub or Hugging Face metadata on the date above and
may not match another local checkout.

## Candidate map

| Candidate | Pinned model/revision checked | Architecture and probability meaning | Context, options, runtime | 16 GB memory screen |
|---|---|---|---|---|
| Eikos | `caiovicentino1/Eikos-4B` at [`2b0f4d1`](https://huggingface.co/caiovicentino1/Eikos-4B/tree/2b0f4d13c0eda1225eaccd6a7e3f09eb07ae38f4); `caiovicentino1/Eikos-27B` at [`103a564`](https://huggingface.co/caiovicentino1/Eikos-27B/tree/103a5647c0131fd00abc165675fcee243d33a789) | Fine-tuned causal Qwen models: 4B base `Qwen/Qwen3.5-4B` at [`851bf6e`](https://huggingface.co/Qwen/Qwen3.5-4B/tree/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a); 27B base `Qwen/Qwen3.8-27B` at [`1d4bf0f`](https://huggingface.co/Qwen/Qwen3.8-27B/tree/1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0). Readout is next-token option-letter logits, softmax restricted to offered options. | Repository reports all three types and a `vLLM >= 0.30` serving path. 4B training inputs up to 32k and 27B up to 12k; it also reports a 64k probe. Default server length is 16,384. Option limits are configuration-dependent; read the pinned `decision_config.json`. | 4B has 4.66B parameters: BF16 weights-only arithmetic is about 8.68 GiB; ideal 4-bit arithmetic about 2.17 GiB. 27B has 27.78B parameters: about 51.75 GiB BF16 or 12.94 GiB ideal 4-bit weights-only. These are not runtime-memory measurements; context, kernels, quantization metadata, and workspace add memory. |
| Shisa DE-1 | `shisa-ai/shisa-de-1` at [`9111f47`](https://huggingface.co/shisa-ai/shisa-de-1/tree/9111f4746a96d6cdf9f1a23a88afd5b57244508b) | Causal `google/gemma-4-26B-A4B-it`, no added task head. Reads next-token logits at the answer position and restricts/normalizes across valid option letters. This establishes a distribution conditional on those options, not calibration. | Card says one request per question, one generated token, and requires each answer letter to tokenize as one token. Base card advertises 256K context; practical prompt and serving limits depend on vLLM configuration. | Hub reports 25.8B BF16 parameters and 48.1 GiB on disk. Ideal 4-bit weights alone would be about 12.0 GiB, but no matching validated 16 GB quantized serving result was found. BF16 does not fit. |
| AutoJev | `denis-pplx/autojev-27b` at [`6f5b557`](https://huggingface.co/denis-pplx/autojev-27b/tree/6f5b557e037f5edb25c7dc92dbc6553e5a19c015) | Full-weight SFT of `Qwen/Qwen3.8-27B`; author describes one-pass-per-question probabilities over declared choices. Endpoint supports text and optional images; image quality was not evaluated in the published README. Scalar temperature is fitted separately. | `choice`, `noul`, and `score`; the accessible README does not establish a context or maximum-option limit. Author documents roughly 49 GiB of BF16 weights plus runtime overhead. | Hub reports 26.1B BF16 parameters, about 48.6 GiB weights-only by arithmetic. Ideal 4-bit arithmetic is about 12.15 GiB before overhead; no 16 GB quantized serving result was found. The Hub metadata currently says public and ungated. An older README sentence says weights are private; treat that sentence as stale relative to the 2026-09-27 Hub metadata. |
| Kev | `jaredpalmer/kev-0.8b`, `kev-4b`, `kev-9b`, `kev-27b`; checked revisions [`9a45d25`](https://huggingface.co/jaredpalmer/kev-0.8b/tree/9a45d25eb2ab761841196625383fa1dff0e56c1e), [`139fdd9`](https://huggingface.co/jaredpalmer/kev-4b/tree/139fdd94f1b6a6ad80cc15e08fcb99cac885a101), [`2629c06`](https://huggingface.co/jaredpalmer/kev-9b/tree/2629c06a5aeb0feb3b9783bafed17ed8f39ecf5c), [`01b8199`](https://huggingface.co/jaredpalmer/kev-27b/tree/01b81998019be550f0ae858727df49bac9511195) | Qwen-family base plus fine-tuned LoRA and a trained pointer head, which scores the option spans directly. Supports Jev-shaped `choice`, `score`, and `noul`. Each checkpoint has a development-set temperature. | Serving accepts up to 65,536 state tokens, while training used at most 384 state tokens and 1,024 state-plus-question tokens. Repository tests commonly use an 8,192-token context and document option-order sensitivity. | Maintainer recommends a 32 GB Mac or L40S/H100 for 4B and 9B; 0.8B is the laptop-sized choice. A 4B BF16 base is about 7.45 GiB of weights by arithmetic; 16 GB is only a plausible short-context test, not a maintainer-verified target. |
| SemIf | Readout project [`TheoLeeCJ/SemIf-OpenJev`](https://github.com/TheoLeeCJ/SemIf-OpenJev/commit/23cf1f39fc9534fe81437200959b6dfc7106e45a); direct baseline uses `Qwen/Qwen3.5-4B` at [`851bf6e`](https://huggingface.co/Qwen/Qwen3.5-4B/tree/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a) | Not a separately fine-tuned checkpoint: a direct option-logit readout over a frozen causal Qwen model. Softmax is applied to the designated answer-token logits; no answer token is generated. Project also contains a distinct reranker mode; do not conflate its yes/no-difference scoring with direct logits. | The pinned method evaluates 2–16 described options. Shared-state mode can prefill state once. Per-workload temperature scaling is reported for selected labeled workloads, with out-of-fold ECE; this is narrow evidence, not universal calibration. README provides a Qwen3.5 4B BF16 path plus quantized GGUF examples. | The 4B BF16 parameter-only estimate is about 7.45 GiB. Project reports an MLX peak allocation of about 8.6 GB on a 24 GB M5; this is a measured configuration, not proof for every 16 GB machine or context. A 4-bit GGUF is smaller but has a different numerical path. |
| OpenJev `verdict-1.4` | Backing checkpoint `heman10x/rlcd-modernbert-151m` at [`8af2496`](https://huggingface.co/heman10x/rlcd-modernbert-151m/tree/8af2496eb63c7fa66d7d234e1f62629380030eb4); OpenJev adapter repository at [`a0ddd7d`](https://github.com/razorback16/openjev/commit/a0ddd7d928298eccef2c17153b00b5636b6d996a) | Bidirectional ModernBERT-base / GLiClass encoder and classification head, about 151.4M parameters. Verdict adds an explicit insufficient-evidence class and post-hoc temperature scaling. OpenJev removes that class and renormalizes remaining probabilities; its adapter also documents that Verdict ignores `noul` criteria. | Verdict v1.4 accepts up to 24 substantive options and 512 input tokens including the options. PyTorch on CPU or GPU; OpenJev reports about 1.2 GB GPU memory in its tested setup. | F32 weights alone are about 0.56 GiB; comfortably within 16 GB. The 512-token cap is likely the tighter operational limit. |

## Evidence and selection limits

The table reports the particular model revision and readout, not a universal
System One capability. A normalized softmax is not evidence of calibration.
Where temperature fitting is disclosed, confirm the calibration data matches
the intended workload and does not overlap evaluation data. Authors' benchmark
reports are not independent replications; preserve the corpus, split, labels,
question text, option order, and runtime when running a matched comparison.

The memory figures multiply parameter counts by bytes per parameter, then
divide by 2^30 to report GiB: BF16/F16 assumes 2 bytes per parameter; ideal
4-bit assumes 0.5 bytes.
They estimate model weights only. They do not predict actual peak VRAM/RAM,
quantized artifact size, cache, image encoder overhead, or context capacity.
An absent 16 GB result means unverified, not impossible. Use published artifact
sizes and a measured target-runtime load before deployment.

The Hub API returned current model revisions and access flags for the listed
models. It reported AutoJev public and ungated on 2026-09-27 despite the stale
private-weight sentence in its README. A direct API lookup for the Eikos data
repository returned HTTP 401, which does not establish whether it is gated or
private; its access state remains unverified. GitHub API heads were captured
during this check:

- [Eikos source at `e8d6936`](https://github.com/caiovicentino/eikos/commit/e8d693620779f1ced5de866b950920a28f900f03)
- [AutoJev source at `ee63c15`](https://github.com/denis-pplx/autojev/commit/ee63c1515980491a742f0bd0685c8dc5ca1f00c3)
- [Kev source at `5920c5f`](https://github.com/jaredpalmer/kev/commit/5920c5fe4ca8e0970ed4209ac2c9b8e18bea5109)
- [Verdict source at `30f1556`](https://github.com/Heman10x-NGU/Verdict-open-jev/commit/30f15564821626ca5c1ad5b2638c4eb7078787dd)

For Verdict, use its upstream repository and model card rather than relying on
the OpenJev adapter summary: [Verdict source](https://github.com/Heman10x-NGU/Verdict-open-jev),
[checkpoint card](https://huggingface.co/heman10x/rlcd-modernbert-151m),
[OpenJev adapter](https://github.com/razorback16/openjev). The authors describe
an Apache-2.0 checkpoint and code; independently confirm any downstream
dependency and dataset terms before redistribution.

## Training, selection, calibration, and licenses

- **Eikos:** The repository documents rank-64 LoRA, one epoch, option-letter
  soft cross-entropy, option permutation, and an auxiliary rationale loss.
  The 4B release combines two recipes; the repository describes generated and
  programmatic training data, decontamination against the named evaluation
  suites, held-out family/topic/language slices, and temperature 1. It
  describes the 4B checkpoint as a two-recipe model soup; the full checkpoint
  selection criterion is not explicit in the checked source. Model cards
  label the fine-tuned weights MIT; the Qwen base models are Apache-2.0, and
  the author lists CC BY 4.0 plus row-level terms for the dataset. The dataset
  metadata request returned HTTP 401 in this check, so download/access status
  remains unverified. Current Hub weight revisions are linked above.
- **Shisa DE-1:** The card describes 3,632 training examples in four use areas,
  trained with cross-entropy on the restricted option-letter rows. It reports
  no post-hoc temperature fitting; probabilities are normalized logits, not
  demonstrated calibrated probabilities. It does disclose 29 evaluation
  suites, 13 option-reversed variants, plus specific failure probes. The exact
  training-corpus composition and checkpoint-selection rule are not stated in
  the checked card. The checkpoint and Gemma base declare Apache-2.0. Confirm
  the applicable Gemma
  terms in the upstream base card for the intended use.
- **AutoJev:** The source repository reports full-weight SFT, 73,000 training
  examples, checkpoint 200 after 286 updates, and a separately fitted scalar
  temperature. The curated training corpus is not bundled. Its accessible
  aggregate evaluation does not disclose enough detail here to verify the
  case-level split or selection protocol. Repository code is MIT and the
  checkpoint/base are listed as Apache-2.0. Hub metadata said the checkpoint
  was public and ungated on 2026-09-27; the repo's “weights are private” note
  appears stale. Do not infer an access failure from that sentence.
- **Kev:** Cards and repository expose training recipes, dataset/source
  manifests, development and locked-test reports, and a per-checkpoint
  temperature fitted on in-distribution development data. Checkpoint
  selection uses development results before a one-time locked-test read.
  Accuracy and probability quality differ by source; do not carry an
  in-distribution temperature or score over to an untested workload. Code,
  adapters, heads, and Qwen bases are Apache-2.0; training datasets retain
  their own terms, listed per card.
- **SemIf:** For its direct Qwen3.5-4B baseline, the model is frozen and the
  readout is not trained. The project reports temperature fitting and
  out-of-fold ECE on selected authored, WANLI, and “Every” workloads. It
  commits prompts, fixtures, row outputs, and revisions, and explicitly
  distinguishes a native-logit baseline from a separate reranker. Project code
  is MIT; upstream model and dataset terms remain in force.
- **Verdict / OpenJev:** Verdict's card documents a ModernBERT/GLiClass
  classifier trained with cross-entropy plus Brier loss, then post-hoc
  L-BFGS temperature fitting; it uses validation NLL for checkpoint selection
  and reports a 1,000-example held-out split plus challenge slices. Its card
  documents limits in missing-option abstention, distractor handling, and
  option-order sensitivity. The upstream model and repo are Apache-2.0. The
  OpenJev adapter changes the output contract by removing Verdict's abstention
  class and renormalizing; test calibration again after that transformation.
  Verify the terms for its training data and transitive libraries before
  redistribution.

## Routing shortlist

Investigate the small encoder Verdict when token budgets are short and its
candidate-set behavior fits; consider SemIf when the goal is to evaluate a
frozen generative base through direct option logits; compare Kev when a
trained pointer head and repository-documented training pipeline matter; and
screen Eikos, Shisa DE-1, or AutoJev when their larger Qwen/Gemma bases or
specific training scope justify local memory and serving costs. These are
investigation triggers only. Choose only after a target-task comparison, and
use a separate vision evaluation before routing images to any multimodal base.
