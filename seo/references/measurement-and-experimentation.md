# AEO measurement and experimentation

## Measurement hierarchy

Track outcomes separately: crawl access, index eligibility, retrieval, mention, citation, citation correctness, share of voice, click, and conversion. A citation count cannot establish authority, ranking, correctness, or revenue.

## Frozen prompt set

Store stable IDs, exact prompt text, target entity, intent, expected source boundary, and version. Include disambiguation, definition, comparison, procedure, troubleshooting, current-status, and negative-control prompts. Do not silently rewrite prompts between runs.

## Observation record

For every run preserve date/time, provider, surface, model/version if known, account/location state, prompt ID/hash, exact answer, cited URLs, target-cited status, citation quality, correctness, and notes about provider changes. Normalize URLs for analysis without destroying the original URL.

## Identity, discovery and recommendation probes

Keep branded factual prompts, unbranded customer discovery and recommendation-fit probes in separate cohorts. Record the actual search/browse state and whether evidence came from supplied text, live retrieval, or an unknown mechanism. A source link is not proof that every adjacent sentence is supported. Preserve omitted brands and absent/no-answer responses in the denominator; do not retry until a favorable result appears.

A fresh or Temporary Chat is not automatically unpersonalized. Inspect current product settings and record memory, custom instructions, connected apps/plugins, search mode, login state, language, geography and time. OpenAI documents that Temporary Chat may still be personalized; use an explicitly unpersonalized mode where available and verify its current controls. If settings are unavailable, label the run uncontrolled rather than pretending to have a neutral baseline. Do not alter the user's persistent settings without permission.

Record “recommended” only when the answer actually recommends the entity for the stated need, and separately score fit and factual accuracy. Ranking within one generated list is not a stable organic rank. Platform runs and prompts are clustered observations, not automatically independent trials.

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

Google documentation is in transition: the older AI-features page includes AI traffic in Web reporting, while its newer AI optimization guide links a dedicated Generative AI performance report. Inspect the current property and report access; preserve the observed reporting definition, dates and available dimensions. Do not claim the report is universally unavailable or promise dimensions not verified. The 2026-11-07 research confirmed the official report link but could not fully inspect its CAPTCHA-protected help page. Bing Webmaster Tools AI Performance reports citations, cited pages, grounding queries, and trends, but its documentation explicitly says aggregate values do not show ranking, authority, placement, or page importance. Preserve those definitions in the report.

## Cadence

Use weekly or monthly checks only when the prompt set and ownership justify them. Re-run after provider changes, high-risk content updates, or observed miscitation. Stop after a bounded experiment when results are inconclusive; do not manufacture a win from more retries.

## References

- [Bing AI Performance](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview)
- [Google AI features measurement](https://developers.google.com/search/docs/appearance/ai-features)
- `templates/citation-observation-log.md`

- [OpenAI: Temporary Chat FAQ](https://help.openai.com/en/articles/8914046-temporary-chat-faq) — verify current personalization controls; reviewed 2026-11-07.

- [Google: AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) and [Generative AI performance report](https://support.google.com/webmasters/answer/16984139?hl=en) — see the documented access limit in `references/geo-practitioner-evidence.md`.
