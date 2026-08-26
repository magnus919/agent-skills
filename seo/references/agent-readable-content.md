# Agent-readable content

## `llms.txt`

`llms.txt` is a community proposal for a concise Markdown map of a site: identity, scope, and links to useful pages or Markdown documents. It is not a universal standard and is not required for Google Search or Google AI features; Google says it ignores the file for those systems. Use it only when the site wants to offer an optional curated context surface to consumers that choose to read it.

Keep it factual, short, maintained, and consistent with public pages. Do not put secrets, private URLs, unsupported claims, or a duplicate site map that nobody owns. A link in `llms.txt` does not bypass robots, authentication, indexing, or provider policy.

## Markdown delivery

A site may offer a Markdown representation or content negotiation, but this is an implementation choice, not a universal AEO requirement. Keep HTML and Markdown semantically equivalent, preserve links and dates, and test caching, canonical behavior, content type, and access controls. Do not assume an AI client sends `Accept: text/markdown` or that a provider will prefer it.

## Provider selection

Before implementing an agent-readable surface, answer:

- Which consumer is expected to use it?
- Is there current provider documentation or only a proposal?
- Who maintains parity with HTML?
- What content is intentionally excluded?
- How will stale links and claims be detected?
- What does success mean, and how will it be observed?

## Primary references

- [llms.txt proposal](https://llmstxt.org/)
- [llms.txt repository](https://github.com/AnswerDotAI/llms-txt)
- [Google AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
