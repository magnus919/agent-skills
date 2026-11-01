# AI-assisted review: model reviewers and model-authored changes

Two problems get conflated: a model reviewing code, and a model writing code. They
have different failure modes, different evidence, and different accountability.
Handle them separately.

## What the measurements say

**Model review in production.** Cihan et al. (ICSE SEIP 2025) studied an
LLM-assisted review tool based on an open-source PR agent across ten projects with
about 238 practitioners. In the three projects analyzed: 4,335 pull requests,
1,568 of them automatically reviewed. **73.8% of automated comments were resolved**
— but average pull-request closure time rose from 5h52m to 8h20m, most
practitioners reported only a minor quality improvement, and reported drawbacks
included faulty reviews, unnecessary corrections, and irrelevant comments.

A high resolution rate is not a precision measure. A comment can be resolved
because it was right, or because it was cheap to satisfy, or because ignoring it
was more expensive than complying.

**Benchmark performance.** Zeng et al. (SWR-Bench, 2025) evaluated mainstream
automated review tools and LLMs on 1,000 manually verified pull requests with full
project context. Current systems underperformed, and tools were better at
functional errors than other classes. Aggregating multiple review passes raised F1
by up to 43.67% — evidence for ensembles, not for the reliability of any single
pass.

**Model-generated tests.** Alshahwan et al. (Meta TestGen-LLM, FSE 2024) report
that of generated test cases, 75% built correctly, 57% passed reliably, and 25%
increased coverage; 73% of recommendations were accepted for production. The tool
filtered candidates against measurable coverage improvement *before* proposing
them. That filter is why acceptance is high; an unfiltered generator would not have
that property.

**What follows for practice:**

1. Model review output is a candidate list, not a verdict.
2. Precision is the weak axis, not volume. Expect noise, and budget triage time.
3. A test that a model derived from the patch proves the patch agrees with itself.
4. Ensembling review passes improves recall at the cost of more noise.
5. Latency and cycle time are real costs of adding a review stage.

## Model reviews a change

### Use it as a first pass, not a final one

A model is good at: scanning a large diff for missing null checks, inconsistent
error handling, deleted assertions, obvious injection sinks, and unstated
assumptions. It is weak at: domain invariants, business rules, subtle concurrency,
whether the *design* is right, and whether a test actually verifies the behavior.

Ask for a candidate finding list with locators and confidence, not a verdict. The AI
pre-review brief template encodes this contract.

### Triage rules

For each candidate finding:

| Check | Action if it fails |
|---|---|
| Does it cite a path and line in the provided diff? | Drop it — location-free findings cannot be verified |
| Can you reproduce or independently reason to the claim? | Downgrade to a question, or drop it |
| Is the severity defensible on your evidence, not the model's? | Re-label with your own severity |
| Does it depend on code the model did not see? | Convert to a question for the author |

Never paste a model's unverified claim into a review thread as `[blocking]`. You
own every comment you post, and the author cannot argue with a machine.

### Automation bias

The failure mode is not that models are wrong. It is that fluent, confident
comments are easy to accept, and that a reviewer who has read forty plausible
comments stops reading critically. Countermeasures:

- Keep a human decision step that can say "no findings" — and use it.
- Require a locator and evidence for every accepted finding; verbosity is not
  evidence.
- Rotate who triages; a single triager absorbs the model's biases.
- Track accepted-versus-dropped rates. A triager who accepts nearly everything is
  not reviewing the reviewer.

### Confidentiality and data handling

Model review sends code somewhere. Before using a tool, know where the diff goes,
whether it is retained, and whether the code is allowed to leave the environment.
For regulated or customer-data-bearing code, this is a gating question, not a
preference.

## A model wrote the change

The risks are different and more consequential, because the reviewer is now the
only independent check on plausible-looking code.

### What to check that you would not check in human-written code

- **Invented symbols.** Verify every external function, flag, environment
  variable, and configuration key exists at the pinned version. Models confidently
  call APIs that never existed.
- **Plausible-but-wrong domain logic.** Fluent code in a domain the model does not
  understand is the highest-risk category. Check the invariant, not the syntax.
- **Tests derived from the implementation.** If the test was written by reading the
  patch, it cannot detect a wrong patch. Ask how the test was derived and, where
  possible, write one from the requirement.
- **Silent dependencies.** New packages added without discussion; a "small" helper
  that pulls a transitive tree.
- **Deprecated patterns.** Code copied from an older version of the library or an
  older internal convention.
- **Comments that assert intent the code does not implement.** Model-written
  comments are often more confident than the code deserves.
- **Scope creep.** Large diffs with no clear authorial intent; behavior changes
  nobody asked for.
- **Provenance and licensing.** Where did the pattern come from? Is the project's
  policy on generated code satisfied?

### Independence rules

- A model reviewing the code it wrote is **not** independent verification. Same
  priors, same blind spots, and it will defend its own structure.
- A different model in a fresh session is *context separation*, not independence:
  it may share systematic errors with the author model.
- A human reviewer who reads only the model's summary is not independent either.
  Read the diff.

### Human accountability

The person who approves an AI-authored change is accountable for it exactly as if
they had written it. "The model wrote it" is not a mitigating fact in an incident
review, and it does not transfer to the model.

## Prompt and brief design

If you brief a model reviewer, the brief determines the output quality more than
the model does:

- Supply intent, scope evidence, the diff, and test output — not a description of
  them.
- Name the defect classes to look for, in priority order.
- Require a locator for every finding and an explicit "what I could not assess"
  section.
- Forbid verdicts and forbid "LGTM".
- Tell it that silence is acceptable; otherwise you get confabulated findings to
  fill the format.

The AI pre-review brief template is a working starting point.

## What not to do

- Do not use a model's review as the second reviewer on a T3 or T4 change.
- Do not let a model's confidence score drive severity.
- Do not treat "the model found nothing" as evidence of correctness.
- Do not send code to a model endpoint whose retention and residency you have not
  checked.
- Do not credit model review toward a review-quorum requirement without saying so
  in the record.
