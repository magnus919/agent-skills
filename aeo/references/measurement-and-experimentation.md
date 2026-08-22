# AEO measurement and experimentation

## Measurement hierarchy

Track outcomes separately: crawl access, index eligibility, retrieval, mention, citation, citation correctness, share of voice, click, and conversion. A citation count cannot establish authority, ranking, correctness, or revenue.

## Frozen prompt set

Store stable IDs, exact prompt text, target entity, intent, expected source boundary, and version. Include disambiguation, definition, comparison, procedure, troubleshooting, current-status, and negative-control prompts. Do not silently rewrite prompts between runs.

## Observation record

For every run preserve date/time, provider, surface, model/version if known, account/location state, prompt ID/hash, exact answer, cited URLs, target-cited status, citation quality, correctness, and notes about provider changes. Normalize URLs for analysis without destroying the original URL.

## Scoring

Use a rubric defined before looking at results:

- target mention: 0/1;
- target citation: 0/1;
- citation relevance: 0–2;
- citation support/correctness: 0–2;
- answer completeness: 0–2;
- harmful or misleading claim: 0/1;
- target answer coverage across the set: percentage, with denominator stated.

Keep human scoring, automated extraction, and provider-native dashboard metrics distinct.

## Experiment design

Write `hypothesis → change → expected mechanism → prompt set → window → metric → result → confounders → decision`. Keep the content change and measurement method stable enough to compare. Repeated model outputs are not independent evidence by default. Provider model, index, UI, location, personalization, and prompt changes can confound the result.

A before/after observation supports “we observed a change under these conditions,” not “the rewrite caused the change,” unless the design supports causal inference.

## Platform-native evidence

Google Search Console reports AI feature traffic within its search reporting and provides a generative AI performance report where available. Bing Webmaster Tools AI Performance reports citations, cited pages, grounding queries, and trends, but its documentation explicitly says aggregate values do not show ranking, authority, placement, or page importance. Preserve those definitions in the report.

## Cadence

Use weekly or monthly checks only when the prompt set and ownership justify them. Re-run after provider changes, high-risk content updates, or observed miscitation. Stop after a bounded experiment when results are inconclusive; do not manufacture a win from more retries.

## References

- [Bing AI Performance](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview)
- [Google AI features measurement](https://developers.google.com/search/docs/appearance/ai-features)
- `templates/citation-observation-log.md`
