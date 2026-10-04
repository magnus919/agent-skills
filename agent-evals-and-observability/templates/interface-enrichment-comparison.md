# Interface Enrichment Comparison

Use with [Agent Interface Enrichment Comparisons](../references/agent-interface-enrichment.md). Copy one row per configuration and case family. Fill unavailable values as `unavailable` with a reason; do not infer them.

## Decision and hypothesis

- Decision this evidence will inform:
- Owner and authority:
- Mechanism-specific failure hypothesis and predicted benefit:
- Plausible adverse outcome and falsifying observation:
- Task population, sampling source, dataset/version, rights, and limitations:
- Decision date and run/configuration identifiers:

## Configurations

| Arm | Discovery configuration | Artifact/inline configuration | Delegation/consumer | Session state | Model/runtime, tool/service versions, identity/permissions |
|---|---|---|---|---|---|
| Baseline | | | | | |
| Candidate | | | | | |
| Ablation (if needed) | | | | | |

Hold task, initial state, authorization, resource policy, result semantics/completeness, and grading constant within pairs. Declare discovery or inline/artifact transport as the treatment; its realized latency and resource usage may differ. If discovery and artifact transport both change, specify the ablation or limit interpretation to the bundled change.

## Task and trajectory contract

- User task and expected end state:
- Required discovery and prerequisite sequence:
- Allowed tools, identities, permissions, and side effects:
- Required artifact properties: intended identity, authorization, freshness, completeness, provenance:
- Required downstream/delegated consumption evidence:
- Fresh-session recurrence behavior:
- Prohibited outcomes, false success claims, recovery, or escalation:
- Graders and evidence sources for each claim:

## Adverse-case coverage

| Case | Included? | Expected safe behavior | Observable evidence | Outcome / gap |
|---|---|---|---|---|
| Irrelevant or ambiguous discovery / similar tool names | | | | |
| Missing prerequisite or permission-filtered capability | | | | |
| Missing artifact | | | | |
| Expired artifact | | | | |
| Partial pagination or incomplete output | | | | |
| Duplicate delivery or stale content | | | | |
| Wrong identity/tenant or revoked permission | | | | |
| Consumer incompatibility or inaccessible source | | | | |
| Delegation denied, partial, or missing provenance | | | | |
| Fresh-session ambiguous or stale match | | | | |

## Results

Keep all attempted runs in the denominator, including failures, denials, timeouts, partial outcomes, and missing observations. Show per-task and per-slice outcomes; retain paired discordances and repeats where stochasticity matters.

| Metric | Definition, denominator, and source | Baseline | Candidate / ablation | Effect and uncertainty | Unavailable reason |
|---|---|---|---|---|---|
| Task success and verified end state | | | | | |
| Correct discovery and prerequisite sequence | | | | | |
| Artifact integrity and actual consumer use | | | | | |
| Authorization, privacy, and side effects | | | | | |
| Failures / denials / timeouts / partial / missing | | | | | |
| Context use | | | | | |
| Latency distribution | | | | | |
| Monetary cost | | | | | |
| Orchestration / storage / transfer / cleanup | | | | | |

## Evidence verdict

- Supported result: improve / regress / inconclusive / not measured
- Claims directly established by observed evidence:
- Claims not shown, conflicting evidence, and missing instrumentation:
- Synthetic, vendor-reported, mocked, or prose-only evidence (label explicitly):
- Residual risks and required live integration or user evidence:
- Decision and owner:
