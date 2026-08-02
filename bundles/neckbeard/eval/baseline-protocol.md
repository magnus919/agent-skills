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

## Trajectory comparisons

When comparing trajectory runs (multi-phase journeys), the same
context-equivalence and shape-neutrality rules apply, extended to the
trajectory structure:

- **Same journey context.** Both arms receive the identical change request
  (`prompt`), repository context, and harness constraints. The fixture's
  `path`, `phases`, and `gates` describe the *expected* structure — they do
  not prescribe how the agent reaches it.
- **Score trajectory outcomes, not phase count.** A baseline that traverses
  fewer phases but reaches the same terminal state with the same verification
  evidence is not inferior for having a shorter journey. Conversely, a run
  that visits all nine phases but leaves the terminal state unresolved has not
  "won" by coverage. Score what the trajectory *achieved* (correct outcome,
  gate evidence, head-SHA binding, skip transparency), not how many phases it
  enumerated.
- **Shape-neutrality extends to trajectory arms.** Do not penalize a baseline
  for recording gates in a different format, naming phases differently, or
  structuring its delivery packet differently — as long as the observable
  outcomes (verdicts, evidence, terminal state, skip reasons) are present and
  correct. The neckbeard arm is expected to use the canonical journey labels;
  the baseline arm is not.
- **Skip transparency is scored, not skip count.** A trajectory that skips
  four phases with recorded, defensible reasons is not penalized for the skip
  count. A trajectory that silently omits phases is penalized on the
  honest-uncertainty and scope-discipline dimensions.
- **Terminal state equivalence.** Compare arms on whether they reach the
  fixture's expected `terminal_state` (merged, closed, blocked, released) with
  the required evidence. A baseline that correctly identifies a blocked state
  and stops is scoring honestly; do not penalize it for not forcing a merge.

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

## Claims scoping

Every comparison claim must state the **model(s)**, **harness version**,
**fixture revision** (git SHA), and **run date**. Do not generalize a result
beyond the tested window. A trajectory comparison is evidence about a specific
skill revision against a specific baseline under specific conditions — not a
universal effectiveness claim.
