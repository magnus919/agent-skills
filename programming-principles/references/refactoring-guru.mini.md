# OBEY Refactoring.Guru

## When to use

Use when changing existing code where code smells, refactoring technique choice, behavior preservation, and cleanup scope control matter.

## Primary bias to correct

Refactoring is not general cleanup or pattern application. It is a small, smell-driven, behavior-preserving treatment with verification and a stop condition.

## Decision rules

- Separate refactoring from feature work and bug fixes.
- Diagnose the smell before choosing a technique: symptom, maintenance cost, expected end state, verification path.
- Prefer the smallest treatment that directly reduces the diagnosed smell.
- Keep code runnable and understandable through small named transformations.
- Stop when the named smell is gone or materially reduced.
- Use the Rule of Three: tolerate uncertain duplication early, refactor the third similar occurrence.
- For bloaters, prefer extraction and responsibility splits before creating method objects or subclasses.
- For switch/type-code smells, isolate the decision first; use polymorphism only when variation is stable.
- For change preventers, move behavior and data toward the owner of the changing concept.
- For dispensables, delete or inline unused structure. Check public/generated/reflected uses first.
- For couplers, reduce navigation and private knowledge. Keep delegating layers only when they hide volatile structure.
- Encapsulation is not finished by adding getters and setters. Move behavior inward.
- Avoid speculative abstractions: do not create wrappers, interfaces, or hierarchy variants without a real concept.

## Trigger rules

- When a method needs comments or scrolling to understand, try Extract Method.
- When a class has multiple reasons to change, use Extract Class.
- When primitives carry meaning, model the concept if it adds naming, validation, or behavior.
- When a parameter list grows, introduce a parameter object only for a real recurring concept.
- When a class mostly forwards, remove the middle man unless it protects boundary policy.
- When null checks dominate, introduce a null object only if absence obeys the same interface.

## Final checklist

- Is this clearly refactoring, feature work, or bug fixing?
- Was the smallest suitable treatment used?
- Did the named smell become materially better?
