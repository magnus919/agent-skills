# Scoping and depth: how much review, and of what

Review fails at the scope step more often than at the judgment step. A reviewer
who skims 2,000 lines and approves has produced an approval that covers very
little, while signalling coverage of everything.

This file covers sizing, tiering, attention budgets, incremental review, stacked
changes, and what to do when a change is simply too big.

## Measure the effective change, not the raw diff

Raw diff size overstates review work and understates risk:

- **Exclude** generated code, lockfiles, vendored dependencies, snapshots, and
  minified assets from the reading budget. Their review question is provenance —
  what produced them, and is the input to that generation in the diff? — not a
  line-by-line read.
- **Count** added plus deleted lines of hand-written source, tests, config, and
  migrations. A rename that touches 400 files may be 20 lines of real change plus
  400 mechanical edits; the mechanical edits need a spot check and a
  compiler/test run, not 400 reads.
- **Treat formatting-only commits separately.** A reformat mixed with behavior
  change hides the behavior change. Ask for the reformat as its own change (this
  is also Google's guidance for authors).

`scripts/review_scope.py` computes effective lines this way and reports the
generated-line total separately so the difference is visible rather than assumed.

## Size bands and what they buy

| Effective lines | Shape | What a reviewer can realistically do |
|---|---|---|
| ≤ 50 | trivial | Full read; check intent and one failure path |
| 50-200 | small | Full read; boundary and error paths; tests |
| 200-400 | standard | Full read at a deliberate pace; one sitting |
| 400-1,000 | large | Split into units or two sessions; design first, then paths |
| > 1,000 | oversized | Do not review in one pass; ask for a split or review by unit with declared partial coverage |

The 200-400 band is the widely cited "review at a time" range, derived from vendor
research on a single team. Use it as a planning default, not a law. The defensible
part — corroborated by academic data — is that larger changes get slower reviews
and shallower comments.

## Risk tier, not size, sets scrutiny

Size sets *effort*. Risk sets *depth* and *who must review*. A 40-line change to
authorization deserves more scrutiny than a 900-line test refactor.

| Tier | Trigger | Review shape |
|---|---|---|
| T1 routine | Docs, test-only, isolated rename, patch dependency with no behavior change | One reviewer, one pass, evidence tests run |
| T2 standard | New bounded behavior, config default change, internal API change | One reviewer with domain knowledge; negative-path test expected |
| T3 sensitive | Auth, authorization, crypto, payments, PII, deletion, migration, public contract, dependency major bump, CI/build | Two reviewers including one who owns the sensitive area; compatibility or threat note; rollback evidence |
| T4 critical | Money movement, tenant isolation, irreversible operations, regulated or safety-critical paths, release hotfix | Named accountable reviewer plus independent second reviewer; rehearsal or dry run; explicit rollback owner |

Tiering is a claim about blast radius. Say which tier you used and why; a tier
asserted silently cannot be challenged.

`review_scope.py` flags risk-bearing paths by name convention. That is a weak
signal in both directions: an innocuous filename can hide a privileged change,
and a file named `auth_cache.py` may be irrelevant. Treat flags as questions for
the author.

## Attention budget

Planning rate: about 300 effective lines per hour, capped at 60 minutes per
session. The arithmetic matters less than the behavior it forces:

- If the estimate exceeds one session, the change does not fit one review. Split
  it, or schedule a second session and say so.
- When the cap is reached, stop and record what remains. A tired reviewer
  continues reading and stops noticing.
- A second session on the same change is normal for large changes. Pretending it
  was one pass is what makes the record dishonest.

Review the risk-bearing units first, while attention is highest. Finish with
documentation and mechanical changes, which degrade least with fatigue.

## Reading order inside a unit

1. **Intent** — the issue or description, before any code.
2. **Interface** — signatures, schemas, routes, config keys: the contract the
   change creates.
3. **Main path** — the behavior the change exists to add.
4. **Boundary paths** — empty, invalid, huge, duplicate, concurrent, unauthorized.
5. **Failure paths** — errors, timeouts, partial writes, retries, cancellation.
6. **Tests** — do they assert the above, and would they fail if the code broke?
7. **Operability** — logs, metrics, flags, rollback.

The order is deliberate: contracts and behavior first, because a defect in a
contract invalidates detailed reading below it.

## Context beyond the diff

Diffs hide the context that makes a change right or wrong. Read the whole function
when a small addition lands in a long one; read the caller when a signature
changes; read the sibling implementation when a new handler mirrors an existing
one. A four-line addition inside a 50-line method that should have been split is a
design finding, and it is invisible in a diff view.

Ask: *if I only saw these lines, what would I be unable to tell?* Then go read
that.

## Incremental review

- Re-review the diff since your last review, plus anything the author says
  changed by inference. Do not re-read the parts you already covered unless the
  change altered their assumptions.
- An approval covers the code you saw. If the change grows materially — new
  files, new dependencies, changed contracts — the approval lapses. Say so
  explicitly rather than letting a stale approval travel.
- A rebase can silently change the change. Confirm the diff you approved is the
  diff being merged (base revision and head commit), not merely the same branch
  name.

## Stacked and dependent changes

- Review each layer against its own intent and the layer beneath it. A layer that
  only makes sense with the next one is a design smell worth naming.
- Each layer should build and pass tests on its own; if it cannot, say which
  evidence is deferred and to which layer.
- Do not review the cumulative diff and the layers as well — you will review the
  same lines twice and miss the seams.

## When the change is too big

In order of preference:

1. **Ask for a split.** A change that cannot be split is usually several changes
   that were not separated. Name the seams you can see.
2. **Review the design first.** Read interfaces, schemas, and entry points, and
   send back design-level comments before detailed reading. This unblocks the
   author faster than a half-finished line review.
3. **Review by unit with declared coverage.** Record exactly which units you read
   and which you did not. A partial review with honest scope is useful; a
   complete-looking review of an unread change is not.

Do not "review" a large change by reading the test names and the diffstat. That is
a triage, and triage can be a legitimate first step, but it is not an approval.

## Stopping rule

Stop when any of these is true:

- The unit is read, its boundary and failure paths are covered, and the tests
  support the claims.
- The session cap is reached — record the remainder and reschedule.
- You cannot understand the code well enough to review it. That is a finding:
  ask the author to clarify or simplify, and say the review is blocked on
  understanding rather than guessing.

The last one is not a failure of the reviewer. In Google's framing, if a strong
engineer cannot follow the code, other future readers will not either.
