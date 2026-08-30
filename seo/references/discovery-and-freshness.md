# AEO discovery and freshness

## Crawl is not citation

A page must be reachable and eligible before many systems can retrieve it, but a successful fetch is not proof of indexing, retrieval, citation, or traffic. Verify each boundary separately.

## Robots policy

Robots Exclusion Protocol rules are crawler-specific. Build a policy matrix before changing them:

- search crawler and search visibility;
- training crawler and training use;
- user-triggered fetch;
- ad, commercial, or partner crawler;
- private paths and sensitive data.

OpenAI explicitly separates OAI-SearchBot, GPTBot, and ChatGPT-User. Google uses Googlebot for Search controls and Google-Extended for certain other systems. Other providers have their own semantics. Never copy a universal allowlist from a blog post.

Check robots at the origin, CDN, and public URL. Record propagation expectations. A robots file is a policy control, not an AEO optimization switch.

## Sitemaps and internal links

Use crawlable internal links and an accurate XML sitemap. Include canonical URLs and truthful `lastmod` values. Bing documents sitemaps and IndexNow as discovery/freshness aids; they do not guarantee AI inclusion. Do not set `lastmod` to sitemap generation time when page content did not change.

## Freshness

Freshness means the answer is current for its question. A real update should identify what changed, update visible dates where appropriate, refresh structured data, repair links, and re-run high-risk observations. Date-only edits, “updated” badges without changed content, and stale citations damage trust.

## Access verification

```text
GET /robots.txt          → expected policy, status, content type
GET /sitemap.xml         → expected URL and true lastmod
GET /target              → status, canonical, robots meta, visible answer
GET /target as crawler   → only where permitted and provider semantics are known
```

Inspect edge caching and authentication. A browser page that renders content only after a client-side request needs a separate rendered verification.

## Primary references

- [RFC 9309 Robots Exclusion Protocol](https://datatracker.ietf.org/doc/html/rfc9309)
- [Google robots.txt interpretation](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)
- [Google AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)
- [OpenAI crawler documentation](https://platform.openai.com/docs/bots)
- [Bing sitemap and IndexNow guidance](https://blogs.bing.com/webmaster/July-2025/Keeping-Content-Discoverable-with-Sitemaps-in-AI-Powered-Search)
- [Sitemaps protocol](https://www.sitemaps.org/protocol.html)
