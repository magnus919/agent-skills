# SEO, AEO, and GEO source index

This source map supports the skill. Re-check provider documentation before relying on version-sensitive crawler names, dashboards, policies, or controls. Initial research pass: 2026-08-26.

## Primary and standards sources

- [Aggarwal et al.: GEO: Generative Engine Optimization](https://arxiv.org/html/2311.09735v3) — KDD 2024 controlled benchmark and generative visibility metrics.
- [Liu et al.: Evaluating Verifiability in Generative Search Engines](https://arxiv.org/abs/2304.09848) — citation support and sentence support evaluation.
- [Google: AI features and your website](https://developers.google.com/search/docs/appearance/ai-features) — existing SEO fundamentals, no additional technical requirements or special AI markup, query fan-out, preview controls, and Search Console measurement.
- [Google: optimizing for generative AI features](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) — RAG, query fan-out, people-first content, technical structure, and mythbusting for `llms.txt`, chunking, exact rewrites, and inauthentic mentions.
- [OpenAI: crawler overview](https://platform.openai.com/docs/bots) — OAI-SearchBot for search, GPTBot for training, ChatGPT-User for user-triggered access, independent robots controls, and propagation caveats.
- [Bing: AI Performance](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview) — citation counts, cited pages, grounding queries, page activity, trends, and metric limits.
- [Bing: sitemaps in AI search](https://blogs.bing.com/webmaster/July-2025/Keeping-Content-Discoverable-with-Sitemaps-in-AI-Powered-Search) — sitemap coverage, truthful `lastmod`, and IndexNow as discovery/freshness aids without an inclusion guarantee.
- [Perplexity: crawlers](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) — provider crawler and robots guidance; verify directly when implementation depends on details.
- [Schema.org FAQPage](https://schema.org/FAQPage), [HowTo](https://schema.org/HowTo), and [FAQ](https://schema.org/docs/faq.html) — vocabulary semantics, not a citation guarantee.
- [IETF RFC 9309](https://datatracker.ietf.org/doc/html/rfc9309) — Robots Exclusion Protocol.
- [Sitemaps protocol](https://www.sitemaps.org/protocol.html) — XML sitemap format.
- [llms.txt proposal](https://llmstxt.org/) and [repository](https://github.com/AnswerDotAI/llms-txt) — optional community proposal; Google says it does not use it for Google Search visibility.

## Secondary methodology sources

- [Graphite / Ethan Smith](https://graphite.io/five-percent/aeo-is-the-new-seo) — hypothesis generation and test/reproduce framing.
- [AirOps AEO guide](https://www.airops.com/blog/aeo-answer-engine-optimization) — practitioner tactics and vendor-reported study claims.
- [Frase AEO guide](https://www.frase.io/blog/what-is-answer-engine-optimization-the-complete-guide-to-getting-cited-by-ai) — practical prompt baselines and citation tracking ideas.
- [CXL AEO guide](https://cxl.com/blog/answer-engine-optimization-aeo-the-comprehensive-guide/) — secondary taxonomy and implementation discussion.

## Rejected or bounded claims

- There is one universal AEO algorithm.
- FAQPage has a fixed citation multiplier.
- `llms.txt` improves Google AI visibility.
- Allowing every crawler guarantees citations.
- More short pages, exact-match questions, or web mentions always win.
- Citation count equals authority, ranking, correctness, traffic, or conversions.

These are unsupported, provider-specific, vendor-reported without portable evidence, or contradicted by current primary guidance.

## Local/national portfolio update (reviewed 2026-11-06)

- [Google spam policies](https://developers.google.com/search/docs/essentials/spam-policies): doorway, scaled content, links and site-reputation boundaries; recheck current regional enforcement.
- [Google Business Profile representation](https://support.google.com/business/answer/3038177), [eligibility](https://support.google.com/business/answer/13763036?hl=en), [local ranking](https://support.google.com/business/answer/7091): profile rules do not equate to organic-site geography.
- [Google ranking systems](https://developers.google.com/search/docs/appearance/ranking-systems-guide): exact-match domains are not a guarantee.
- [Google updates](https://developers.google.com/search/updates), [HowTo/FAQ deprecation](https://developers.google.com/search/blog/2023/08/howto-faq-changes), [featured snippets](https://developers.google.com/search/docs/appearance/featured-snippets): time-sensitive feature support; no fixed snippet word-count rule.
- [FTC review rule Q&A](https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers): false testimonials and independence claims, not a full legal opinion.
- `references/microsite-evidence.md` records public practitioner transcripts, promotional incentives and inaccessible archive limits. They inform workflow hypotheses, not a demonstrated profitable portfolio.

Refresh on provider policy/feature changes, new geography or business model, stale claims, complaints or launch decisions. Preserve source/date/provider scope instead of retroactively asserting universal rules.
