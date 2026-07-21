# OBEY Working Effectively with Legacy Code by Michael Feathers

## Purpose

This repository follows the discipline of **Working Effectively with Legacy Code** in the sense of Michael Feathers:
make risky existing code changeable by gaining understanding, creating seams, and establishing tests.

All code generation, edits, and reviews must optimize for:
- safe change in poorly understood code
- characterization before redesign
- breaking dependencies that block tests
- introducing seams
- reducing fear around modification
- incremental improvement instead of heroic rewrites

This file is a binding engineering policy: `MUST` is binding, `SHOULD` is a strong default, and `MUST NOT` is forbidden.

---

## Primary Directive

Legacy code is code that is expensive to change safely.
In practice, the default assumption is:

**If a part of the code lacks trustworthy tests, treat it as legacy code.**

When modifying legacy code:
1. understand what it does now
2. protect that behavior with tests where possible
3. find or create a seam
4. break dependencies that prevent observation or isolation
5. make the requested change
6. leave the area more testable than before

Do not begin with a rewrite unless explicitly required.

---

## Non-Negotiable Rules

1. **Do Not Rewrite by Reflex**
   - Prefer targeted extraction and improvement.
   - Rewrite only when explicitly requested or clearly safer than continued change.

2. **Characterize Before You Redesign**
   - When current behavior is uncertain, capture it.
   - Use characterization tests to document what the code does today, even if the behavior is ugly.

3. **Find or Create a Seam**
   - A seam is a place where behavior can be changed without editing the surrounding code directly.
   - Use seams to inject doubles, isolate dependencies, and observe behavior.

4. **Break Dependencies Deliberately**
   - Remove direct dependence on time, randomness, files, network, process environment, globals, frameworks, and static construction where they block testing.

5. **Leave the Code More Changeable**
   - Every change should ideally improve testability, visibility, or modularity.

---

## Default Workflow for Legacy Changes

1. Identify the exact area affected.
2. Determine whether trusted tests already protect the behavior.
3. If not, add characterization tests around current behavior where possible.
4. Identify the dependency that makes change difficult.
5. Introduce or exploit a seam.
6. Break the blocking dependency.
7. Make the functional change.
8. Refactor for clarity and keep the seam or new structure if it still pays for itself.

Short form: identify change points, find test points, break dependencies, write tests, make changes, then refactor.

Do not start by cleaning the whole module.

---

## Testing Strategy Rules

### Characterization Tests
1. Use characterization tests when you do not yet know whether the current behavior is intentional.
2. Test externally visible behavior first.
3. Prefer narrow tests around the slice you are about to modify.
4. Capture ugly behavior if real consumers rely on it.
5. Once behavior is protected, improve structure safely.
6. Mark suspicious current behavior for clarification instead of silently "fixing" it during characterization.
7. Use sensing variables or temporary probes only to confirm that a test reaches the intended path; remove them after use.

### New Behavior Tests
1. Add focused tests for the requested change.
2. Keep old behavior tests unless the behavior change is intentional.
3. Separate tests that describe legacy behavior from tests that describe the new requirement when useful.

### Testability Improvements
1. Make dependencies explicit.
2. Remove hard-coded collaborators.
3. Break apart mixed responsibilities that force expensive setup.
4. Reduce constructor side effects and static initialization side effects.

---

## Seam Rules

### What Counts as a Useful Seam
A useful seam is any boundary that allows substitution, observation, or interception.

Examples:
- constructor injection
- parameter injection
- extracted method
- wrapper around static call
- adapter around framework object
- factory indirection
- module boundary
- link seam, import seam, or preprocessing seam where the language/build system supports it
- subclass seam when forced by language constraints

### Required Behavior
1. Use the smallest seam that unlocks the change.
2. Prefer explicit seams over magical test hooks.
3. Prefer seams that remain useful after the current task.
4. Create seams near hard dependencies, not randomly in the code.
5. Separate sensing from separation: decide whether the seam observes behavior, substitutes a dependency, or both.
6. Use link and preprocessing seams carefully; they can unlock tests but do not usually improve design by themselves.

---

## Dependency Breaking Rules

When legacy code is hard to test, first look for these dependency types:

### Hidden Inputs
- current time
- random values
- environment variables
- thread-local state
- static singletons
- global configuration
- implicit current user or request

### Hard Outputs
- direct file writes
- direct network calls
- process exits
- direct database writes
- direct message publication
- logging used as control flow

### Construction Problems
- constructors that do real work
- new allocations of complex collaborators buried inside methods
- factory calls hidden deep in behavior
- object graphs built in the middle of logic

### Required Moves
- wrap static and global access
- inject clocks, random generators, external interfaces, and hard collaborators
- split construction from use
- extract side effects behind explicit collaborators
- narrow the code under test to a manageable slice

---

## Test Selection and Understanding Rules

1. Use effect sketches when the impact of a change is unclear.
2. Start from the change point and trace affected values, calls, fields, outputs, and collaborators outward.
3. Choose test points where effects can be observed with useful precision.
4. Use interception points when several planned changes can be protected by one broader test.
5. Use pinch points when many effects pass through one narrow point.
6. Treat broad tests at interception points as a first step toward narrower tests.
7. Use scratch refactoring to understand code, but discard it unless later backed by tests and review.
8. Sketch, mark, or group responsibilities in large code before moving behavior.
9. Do not check in exploratory restructuring that was only used to learn.

---

## Preferred Legacy Techniques

### Sprout Method
Use when new behavior can be added without deeply editing fragile code.

Rules (MUST unless marked SHOULD or MUST NOT):
- extract the new behavior into a new method
- keep the old code mostly untouched
- route to the new method from a small insertion point

### Sprout Class
Use when a new responsibility does not fit the old class or the old class is too risky to reshape first.

Rules (MUST unless marked SHOULD or MUST NOT):
- add a focused new collaborator
- delegate from the legacy class
- slowly move behavior over if later justified

### Wrap Method
Use when you need pre/post behavior around a risky method or a better way to observe effects.

### Wrap Class
Use when a class is too hard to test directly and behavior can be mediated through a new abstraction.

### Extract and Override Call
Use only when language constraints leave few better options.
Prefer composition once a cleaner route appears.

---

## Dependency-Breaking Technique Index

- USE Adapt Parameter when a method needs only a narrow view of a hard-to-create parameter.
- USE Break Out Method Object when a large method has local state that blocks extraction and testing.
- USE Definition Completion when missing definitions block tests in languages that allow completion in test code.
- USE Encapsulate Global References when globals or singletons prevent substitution.
- USE Expose Static Method when useful logic does not need instance state but is trapped behind instance setup.
- USE Extract and Override Factory Method when construction of a hard dependency must vary under test.
- USE Extract Implementer or Extract Interface when concrete dependencies make compilation or substitution hard.
- USE Introduce Instance Delegator when static behavior needs an instance seam.
- USE Parameterize Constructor or Parameterize Method when hidden collaborators should become explicit inputs.
- USE Primitivize Parameter only when the real type is too costly to bring into a harness and primitive data is enough for the new logic.
- USE Pull Up Feature or Push Down Dependency to move behavior or dependencies to a more testable level in a hierarchy.
- USE Replace Global Reference with Getter when direct global access needs a seam.
- USE Subclass and Override Method only when safer composition seams are not available.
- USE Supersede Instance Variable when a test needs to replace a hard dependency held in a field.
- USE Template Redefinition, Text Redefinition, link seams, or preprocessing seams only when language or build constraints make ordinary object seams impractical.

---

## Legacy Refactoring Heuristics

1. Work near the change point, not across the whole system.
2. Prefer one small dependency break over a broad redesign.
3. If a test requires too much setup, the design is telling you something useful.
4. If code is impossible to observe, expose outcomes through smaller units.
5. If code is impossible to invoke without full runtime setup, isolate the policy from the runtime.
6. If code depends on many details, separate policy from mechanism.
7. If the old code cannot be safely changed, insert new code beside it and redirect gradually.

---

## Handling Risky Areas

### Large Methods
- carve out pure computation first
- isolate side effects second
- add tests around extracted parts
- avoid editing many branches at once

### Static and Global Dependencies
- create a wrapper or façade
- move callers to the wrapper
- inject the wrapper where possible
- reduce direct calls incrementally

### Database-Heavy Code
- separate query and mapping concerns from policy
- test policy without a real database where possible
- keep integration tests for actual persistence behavior

### UI or Framework Code
- move decision logic out of handlers and callbacks
- test the moved logic independently
- keep adapters thin

### Constructors Doing Too Much
- stop doing I/O, network, or configuration lookup in constructors
- move setup into factories, builders, or composition roots
- keep constructed objects easy to instantiate under test

---

## Review Rules

When reviewing legacy-oriented changes, actively look for:
- no tests around modified logic
- structural and behavioral changes mixed together
- broad edits in poorly understood modules
- hidden global dependencies left untouched
- hard-coded collaborators
- direct static calls
- constructors with side effects
- business logic trapped in framework entry points
- places where a sprout method or sprout class lowers risk

---

## Forbidden Patterns

### Rewrite as the First Move
- replacing a subsystem before understanding current behavior
- rebuilding instead of gaining test leverage
- assuming old behavior is irrelevant because the code looks bad

### No-Safety Change
- changing legacy code with no tests or observation strategy
- large edits with no characterization
- relying on manual reasoning alone for risky behavior

### Hidden Dependency Expansion
- adding more globals, statics, ambient context, or framework reach-through in already hard-to-test code
- embedding new hard dependencies in the same style as the legacy code

### Cosmetic Refactoring Only
- renaming and formatting while leaving the real dependency knots intact
- “cleanup” that does not make the next change safer

---

## Code Generation Rules

When asked to modify legacy code, default to producing:
- characterization tests where needed
- small seams
- wrappers around hard dependencies
- explicit collaborators
- extracted pure logic
- minimal structural edits that unlock safe change

Preferred first moves:
- extract method
- wrap static call
- inject collaborator
- split construction from behavior
- move logic out of framework entry points
- introduce a focused new class for new behavior
- add a narrow characterization test

Preferred avoidance:
- huge dependency-breaking rewrites
- replacing old modules wholesale
- introducing large new architectures before basic seams exist
- mocking untestable structure instead of improving it

---

## Testing Rules

1. Prefer fast tests around the behavior you are changing.
2. Use characterization tests to lock current behavior before deeper edits.
3. Prefer tests at the highest level that still isolate the change safely.
4. Keep integration tests for real boundaries, but do not depend on them alone.
5. Once a seam exists, test through the seam.

---

## Review Checklist

Before finalizing any change, verify:
- Did we treat untested code as risky legacy code?
- Did we capture current behavior where it was unclear?
- Did we create or exploit a seam?
- Did we reduce at least one hard dependency?
- Is the changed area easier to test than before?
- Did we avoid a rewrite as the first move?
- Did we keep edits local to the requested change?
- Did we separate structural changes from behavior changes where practical?
- Did we leave the code more changeable than we found it?

If any answer is no, revise before shipping.

---

## Final Instruction

When uncertain, choose the smallest change that:
1. increases understanding
2. increases testability
3. breaks one hard dependency
4. preserves current behavior
5. makes the next change cheaper

Reject big rewrites and heroic cleanup when a seam and a test would do.
