# CI Failure Triage

Systematic diagnosis of CI failures. Load when a CI check is red and you need
to find the root cause — not when you're designing test strategy (that's
`test-strategy.md`) or building quality gates (that's
`test-automation-gates-metrics.md`).

## The One Rule

**RED IS DEAD.** Any non-green CI conclusion (failure, canceled, timed-out job)
blocks the PR. Do not dismiss a failure as "pre-existing" or "unrelated" without
evidence. The only valid response to a red run is investigation. The only valid
declaration of "ready" is a fully green run.

What does NOT count as proof of "pre-existing":

- "The failing test doesn't touch my changed files" — dependencies cascade
- "The first CI run on this branch passed" — evidence of flakiness, not safety
- "This test is known to be flaky" — belief, not evidence, until you rerun
- A verbal reassurance in the PR body without a rerun or log excerpt

## Diagnostic Chain (in order)

Start broad, drill narrow. Each step rules out an entire class of causes.

### 1. Runner Availability

Are there runners registered, and are they online?

```bash
# Repo-level runners
gh api repos/<owner>/<repo>/actions/runners

# Org-level runners (often where they actually live)
gh api orgs/<owner>/actions/runners
```

Look for: `status=online`, `busy=false`, and that labels match the workflow's
`runs-on:` directive.

| Finding | Meaning |
|---------|---------|
| 0 runners | No runner deployed, or runner container crashed |
| All busy | Insufficient capacity, previous runs stacking up |
| Runner exists but job stays queued | Label mismatch between workflow and runner |

### 2. Are CI Runs Being Created?

```bash
gh run list --repo <owner>/<repo> --branch <branch> --limit 5 \
  --json databaseId,status,conclusion
```

| Conclusion | Meaning |
|------------|---------|
| `skipped` | Workflow didn't run — `[skip ci]` in commit, bot push without trigger permissions, or branch protection blocked it |
| `queued` | Runner hasn't picked it up yet |
| Empty + `in_progress` | Running normally |
| Empty + no runs at all | Workflow trigger doesn't match the PR event |

### 3. Per-PR Check Status

```bash
gh pr view <num> --json statusCheckRollup \
  --jq '.statusCheckRollup[] | {name: .name, status: .status, conclusion: .conclusion}'
```

### 4. Get Failure Logs

```bash
# List recent runs for the branch
gh run list --repo owner/repo --branch feat/my-branch --limit 3 \
  --json status,conclusion,databaseId,url

# Get job IDs for a failed run
gh run view <run_id> --json jobs \
  --jq '.jobs[] | {name: .name, conclusion: .conclusion, id: .databaseId}'

# Stream full logs for a failed job
gh run view <run_id> --log --job <job_id>

# Grep for the actual failure (pytest compact mode hides assertions)
gh run view <run_id> --log --job <job_id> | grep -A 20 'FAILURES\|assert\|Error\|traceback'
```

**Pull the full log, not the dot summary.** pytest compact mode (`....F......`)
hides the assertion. Always grep for `FAILURES`, `assert`, `Error`, `traceback`.

### 5. Classify the Failure

| Signal | Classification |
|--------|---------------|
| Failure in a file your PR modified | Likely your regression |
| Failure in a file your PR didn't modify | Possibly pre-existing — but verify, don't assume |
| `ModuleNotFoundError` for unrelated module | Test container missing a dependency |
| "Timed out waiting for stack" | Test infrastructure, not your code |
| All dependabot PRs fail the same checks | CI infrastructure is broken |
| Gitleaks flags a line that existed on main | False positive — verify the line predates your PR |
| Exit 137 | See Exit 137 section below |

### 6. Rerun and Confirm

```bash
gh run rerun <run_id>
```

If it passes on rerun: evidence of transient failure. Document the rerun in the
PR thread. If it fails the same way: it's real. Trace the root cause before
claiming it's unrelated to your change.

## Exit 137: Container Termination

Exit 137 indicates SIGKILL but does **not** prove OOM. Do not call it a flake
or change memory limits until container and host evidence establishes the cause.

### Procedure

1. **Preserve the baseline.** Record the exact run URL, commit SHA, runner
   labels, failing step, and the preceding successful step.
2. **Compare recent runs.** Check whether the same workflow passed and failed
   on nearby commits. Separate deterministic test failures from abrupt process
   termination.
3. **Re-run once under observation.** A green rerun establishes intermittency;
   it does not clear the historical red run or prove resource pressure. While
   the job is active, capture a read-only snapshot:
   - Host memory, swap, and disk availability
   - `docker stats --no-stream`
   - `docker inspect` state for project containers (`State.ExitCode`, `State.OOMKilled`)
   - Recent kernel OOM messages (`dmesg | grep -i oom`)
4. **Fix evidence collection before guessing.** The CI workflow must collect
   diagnostics *before* teardown:
   - `docker compose ps -a`
   - Bounded `docker compose logs`
   - Inspect output for every project container
   - Runner memory/disk snapshot
   - Test-process exit status
   - A failure-only workflow artifact containing the report

   Treat every collection command as best-effort (`|| true`). A dead container
   must not abort collection of remaining evidence.
5. **Classify only from evidence.** Possible outcomes: container OOM,
   host-level kill, test-process crash, runner contention, or a real test
   assertion failure. Each has a different repair.

### Workflow Pattern

Failure collection must be `if: failure()` and must precede an `if: always()`
cleanup step. Do not rely only on `docker compose logs`: a dead or removed
container may make that command fail and erase the only diagnostic step.

## Pre-existing vs Regression Classification

```bash
# Check whether the failing file is in your diff
git diff --stat main | grep <failing_file>
```

| Signal | Pre-existing | Regression |
|--------|-------------|------------|
| Failing file not in your diff | Likely | Unlikely |
| ImportError for unrelated module | Likely | Unlikely |
| Fixture timeout ("waiting for stack") | Likely | Unlikely |
| All PRs fail the same check | Yes (infra) | No |
| Failing file IS in your diff | Unlikely | Likely |
| New assertion failure in your test | No | Yes |

**Even when classified as pre-existing:** rerun the job. If it stays red, the
failure is real regardless of who introduced it. File an issue if genuinely out
of scope, and link it from the PR body.

## Flaky Test Management

| Condition | Action |
|-----------|--------|
| Test flakes > 1% over 10 runs | Investigate and fix or remove immediately |
| Test depends on external service availability | Seed through deterministic fixture; give external availability its own test |
| Test depends on timing/race | Loop 50-100 times, document failure rate, fix the race |
| Test passes on rerun but failed first | Document the rerun. Do not merge while the original red run stands unexplained |

## Compose Readiness Corollary

When a dependency exposes a readiness endpoint, use a Compose healthcheck plus
`depends_on.condition: service_healthy`. `service_started` only proves process
creation. Base the healthcheck on the endpoint's documented ready state, use
standard-library tools already in the image, and keep its total retry budget
inside the CI wait budget.

## Pitfalls

- **Do not change memory limits, retry counts, or dependency timing until the
  failed run's primary test log and failure artifact agree on what failed.**
  An exit code is a symptom, not a root cause.
- **Do not classify the whole run from the last visible message.** When a long
  `set -e` validation chain returns non-zero after printing several PASS lines,
  rerun each check independently and record its exit status.
- **A green rerun does not clear the historical red run.** It establishes
  intermittency. The original failure still needs an explanation.
- **Do not repeat the identical failing chain without isolating the failing
  command.** Isolate first, then fix.
