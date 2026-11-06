---
name: go-to-market
description: >-
  Plan and evaluate go-to-market strategy using positioning, acquisition,
  growth economics, market-entry, competitive-response, and governed
  agent-assisted acquisition experiments. Use for ICP, customer-centered messaging,
  website narrative, channel,
  CAC/LTV, beachhead, or automated-GTM strategy decisions. Do not use for
  campaign execution, CRM mutations, legal interpretation, product strategy,
  or visual brand design.
license: MIT
metadata:
  tags: go-to-market, cmo, marketing, positioning, messaging, acquisition, brand-architecture,
    growth-modeling, competitive-response, plg, slg
  source_repo: https://github.com/magnus919/hermes-profiles
---

# Go-to-Market — CMO Methodology

CMO-level methodology for go-to-market strategy, positioning, acquisition, brand, and growth modeling. This skill provides the frameworks and reference material for a chief marketing officer profile.

## When to Load

| Trigger | What's Needed |
|---------|---------------|
| Define positioning and messaging | `references/positioning-messaging.md` — Dunford framework, message hierarchy |
| Clarify a website offer or customer narrative | Read `references/customer-centered-messaging.md` after positioning; fill `templates/customer-message-brief.md` |
| Build acquisition channel strategy | `references/acquisition-strategy.md` — channel mix, PLG/SLG, funnel metrics |
| Design brand architecture | `references/acquisition-strategy.md` — brand systems, visual identity, brand health |
| Model growth economics | `references/growth-modeling.md` — CAC/LTV, cohort analysis, market entry |
| Develop competitive response | `references/acquisition-strategy.md` — pricing wars, feature races, brand defense |
| Plan market entry | `references/growth-modeling.md` — beachhead, land-and-expand, channel economics |
| Design AI-assisted or automated acquisition experiments | `references/agent-assisted-acquisition-experiments.md` — experiment contract, readiness gate, earned authority, signal quality, stop rules |

## Loading Order

```text
skill_view('go-to-market')
# Then domain-specific references:
skill_view('go-to-market', file_path='references/positioning-messaging.md')
skill_view('go-to-market', file_path='references/acquisition-strategy.md')
skill_view('go-to-market', file_path='references/growth-modeling.md')
# For AI-assisted targeting, outreach, reply handling, or optimization:
skill_view('go-to-market', file_path='references/agent-assisted-acquisition-experiments.md')
```

## Reference Files

| Reference | Purpose |
|-----------|---------|
| `references/positioning-messaging.md` | April Dunford positioning, message hierarchy (elevator pitch → value prop → narrative), positioning diagnostic |
| `references/acquisition-strategy.md` | Channel taxonomy, PLG vs SLG playbooks, sales funnel ratios, competitive response playbook, brand architecture |
| `references/growth-modeling.md` | CAC/LTV deep dive, cohort analysis practical guide, NRR, market entry strategy (beachhead, land-and-expand) |
| `references/customer-centered-messaging.md` | Customer goal, obstacle, credible help, path, action, outcome, channel adaptation and testing |
| `references/final-copy-fact-check.md` | Facts/proposals/unknowns, final-expression audit and supported replacements |
| `references/message-drafting-and-revision.md` | Evidence-to-copy technique, candidate selection, diagnosis and revision |
| `references/messaging-worked-examples.md` | Complete fictional service and enterprise examples from inputs to channel handoff |
| `templates/customer-message-brief.md` | Evidence-linked message draft and strategy/voice/UX handoff |
| `references/decision-workflow.md` | Bounded launch/channel decisions, worked beachhead example, reusable memo, and owner routing matrix |
| `references/agent-assisted-acquisition-experiments.md` | Bounded experiment contract, readiness and responsibility gate, capability-specific earned authority, signal-quality ladder, decision loop, and stop conditions |


## Customer-Centered Messaging

For an unclear offer, website message, or customer narrative, establish audience,
alternatives, differentiation and evidence before drafting. Read
`references/customer-centered-messaging.md` and use
`templates/customer-message-brief.md`. Mark unknowns instead of inventing customer
feelings or results. Produce a plain offer, credible help, realistic path to value,
clear next action and claim/proof mapping. Keep approved voice intact; do not
require a fixed page order or step count.

When drafting alternatives or revising weak copy, read
`references/message-drafting-and-revision.md`. For complete evidence-to-copy
examples, read `references/messaging-worked-examples.md`. Record why the chosen
copy fits the audience, the tradeoff, and the actual revised passages.

Before handoff, read `references/final-copy-fact-check.md` and audit the actual
headline, proof, objections, action and adaptations. Before emitting final copy,
show a compact plan of the proposed NEW claims with their supplied support and
disposition, then render the accepted wording. A revision table about old copy
is not a substitute. Keep unknowns unknown; do not
turn plausible process choices into existing promises. Repair unsupported copy
while preserving the supplied offer and differentiator.

Hand the versioned message brief to `brand-designer` for strategy/voice documentation,
and action expectations to `product-design-and-ux` for page behavior. Drafting does
not authorize publishing or outreach. Complete when the brief, evidence gaps,
validation state and next owner are explicit; a structural check is not sales proof.

## Output Contract

The profile using this skill produces artifact pyramids. The response to any caller is the absolute path to `00-index.md`. See `artifact-pyramids` skill for the specification.

## When not to use

- **Sales execution and pipeline management** — this skill owns acquisition *strategy*, not running the funnel. CRM operations (contact lookup, deal pipeline views, confirmed stage changes) belong to [crm](../crm/SKILL.md).
- **Product strategy and roadmap** — product vision, PMF, and prioritization belong to `product-strategy` and `product-methodology`.
- **Visual brand identity design** — logo, palette, and brand systems belong to `brand-designer`.
- **Marketing campaign execution** — this skill defines the channel strategy and positioning; operating the channel tools is the corresponding tool skill's job.
- **Legal interpretation** — this skill records the jurisdiction, recipient type, and responsible owner as readiness inputs; `legal-strategy` or qualified counsel determines what law permits.

## Related Skills

- [artifact-pyramids](../artifact-pyramids/SKILL.md) — output contract
- [product-strategy](../product-strategy/SKILL.md) — CPO methodology (product vision, PMF, market sizing)
- [brand-designer](../brand-designer/SKILL.md) — visual brand identity design
- [seo](../seo/SKILL.md) — organic search, answer-engine, and generative-search audit and content strategy
- [crm](../crm/SKILL.md) — HubSpot CRM operations: contact lookup, deal pipeline views, and confirmed deal stage changes
- [ai-governance](../ai-governance/SKILL.md) — organizational AI risk, lifecycle gates, decision rights, and agentic controls
- [legal-strategy](../legal-strategy/SKILL.md) — legal analysis when outreach or data-use rules require interpretation
