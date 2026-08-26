# AEO platform guidance

## Google Search AI features

Google Search Central says AI Overviews and AI Mode use existing Search systems. Pages need to be indexed and snippet-eligible; there are no additional technical requirements or special AI markup. Continue people-first content, crawlable internal links, textual content, accurate structured data, and Search Console measurement. Google explicitly says `llms.txt`, mandatory chunking, exact long-tail rewrites, and inauthentic mentions are not required for Google Search AI features.

## Bing and Copilot

Bing documents AI Performance in Webmaster Tools: total citations, average cited pages, grounding queries, page-level activity, and trends. These are visibility observations, not ranking, authority, placement, or correctness measures. Bing also documents sitemaps, truthful `lastmod`, and IndexNow as discovery/freshness support. Use provider-native definitions and do not generalize dashboard data to all engines.

## OpenAI

OpenAI documents separate robots controls for OAI-SearchBot (search), GPTBot (training), and ChatGPT-User (user-triggered actions). Allowing one does not imply allowing the others. Treat published bot names, IP ranges, and propagation timing as version-sensitive.

## Perplexity and other answer providers

Use the provider's current crawler and publisher documentation when available. Do not infer search, training, user-fetch, or citation semantics from a user-agent string alone. If documentation is inaccessible or ambiguous, record the gap and avoid a policy change based on guesswork.

## Provider comparison table

| Question | Google | Bing | OpenAI | Other providers |
|---|---|---|---|---|
| What enables search visibility? | Search indexing and snippet eligibility | Bing indexing/crawl | OAI-SearchBot policy plus provider systems | Provider-specific |
| Is special AEO markup required? | No current special requirement | No universal requirement established | No universal requirement established | Unknown unless documented |
| Is `llms.txt` authoritative? | Google says it is ignored for Search | No universal requirement | Provider-specific/undocumented unless stated | Proposal-dependent |
| What can be measured? | Search Console AI reporting where available | AI Performance | Usually external observation unless provider publishes data | Provider-native or manual |

## Refresh triggers

Re-read official pages when a provider changes crawler names, AI surfaces, reporting definitions, robots controls, indexing guidance, or content policies. Record access date and exact scope in `references/source-index.md`.
