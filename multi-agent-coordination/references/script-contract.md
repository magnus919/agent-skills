# Offline snapshot helper contract v1

`python3 scripts/coordination.py --help` describes the public interface. Resolve
paths from the skill root. Python 3.10+, standard library, no environment variables,
credentials, external processes or network. Both commands only read the given
file and print a report; `--dry-run` is accepted as a no-op. `--json` emits one
JSON object even for application input errors. Argument syntax errors use argparse
and exit 2. No report file is created.

## Input

Use templates/team-snapshot.json as a runnable fictional example. JSON must have
unique keys, finite numbers, a version exactly equal to integer 1, and exactly
the fields demonstrated at each record level. UTF-8 input is capped at 1 MB;
arrays at 5000 entries, tasks at 1000, total task dependency edges at 5000. IDs,
versions and other text fields are nonempty strings of at most 256 characters.
Timestamps need an explicit timezone. Snapshot `as_of` determines expiration;
the helper never substitutes wall-clock time.

- `seats`: unique `id`, current `execution`.
- `tasks`: unique `id`, declared `owner` referencing a seat, `status`,
  `intent_version`, `depends_on` task IDs, `claims`, `continuation`.
- Status: queued, claimed, working, blocked, delivered, accepted, canceled,
  denied or failed. Active means claimed/working/blocked/delivered.
- Claim: `seat`, `execution`, nonnegative integer `epoch`, `expires_at`.
- Continuation: null or `blocker`, `wake`, `owner` seat ID. Blocker/wake are
  descriptions or opaque references, not authenticated executable instructions.
- `knowledge`: unique `id`, `kind` (source/artifact/consumer), `status`
  (current/suspect/invalidated/unknown).
- `edges`: unique directed `source` → `target` knowledge IDs, meaning derivation
  or consumption. Cycles are allowed and traversal terminates.

All references must resolve. An invalid status, missing field, duplicate ID/key,
nonfinite number, dangling reference, timezone-free date or malformed record is
invalid input (exit 2), not a healthy snapshot.

## Output

`audit --file PATH --json`: deterministic findings for dependency cycles or
cycle-blocked downstream tasks; active tasks with stale intent, missing/multiple
claims, owner mismatch, obsolete occupant, expired claim; blocked active tasks
without a continuation; and non-blocked active tasks with unaccepted prerequisites.
Historical terminal tasks are not checked for current claims/intent. Task
prerequisites are modeled as a DAG, not every allowed conversational cycle.
The cycle finding lists a Kahn remainder, explicitly **not** exact cycle membership.
No finding means exit 0; findings mean 1. The example has no audit findings but
contains an invalidated knowledge source: audit does not certify knowledge safety.

`exposure --file PATH --source ID --json`: lists all reachable knowledge descendants
and the subset declared consumers. Exit 0 means traversal completed, including
when nothing was reachable. `coverage: unknown` is always emitted: the helper
cannot establish that supplied edges represent all actual readers/copies.
A reachable consumer may be unaffected if it never used the claim; exposure is
not infection. Missing source is exit 2. `--source` on audit is rejected.

Reports retain `runtime_acceptance: not_assessed`. The helper cannot authenticate
claims, leases, grants, actual side effects, epoch enforcement, memory truth,
consumption, comprehension, task acceptance or live recovery. Epoch is declared
metadata; runtime fencing still needs a trusted executor. Inspect findings before
any authorized action; the script never resolves them itself.

## Tests

Run `python3 -m unittest discover -s scripts -p 'test_*.py'` from the skill root.
The tests challenge concurrent claims, expired/obsolete occupants, cyclic graphs,
missing references, malformed/oversized input and exposed knowledge. These prove
the helper's bounded calculations, not behavioral quality or a deployed fleet.
