# Entry points and worked use cases

Choose an entry point from the user's problem. Deliver the smallest useful
artifact for that mode; do not run every workflow because it is available.

| User starting point | Initial evidence | Procedure | Exit artifact |
|---|---|---|---|
| New repository setup | Commands, CI, existing guidance and task store | Fresh-session audit → minimal additive scaffold → real task → restart | Tailored entry map and verified startup/handoff |
| Agent repeatedly fails | One trace and expected behavior | First divergence → competing hypotheses → discriminating probe → repair | Failure analysis and bounded experiment |
| Custom agent runtime | Tool API, trust model, storage, cancellation | Runtime boundary → contracts → failure/replay tests | Runtime design and control implementation |
| Too much context/cost | Stage timings and loaded context | Attribute → remove/retrieve/compress → paired task comparison | Budget and supported cost/quality tradeoff |
| Recurring autonomous work | Work discovery, authority and acceptance | Single bounded loop → escalation → persistent recovery | Loop contract and exercised stop paths |
| Several workers conflict | Ownership and shared-state traces | Resource partition → serialized integration → explicit routing | Graph/ownership contract and integration evidence |
| Harness is aging | Rule owners, model changes, stale artifacts | Usage review → one retirement candidate → challenge test → rollback/adopt | Maintenance decision and updated source map |

## Case 1: Existing Makefile, unreliable agent

A Python repo already has a curated entry file, Makefile checks, and issue-tracker
state. The agent adds a search route and says done without exercising pagination.
Do not create a second feature list or replace the Makefile with init.sh.

1. Read accepted pagination behavior, the agent trace, and the current check path.
2. Locate the first divergence: implementation or completion judgment?
3. Define acceptance: page 2 returns the next bounded slice with stable ordering.
4. Run the existing suite and an integration case with enough records to expose
   the near miss. A mocked handler test alone may not exercise storage ordering.
5. Add the exact missing route/check reference to existing guidance, or strengthen
   the verifier if the command was already visible. One failure does not prove
   instruction bloat caused it.
6. Record revision-bound evidence and an interruption handoff. Roll back only
   this intervention if it worsens the representative tasks.

Exit: accepted route behavior plus a discoverable real check. A generated
scaffold is not the outcome.

## Case 2: The next session cannot recover an indexing task

The first session imported documents and changed chunking, but died before
persisting task state. The next session wants to repeat the entire import.

1. Recover source revision, documents already stored, and last verified operation.
2. Reconcile an operation ID with the real data store before replay; imported files
   are side effects, even when they are local.
3. Persist objective, active task, candidate revision, dependency state, evidence,
   unresolved operation, and next step. Reuse the existing state owner.
4. Start a clean session with only documented sources. Ask it to identify system,
   structure, startup, verification, and current work with source references.
5. Interrupt at another boundary and repeat recovery. A correct handoff document
   is weaker evidence than successful reconciliation after actual interruption.

Exit: no duplicate import and recovery of the same task from durable state.

## Case 3: Custom runtime has too many similar tools

Three tools overlap: search files, search code, and search repository. The agent
chooses inconsistently, retries malformed calls, and receives huge output.

1. Inspect tool selection/errors/response sizes before changing the model.
2. Choose clear ownership: one general search affordance or distinct semantics
   that a user can explain without implementation knowledge.
3. Define typed inputs, bounded results, truncation/recovery pointer, timeout,
   explicit denial, and error categories. Use the tool-contract template.
4. Compare selection accuracy, correction attempts, bytes/tokens returned, and
   task acceptance on representative calls including no-result and denied cases.
5. Keep permission enforcement in the executor. A clearer description does not
   make an unsafe command safe.

Exit: a tested tool contract and evidence about the observed selection failure.

## Case 4: Scheduled dependency repair

The user wants a daily bot to find failing dependency checks and propose repairs.
The scope authorizes local edits and reviewable branches, but not merge/deploy.

1. Define discovery cursor, one issue at a time, lock/lease, and eligible work.
2. Pin goal/acceptance outside the maker's unrestricted control.
3. Limit attempts, wall time/cost, no-progress cycles, and dependency failures.
4. Checker reruns the relevant real checks on the candidate. Unknown → escalation.
5. Persist run identity and side-effect reconciliation before retry. A scheduler
   retry must not open duplicate branches/issues or send repeated messages.
6. Stop at a reviewable proposal. Only use the host's scheduler if scheduling
   was requested; obey its authorization and notification contract.

Exit: exercised success, failed-check, unknown, budget-exhausted, and resume paths.

## Case 5: Parallel refactor with a shared API

UI and service workers own different modules but both depend on an interface.
Separate worktrees prevent file clobbering; they do not prevent semantic conflict.

1. Freeze the interface or assign a single owner to version it.
2. Send each worker goal, constraints, accepted input/output shape, authority,
   file ownership, and failure-report format. Avoid a full transcript dump.
3. Integrator reconciles revisions, contracts, and evidence; it cannot simply
   concatenate reports of independent passes.
4. Run the combined user journey. Changes to shared types invalidate prior
   evidence. On conflict, route to the contract owner rather than retrying both
   agents indefinitely.
5. Include the integration owner's review time in the comparison. Parallel code
   generation may increase total lead time if reconciliation dominates.

Exit: compatible integrated behavior and an inspectable ownership/evidence record.

## Case 6: Stronger model, increasingly stale harness

A harness uses forced context resets because an older model wrapped up early.
A newer model behaves differently. Do not assume either removal or retention.

Keep the goal and tasks fixed, compare reset versus compaction on interruption,
long-session behavior, cost, and verified acceptance. Retire resets only if the
representative evidence supports it. Keep a rollback and a challenge task likely
to reveal lost state. The best harness can be smaller; extra process is not
intrinsically more expert.
