# Local specialization: research brief

Question: which data, verifier, compute and evaluation conditions justify local
model specialization, and what expertise should the catalog supply?
Commissioned by Magnus; comprehensive technical track; 2026-10-13.

## Conclusion

Specialization is useful when a defined workload benefits under a measured
quality/cost contract. A language model is one candidate, not the default
architecture for every verdict. Enrich existing ML Engineering for selection and
Unsloth for local execution. Retain stronger classifier/rules, zero-shot/NLI,
retrieval and task-specific inference alternatives; do not add a thin SkyRL or
hosted CDM wrapper. Coding specialization needs runnable tasks, reviewed data,
trusted verifiers and independent fixed-budget acceptance, not just falling loss.

## Findings and evidence

| Finding | Confidence and interpretation | Source records | Contrary/limiting evidence |
|---|---|---|---|
| Start with task-appropriate simpler alternatives and comparable information | High as a decision requirement; winner unresolved on private data | trees-tabular, zero-shot-benchmark, hf-zero-shot, coinbase-1/2/3 | booking-fraud challenges universal tree superiority; no matched Coinbase classifier comparison |
| Runnable tasks and reviewed trajectories support software specialization | Medium-high for published settings; local benefit unmeasured | swe-gym, swe-smith-paper, evalplus-paper, deepswe | Synthetic tasks/public benchmarks/resource scales differ from user workloads |
| SFT/RL choice is empirical, not a universal title or capability claim | High about uncertainty; expected local uplift unresolved | sft-rl-generalization, rlvr-limits, rlvr-reasoning, small-code-rl | Different domains/metrics; LLM reasoning judges; sparse/all-equal rewards |
| Verifier integrity is a separate engineering problem from learning | High for need; prevalence/effect task-specific | evalplus-paper, verifier-audit, leaky-reward-abstract, anthropic-reward | Stronger tests can falsely reject gold; hardening need not raise held-out capability |
| Consumer-GPU feasibility needs a representative complete-loop measurement | High as an engineering boundary | qlora, unsloth-memory, small-code-rl, coinbase-3 | 24GB/96GB/64-H100 findings do not validate this 16GB host; paging may use CPU RAM |
| Adaptation/export success can regress other capabilities | Medium-high for risk; specific remedies need trials | lora-forgetting, peft-merge, vllm-lora | Hyperparameter/data/runtime differences and lossy quantization require independent checks |
| Task-specific classification/extraction/summarization are additional alternatives | Medium for documented contracts; architecture/quality claims unverified | patel-concept, scaledown-classify/extract/summarize/provider | Hosted availability does not imply local weights/training, calibrated scores or faithful summaries |

## Confidence assessment

Primary papers, author repositories and official docs form the retained corpus.
Case studies and vendor benchmarks are labeled author-reported; no numerical
performance result was reproduced on a GPU. Paper/project/README versions from
the same work are linked evidence, not counted as independent experiments.
Conflicting RL interpretations and classifier findings are preserved explicitly.
The supplied X thread was only partially visible; the user-described classifier
critique is orientation, not an attributed quote from unseen replies.

## Implemented expertise

- Unsloth references: coding dataset/label/SFT acceptance, local RLVR/verifier/
  isolation/resource workflow, and primary-source evidence routing.
- Unsloth templates: specialization record, reward contract and explicitly
  synthetic six-category verifier receipts.
- Read-only specialization audit: provenance fields, source-group/prompt/content
  overlap, bounded scans and verifier challenge consistency; no model/code execution.
- ML Engineering references: rules/classifier/zero-shot/generative/task-specific
  choice, temporal/class-prevalence concerns, matched-budget comparisons and
  explicit research limitations.
- Study template and synthetic task receipts; descriptive paired comparison
  helper with complete roster/pins, distinct execution statuses and group bootstrap.
- Stable output-quality eval cases with satisfying/contradictory/omission
  challenges; these manifests are review assets, not semantic passes.

The inherited GPU SFT recipe remains distinct. New coding/RL stages are prepared,
not run; the helpers' offline tests establish their contracts only.

## Open questions and proposed next experiment

1. Does a task-appropriate classifier match contextual LLM review at lower cost
   under equal history/features and label maturity? Coinbase's data is unavailable.
2. Which supported small code instruction model has sufficient baseline task
   success and useful reward variation on our real workload?
3. Does SFT add value over a tuned prompt/retrieval control? Does optional RL add
   further benefit at equal inference and development-selection budgets?
4. Can representative prompt/generation groups fit the shared GPU with no
   unauthorized paging/offload, contention or environmental changes?
5. Are task-specific CDM scores calibrated and extractions/summaries faithful on
   our inputs, and what architecture/local-weight evidence is actually available?

Use the new study template to preregister a bounded real-task pilot before any
training. Freeze numerical acceptance and regression/resource thresholds from
user goals and baseline evidence; do not select thresholds after seeing outcomes.

## Durable artifact and preservation gate

[Evidence corpus](evidence-corpus.md) contains 45 original source-level records,
including explicit exclusions; [machine-readable ledger](evidence-ledger.json)
retains URLs, access date, extraction scope, limitations and snapshot hashes.
[Search/exclusion log](research-log.json) records discovery and follow-up chains.
[Scope protocol](research-scope.md) records prior hypotheses and boundaries.
Skill references link to relevant primary sources; this synthesis maps findings
to those source records. Whole publications were read locally through GroktoCrawl
but are not redistributed in the repository. Inaccessible and incomplete sources
have explicit status. No critical claim depends only on chat or a scratch summary.
