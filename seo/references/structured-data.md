# AEO structured data

## Principle

Schema.org describes content; it does not guarantee inclusion, ranking, or citation. Add JSON-LD only when the page visibly and materially satisfies the chosen type. Visible content is the source of truth. Provider rich-result support changes over time, so do not treat older FAQ-focused guidance or a schema type's existence as evidence of current Google eligibility.

## Type selection

- **Article/BlogPosting/TechArticle:** an authored article; include accurate headline, author, dates, publisher, and about fields.
- **FAQPage:** a page presenting real frequently asked questions and answers. Do not use it for implied answers or every heading.
- **HowTo:** a procedure with ordered steps, tools/supplies, and conditions. Do not use it for explanatory prose.
- **QAPage:** a user question with user-submitted answers, not a publisher FAQ.
- **Organization/Person:** identity and authorship only when the page and site can substantiate it.
- **BreadcrumbList:** navigational hierarchy, not a substitute for internal links.

Use the Schema.org type definition and the target provider's feature documentation. Schema.org's vocabulary is broader than any one search feature's eligibility rules.

## Parity checklist

For each JSON-LD block:

- every material name, answer, step, date, author, URL, and relationship appears visibly or is a faithful machine-readable equivalent;
- FAQ answers are complete enough to stand alone and match their visible wording;
- HowTo steps are ordered, actionable, and visible;
- dates describe publication or real modification, not deployment time;
- URLs are canonical and fetchable;
- no hidden or contradictory markup is added to influence systems;
- the JSON parses and the rendered page remains correct without JavaScript when feasible.

## Validation pattern

1. Parse JSON-LD as JSON.
2. Validate required shape for the selected type.
3. Extract visible headings, questions, answers, steps, names, and dates.
4. Compare material fields, allowing only documented normalization such as whitespace.
5. Run the provider's own rich-result or structured-data test where applicable.
6. Inspect the rendered page and record what the validator does not prove.

A valid JSON document proves syntax. It does not prove truth, visible parity, eligibility, retrieval, or citation.

## Common mistakes

- FAQ schema on a page without visible Q&A;
- HowTo schema on a conceptual article;
- multiple conflicting author or date values;
- `sameAs` links chosen from ambiguous search results;
- using schema to encode a vendor claim as an objective fact;
- assuming rich-result eligibility is an AEO performance metric;
- adding every plausible schema type instead of the smallest accurate set.

## Primary references

- [Schema.org FAQPage](https://schema.org/FAQPage)
- [Schema.org HowTo](https://schema.org/HowTo)
- [Schema.org FAQ](https://schema.org/docs/faq.html)
- [Google structured data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
