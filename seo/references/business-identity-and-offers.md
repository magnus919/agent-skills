# Business identity and offer discovery

Use when an answer system misdescribes a business, recommends it for the wrong service, or omits a commercially important offer. Accuracy comes before increasing mentions. This is an audit and planning workflow, not permission to edit profiles.

## 1. Separate three investigations

- **Identity:** “What does [business] do, and for whom?” Compare each material claim with verified current records. A correct answer can still cite outdated evidence.
- **Discovery:** Ask an unbranded customer question about hiring or solving a problem. The business name must not be supplied as a hint. Record eligible alternatives, not only the desired brand.
- **Recommendation fit:** Inspect why a provider recommends a business, including service, audience, geography, budget, availability, and exclusions. A brand mention does not establish a recommendation or qualified lead.

Use the same exact prompts across baseline and follow-up, retaining failures and no-answer runs. An isolated “number one” answer is a sample, not a stable rank. Pasting homepage text into a model can test comprehension of supplied text; it cannot test search retrieval or public discovery.

## 2. Build a verified identity record

Use `templates/business-identity-audit.md`. Verify canonical name, legitimate aliases, official domain, current services, customer fit, real operating geography, credentials, ownership and historical roles. Distinguish a former service, sold business or prior podcast from the current offer. Preserve truthful history with dates rather than rewriting it away.

Compare the homepage, About, services, contact information, relevant profiles and independent coverage. For each conflict record the exact claim, URL, date, source owner, severity, correction evidence and authority to change it. Prioritize harmful false facts over cosmetic wording differences. Consistent meaning is the goal; every biography need not use identical wording. Never infer ownership from a matching name or invent `sameAs` relationships.

A profile behind authentication, an unavailable page, or an inaccessible provider is **not assessed**, not “absent” or “AI cannot read it.” Check actual public availability and provider retrieval evidence separately. Do not scrape private groups or use client data in public prompts without authorization.

## 3. Make offers understandable

The first relevant section should explain who the business helps, what it actually delivers, the problem addressed and material fit limits. Verify statements with the business owner or authoritative records. Add useful process, scope, deliverables, current pricing context when appropriate, evidence, geography and next steps.

If several genuine services are scattered across the site, consider a services hub that links to distinct detailed offers. Reuse an existing navigation or overview page if it already solves the task. Do not create a compulsory page checklist or claim that engines require a page literally named “Services.” Homepage, About, reviews and service pages are information architecture choices, not universal ranking prerequisites.

Use actual buyer questions for FAQs. Keep them visible and accurate; adding FAQPage schema is not a prerequisite or citation multiplier. Link service claims to relevant proof and distinguish self-reported testimonials from independently established results.

## 4. Close the correction loop

For each approved correction record owner, scope, rollback, published URL and final public verification. Third-party biographies may require a separately approved correction request; an SEO audit does not authorize contacting the author. Preserve unresolved discrepancies and recheck with a bounded prompt sample after a reasonable discovery window. Do not promise recrawl time or propagate a correction to platforms the user did not authorize.

## Basis and limits

Google's [people-first content guidance](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) supports clear purpose, first-hand experience and trust. Its [AI guidance](https://developers.google.com/search/docs/appearance/ai-features) retains normal SEO foundations. Neither establishes a services-hub ranking factor. The practitioner examples in `references/geo-practitioner-evidence.md` motivate tests, not causal conclusions.
