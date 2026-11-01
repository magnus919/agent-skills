# Defect taxonomy: what to look for, and how to know

A reviewer without a taxonomy reviews whatever catches the eye, which is usually
style. This file lists the classes worth spending attention on, how to detect
each one in a diff, what evidence settles it, and the traps that produce false
positives.

Use it as a question set, not a checklist to tick. The questions that matter most
are the ones the diff does not answer.

## 1. Intent mismatch

**Looks like:** behavior described but not implemented; implementation that does
more than described; unrelated files in the diff; a "fix" that changes semantics
elsewhere; tests that assert the new behavior while the description claims the old
one.

**Detect:** read the issue or PR description first, then the diff, and note the
delta. Check the file list against the stated scope.

**Evidence:** the description and the diff side by side; a question to the author
about the extra scope.

**Traps:** a description can be wrong rather than the code. Ask which is
authoritative instead of assuming the code drifted.

## 2. Correctness and invariants

**Looks like:** off-by-one boundaries; empty, single-element, or maximum-size
input; null or absent values; ordering assumptions; duplicate handling; rounding
and precision (money in floats); units (ms vs s, bytes vs KiB); time zones and
DST; encoding and normalization (Unicode, case folding); locale-dependent
formatting; integer overflow.

**Detect:** for each changed condition, ask what the boundary values are and
whether the code handles them. Look for `<=` versus `<`, `len(x) - 1`, array
indexing, and arithmetic on user-supplied values.

**Evidence:** a test at the boundary, or a one-line execution in a REPL.
Prefer running it to reasoning about it when the setup is cheap.

**Traps:** flagging every comparison without stating which input breaks it. A
boundary claim without a failing input is a guess.

## 3. Failure handling

**Looks like:** swallowed exceptions (`except: pass`); broad catches that hide
programming errors; errors logged and then ignored; partial writes without a
transaction or compensating action; retries that are not idempotent; missing
timeouts on network calls; resource leaks (files, connections, locks, temp dirs);
cancellation or shutdown paths that skip cleanup.

**Detect:** trace what happens when each external call fails, times out, or
returns a malformed response. Check whether the function's error contract is
documented and whether callers can distinguish "not found" from "failed".

**Evidence:** a test that forces the failure (fault injection, stub that raises)
and asserts the observable outcome.

**Traps:** demanding a retry for an operation that must not be retried (payments
without idempotency keys). Ask what the correct failure behavior is before asking
for the mechanism.

## 4. Concurrency and shared state

**Looks like:** check-then-act races; unsynchronized mutation of shared
structures; lock ordering that can deadlock; `await` inside a lock; missing
`await` so a coroutine never runs; fire-and-forget tasks that outlive the request;
cache invalidation on the wrong key; global mutable state; transaction boundaries
that do not match the invariant.

**Detect:** list the shared mutable state the change touches and the interleavings
that matter. Read the whole function, not the changed lines.

**Evidence:** rarely a test — concurrency bugs resist reproduction. Reasoning from
the code, a stress test, or a documented invariant is the realistic evidence.
Say which one you used.

**Traps:** asserting a race without naming the two interleaved operations. If you
cannot name them, you have a suspicion, not a finding — write it as a question.

## 5. Trust boundaries and security

**Looks like:** unvalidated input reaching a privileged sink (SQL, shell, file
path, URL, template, deserializer, model prompt, log); authentication without
object-level authorization; tenant or user context not threaded to the query;
secrets in code, logs, errors, or URLs; home-grown crypto; disabled certificate
verification; permissive CORS; mass assignment; unsafe deserialization; SSRF;
path traversal; missing rate limits on an abusable endpoint; prompt injection
where model output drives a tool.

**Detect:** for every new entry point, ask three questions — who can call it, what
object does it act on, and who is allowed to act on that object. Then trace the
input to the sink.

**Evidence:** a denial test: the request that should be refused and is not. A
passing authorization test proves the allowed path; only a denial test proves the
boundary.

**Traps:** reviewing only the changed lines when the change alters a system-wide
boundary. A new endpoint, a new dependency, or a new deserialization path can
change the threat model far from the diff.

For threat modeling and secure design, use the `secure-software-engineering`
skill; this taxonomy is the review-time lens, not a security program.

## 6. Data, schema, and compatibility

**Looks like:** a migration with no rollback; a column added `NOT NULL` without a
default on a large table; a backfill with no batching or resume; a destructive
`DROP`/rename without a compatibility window; a wire-format change that older
clients cannot parse; changed defaults that silently alter behavior for existing
users; index changes that lock a table; cache keys whose shape changed.

**Detect:** ask what happens to rows written by the old code and read by the new
code, and vice versa. Check the deploy order: does the migration run before the
code that needs it, and does the old code still work after it?

**Evidence:** forward and backward migration run on representative data; a
compatibility test with an old payload fixture; timing on realistic volume.

**Traps:** treating a migration as a code change. It is an operational event with
a rollback story, and it belongs in the tier that requires one.

Deep migration methodology belongs to `data-engineering` and `data-architect`.

## 7. API and contract evolution

**Looks like:** a field removed or renamed without deprecation; a new required
parameter; a changed error shape or status code; pagination semantics changed;
idempotency keys ignored; a breaking change announced only in a changelog;
webhooks whose payload or retry behavior changed; event schemas changed without a
version.

**Detect:** diff the contract, not just the implementation. Find the consumers —
grep for the field name, check generated clients, ask for the consumer list.

**Evidence:** a contract test or a consumer build against the new schema.

**Traps:** assuming "internal" means "no consumers". Internal consumers are often
the hardest to enumerate.

Contract ownership and deprecation policy belong to `api-design-and-evolution`.

## 8. Performance and resource use

**Looks like:** a query in a loop (N+1); unbounded result sets; loading a whole
table into memory; missing index on a new filter; synchronous work on a request
path that should be queued; cache stampede on expiry; per-request client
construction; log volume in a hot path.

**Detect:** identify the hot path and the growth variable. Ask what happens at
10× the current data.

**Evidence:** a benchmark or profile, not intuition. Without one, write a question
about expected volume rather than a blocking performance claim.

**Traps:** micro-optimizing readability away for unmeasured gains. The burden of
proof is on the optimization when it costs clarity.

Measurement method belongs to `performance-optimization`.

## 9. Test adequacy

**Looks like:** a test that executes code but asserts nothing meaningful; a test
that asserts a mock was called rather than an outcome; no negative-path test for a
new guard; assertions weakened or deleted in the diff; a test that would pass with
the change reverted; sleeps instead of synchronization; shared mutable fixtures;
tests that mirror the implementation line by line.

**Detect:** for each behavior the change claims, find the test that fails if the
behavior is removed. If none exists, that is the finding. Check the diff for
deleted or loosened assertions — they are easy to miss and often deliberate.

**Evidence:** revert the change, run the test, watch it fail, restore. That is the
only proof that a test is a test.

**Traps:** demanding 100% coverage. Coverage measures execution, not verification.
A high-coverage suite of assertion-free tests proves less than a small, sharp one.

Independence models and mutation evidence belong to `qa-methodology`.

## 10. Operability

**Looks like:** a new failure mode with no log line, or a log line at the wrong
level; secrets or PII in logs; no metric to distinguish success from failure; a
feature flag with no removal plan; config added without validation or a default;
health check that passes while the dependency is down; no way to roll back.

**Detect:** ask what the on-call engineer sees at 3 a.m. when this fails. If the
answer is "nothing", that is a finding.

**Evidence:** the log or metric in a failure-path test; a config schema; a
documented rollback step.

**Traps:** demanding dashboards for every change. Proportionate observability is
the standard, and the tier tells you the proportion.

## 11. Documentation and decision records

**Looks like:** README or runbook not updated for a changed command or flag;
public docs still describing removed behavior; no ADR for a consequential choice;
changelog missing a breaking change; comments that explain *what* rather than
*why*; TODO added without an owner.

**Detect:** check whether the change alters how someone builds, tests, operates,
or upgrades the system. If it does, documentation is in scope.

**Evidence:** the updated doc in the same change.

**Traps:** blocking on doc style. Content and correctness are reviewable; prose
polish is not worth a blocking comment.

Documentation review method belongs to `technical-documentation`; durable decision
records to `adr-authoring`.

## 12. Dependencies and supply chain

**Looks like:** a new dependency for something trivial; unpinned or wildly ranged
version; a major bump with no changelog read; new transitive packages; a license
change; an install hook or post-install script; a typosquat-looking name; a
dependency that duplicates an existing one.

**Detect:** read the lockfile diff, not just the manifest. Count new transitive
packages. Check the project's dependency policy.

**Evidence:** the lockfile diff, the upstream changelog, a license check, and a
successful build from a clean cache.

**Traps:** "it's just a small library" — a dependency is a permanent operational
and security commitment, not a code-size decision.

## 13. AI-generated change specifics

**Looks like:** invented APIs or configuration keys; plausible-but-wrong logic in
an unfamiliar domain; tests derived from the implementation; a pattern copied from
a deprecated version; new dependencies added silently; confidently wrong comments;
large diffs with no clear authorial intent.

**Detect:** verify every external symbol the change calls actually exists at the
pinned version. Check whether tests were written before or after the code. Ask
what the author verified themselves.

**Evidence:** a build against the real dependency versions; a test derived from
the requirement.

**Traps:** treating fluency as correctness, and treating the model's own review of
its output as independent verification.

See the AI-assisted review reference for the full model.

## Using the taxonomy

- Pick the classes the tier makes relevant. A docs change does not need
  concurrency analysis.
- For each class you examined, you can say either "checked, nothing found" or
  "not checked". Both are honest; only silence is not.
- Convert anything you cannot settle into a `[question]`, not a soft `[blocking]`.
  Precision in severity is what keeps the review credible.
