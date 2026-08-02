# CI Failure Triage

Systematic diagnosis of CI failures. Load when a CI check is red and you need to find the root cause — not when you're designing test strategy (that's [test-strategy.md](./test-strategy.md)) or building quality gates (that's [quality-gates-and-metrics.md](./quality-gates-and-metrics.md)).

## The One Rule

**RED IS DEAD.** Any non-green CI conclusion (failure, canceled, timed-out job) blocks the PR. Do not dismiss a failure as "pre-existing" or "unrelated" without evidence. The only valid response to a red run is investigation.

What does NOT count as proof of "pre-existing":

- "The failing test doesn't touch my changed files" — dependencies cascade
- "The first CI run on this branch passed" — evidence of flakiness, not safety
- "This test is known to be flaky" — belief, not evidence, until you rerun
- A verbal reassurance in the PR body without a rerun or log excerpt

## Diagnostic Procedure

Follow these steps in order. Each step rules out an entire class of causes before moving to the next.

1. **Reproduce and confirm the failure.** Rerun the failing job to confirm it is deterministic. Pull the full log (not the dot summary) and grep for the actual assertion or error: `gh run view <run_id> --log --job <job_id> | grep -A 20 'FAILURES\|assert\|Error\|traceback'`. If it passes on rerun, apply the flake protocol below before proceeding.

2. **Classify by exit code or error type.** Use the exit-code taxonomy below to determine whether the failure is a test assertion failure (code bug), an infrastructure failure (environment), or a resource failure (OOM/timeout). This determines which investigation path to follow.

3. **Isolate: environment vs code vs flake.** Check whether the failure is in a file your PR modified (`git diff --stat main | grep <failing_file>`). If not in your diff and all other PRs fail the same check, it is infrastructure. If only your branch fails and the file is in your diff, it is likely your regression.

4. **Localize the fault.** Use `git bisect run` for regressions (see below), diff analysis for new failures, or log timeline analysis for infrastructure issues. Narrow to the specific commit, configuration change, or resource threshold.

5. **Fix and verify.** Apply the fix, push, and confirm the CI run goes green. A green rerun after a fix is evidence of resolution. Document the root cause in the PR thread. If the fix is in infrastructure (not your PR), file an issue and link it.

## Exit-Code Taxonomy

| Code | Signal | Meaning | Common Cause | Triage Path |
|------|--------|---------|-------------|-------------|
| 1 | — | Generic failure | Test assertion failed, uncaught exception | Read traceback; fix code or test |
| 2 | — | Usage error / shell builtin misuse | Invalid CLI arguments, bash syntax error | Check command invocation in CI config |
| 126 | — | Permission denied | Script not executable, file permissions wrong | `chmod +x` the script; check CI user |
| 127 | — | Command not found | Missing dependency, wrong PATH, typo in command | Verify tool installation step; check `$PATH` |
| 137 | SIGKILL (9) | OOM kill or forced termination | Container exceeded memory limit; host OOM killer | Check `docker inspect` for `OOMKilled`; increase memory or fix leak |
| 139 | SIGSEGV (11) | Segmentation fault | Native code crash, corrupted memory, C extension bug | Reproduce locally with ASAN; check native deps |
| 143 | SIGTERM (15) | Graceful termination request | CI timeout, orchestrator cancellation, shutdown hook | Check job timeout settings; look for slow tests |

### Exit 137 Deep Dive

Exit 137 indicates SIGKILL but does **not** prove OOM. Do not change memory limits until evidence establishes the cause.

**Evidence to collect before classifying:**
- `docker inspect <container>` → `State.OOMKilled: true/false`
- `dmesg | grep -i oom` on the host
- `docker stats --no-stream` snapshot during the run
- Whether the same test passes with higher memory limits

## Flake-vs-Failure Protocol

| Condition | Action |
|-----------|--------|
| Test fails once, passes on immediate rerun | Rerun once. If it passes, document the rerun in the PR thread. Do **not** rerun twice — two reruns masks a 50%-flaky test. |
| Test fails the same way on rerun | It is a real failure. Proceed with full triage. |
| Test flakes > 1% over 10 runs | Investigate root cause immediately (timing, shared state, external dependency). Do not suppress. |
| Test passes on rerun but the original red run stands unexplained | The failure is not cleared. Investigate or quarantine. |

**The rerun-once rule:** rerun exactly once to distinguish flake from failure. Never rerun until green — that converts a signal into noise.

## Git Bisect for Automated Fault Localization

When a regression appeared somewhere in a range of commits, `git bisect run` automates binary search:

```bash
# Find which commit broke the test suite
git bisect start
git bisect bad HEAD
git bisect good <last-known-green-sha>
git bisect run pytest tests/test_payment.py -x --timeout=60
```

The script passed to `bisect run` must exit 0 for "good" and non-zero for "bad". Exit 125 tells bisect to skip the current commit (useful for commits that don't compile).

```bash
# Skip commits that don't build
git bisect run bash -c 'make build || exit 125; pytest tests/ -x'
```

**When to use bisect:** the failure is deterministic, the green→red transition happened within a known commit range, and the test can run unattended in < 5 minutes.

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

**Even when classified as pre-existing:** rerun the job. If it stays red, the failure is real regardless of who introduced it. File an issue if genuinely out of scope, and link it from the PR body.

## Runner and Infrastructure Checks

| Finding | Meaning | Action |
|---------|---------|--------|
| 0 runners online | Runner crashed or never deployed | Contact infra; check runner container |
| All runners busy | Capacity issue; previous runs stacking | Wait or add runners |
| Job queued indefinitely | Label mismatch (`runs-on:` vs runner labels) | Fix workflow label |
| `skipped` conclusion | `[skip ci]` in commit, or trigger mismatch | Check commit message and workflow `on:` |

## Compose Readiness Corollary

When a dependency exposes a readiness endpoint, use a Compose healthcheck plus `depends_on.condition: service_healthy`. `service_started` only proves process creation. Keep the healthcheck retry budget inside the CI wait budget.

## Gotchas

- **Do not change memory limits, retry counts, or dependency timing until the failed run's primary test log and failure artifact agree on what failed.** An exit code is a symptom, not a root cause.
- **Do not classify the whole run from the last visible message.** When a long `set -e` chain returns non-zero, rerun each check independently.
- **A green rerun does not clear the historical red run.** It establishes intermittency. The original failure still needs an explanation.
- **Rerunning more than once converts signal to noise.** One rerun distinguishes flake from failure; two reruns hides a coin-flip test.

## Composition

- Systematic debugging methodology for complex root-cause analysis: [systematic-debugging](../../systematic-debugging/SKILL.md)
- Test isolation and CI-vs-local divergence: [test-debugging.md](./test-debugging.md)

*Sources: git-bisect documentation (git-scm.com/docs/git-bisect), GitHub Actions exit codes (docs.github.com), Linux signal numbers (man 7 signal), DORA State of DevOps Reports (CI failure analysis).*
