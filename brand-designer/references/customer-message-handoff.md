# Customer message handoff

Read when an approved customer message must become strategy, voice or application
guidelines. `go-to-market` owns positioning and narrative development; its
[messaging method](../../go-to-market/references/customer-centered-messaging.md) and
[message brief](../../go-to-market/templates/customer-message-brief.md) define that workflow. Load that skill if the
audience, alternatives or value proposition are unresolved. Do not duplicate the
method here or infer positioning from a preferred tone or image.

## Intake and translation

1. Record the message brief's location, revision, owner, approval scope and date.
   Distinguish approval, source support, comprehension testing and commercial
   outcomes. A draft may be documented as a draft; it cannot silently become policy.
2. Carry audience, goal, current alternative, meaningful difference, offer limits
   and claim/proof references into `templates/strategy.md`. Separate supplied facts,
   observed evidence, hypotheses and unknowns. Do not invent feelings or customer
   quotes to make the document persuasive.
3. In `templates/voice.md`, express approved claims in the existing voice. Preserve
   their scope, qualifiers and action expectations. Clarity does not require every
   brand to sound friendly, playful or identical. Record an on-voice example and a
   misleading near miss with the reason it changes the meaning.
4. Use benefit imagery only where it clarifies the offer. A real demonstration,
   process diagram or product view may communicate better than a lifestyle scene.
   Generated scenes are illustrations, not customer evidence. Preserve supplied
   asset constraints and approved visual decisions.
5. Adapt length, order and vocabulary for the channel and audience. Keep the core
   promise and its limits consistent, without forcing identical wording. For
   separate users, buyers and approvers, retain role-specific messages under the
   same defensible offer. Product errors and support instructions should help
   complete the task; do not inject a sales pitch into them.
6. Review strategy, voice, brand card and proposed application examples together.
   Check that a short headline or image caption has not turned a qualified claim
   into a guarantee. Send action expectations, required information, resulting
   state and unknowns to `product-design-and-ux`; implementation belongs to
   `frontend-engineering`. Do not claim a working or accessible page from a brand
   document alone.

For concrete channel and audience expressions, read
`references/message-adaptation-examples.md`. Use its semantic-anchor review to
check actual copy rather than only naming voice attributes.

## Conflict handling

| Conflict | Action |
|---|---|
| Approved slogan obscures the offer | Keep its approval record; propose a plain supporting line and request an explicit revision decision |
| Leadership requests an unsupported result | Flag the proof gap; draft a supported deliverable statement rather than publish the claim |
| Brand voice changes the action promise | Preserve what actually happens; change tone without changing the service terms |
| Different audiences need incompatible promises | Return segmentation/positioning to `go-to-market`; do not merge into a vague universal claim |
| New evidence contradicts an approved pillar | Mark affected examples for review and return the decision to the message owner |

## Worked translation — fictional supplied brief

Input: forecasting service for independent shops; weekly forecast, accounting-data
connection and assumption review required; no proven savings. Established voice:
precise, calm, practical.

| Artifact | Candidate | Review |
|---|---|---|
| Strategy | Weekly cash-flow forecasts for independent shops | Retains offer and audience |
| Voice example | Plan next week's payments with a weekly cash-flow forecast | Expresses intended use; no guaranteed result |
| Action | Request a walkthrough | Follow-up terms remain unknown until supplied |
| Misleading near miss | Never run short of cash again | Unsupported guarantee; reject |
| Imagery direction | Annotated sample forecast, clearly labeled illustrative | Helps explain the deliverable; not proof of client results |

## Exit and provenance

Complete when versioned strategy/voice artifacts preserve the message, claim
limits, approval state and unresolved decisions, with a named next owner. CLI
validation checks document structure; editorial review checks message fidelity;
user research and experiments assess comprehension and outcomes separately.

This handoff is an authored catalog integration recommendation. Source attribution
and evidence limits for the underlying messaging synthesis are in the repository
[research provenance](../../docs/research/customer-centered-messaging/sources.md).
