# OBEY Working Effectively with Legacy Code by Michael Feathers

## When to use

Use when changing code that is expensive to change safely because behavior is unclear, tests are weak or missing, dependencies are hidden, or runtime/framework setup blocks local feedback.

## Primary bias to correct

Gain control before improving design. Understand current behavior, protect what must stay, create the smallest useful seam, break the dependency that blocks feedback, make the requested change, then leave the area more testable.

## Decision rules

- Treat any area without trustworthy tests as legacy code. Do not start with rewrite.
- Before editing, state the requested behavior change and the current behavior that must remain.
- Follow the legacy loop: identify change point, check protection, add characterization, find a seam, break the blocking dependency, change behavior, refactor locally.
- Prefer fast, focused tests around the slice being changed.
- Choose test points by tracing effects outward from the change point.
- Use the smallest seam that allows substitution, observation, or interception.
- Break dependencies deliberately: expose hidden inputs, hard outputs, hard construction, globals, statics, ambient context.
- Keep behavior changes, structural refactorings, and cleanup separate.
- Use sprout method, sprout class, wrap method, wrap class when direct edits are risky.
- For hard-to-test methods, split construction from use, extract side effects, carve pure computation first.
- Leave the touched area easier to understand, test, or change.

## Trigger rules

- When behavior is uncertain, add characterization or another explicit observation path before changing semantics.
- When tests require too much setup, break the first real barrier: constructor work, hidden allocation, global state, static construction.
- When time, randomness, environment, files, network, or process exits block repeatable tests, wrap that boundary.
- When a large method defeats local reasoning, extract pure computation first.
- When rewrite feels tempting, choose the smallest sprout, wrap, seam, or refactoring step.

## Final checklist

- Untested area treated as legacy risk?
- Behavior delta and behavior-to-preserve stated?
- Smallest useful seam chosen?
- Blocking dependency reduced?
- Temporary seam has a cleanup path?
- Touched area more changeable than before?
