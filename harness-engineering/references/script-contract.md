# Script contracts

Run `python3 scripts/harness.py --help` from the installed skill directory.
Python 3.10+; standard library only. Explicit check execution currently assumes
POSIX process groups (macOS/Linux). It is not a sandbox: authorized commands can
mutate the target, access the network, and spawn processes. Review argv and scope
before `--execute`; hostile programs require a separate sandbox.

## Audit

`audit --target DIR [--html NEW_FILE]` reads only artifact presence in known root
paths and CI files. JSON reports all five subsystems plus lifecycle, discovered
artifacts, and unknown behavior/cause. It does not parse content, follow nested
instructions, query remote state, or run project commands. No readiness score.
HTML contains the same findings with escaped text and never overwrites a file.

## Scaffold

`scaffold --target DIR [--apply]` previews missing AGENTS.md, harness-state.json,
and handoff.md. `--apply` creates only missing paths, skips existing paths including
symlinks, and uses exclusive writes. No overwrite flag. It does not install or
execute anything. There is no mandatory init.sh: setup and real verification stay
in the project's existing commands. Review duplicate state stores before applying.

## Verify

Create a JSON list of argv lists, for example:

```json
[["python3", "-m", "pytest", "tests/", "-q"]]
```

`verify --target DIR --commands FILE` previews without running commands.
`--execute --report NEW_FILE` reserves the report path before running commands, executes serially without an
implicit shell, stops on first nonzero exit/launch error/timeout/output limit,
and writes JSON evidence. Progress snapshots replace the owned report atomically;
after interruption a running record means unknown completion, not safe replay.
File contents are fsynced, but full power-loss durability is not guaranteed without
a directory sync and filesystem-specific guarantees. This is a command report,
not a transactional side-effect ledger. A per-command
`--timeout SECONDS` defaults to 60, maximum 3600. The number of commands times
this timeout is an upper bound, not a separate task budget. Choose it accordingly.
The timeout kills the POSIX process group; detached processes may escape, which
is another reason this runner must not execute hostile code.

The report records argv, timestamps, pre/post Git revisions and dirty-state
fingerprints, command exits, durations, and output hashes. It suppresses raw
stdout/stderr to reduce accidental disclosure, but argv itself can contain secrets:
use environment or an appropriate credential mechanism, never literal tokens.
Output hashes cannot prove semantic acceptance; inspect authorized output separately.
Output streams are hashed incrementally. The default combined cap is 4 MiB per
command; --max-output-bytes sets a cap from 1 byte to 64 MiB. Exceeding it stops
the process group and records output_limit with partial hashes. Stdin is closed
to avoid interactive prompts. Raw output is not saved. Do not confuse a Git status fingerprint with a content snapshot.

Exit 0: completed audit/scaffold/preview, or every executed command exited zero.
Exit 1: an executed command failed/timed out/could not launch. Exit 2: invalid input
or output path. Zero-test runs and placeholders remain acceptance `not_assessed`.
No feature transitions, merge, deployment, or release is performed.

## Migration from upstream scripts

- create-harness.mjs → `scaffold` (preview first, no force/overwrite; reconcile
  existing feature_list.json rather than creating a second tracker).
- validate-harness.mjs → `audit` (findings replace scores).
- render-assessment-html.mjs → `audit --html NEW_FILE`.
- run-benchmark.mjs → audit for structure, then the experiment template for
  comparable real agent sessions; no artificial score is carried over.

## Contract validation and recorded comparisons

Run contracts.py validate with --kind state, graph, or run and --file JSON.
State checks IDs/dependencies/WIP, active owners, and criterion evidence bound to
the declared candidate. Graph checks typed nodes, routes, terminal reachability,
verifier unknown routing, and declared budgets/checkpoint store. Run checks stable
case IDs, input fingerprints, outcomes, evidence references, and finite measures.
Malformed input exits 2 with JSON; valid declarations exit 0 with behavior
not_assessed. These are example repository-owned contracts, not an industry schema.

Run contracts.py compare with --baseline and --candidate JSON. Both records need
identical model_config, environment, taskset, authority, and verifier SHA256
fingerprints, identical case IDs, and matching input hashes. Hash normalized
actual configuration/input bytes consistently; example template hashes are not
measurements. Include secrets by secure identity/version reference, never embed
credentials. Harness revisions may differ. Output is a descriptive paired table
with acceptance regressions, latency/cost/intervention deltas, and no significance
or release verdict. Provider/model/task changes require a differently framed
experiment; this helper intentionally refuses that comparison.

Validate templates before customization:

```sh
python3 scripts/contracts.py validate --kind state --file templates/state.json
python3 scripts/contracts.py validate --kind graph --file templates/graph.json
python3 scripts/contracts.py validate --kind run --file templates/run-record.json
```

Template declarations can pass validation while containing placeholders. Passing
means structural consistency, not usable deployment configuration or verified
behavior. Run the documented tests with Python or pytest; preserve source-faithful
limits when interpreting their results.
