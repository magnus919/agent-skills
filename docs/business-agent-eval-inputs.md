# Business-agent evaluation inputs and challenge evidence

Follow-up to PR #683 and advisory run [37955122624](https://github.com/magnus919/agent-skills/actions/runs/37955122624). Generated-output omissions are not established defects in the checked-in worked examples. That run supplied SKILL.md only, with no file tools or reference contents. Its baseline was **no skill**, not the pre-PR skill. No old-versus-new improvement can be inferred.

## Explicit inputs

The optional `evals/openai-reference-inputs.json` adapter contract (version 1) maps existing case IDs to direct `references/*.md` files and full SHA-256 pins. It is separate from portable evals-v1; assertion text and IDs remain unchanged. Only the three new business cases opt in. Each gets its existing worked example; other cases retain entry-point-only behavior.

- Product UX: `embedded-loan-recovery` → `references/embedded-business-agent.md`.
- PydanticAI: `non-chat-proposal` → `references/application-proposals.md`.
- SDD: `policy-translation-fidelity` → `references/executable-business-policy.md`.

Only explicit files are injected. No directory discovery, recursive includes, fixture/oracle injection, or file tools are provided. Paths must be direct non-hidden Markdown references under the skill root; absolute/traversal paths, symlinks, missing files, pin mismatches, nonregular files, non-UTF-8 content, unknown case IDs, and size overflows fail closed before a model request. Limits: at most three references, 60,000 bytes per source, 80,000 aggregate reference bytes. SKILL.md also has a 60,000-byte bound; optional entry-point truncation is recorded. Source pins must be reviewed and updated deliberately when a reference changes.

`outputs.input_provenance` records actual source paths, full hashes, byte sizes, entry-point truncation, condition, comparison semantics, and the SHA-256 of the exact serialized transmitted messages. API credentials are outside that digest. No-skill baseline provenance has no sources and the same user prompt. Supplying a source does not prove the model applied it; adapter activation evidence is not behavioral evidence.

Tests inspect the actual HTTP request payload and provenance for all three cases, and prove unrelated/private sentinels and assertion/expected-output oracles are absent. Input-contract tests do not evaluate human usefulness.

## Grader challenges

`eval_runner/tests/fixtures/business_agent_judge_challenges.json` preserves exact bounded function excerpts from two independently reviewed false-positive baseline outputs, their full-response hashes, excerpt hashes, original assertions, and the original run. The parent-side artifact reviewer was an independent model reviewer (`model_teacher`), not a human adjudicator. These labels are review evidence, not calibrated ground truth.

The UX negative directly invokes `_attempt_reservation`, which generates a new UUID, during timeout recovery. It must not be credited with querying the original command. The PydanticAI negative checks role during approval but omits current permission/revision checks during execution. It must not be credited with execution-time authorization. Each has a synthetic corrected example and a missing-evidence example to distinguish `met`, `not_met`, and `not_shown`. No expectation was loosened. The deterministic grader still reports all prose as `manual_review`; fixture contract tests do not convert these labels to semantic passes or tune Jev to pass known misses. Future judge calibration needs independent labels and held-out outputs.

The SDD artifact also invented policy assumptions, accepted explicit version override and incomplete facts, described zero-day acceptance, and claimed unexecuted tests/100% compliance. These are generated-output flaws; entry-point safeguards now explicitly prohibit those shortcuts. Independent assessment of new outputs must preserve unrun/unsupported evidence as `not_shown`.

## Bounded live evaluation

The existing trusted-main-only workflow now permits these three skills in its manual allowlist. Dispatch each named case **once**, with the existing configured provider, 65,536 output-token ceiling and 300-second request timeout (normal push conventions). Candidate and no-skill baseline produce at most six initial generation requests in total. Existing adapter policy permits one bounded 429 retry respecting Retry-After up to 60 seconds; no unbounded reruns. Preserve partial failures and audit selection completeness. Jev remains advisory.

The trusted-main restriction is unchanged. This environment has no provider credentials, so live dispatch follows reviewed merge onto main. Do not claim its results before those bounded runs finish. Automated repository checks retain their existing scope; this change adds no unrelated eval manifests or general platform rewrite.
