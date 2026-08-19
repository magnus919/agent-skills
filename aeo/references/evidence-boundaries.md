# AEO evidence boundaries

## Working definition

Answer Engine Optimization is the disciplined work of improving the chance that a useful, attributable answer about a defined entity or topic can be discovered, retrieved, interpreted, and cited by an AI answer surface. The definition is operational, not a claim that providers expose one controllable ranking system.

AEO overlaps with SEO because many answer surfaces retrieve from search indexes. It is narrower because the primary outcome is answer inclusion and citation quality rather than a blue-link position. GEO, LLMO, AI search optimization, and answer optimization are overlapping industry labels; preserve the label used by the target provider or stakeholder, then define the actual outcome.

## Outcome taxonomy

Never collapse these into one metric:

| Outcome | Meaning | Evidence needed |
|---|---|---|
| Crawl access | A named crawler could fetch the resource | Server/CDN logs or provider documentation |
| Index eligibility | A page can enter a provider's index | Provider diagnostics; not guaranteed by a 200 |
| Retrieval | A page was selected for a query or grounding step | Provider-native data or a reproducible observation |
| Mention | Entity appears in generated text | Exact answer snapshot |
| Citation | Answer links or names a source | Exact answer plus URL |
| Citation correctness | Citation supports the adjacent claim | Read the cited source and compare scope |
| Share of voice | Entity appears relative to a defined comparator set | Frozen prompts, sampling, date, scoring rules |
| Click/referral | User visits after an answer interaction | Analytics with known attribution limits |
| Conversion | User completes a defined outcome | Instrumented funnel and causal design |

## Evidence labels

Use these labels in plans, reports, and references:

- **Primary documentation:** provider, standards body, schema vocabulary, or tool owner documents its own behavior.
- **Observed:** a recorded answer, crawl, response header, rendered page, dashboard value, or reproducible local result.
- **Independent study:** a method and dataset are disclosed well enough to assess, but it may not generalize.
- **Vendor-reported:** a commercial provider reports an analysis, lift, or benchmark. Useful as a hypothesis source, not a universal rule.
- **Inference:** a reasoned interpretation that goes beyond direct observation. Mark it as such.
- **Unresolved:** plausible but not verified, provider-dependent, stale, or contradicted.

## What Google establishes

Google's current Search Central guidance says its AI Overviews and AI Mode use existing Search systems and that there are no additional technical requirements or special AI markup required. It recommends ordinary crawlability, index eligibility, helpful people-first content, clear textual content, internal links, accurate structured data, and Search Console measurement. Google also says it does not use `llms.txt` for Google Search visibility and rejects mandatory chunking, exact long-tail rewrites, and inauthentic mentions as universal requirements.

This is not evidence about every other answer engine. Store provider scope beside every tactic.

## Strong claims to reject

Reject or narrow claims such as:

- “Do X and ChatGPT will cite you.”
- “FAQPage gives a fixed citation multiplier.”
- “Short paragraphs are required by all LLMs.”
- “`llms.txt` is a standard adopted by search engines.”
- “A successful crawl proves indexing or citation.”
- “More pages or more mentions create authority.”
- “A before/after citation change proves causation.”

A useful replacement states the target provider, the observed behavior, the evidence source, the date, and what remains unknown.

## Source review card

For every material claim, record:

```text
claim:
source_url:
source_title:
authority_tier: primary | standard | independent | vendor | discovery-only
provider_scope:
accessed_on:
exact_supporting_observation:
what_it_does_not_prove:
confidence: high | medium | low
refresh_trigger:
```

## Completion boundary

An AEO implementation is complete only when the requested changes exist, each changed boundary has been verified, and the report separates implemented, observed, inferred, and unresolved outcomes. A citation or traffic improvement is an outcome to measure later, not a completion prerequisite that can be fabricated.
