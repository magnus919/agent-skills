# Fair six-skill evaluation pilot

[`fair-skill-evaluation-pilot-v1.json`](fair-skill-evaluation-pilot-v1.json)
pins six representative cases, historical skill revisions, source-grounded
oracle facts, and mutation targets. It records inventory presence separately
from behavioral verification. The current plan is intentionally `plan_only`:
it made no generation or Jev calls, and frozen outputs are suitable only for
testing evidence handling.

The primary comparison is `pinned_skill_vs_skill` with the explicit
`complete_package` policy. Both skill roots must be clean Git snapshots at the
declared full revisions. The runner verifies both identities and preflights
both arms' context hashes before its first adapter call. Candidate references
come from the candidate snapshot; baseline references come from the baseline
snapshot or a case-specific `--baseline-reference-map` that points to files in
that old snapshot. It never copies a candidate reference into the baseline. If
the old snapshot has no matching case manifest, provide that explicit baseline
map or choose `instruction_only`, which sends each arm's `SKILL.md` without
reference files. Reports label the policy and both source revisions. The
separate `skill_vs_no_skill` mode remains a diagnostic.

For example, after preparing clean detached worktrees for both revisions:

```sh
python3 -m eval_runner.paired product-design-and-ux/evals/evals.json \
  --adapter fake \
  --case embedded-loan-recovery \
  --comparison-mode pinned_skill_vs_skill \
  --comparison-policy complete_package \
  --candidate-revision 20ff7c0beb8241f085383927a567d36a0bccd040 \
  --baseline-skill-path /tmp/pilot-baseline/product-design-and-ux \
  --baseline-revision 6384b6c1e327022b373f05b560974e2611cbd6a1 \
  --baseline-reference-map docs/fair-skill-evaluation-baseline-references-v1.json \
  --output-dir /tmp/pilot-output
```

The checked-in [baseline reference map](fair-skill-evaluation-baseline-references-v1.json)
binds `embedded-loan-recovery` to three relevant UX references from its exact
historical snapshot. For other cases whose old eval manifest lacks the new
case ID, create a version-1 map with paths and SHA-256 pins from that baseline
snapshot. An explicit empty map for a case means that snapshot contributes no
reference files; it does not authorize using candidate references.

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
