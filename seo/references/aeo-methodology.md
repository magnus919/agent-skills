# Search, Answer, and Generative Engine Optimization

## Working definition

SEO is the umbrella discipline for improving a site's eligibility, discovery, interpretation, and useful visibility in search systems. AEO and GEO are overlapping labels for work on answer-producing surfaces. Use the stakeholder's label, but define the actual provider, mechanism, and measurable outcome.

- **AEO** commonly emphasizes direct answers, featured snippets, knowledge surfaces, and answer-engine inclusion.
- **GEO** commonly emphasizes generated answers, source selection, citation, and whether source evidence is reflected in the answer. The term was formalized as Generative Engine Optimization in Aggarwal et al.'s KDD 2024 paper.
- **LLMO** and **AI-search optimization** are overlapping industry labels, not standardized disciplines.

None of these labels identifies a universal ranking algorithm or guarantees inclusion, citation, recommendation, traffic, or conversion.

## Generative search model

Many current systems combine search or retrieval with generation, but their indexes, ranking systems, crawlers, models, interfaces, and policies differ. A useful working decomposition is:

1. query interpretation or fan-out;
2. candidate retrieval;
3. source selection or reranking;
4. answer synthesis;
5. citation, link, or attribution rendering;
6. user click, action, or conversion.

This model helps locate evidence. It is not a provider specification. A publisher can improve the quality and accessibility of its content and observe outcomes, but cannot directly control a provider's retrieval or generation decision.

## What the strongest evidence supports

### Academic evidence

Aggarwal et al. (KDD 2024, arXiv:2311.09735) introduced GEO and evaluated content transformations in a controlled benchmark of generative engines. The paper reports that some transformations, including adding citations, quotations, and statistics, improved its benchmark visibility metrics, while effects varied by domain and method. Its metrics account for the amount and position of answer text associated with a citation, rather than treating every citation as an equivalent blue-link impression. This is evidence for testable hypotheses in that benchmark, not a cross-provider ranking recipe.

Liu et al. (2023, arXiv:2304.09848) found substantial citation-support and sentence-support failures in generative search answers. Citation presence therefore cannot substitute for checking whether the cited source supports the adjacent claim.

Later papers and surveys may provide useful hypotheses, but check version, venue, dataset, engine, prompt set, and reproducibility before treating a reported lift as portable.

### First-party guidance

Google says its AI Overviews and AI Mode use core Search systems and that ordinary SEO fundamentals remain relevant. It states that there are no additional technical requirements or special AI markup, and that Google Search does not use `llms.txt` for visibility. It recommends useful people-first content, clear technical structure, textual content, relevant media, internal links, accurate structured data, and truthful business or product data. Google also warns against scaled, inauthentic, or query-variant content created to manipulate AI responses.

Bing's AI Performance report exposes citations, cited pages, grounding queries, and trends across supported Microsoft AI experiences. Bing explicitly limits those metrics: they show citation activity, not ranking, authority, page importance, or placement.

OpenAI documents separate crawler controls for OAI-SearchBot, GPTBot, and ChatGPT-User. Allowing a search crawler can make a page eligible for consideration, but OpenAI does not guarantee placement. Anthropic and Perplexity publish their own crawler and robots guidance. Never transfer one provider's crawler semantics to another.

## Implementation principles

- Answer the user's question near the relevant heading, then provide evidence, scope, caveats, and useful detail. This is a usability and extraction hypothesis, not a universal formatting rule.
- Use clear headings, descriptive titles, coherent entity names, accessible text, links, tables, and lists where they help people. Do not reduce prose to fragments or duplicate pages for every query variant.
- Support material claims with primary sources, dates, methods, first-hand experience, or clearly labeled analysis. Preserve uncertainty.
- Keep visible content, metadata, JSON-LD, feeds, Markdown representations, and summaries semantically consistent. Structured data describes visible facts; it does not create them.
- Treat robots directives as access and preview policy controls. Separate search access, training use, user-triggered fetching, and commercial permissions where the provider supports those distinctions.
- Use sitemaps, truthful `lastmod`, IndexNow, and recrawl requests as discovery or freshness mechanisms where supported. None guarantees retrieval or citation.
- Treat `llms.txt` as an optional community proposal. It may be useful to a consumer that chooses to read it, but it is not a W3C, IETF, or universal search requirement, and Google says it ignores it for Search visibility.

## Outcome taxonomy

Track these separately:

| Outcome | Meaning | Evidence |
|---|---|---|
| Crawl access | A named crawler fetched a resource | Logs, headers, provider documentation |
| Index eligibility | A resource can enter a provider index | Provider diagnostics; a 200 is insufficient |
| Retrieval | A resource was selected for a query or grounding step | Provider-native data or reproducible observation |
| Mention | The entity appears in generated text | Exact answer snapshot |
| Citation | The answer links or names the source | Exact answer and URL |
| Citation correctness | The source supports the adjacent claim | Source-to-claim comparison |
| Share of voice | Visibility relative to a defined comparator set | Frozen prompts and scoring rules |
| Referral | A user visits after an answer interaction | Analytics with attribution limits |
| Conversion | A defined downstream action occurs | Instrumented funnel and causal design |

## Measurement protocol

Freeze a prompt matrix with stable IDs, exact text, intent, target entity, expected source boundary, and version. Include definition, comparison, procedure, troubleshooting, current-status, disambiguation, and negative-control prompts.

For each observation preserve the date, provider, surface, model/version if known, account/location state, prompt ID, exact answer, cited URLs, mention and citation status, relevance, support, completeness, misleading claims, and provider changes. Normalize URLs for analysis without discarding originals.

Define a rubric before looking at results. A practical record can score target mention (0/1), target citation (0/1), citation relevance (0-2), citation support (0-2), answer completeness (0-2), and harmful or misleading claims (0/1). Keep human scoring, automated extraction, and provider-native dashboards distinct.

For experiments record: `hypothesis -> change -> expected mechanism -> prompt set -> window -> metric -> result -> confounders -> decision`. A before/after change supports an observation under stated conditions, not causal attribution, unless the design supports it. Repeated model outputs are not automatically independent observations.

## Claims to reject or narrow

Do not publish or encode as rules:

- fixed citation or conversion multipliers from an opaque vendor study;
- “FAQPage guarantees AI citations” or any universal schema multiplier;
- “short paragraphs,” exact-match questions, keyword variants, or chunking are required by all engines;
- allowing every AI crawler guarantees inclusion or citation;
- `llms.txt` is a universal standard or a Google ranking signal;
- a citation count proves authority, ranking, correctness, traffic, or revenue;
- a passing structural audit proves retrieval or citation.

Record authority tier, provider scope, access date, exact supporting observation, non-proof, confidence, and refresh trigger for every material claim.

## Sources

- Google, [Optimizing your website for generative AI features on Google Search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), accessed 2026-08-26.
- Google, [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features), accessed 2026-08-26.
- Microsoft Bing, [Introducing AI Performance in Bing Webmaster Tools](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview), accessed 2026-08-26.
- OpenAI, [Overview of OpenAI Crawlers](https://developers.openai.com/api/docs/bots), accessed 2026-08-26.
- OpenAI, [ChatGPT search](https://help.openai.com/en/articles/9237897), accessed 2026-08-26.
- Perplexity, [Perplexity Crawlers](https://docs.perplexity.ai/docs/resources/perplexity-crawlers), accessed 2026-08-26.
- Anthropic, [Does Anthropic crawl data from the web?](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler), accessed 2026-08-26.
- Aggarwal et al., [GEO: Generative Engine Optimization](https://arxiv.org/html/2311.09735v3), KDD 2024, accessed 2026-08-26.
- Liu et al., [Evaluating Verifiability in Generative Search Engines](https://arxiv.org/abs/2304.09848), 2023, accessed 2026-08-26.
- [llms.txt proposal](https://llmstxt.org/), accessed 2026-08-26.
