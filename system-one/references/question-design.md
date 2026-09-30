# Designing System One questions

Use this reference when writing or reviewing typed question instructions,
criteria, candidate sets, or branch-specific questions. These patterns are
informed by TypeSafe's [System One skill](https://github.com/typesafe-ai/skills/blob/65a39f393687675ce170e6094757de20370365b9/skills/typesafe-ai/SKILL.md)
at commit [`65a39f3`](https://github.com/typesafe-ai/skills/tree/65a39f393687675ce170e6094757de20370365b9)
and its linked live documentation. They are design guidance, not evidence of
quality on your workload; preserve this skill's evaluation and authority gates.
For existing evaluation challenge examples and rubric scope, see
`references/question-design-eval-review.md`.

## Make each question self-contained

The question ID connects a returned answer to application code. Do not rely on
that ID to explain the task: TypeSafe's Jev guidance says question IDs are not
sent to the model. Other providers may have different contracts. Put the
complete judgment in the trusted `instructions`, provide the relevant evidence
in `state`, and define answer meanings in `criteria`.
Question IDs, instruction text, criteria, and thresholds belong in versioned
application configuration; never let untrusted state rewrite them.

Ask one coherent judgment per question. Split dimensions when each answer is
independently useful; retain a contextual question when splitting would lose
the relationship that determines the answer. A Choice question selects one
defined option, a Noul answers one proposition, and a Score places the case on
an ordered, concrete scale. Read `references/concepts-and-patterns.md` for
primitive semantics and composition.

## Select from candidates for exact extraction

When the desired output must come from supplied text, let code enumerate the
candidate values or source spans, ask the model which candidate fits, then have
code copy or normalize the selected source. Do not ask the model to recreate
an exact identifier, URL, date, or quotation from memory.

For example, code can parse a message and provide:

```json
{
  "message": "Please send the refund to acct-4821, not acct-9910.",
  "account_candidates": ["acct-4821", "acct-9910"]
}
```

Then ask: “Which account candidate does the customer identify as the refund
destination? Select `none` if the message does not identify one.” Define the
Choice options as the candidate IDs plus `none`; have code map a selected ID
back to its exact source text. This avoids extraction drift and lets the
application normalize the selected value deterministically. Selection
identifies the requested destination value; it does not authorize issuing a
refund or performing any other external action.

Measure candidate coverage separately from selection accuracy. If the desired
value is absent from the candidates, the model cannot select it; report that as
a candidate-generation miss, not a selection error. Include an explicit no
match option when an empty match is possible, and consider a separate
presence question when knowing whether a value exists is independently useful.
If candidates are too numerous, shortlist them in code and measure shortlist
recall before evaluating model selection. Probabilities are conditional on the
provided candidate set.

## Read uncertainty in context

For TypeSafe Jev, a Noul returns the probability of “yes” and has no separate
confidence value; see the [primitive reference](https://docs.typesafe.ai/primitives.md).
A probability near 0.5 means uncertainty about yes versus no. It does not
mean a medium amount of the property. Choice or Score confidence reflects
how concentrated the alternatives are, not whether the whole workflow is
correct. When several alternatives are acceptable for a harmless preference,
probability may spread among them; low concentration alone need not make the
choice unusable. Set review or escalation behavior from held-out results and
the consequences of mistakes.

## State speculative premises explicitly

Independent questions can be sent together to reduce round trips, but each
question sees the supplied state, not the answers to sibling questions. State
the premise in each speculative question and consume its result only if code
selects the matching branch. For example, “If the selected route is billing,
which billing issue best fits?” remains conditional; code ignores its answer
when another route was selected. Do not let uncertainty in an unused branch
block the selected route. If an earlier answer must construct evidence or
options for a later question, make a second request.

## Keep preferences distinct from vetoes

Use weighted scores when preferences can compensate for one another. Keep
serious violations as separate conditions when any one violation must veto an
action; an average can hide a critical failure. Deterministic authorization,
hard limits, and approval remain in code or human control. Preserve component
judgments so policy outcomes can be inspected and replayed.

## Further reading

TypeSafe's [value extraction cookbook](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook.md),
[confidence guide](https://docs.typesafe.ai/confidence.md),
[fan-out pattern](https://docs.typesafe.ai/patterns/fan-out.md), and
[composite scoring pattern](https://docs.typesafe.ai/patterns/composite-scoring.md)
are useful starting points. Follow the live documentation index and verify
current provider semantics before relying on version-specific behavior.
