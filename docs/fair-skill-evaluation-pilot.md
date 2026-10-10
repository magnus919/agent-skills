# Fair six-skill evaluation pilot

[`fair-skill-evaluation-pilot-v1.json`](fair-skill-evaluation-pilot-v1.json)
pins six representative cases, historical skill revisions, source-grounded
oracle facts, and mutation targets. It records inventory presence separately
from behavioral verification. The current plan is intentionally `plan_only`:
it made no generation or Jev calls, and frozen outputs are suitable only for
testing evidence handling.

The primary comparison is `pinned_skill_vs_skill`. Stage the baseline skill
from the exact per-case Git revision in the manifest, then pass that root with
`--baseline-skill-path`. Both arms receive the same neutral system wrapper and
the same task prompt. The candidate arm resolves reference pins from its own
snapshot; the baseline arm resolves them only from the baseline snapshot. The
separate `skill_vs_no_skill` mode remains a diagnostic and is labeled in each
comparison report.

For example, after preparing a detached baseline worktree:

```sh
python3 -m eval_runner.paired product-design-and-ux/evals/evals.json \
  --adapter fake \
  --comparison-mode pinned_skill_vs_skill \
  --baseline-skill-path /tmp/pilot-baseline/product-design-and-ux \
  --output-dir /tmp/pilot-output
```

Generation payloads contain the task, neutral wrapper, and that arm's pinned
skill/reference context. Expected output, assertions, oracle labels, and
mutation targets remain outside generation. The adapter records full SHA-256
pins for each supplied source, task prompt, neutral wrapper, and model
settings, plus the exact serialized message hash.

The optional evidence contract is kept in
[`eval_runner/fair-pilot-evidence-contracts-v1.json`](../eval_runner/fair-pilot-evidence-contracts-v1.json)
so a six-case pilot does not count as six modified skill roots in the
five-skill CI selector. It separates task-input hashes, authoritative source
hashes, expected observable outcomes, prohibited behavior, required evidence,
and oracle type without changing `evals-v1`. The selector puts only the task
prompt and hash-verified authoritative source text into a separate
`judgment_context` field for the post-generation Jev audit. The auditor treats
that material as untrusted reference data, retains its hash, and still judges
the generated response against the assertion. None of this context is read by
the generation adapter.

The offline oracle module has deterministic positive and mutation fixtures for
business state transitions, typed proposals, policy boundaries, stakeholder
coverage, and judge qualification. These oracles check structured facts; they
do not parse prose. The Raleigh case also has executable command/tool fixture
checks in its existing test suite. All six prose outcomes still require
independent human review. A fake-adapter smoke can confirm the six pinned pair
artifacts and input wiring; it cannot establish that a skill improves an
answer.
