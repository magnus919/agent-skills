# Claim Audit and High-Stakes Escalation

Load this reference when a message contains numbers, comparisons, testimonials, studies, causal claims, or a decision that could cause material harm.

## Claim decomposition patterns

| Pattern | Ask | Common failure |
|---|---|---|
| “X% improvement” | Compared with what, over what period, among whom, using which metric? | Relative change presented as absolute impact. |
| “Up to / as low as / starting at” | What conditions produce that result, and how common are they? | Best case presented as expectation. |
| “Experts agree” | Which experts, in what field, based on which review or data? | Prestige substituted for domain-relevant evidence. |
| “Studies show” | Which study, population, outcome, comparator, effect size, and limitation? | A real study used to imply a broader conclusion. |
| Testimonial | Is it representative, independently verified, and relevant to this claim? | Anecdote treated as typical outcome. |
| “X caused Y” | What is the counterfactual, alternative cause, mechanism, and study design? | Correlation, sequence, or story treated as causation. |
| “Everyone is saying” | How many independent origins exist? | Reposts and affiliated outlets treated as corroboration. |
| “Act now” | What becomes worse if independent verification happens first? | Urgency suppresses normal evidence standards. |

## Evidence hierarchy

1. **Primary evidence:** original data, full study, official record, filing, source code, direct measurement, or on-the-record statement.
2. **Independent synthesis:** systematic review, meta-analysis, trusted research institution, or careful investigative reporting that exposes methods and sources.
3. **Secondary reporting:** useful for discovery, but trace its most important claims upstream.
4. **Interested party material:** press release, marketing page, testimonial, advocacy argument, or social post. Treat as a claim to verify, not proof.

Evidence strength depends on relevance, methodology, independence, recency, and whether it supports the exact claim rather than a neighboring one.

## Authoritative-source check

For every material factual claim, pick the source of truth that can settle the claim type, retrieve it directly, and record the URL, access date, scope, and result.

| Claim type | Preferred source of truth | Do not substitute |
|---|---|---|
| Empirical result | Original dataset, full study, protocol, or systematic review when it answers the exact question | An abstract, press release, or article about the study |
| Legal or regulatory claim | Controlling law, regulation, court record, regulator guidance, or official filing | A commentator’s summary or a law firm’s marketing page |
| Product capability or incident | Current owner documentation plus direct reproduction, status record, or incident report | A demo, testimonial, or stale comparison |
| Financial or corporate claim | Filing, audited report, regulator record, or the company’s primary disclosure, then independent context | An affiliate article or reposted announcement |
| Public statistic | Responsible agency’s dataset, methodology, and release | An infographic or chart without a dataset |

When the claimant controls the source, distinguish “the organization says” from independently established fact. A source of truth may confirm a narrow fact while leaving the message’s larger implication unproven.

## Lateral-reading sequence

1. Capture the precise claim and URL.
2. Search the organization or author plus `funding`, `ownership`, `criticism`, `methodology`, or the claimed study/report title.
3. Open at least two independent sources before assigning high confidence.
4. Trace statistics to original tables, datasets, or methods.
5. Check whether apparent corroborators cite one original source or have independent evidence.

## High-stakes escalation

**Applicability:** financial transfers, medical choices, legal claims, security incidents, identity or authorization requests, public allegations, or irreversible actions.

- Separate identity from authorization: a known voice, logo, or video is not permission.
- Require an independent primary source or out-of-band confirmation.
- Preserve the exact claim, source URL, access date, and key evidence before acting.
- Escalate to a qualified human where professional judgment or authority is required.
- Do not report a “false” verdict unless the contradiction is documented and directly relevant.

## Effort budget and output template

Choose the smallest evidence pass that fits the decision. Stop when the pass either reaches its evidence gate or documents why it cannot.

| Stakes | Minimum pass | Stop or escalate when |
|---|---|---|
| Low | Decompose the claim, identify the source of truth for any material factual assertion, and retrieve it when it can settle the point. | The authoritative source settles the narrow claim, or the output records why the claim remains Unsupported or Unknown. |
| Medium | Trace the strongest factual claim to a primary source and check one independent source for corroboration or contradiction. | The primary source and independent check agree, or their disagreement has a named cause. |
| High | Preserve the claim and evidence trail; seek primary, independent confirmation or out-of-band authorization. | The decision can be deferred, evidence remains unavailable, or qualified human authority is required. |

Do not keep collecting sources after a pass has reached its gate. Report an evidence gap rather than manufacturing confidence.

Use `assets/claim-audit.md` for the single canonical report template.
