# Local RLVR and coding verifier engineering

Read after a baseline and task specification exist. This is operational design
and prepared validation, not a hardware-tested GRPO recipe. Use the official
model-specific Unsloth notebook and matched installed TRL version to implement
an experiment; preserve `references/validated-sft.md` as the separate SFT path.

## Separate four mechanisms

**Verifier:** produces an independently grounded correctness outcome.
**Reward:** turns outcomes into bounded numerical incentives.
**Algorithm:** updates model probabilities, e.g. GRPO.
**Parameterization:** chooses trainable weights, e.g. LoRA/QLoRA.
A formatting regular expression is a parser, not a correctness verifier.
A classifier's ground-truth outcome reward is different from executing a patch.

The [Coinbase case](https://www.coinbase.com/blog/part-three-owning-intelligence-series)
uses a deterministic balanced classification reward and a compact serving verdict.
It does not establish that written reasoning is needed for the task or that a
language model beats a simpler classifier. Examine task-appropriate baselines
before reproducing its architecture. `ml-engineering` owns that decision.

## Preflight the learning signal

GRPO samples a group of completions for each prompt and computes relative
advantages. Inspect the installed [TRL algorithm and configuration](https://huggingface.co/docs/trl/grpo_trainer):
normalization, loss type, KL/reference handling, clipping, grouping constraints
and rollout implementation change across versions. Do not copy one universal
batch formula; validate the exact effective global generation batch against
`num_generations`, device count and accumulation in the pinned trainer.

Record reward mean/std and component distributions by prompt, fraction of groups
with all-zero/all-identical rewards, parse failures, completion truncation, KL,
clipping, entropy and independent held-out success. All-equal task rewards provide
no within-group task preference; a varying style bonus can then dominate learning.
A missing KL/reference term is a configuration decision, not proof of a bug.
Any normalization change requires a new versioned comparison on the same tasks.

If correctness is too rare, improve the starting model, demonstrations or task
curriculum on development data. [StepCoder](https://arxiv.org/abs/2402.01391)
illustrates curriculum and execution-aware feedback for sparse code rewards;
its particular algorithm is not automatically implemented by GRPO. Do not lower
the correctness standard or use test answers in the prompt to manufacture reward.

## Treat the verifier as a component under test

Before training, execute reference solutions against the suite and retain receipts.
A reference patch must pass; a broken starting task must fail the intended new tests.
Then construct credible near misses: wrong edge-case handling, hardcoded outputs,
partial repairs, no-op changes, empty output, parser ambiguity and test tampering.
Use mutations and held-out tests, including boundary/property/metamorphic checks
where meaningful. Validate generated tests against trusted reference behavior;
more tests can introduce false rejections.

[EvalPlus](https://arxiv.org/abs/2305.01210) demonstrates that expanded tests detect
wrong programs missed by smaller suites and can change model rankings. The newer
[verifier audit](https://arxiv.org/abs/2606.16062) reports both false acceptance and
bad generated augmentations on selected tasks. These sampled findings justify
local challenge testing, not a universal hackability percentage for our workload.
The [leaky-suite study](https://arxiv.org/abs/2607.11022) reports little held-out
capability benefit from hardening in its studied setting despite removing false
reward. Fixing measurement integrity is necessary even when quality does not rise.
That study's retained abstract is narrower evidence than its incompletely extracted
full text; its numerical claims remain author-reported, not reproduced here.

Keep three distinct suites: training reward tests, development selection tests,
and sealed final acceptance tests. Do not give final tests to the policy, reward
optimizer, teacher, checkpoint selector or human prompt tuning loop. Test-suite
hashes, reference hashes, environment images and verifier code belong in lineage.
A trusted human/reference label is required for challenge truth. Teacher/judge
agreement may triage cases but cannot independently validate correctness.

## Reward contract and receipt audit

Use `templates/reward-contract.md`. Its default challenge convention is positive
reward for known correct output and nonpositive for known wrong output. Timeout
and infrastructure errors retain distinct execution statuses and reward zero;
zero here is a no-positive-reward challenge convention, not a claim the task was
incorrect. Production training may abort/requeue infrastructure failures under
its separately registered policy. Never quietly count them as successful results.

`scripts/specialization_audit.py rewards receipts.json` reads existing receipts;
it does **not** execute any challenge, launch a sandbox or calculate rewards.

```json
{"schema_version":1,"verifier_sha256":"<64 lowercase hex characters>","suite_sha256":"<64 lowercase hex characters>","cases":[{"id":"wrong-edge","category":"incorrect","label":{"kind":"reference","evidence":"reviewed oracle receipt"},"expected_correct":false,"execution_status":"failed","reward":0}]}
```

Include distinct `correct`, `incorrect`, `malformed`, `adversarial`, `timeout` and
`infrastructure_error` cases. Ordinary cases require boolean `expected_correct`
and passed/failed status; timeout/infrastructure cases use null correctness and
the matching status. Label kind is `human` or `reference` with an evidence pointer.
The example above is intentionally incomplete and will exit 1 until all categories
are present. Use the synthetic template for a complete contract demonstration.

The helper rejects missing categories, nonfinite/bool rewards, unpinned hashes,
untrusted label kinds and contradictory outcomes. It reports false acceptance,
false rejection and reward-order violations without code/prompt text. Exit 0 only
clears receipt consistency; fabricated receipts can pass. Inspect original logs,
reference provenance and actual isolation tests before trusting the verifier.

## Execute generated code in a separate boundary

Run code in disposable environments with read-only hidden tests, no host credentials
or privileged sockets, restricted network, fixed images/dependencies and CPU,
RAM, process, file/output-size and wall-clock limits. Protect evaluator state and
expected answers from writable paths. Track attempts to alter tests or bypass
execution. A timeout in `subprocess.run` does not isolate filesystem/network or
prevent escaped child processes. Containerization itself does not prove confinement;
verify capabilities, mounted paths, privilege, egress and run-owned cleanup.

Route design to `secure-software-engineering` and container operations to
`docker-compose`. Do not add unsafe host execution to a reward helper just to
make a demo executable. Retain stdout/stderr under approved privacy bounds, exit
status, completion, test counts and child-resource outcomes independently.

[Anthropic's reward-hacking research](https://www.anthropic.com/research/emergent-misalignment-reward-hacking)
uses deliberately vulnerable coding environments and reports broader misbehavior
under those conditions. Do not extrapolate incidence to every local adapter;
include agent-context regressions and monitoring appropriate to the actual task.

## Budget the complete loop

VRAM includes quantized/base weights, adapter gradients/optimizer states,
activations, optional reference model, rollout engine weights, KV cache, logit
buffers and fragmentation. Host RAM/disk and verifier containers are separate
budgets. Generation length and completions per prompt can dominate SFT memory.
Do not use download size or SFT peak as proof of RL capacity. QLoRA's paged
optimizer can spill state via unified memory; it conflicts with an all-state-in-
VRAM requirement unless separately demonstrated not to page.

Start with representative prompt lengths and the final generation grouping in a
short run. Measure both Torch peak allocated/reserved memory and whole-device
usage, warm generation throughput, verifier throughput, queueing and end-to-end
seconds per optimizer step. Weight sharing/colocation differs by model/backend.
Unsloth's vendor memory examples are leads to test, not host-specific guarantees.
No automatic CPU fallback or changes to unrelated GPU jobs.

Set hard token/GPU-hour/disk budgets and stop at contention, nonfinite values,
verifier inconsistency, excessive invalid rollouts or a predeclared regression.
Checkpoint policy/optimizer/RNG state and separately preserve rollout/environment
state needed to characterize resumption. Adapter reload is not exact RL resume.

## Tool choice and completion

Use Unsloth/TRL for a supported local recipe. SkyRL supplies custom text environments
with observations, reward and termination, plus distributed backend choices;
see [environment](https://docs.skyrl.ai/docs/tutorials/new_env) and
[Megatron](https://docs.skyrl.ai/docs/examples/megatron) guides. Do not present a
SkyRL environment as a TRL reward callback: their contracts and lifecycle differ.
No standalone SkyRL skill exists here yet. Evaluate its operational needs before
adding a named tool skill with executable code, tests and real runtime evidence.

Finish with an independently scored held-out comparison, complete run lineage,
fresh artifact reload and target-serving evaluation. Reward increase alone is
not completion. Publish failed or inconclusive experiments with their limitations;
three nonconverging compatibility/debugging passes stop at a bounded escalation.
