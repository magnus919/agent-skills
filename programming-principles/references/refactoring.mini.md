# OBEY Refactoring by Martin Fowler

## When to use

Use when changing existing code, preparing a feature or bug fix, reviewing cleanup, or reducing structural friction without intending to change observable behavior.

## Primary bias to correct

Refactoring is behavior-preserving design work in small steps. Do not turn cleanup into a rewrite, a hidden feature change, or speculative architecture.

## Decision rules

- Preserve observable behavior during refactoring. Isolate behavior changes from structural changes.
- Work in small, reversible, buildable, testable, reviewable steps. Split a patch when it is too large to reason about locally.
- Establish or identify a safety net before risky refactoring. Use characterization tests for unclear behavior.
- Use preparatory and follow-up refactoring around feature work: reshape blocking structure first, make the behavior change, then clean debt.
- Refactor the current blocking smell, not every smell in sight: duplication, long functions, long parameter lists, globals, divergent change, shotgun surgery, feature envy, primitive obsession, repeated conditionals, temporary fields, middle men, speculative generality.
- Prefer the simplest named move: rename, extract, inline, move, introduce parameter object, encapsulate, decompose conditionals, use guard clauses, substitute algorithm.
- Make names and functions reveal intent. Rename before deeper work when bad names block understanding.
- Put behavior and state with the concept that owns them. Split classes with multiple reasons to change.
- Simplify conditionals honestly. Use polymorphism, state, strategy, or tables only when variation is real and repeated.
- Keep patch intent reviewable. Group related refactorings. Avoid giant mixed patches.
- Stop when the requested change is easy, the blocking smell is gone, and the next cleanup would be speculative.

## Trigger rules

- When adding behavior, first ask what structural friction blocks the change.
- When fixing a bug in unclear code, characterize the current failure first.
- When the same edit appears a third time, remove duplication.
- When a function mixes responsibilities, rename, extract, or split.
- When one change forces edits across many files, centralize the knowledge.
- When tempted to rewrite, choose the next small behavior-preserving transformation.

## Final checklist

- Observable behavior preserved?
- Structural change, behavior change, and test updates separated?
- At least one real source of friction removed?
- Patch still reviewable and runnable?
