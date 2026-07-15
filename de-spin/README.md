# De-Spin

Turn persuasive claims into inspectable questions instead of being won over by confidence, repetition, prestige, or a carefully chosen statistic.

## Why Install This Skill

A message can be technically true and still leave you with the wrong conclusion. A headline may use a real number without its denominator. A testimonial may be genuine but unrepresentative. A dozen articles may repeat one original, unverified claim. This skill gives an agent a repeatable way to separate what is supported from what is implied, omitted, or unknown, then check material factual claims directly against the appropriate source of truth.

It does not try to read a speaker’s body language or guess their intent. It helps a person make a better decision by tracing claims to evidence and identifying the missing context.

The result is not a reflexive “lie” label. It explains what is true, what is false, what is genuinely complicated and why, plus the smallest independent check that could change the decision.

## What You Get

| Path | What it provides |
|---|---|
| `SKILL.md` | Claim-audit workflow, verdict definitions, and escalation rules. |
| `references/claim-audit.md` | Tests for numbers, comparisons, testimonials, causal stories, urgency, and high-stakes claims. |
| `references/empirical-foundations.md` | Research and regulatory foundations, source links, and limits of the method. |
| `assets/claim-audit.md` | Reusable report template for what is true, false, and complicated. |
| `evals/evals.json` | Representative quality checks for marketing, viral rumors, and causal claims. |

## Quick Start

Install or expose this directory using your agent’s standard Agent Skills loading mechanism, then ask your agent to audit a specific message:

```text
De-spin this claim: “Our product cuts costs by up to 70%, trusted by thousands.”
Tell me what is true, false, misleading, and complicated.
```

The response should distinguish literal wording from its likely implication, show the evidence needed to resolve it, and recommend the smallest safe next check.

## Triggers

- “Is this spin?” “De-spin this.” “What is this leaving out?”
- Audit a sales pitch, advertisement, policy claim, press release, viral post, executive memo, or AI-generated argument.
- Separate a claim into what is true, false, misleading, unknown, or complicated.
- Verify whether multiple sources are independent corroboration or repeated reporting of one origin.
- Analyze urgency, authority, social proof, selective statistics, testimonials, or qualified language such as “up to” and “starting at.”

## Requirements

No runtime dependency. For claims that matter, the agent needs access to independent sources and should retain source URLs and access dates. High-stakes decisions may require qualified human review.
