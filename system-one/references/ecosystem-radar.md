# System One ecosystem radar

Snapshot checked 2026-09-25. This is a discovery aid, not a quality ranking.
Download counts, stars, and community benchmark claims move quickly. Confirm
model card, code, license, revision, and target-data evaluation before adoption.

## Primary candidates

| Candidate | What is established publicly | Operational posture |
|---|---|---|
| TypeSafe Jev | Managed System One API; Choice/Score/Noul; parallel questions; official docs and SDK | Hosted only; no public weight download |
| Convai Innovations Laya | Open Apache-2.0 family; Python runtime; English, multilingual, and specialist checkpoints; router | Self-host Python; community ONNX/Node adapter also exists |
| Laya typed-decisions | Laya specialist checkpoint for four documented workflows | Explicit opt-in specialist; not a general silent default |
| Contrastive-LM CLM-v0.1-8B | Open Apache-2.0 head over frozen Qwen3-8B; Choice/Score/Noul wire API plus candidate ranking | Self-host Qwen3-8B pooling encoder and CLM head; see [CLM guidance](clm.md) |

## Select a model for the actual decision

Start with the cheapest deterministic rule or existing workflow that can meet the decision contract. If learned judgment is needed, use these as **shortlist rules**, then run a matched held-out comparison before selecting a winner:

| Need or constraint | Candidate to investigate first | Decision boundary |
|---|---|---|
| Managed typed API with no model-hosting capacity | Jev | Keep provider egress, cost, and availability in the contract; no self-hosted Jev weights |
| Private typed Choice/Score/Noul service with smaller or multilingual checkpoint choices | Laya family | Select the exact checkpoint and validate language, option budget, calibration, and runtime |
| Closed candidate ranking, repeated action pool, or best-of-N verifier with 8B encoder capacity | CLM | Candidate-set probabilities are relative; published verifier wins require task fine-tuning and do not transfer automatically |
| Local English label classification without a probability-distribution requirement | GLiNER2.5-Decide | Its labels are not Jev-shaped Choice/Score/Noul probabilities; use an explicit adapter |
| Exact eligibility, arithmetic, permissions, or irreversible approval | Deterministic code or accountable human | No model probability authorizes the action |
| Open-ended text or image understanding | Appropriate generative or multimodal model | A closed text-candidate model cannot generate or inspect unseen modalities |

For Jev, Laya, and CLM on the same contract, preserve state, question wording, candidate descriptions, option order policy, and independently assigned labels. Measure quality and calibration by primitive, unknown/review coverage, cold and warm latency at the same client boundary, resource cost, and end-to-end outcomes. CLM's `clm-raw` is an ablation of its encoder; it is not an independent model choice. A task-fine-tuned CLM head should be compared separately from the zero-shot reference and from any specialist Laya checkpoint.

## Open/community candidates worth screening

These projects use a similar typed-decision contract but are independent unless
their own cards say otherwise:

- `Meanblock/JEV-CPU`: Qwen3-0.6B fine-tune with a small CPU-oriented scope.
- `Mapika/decider-0.8b` and `Mapika/decider-2b`: open typed-decision family;
  inspect the model card for context, limits, and serving path.
- `GestaltLabs/Jeff-1`: a LoRA-based Jev-style adapter with a local HTTP demo.
- `lostargon/Tiny-Jev`: a small local model with Choice/Score/Noul-style
  methods and remote-code loading; review code before enabling `trust_remote_code`.
- `AmeenAhmed2/zico`: a larger open decision model with a PyTorch/MLX local
  path and its own input/runtime contract.
- `Praveenrajus/jevify-qwen3.5-4b` and other “Jev-style” cards: candidate
  compatibility work, not evidence of TypeSafe model identity or parity.
- Vision/edge variants such as Laya Vision or AXERA Laya packages: useful only
  when the input modality or accelerator is in scope; verify license and the
  fixed option/sequence limits.
- `fastino/GLiNER2.5-Decide`: local English classifier with call-time labels,
  multiple heads, and optional multi-label output. Its `classify_text` result
  is a label or labels, not a Jev-compatible probability response. See
  [operational guidance](gliner25-decide.md) before adapting a decision client.

## Screening procedure

For each candidate, capture:

1. Owner and model-card/repository URL; last release and immutable revision.
2. License for weights, code, base model, tokenizer, and datasets.
3. Actual primitives and response schema; whether probabilities are normalized.
4. Input modality, context/head limits, option cardinality, languages, and
   batching behavior.
5. Load/runtime requirements, device fallback, server/client maturity, and
   offline artifact path.
6. Training/evaluation data, calibration method, independent held-out evidence,
   and known failure cases.
7. Privacy, telemetry, `trust_remote_code`, network egress, and supply-chain
   risks.
8. A matched target-data result and a decision: adopt, shadow, investigate, or
   reject.

## Source links

- Jev official: https://typesafe.ai/blog/introducing-system-one-models-and-jev
- Laya official repository: https://github.com/NandhaKishorM/laya
- CLM repository and model card: https://github.com/Contrastive-LM/CLM and https://huggingface.co/Contrastive-LM/CLM-v0.1-8B
- Open model catalog (discovery only): https://decisioneval.dev/compare/
- JEV-CPU card: https://huggingface.co/Meanblock/JEV-CPU
- Decider card: https://huggingface.co/Mapika/decider-0.8b
- Jeff-1 card: https://huggingface.co/GestaltLabs/Jeff-1
- Tiny-Jev card: https://huggingface.co/lostargon/Tiny-Jev
- Zico card: https://huggingface.co/AmeenAhmed2/zico
- GLiNER2.5-Decide card: https://huggingface.co/fastino/GLiNER2.5-Decide
