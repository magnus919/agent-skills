# Lightweight Test-Hardening Path

Test-hardening is a subtype of the lightweight delivery path. Use it when the
production behavior is already correct and the change adds a regression guard
for a known coverage gap, mutation survivor, or controlled weakening.

It is not an ordinary production bugfix. Do not require the new test to fail on
clean `main` when the purpose of the test is to distinguish the clean behavior
from a named mutant.

## Applicability

Use this subtype only when all of these are true:

- production/runtime code remains unchanged;
- the change is confined to one or a few test or fixture files;
- no dependency, configuration, authentication, cryptography, deployment, or
  public API surface changes;
- the current behavior and the intended invariant are understood; and
- the regression can be exposed by a focused deterministic test plus a bounded
  controlled weakening or targeted mutant.

If any condition fails, select the ordinary lightweight, full, refactor, or
high-risk path instead.

## Required evidence

Record a compact contract containing:

1. the public behavior or invariant being protected;
2. evidence that the clean implementation already satisfies it;
3. the named mutation or controlled weakening that must be rejected; and
4. explicit non-goals, including production-code changes when none are needed.

The test should exercise the public contract, use hermetic setup at the relevant
failure boundary, and assert the semantic invariant rather than an incidental
current implementation subtype or message.

The minimum verification set is:

- clean baseline passes;
- the named mutant or controlled weakening fails the new test;
- the focused suite passes on the clean candidate;
- lint, compilation, and changed-scope checks pass; and
- changed-file security and public-metadata checks pass.

When the repository already has a mutation-testing setup, record the mutant
evidence in `qa-methodology`'s bounded mutation-review format
([templates/mutation-review.md](../../qa-methodology/templates/mutation-review.md))
and follow its mutation-guided hardening methodology
([references/test-automation.md](../../qa-methodology/references/test-automation.md)).
The evidence contract above still governs; the mutation-review record is the
format, not a relaxation of the thresholds.

A full mutation campaign, full-repository scan, or broad integration run is not
required by this subtype unless the changed surface or repository policy makes
it relevant. Record any boundary that was not exercised.

## Finality before remote CI

For repositories with expensive or serialized CI, finish the test design,
hermeticity review, targeted mutation, focused suite, lint, compilation, and
scope checks before the first push. The goal is one stable candidate and one
remote verification cycle.

After the candidate is frozen, use one bounded independent review or the
repository's required platform review. Do not start multiple long-running
reviewers by default. A timeout is inconclusive; it does not justify launching
another review against a mutable or superseded candidate.

A material review-driven change invalidates the relevant verification and
requires re-verification at the new exact head SHA. Formatting-only or
comment-only changes may follow the repository's non-material update rule.
