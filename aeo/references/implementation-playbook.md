# AEO implementation playbook

## Phase 0: Scope the answer surface

Write a one-page scope before editing:

- audience and decision/job to be done;
- canonical entities, aliases, products, places, and disambiguators;
- target providers and surfaces, such as Google AI features, Bing Copilot, ChatGPT Search, or Perplexity;
- question families: definition, comparison, procedure, recommendation, troubleshooting, current status;
- desired outcome and non-goals;
- access, privacy, legal, and publication constraints;
- baseline date and evidence cutoff.

If the target surface is unknown, do not invent provider-specific tactics. Run a discovery pass and label the target as unresolved.

## Phase 1: Build the evidence and question map

1. Gather provider documentation before practitioner advice.
2. Gather authoritative subject sources and independent corroboration.
3. Build question clusters. Merge near-duplicates and identify questions that need separate pages because their answer, audience, freshness, or evidence differs.
4. Assign one canonical answer location to every retained question.
5. Record claims as source observation, vendor claim, inference, or unresolved conflict.
6. Identify stale, contradictory, or unsupported existing answers before rewriting them.

Use `templates/question-cluster.md` and the source card in `references/evidence-boundaries.md`.

## Phase 2: Implement the answer asset

For every canonical page or section:

1. State the answer in the opening sentence or compact summary.
2. Follow with scope, conditions, evidence, examples, and useful next actions.
3. Use headings that describe the reader's question without turning every keyword permutation into a page.
4. Use lists, tables, definitions, and examples where they improve human comprehension.
5. Keep entity names, versions, dates, units, and terminology consistent.
6. Link to primary evidence at the claim it supports, not only in a distant bibliography.
7. Distinguish current facts from historical context and forecasts.
8. Preserve a clear author/reviewer/update record where the subject warrants it.
9. Add a “what this does not mean” boundary for comparisons, safety, policy, or high-stakes claims.

Do not delete nuance to make a page more extractable. A concise answer followed by a qualification is better than an unqualified slogan.

## Phase 3: Add machine-readable and discovery support selectively

Choose only changes justified by the target provider and page content:

- JSON-LD that matches visible content and the correct Schema.org type;
- canonical links, crawlable internal links, accurate sitemap entries, and truthful `lastmod`;
- provider-specific robots controls after an explicit search/training/user-fetch policy decision;
- optional `llms.txt` when a site wants to publish a curated map for systems that choose to consume the proposal;
- a Markdown representation or content negotiation only when the site can keep it equivalent to the rendered HTML and the target consumer benefits from it;
- IndexNow or provider-native submission only through the platform's operational skill and only after the URL is actually ready.

AEO does not authorize publishing, changing robots policy, or sending URLs. Confirm target, scope, and rollback before mutation, then verify the public boundary.

## Phase 4: Verify before measurement

Run the read-only script and platform checks:

- fetch the final URL and inspect status, canonical, robots meta, headings, visible answer text, links, and JSON-LD;
- parse every JSON-LD block and compare material fields with visible content;
- check the public robots file and sitemap, including CDN/edge behavior;
- confirm true modification dates rather than generated-file timestamps;
- inspect a browser-rendered page when content is client-rendered;
- record what each check cannot prove: a 200 is not indexing, parsing is not eligibility, and eligibility is not citation.

## Phase 5: Establish a frozen answer baseline

Use a prompt set with:

- stable IDs and exact prompt text;
- head, mid-tail, long-tail, comparison, and troubleshooting variants;
- entity disambiguation prompts;
- prompts where the correct answer should cite the target and prompts where it should not;
- competitor or alternative entities only when the comparison is fair and evidence-supported.

Record exact output and citations. Do not summarize from memory. Use `templates/citation-observation-log.md`.

## Phase 6: Run bounded experiments

Change one meaningful variable or a coherent bundle whose rationale is documented. Keep the prompt set, observation method, date window, and scoring rubric stable. Re-run enough samples to expose variability, but do not imply statistical certainty without an appropriate design. For platform-native metrics, preserve the dashboard definition and aggregation limits.

A useful decision record says:

```text
hypothesis → change → expected mechanism → observation window → metric → result → confounders → next decision
```

## Phase 7: Maintain

Set review triggers based on content risk and volatility:

- source or specification change;
- product/version release;
- policy or legal change;
- answer error or miscitation;
- provider crawler or dashboard change;
- meaningful query or conversion shift.

Do not “refresh” a page by changing dates alone. Re-verify the claims, sources, links, schema, and answer observations after material updates.

## Acceptance gate

Pass only when:

- scope and provider boundaries are explicit;
- every retained question has a canonical answer location and owner;
- visible content answers accurately before elaborating;
- evidence, caveats, and dates are preserved;
- machine-readable fields match visible content;
- discovery and crawler changes are policy-approved and publicly verified;
- the prompt baseline and post-change observations are reproducible;
- the final report distinguishes implementation from observed impact.
