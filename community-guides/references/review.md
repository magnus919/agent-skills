# Review and evaluation

## Check the delivered guide

1. Trace each requested capability through activity, worksheet/output, next action,
   and check. Remove orphan topics and supply missing dependencies.
2. Walk through from a new facilitator's perspective using only delivered materials.
   Record missing preparation, ambiguous instructions, time overruns, and unavailable
   helpers. Check both host notes and participant copies after fixing each problem.
3. Try filling out every unfamiliar worksheet with fictional data. Make sure a blank
   copy exists and that shared copies do not require private information.
4. Inspect rendered pages if providing a formatted document. Check writing space,
   page breaks, type size, grayscale readability, and complete offline instructions.
5. Distinguish structural validation, agent walkthrough, and actual participant pilot.
   Never claim the last based on the first two.

## Pilot invitation and observation

Prepare, but do not send without authorization, a short invitation to representative
participants. Ask whether they can complete an activity without extra explanation,
what prevented participation, and whether the next action fits their circumstances.
Obtain permission before recording or retaining personal feedback. Record the
activity, observed barrier, proposed change, and subsequent check. A pilot of one
session is evidence for that session, not the whole guide or every population.

## Skill evaluations

The portable manifest is `evals/evals.json`: repository schema version 1, stable case
IDs, realistic prompts, original supplied fixtures, expected outcomes, and observable
assertions. Separate trigger queries live in `evals/trigger-queries.json`; they are
harness-specific probes, not portable output-quality cases.

Use fresh contexts for with-skill and baseline runs. Give each the same case prompt,
raw fixture, model settings, and tool access; only the with-skill run receives the
skill. Do not supply assertions or desired answers to the generation agent. Keep
outputs in isolated directories. Record model, settings, case ID, skill revision or
content digest, run ID, actual outputs, and available elapsed time/token data. Mark
unavailable telemetry explicitly rather than estimating it as observed usage.

Run initial development cases and compare to baseline. Keep release cases out of
instruction tuning until the first full evaluation. If a release case drives a fix,
report that it is no longer untouched and add a fresh check when necessary.

Grade assertions against concrete output excerpts or paths, using code for mechanical
checks and an independent reader for behavioral judgments. Require evidence for a
pass. Compare outputs without revealing which used the skill when feasible. Track
critical failures separately so an aggregate score cannot hide invented local facts,
unaccepted assignments, missing activities, or unusable essential instructions.

Inspect the traces when a result disappoints. Change the general decision rule that
caused the problem, rerun affected cases, then check the suite. Avoid adding wording
requirements that merely match the evaluator. Retain negative baseline comparisons;
the skill may help some tasks and add overhead on others.

The manifest proves only that cases exist and satisfy the repository's structural
contract. Behavioral records are separate evidence, not v1 grader bindings or CI
release gates. Agent evaluations do not establish real community effectiveness.
