# Semantic lint rule design

Complete one copy per semantic rule. Keep exact syntax, schema, policy, and
format checks deterministic; this template is for a bounded judgment that needs
code context. Start with advisory reporting. A missing or incomplete reading is
unknown/review, never an implicit pass.

## Claim and scope

- Rule name and revision:
- Owner who can interpret the code requirement:
- User or maintainer harm the rule is intended to catch:
- Exact invariant in one sentence:
- Target selector (`where`):
- Unit (`file`, `method`, `test`, or equivalent):
- Included paths/units and explicit exclusions:
- Required context (`sees`, caller/callee, tests, configuration, or other):
- Known parser, graph, chunk, or context limits:

## Evidence and decision contract

| Outcome | Example from the actual rule scope | Evidence available to the model/reviewer | Correct treatment |
|---|---|---|---|
| Satisfying | | | `met` only when the shown evidence supports the invariant |
| Contradictory near miss | | | `not met`; lexical overlap must not override the counterexample |
| Missing or conflicting evidence | | | `not shown` / unknown / human review; request the missing source or test |

- Primitive and answer meanings (Noul / Choice / Score):
- Evidence span or source/test artifact required for a finding:
- Exact boundary between false and unjudgeable:
- Behavior for missing, partial, stale, contradictory, or unreadable context:
- Human/domain reviewer and disagreement disposition:
- Why the claim fits the selected primitive and unit:

## Candidate rule

```yaml
- name: <stable-rule-name>
  where: <narrow glob or graph selector>
  each: <method|test|file>
  sees: <needed context, when applicable>
  ensure: >-
    <one observable semantic invariant with a concrete failure condition>
  # Include `min` only after a predeclared calibration study supports it.
  # Keep `gate: false` during the advisory evaluation period.
  gate: false
```

Use the narrowest justified scope and ask one independently reviewable claim
per rule. A codebase-level `ensure_present` search can establish presence when
it finds an evidenced witness. A no-witness result for `ensure_present`, or a
passing `ensure_absent` result, supports absence only after a complete search
of the declared scope; capped, partial, or failed searches remain unknown. If
the target contract needs a real unknown lane, encode and validate it explicitly
or keep uncertain outputs in a separate review path; do not assume a binary
rule response has an abstention state.

## Operating policy

- Policy owner and action allowed by this result:
- Explicit advisory / review / block mapping (initially advisory):
- Evidence required before any threshold or gate change:
- False-pass, false-block, not-shown, malformed, and failed-request handling:
- Maximum repair attempts and stop/escalation condition:
- Deterministic tests and regression checks that remain required:
- Rule, question text, provider/model, adapter, and policy revision record:
