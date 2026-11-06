# Structured data implementation

`references/structured-data.md` owns type selection, evidence parity and provider feature eligibility. This file owns implementation examples only. Schema.org vocabulary validity, JSON validity, provider eligibility and actual display are different checks. Markup never guarantees rankings or AI citations.

## Minimal JSON-LD example

Use real, verified values matching the rendered page; this is illustrative data, not a ready-to-publish business identity:

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Example article",
  "datePublished": "2026-05-01",
  "author": {"@type": "Person", "name": "Example Author"},
  "publisher": {"@type": "Organization", "name": "Example Publisher"},
  "mainEntityOfPage": "https://example.com/article"
}
```

Select the smallest justified type set. Required fields differ by provider feature; consult current documentation. Do not describe FAQPage or HowTo vocabulary as an active Google rich-result opportunity. Do not add review aggregates, an office or a LocalBusiness identity that the real operator cannot substantiate. BreadcrumbList describes the actual navigation path; provider/device display support must be checked.

## CMS and template delivery

Inspect existing rendered output first to avoid conflicting blocks. A CMS/theme may already emit author, organization, article or breadcrumb data; merge or configure it through its supported mechanism rather than injecting duplicates. Ghost defaults and theme behavior vary: use `ghost` for operations and `references/ghost-metadata.md` for the current integration pattern. Hugo templates should use properly escaped JSON serialization rather than unsafe string interpolation; route implementation to `hugo-theme`.

Confirm target, scope and rollback before editing templates, injection, plugins or public content. Preview first and inspect the delivered page, not only source configuration. Keep credentials and private evidence out of markup.

## Validation

1. Parse the actual delivered JSON-LD.
2. Check vocabulary/type with [Schema.org Validator](https://validator.schema.org/).
3. Compare every material claim with visible content and verified source data.
4. Check canonical URLs, author identity, publication/modification semantics and duplicates.
5. Use [Google Rich Results Test](https://search.google.com/test/rich-results) only for supported Google features; an unsupported type is not automatically invalid Schema.org.
6. Inspect rendered desktop/mobile content and document provider/date-specific eligibility and remaining limits.

Never report generic “schema passed” when only syntax was checked. Follow `references/structured-data.md` for the full parity checklist.
