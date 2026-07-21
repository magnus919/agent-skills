# Baseline Protocol

A result is only meaningful against a **fair** baseline. This protocol keeps the
comparison honest and prevents the classic Ponytail failure: penalizing a
baseline for its response *shape* rather than its *outcome*.

## The baseline must be context-equivalent

The baseline arm sees the **same**:
- repository context (`context` in the fixture),
- harness constraints (tools, authority class, budget),
- task prompt.

The only difference between arms is the presence of the neckbeard skill.

## Do not penalize response shape

A baseline that offers explanations, examples, or multiple options is **not**
wrong for doing so — unless that behavior is itself the task failure (e.g. the
task is "give one decisive answer"). Score outcomes, not verbosity.

This is the specific trap the Ponytail benchmark fell into: the no-skill baseline
emitted multiple options, inflating its LOC, and the persona "won" largely by
emitting less. LOC is diagnostic metadata here, never a scoring dimension.

## Arms to compare

At minimum:
1. **neckbeard** — the bundle loaded.
2. **context-equivalent baseline** — same harness and context, no bundle.

Optionally add a **prompt-only** arm (e.g. "Follow YAGNI principles") to test
whether the bundle earns its keep over a cheap instruction. If a few plain words
match the bundle, that is a real finding — report it.

## Multi-run, multi-model

- Run each arm multiple times per fixture; report variance / confidence
  intervals, not a single point estimate.
- Run across more than one model when claiming generality. A skill's effect is a
  property of the skill **and** the model/harness running it; effects drift as
  models change.
- Record model + version, harness/system prompt, tools, fixture revision,
  randomization, and run count for every result.

## Regression gate

A change to the bundle cannot claim improvement without running the public suite
and reporting holdout results through the maintainers' controlled workflow. A
single favorable run is not a claim.
