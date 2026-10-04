# Implementation patterns from Jev projects

These examples show ways to place a typed System One classifier inside a
larger deterministic workflow. They are implementation patterns, not evidence
that Jev or another classifier is accurate enough for a particular domain.
Use the lessons to design a pilot; validate the full path on representative
local data before relying on it.

## Four implementation patterns

### Browser action selection

In `browser-use/jev-ultrafast` (inspected at commit
`1231850a0bf1a0c0341fe408ef1668dbbfdfac46`), the agent constructs an action
table from the current page and asks the classifier to choose an operation
and compatible target. Deterministic code validates both selections, ties the
proposal to the observed page state, checks that state again before acting,
and verifies the requested result separately from the model's `DONE` label.
The agent also bounds its action loop and detects repeated no-progress steps.

**Reusable pattern:** generate candidates from fresh state, bind the answer
to that state, validate operation/target compatibility, reject stale answers,
and verify the postcondition independently.

**Avoid:** passing arbitrary model-produced selectors or arguments to a browser
executor; treating a completion label as proof; retrying unchanged actions
without a progress check.

### Two-stage skill routing

In `DECRUX9812/typesafe-skill-router` (commit
`94fe114b3c53b3d6b81ba72890eb6db596cbaa12`), an opt-in hook first narrows a
large skill roster, then asks per-candidate fit questions. It chunks rosters
to respect the classifier's option limit, includes a none-of-these outcome,
applies explicit relevance/fit/disagreement rules, and allows silence. The
hook adds an advisory relevance block to the request; it does not load the
skill or prove that downstream runtime behavior followed the suggestion.
Timeouts and errors produce no hint.

**Reusable pattern:** separate shortlist recall from final fit, preserve a
no-match outcome, and measure whether the correct capability was actually
loaded and used.

**Avoid:** assuming a correct-looking suggestion guarantees correct routing;
silently forcing the nearest available skill; ignoring added calls, latency,
or chunk-boundary effects.

### TypeSafe's progressive-disclosure skill suggestion

The [official cookbook](https://docs.typesafe.ai/cookbooks/skill_suggestion),
checked 2026-10-04, adds a concrete recipe to the pattern above:

1. Rank the full roster with Choice while separate Noul questions assess
   whether the request needs a skill. Ranking alone always has a nearest option.
2. Recheck the top three using full descriptions and opening instruction
   excerpts; per-candidate fit questions allow rejecting the entire shortlist.
3. Return at most one advisory suggestion. Keep the roster unchanged and append
   the hint after it to preserve prefix caching; the agent still decides what
   to load.

The published Jev 1.12 / Claude Haiku 4.5 run uses 488 synthetic requests:
315 covered and 173 uncovered. Wrong first loads fell from 16.8% to 7.3%;
needless loads from 9.8% to 4.0%. Wrong-load accounting includes covered turns
that load nothing. These are first-response skill-load outcomes, not downstream
task success; covered requests were model-written from the skills themselves.
The cookbook's thresholds and shortlist size are example settings, not portable
calibration or universal defaults.

For an adoption study, separate shortlist misses, no-fit rejection, final hints,
actual loads, and successful skill use. Compare the unchanged agent with the
hinted agent on independently labeled real-shaped turns, including near-neighbor
skills and requests no installed skill serves. Preserve mandatory skill routing;
a semantic hint cannot suppress an explicit skill request or widen permissions.
Count both decision calls and final agent overhead in cost and latency. Keep
no-hint behavior for invalid or unavailable decisions. See
[selective judgment](selective-judgment.md) before deploying confidence gates.

### Supervisory action judge

In `DevMortimer/pi-warden` (commit
`ba615afae10d066d781771d1a922c0205910b968`), local rules and per-violation
authorization run before model judgment. Hard-denied actions stop without a
model call, and selected read-only actions can skip judgment. Otherwise, a
typed judge reviews a bounded action summary and context. Deterministic floors
and configured thresholds map the result to explicit allow, warn, confirm,
or deny lanes. The integration makes provider-failure behavior configurable:
fail-open can permit the action with an error verdict; fail-closed escalates
to confirmation; evidence-floor behavior reapplies built-in rules.

**Reusable pattern:** preserve deterministic authority boundaries, constrain
the model to explicit advisory or escalation lanes, and choose outage behavior
according to action risk. Evaluate each judgment signal and the combined
supervisor separately.

**Avoid:** giving a judge authority to override hard policy; assuming all
sub-questions have the same reliability; allowing weak signals to silently
control high-impact actions; treating fail-open as a neutral default.

### Moderation with an availability fallback

In `CodeAlive-AI/mastra-jev-moderation` (commit
`8735ea80efad6ec1dab26f74f1a7851007758915`), middleware asks a typed block
question and a separate category question. The block decision controls the
abort; category is logged only. The implementation bounds input length and
uses a fixed rejection reason. On provider timeout, HTTP/shape failure, or
open circuit breaker, it logs and passes the message through; without a key,
the example does not install the processor.

**Reusable pattern:** separate enforceable outcome from diagnostic labels,
bound the input, and write the provider-outage lane as an explicit policy.

**Avoid:** confusing valid typed output with correct moderation; letting a
logging category affect enforcement accidentally; using fail-open where
provider unavailability must not bypass a safety control.

## Cross-cutting design guidance

- Treat classifier output as a proposal. Deterministic code owns validation,
  authorization, state freshness, side effects, and completion checks.
- Specify no-fit, abstention, malformed output, timeout, and provider outage
  behavior as part of the interface. A missing decision is not automatically
  safe or unsafe; the domain policy must say what happens.
- Test the handoff and consequence, not only the answer schema: whether the
  intended action was held or executed, whether a skill was actually used, and
  whether the user-requested postcondition was observed.
- Measure both individual questions and the end-to-end system. More stages can
  add cost, latency, new error modes, and mismatched judgments.
- Keep demonstrations, source-code behavior, and independently reproduced
  target-domain evidence distinct. These four source reviews do not establish
  production quality, safety, or portability to another System One model.

## Source attribution

The commit identifiers above identify the reviewed snapshots of the four
named public repositories. The behavioral summaries here are self-contained;
no external reading is required to apply the patterns. Repository claims,
benchmarks, and test results are intentionally not repeated as evidence of
general effectiveness.
