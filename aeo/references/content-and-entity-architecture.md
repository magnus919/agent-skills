# AEO content and entity architecture

## Page model

Treat a page as an answer asset with explicit contracts:

```text
entity/topic → audience → question cluster → canonical page → answer blocks
            → evidence → qualifiers → related links → owner → review trigger
```

A page should have one primary subject. A cluster may contain related questions, but do not create a page for every phrasing variant. Split when the audience, answer, evidence, freshness, or decision differs materially.

## Question cluster design

Collect questions from real user language, support tickets, sales calls, site search, forums, interviews, and observed answer prompts. Normalize them into intents:

- definition and disambiguation;
- “how does it work?” and procedure;
- comparison and alternatives;
- recommendation and fit;
- troubleshooting and failure recovery;
- current status, price, compatibility, policy, or availability.

For every question record:

- exact wording and normalized intent;
- named entities and aliases;
- expected answer type and confidence;
- canonical page/section;
- evidence and date boundary;
- caveat or non-answer condition;
- next useful internal link;
- owner and review trigger.

## Answer block pattern

```markdown
## [Reader's question]

[Direct answer in one or two sentences, including the scope or key qualification.]

[Evidence, mechanism, examples, trade-offs, and exceptions.]

[Primary source link at the claim it supports.]

[What this does not establish, if omission could mislead.]
```

The opening answer should stand alone when extracted, but it must not become falsely absolute. Put the entity, version, geography, date, and condition in the answer when they change its truth.

## Entity clarity

Use one canonical name consistently, then introduce legitimate aliases once. Disambiguate names that collide with other products, companies, people, places, or concepts. Link to authoritative identity pages where useful, but do not create `sameAs` links merely because a name looks similar.

Maintain a small entity record:

```text
canonical_name:
aliases:
entity_type:
identifier:
official_url:
related_entities:
not_this_entity:
last_verified:
owner:
```

Do not infer identity from a search snippet. Verify official URLs, identifiers, ownership, and version scope.

## Evidence placement

Place evidence beside the claim it supports. Prefer:

1. official specification, documentation, filing, policy, or source code;
2. independent reproduction or reputable reporting;
3. first-hand observation with method and date;
4. vendor claim, explicitly attributed;
5. inference, explicitly marked.

A bibliography cannot repair a source mismatch. A source can support a fact without supporting the causal explanation drawn from it.

## Comparison pages

Comparisons need a shared evaluation frame. Record artifact/version, scope, criteria, test conditions, missing capabilities, and who measured the result. Separate fit, task success, latency, cost, reliability, and qualitative judgment. If conditions are not comparable, present parallel evidence and a decision framework instead of a ranking.

## Anti-patterns

- exact-match question pages with no distinct answer;
- a glossary that repeats a definition without sources or disambiguation;
- “answer-first” copy that hides material qualifications below the fold;
- inconsistent names, versions, dates, and units across pages;
- entity links chosen for SEO rather than identity confidence;
- a generic FAQ bolted onto an article solely to justify FAQPage markup;
- citations that support a neighboring claim but not the sentence they follow.

## Review gate

A content architecture passes when a reviewer can answer: what question is this page for, what entity does it describe, where is the canonical answer, what source proves each material claim, what would make it stale, and where should a reader go next?
