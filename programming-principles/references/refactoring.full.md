# OBEY Refactoring by Martin Fowler

## Purpose

This repository follows the discipline of **Refactoring** in the sense of Martin Fowler:
improve the internal structure of code **without changing its observable behavior**.

All code generation, edits, and reviews must optimize for:
- small behavior-preserving changes
- clearer names and simpler control flow
- lower duplication
- smaller units of responsibility
- explicit movement from bad design toward good design
- steady design improvement as part of daily work

This file is a binding engineering policy: `MUST` is binding, `SHOULD` is a strong default, and `MUST NOT` is forbidden.

---

## Primary Directive

When modifying existing code, do **not** start by rewriting large areas.
Start by making the next safe structural improvement that makes the desired change easier.

Prefer:
1. establish a safety net
2. make a preparatory refactoring
3. make the functional change
4. refactor again if needed

Reject changes that bundle large functional changes with unrelated structural churn.

---

## What Counts as Refactoring

Refactoring here means:
- changing structure without changing external behavior
- applying small, composable transformations
- removing code smells before or during feature work
- making the next change easier
- improving readability, locality, and testability

Refactoring here does **not** mean:
- large rewrites
- unverified cleanup
- “modernization” with unclear behavioral impact
- renaming everything at once
- mixing architecture migration, feature work, and cleanup in one uncontrolled patch

---

## Non-Negotiable Rules

1. **Preserve Behavior**
   - Refactorings must preserve observable behavior.
   - If behavior must change, isolate the behavior change from structural refactoring.
   - Never disguise a feature change as a refactoring.

2. **Work in Small Steps**
   - Prefer many small safe edits over one large transformation.
   - Each step should be understandable and reversible.
   - If a patch feels too large to reason about locally, split it.

3. **Keep the System Running**
   - Do not leave code in a broken intermediate state unless explicitly asked for a draft.
   - Every refactoring sequence should maintain a runnable, buildable state where practical.

4. **Refactor Before and After Feature Work**
   - If code is hard to change, first reshape it.
   - After the feature lands, clean remaining structural debt introduced by the change.

5. **Use the Simplest Helpful Refactoring**
   - Do not introduce patterns or abstractions earlier than needed.
   - Prefer local simplification before large-scale abstraction.

---

## Safety Rules

### Tests and Verification
1. Create or identify a safety net before risky refactoring.
2. Prefer characterization tests when working on unclear existing behavior.
3. If tests are absent, make the smallest changes possible and improve testability first.
4. Keep refactoring and test updates aligned with preserved behavior.
5. Never delete a failing test just to complete a refactoring.

### Commit and Patch Discipline
1. Separate structural edits from behavior changes whenever practical.
2. Group related refactorings together.
3. Avoid giant mixed commits that rename, move, redesign, and change logic all at once.
4. Prefer reviewable sequences of transformations.

### Preparatory Refactoring
Before implementing a feature, ask:
- what makes this change awkward?
- what local structural change would make it straightforward?
- can I rename, extract, move, split, or inline first?

Do the preparatory refactoring before the feature change.

---

## Code Smell Policy

When modifying code, actively look for these smells.

### Duplicated Code
- Duplicate logic is a default target for elimination.
- Remove duplication by extracting shared behavior, not by introducing vague utility dumping grounds.
- Do not abstract coincidental similarity.

### Long Functions
- Split long functions when they mix responsibilities, levels of abstraction, or phases of work.
- Extract meaningful chunks with names that explain intent.
- Do not create micro-method noise with no explanatory value.

### Long Parameter Lists
- Replace repeated clumps with parameter objects or richer domain objects where appropriate.
- Remove boolean flags that switch behavior.
- Avoid signatures that require callers to memorize argument order.

### Global Data and Hidden Dependencies
- Reduce reliance on globals, singletons, and ambient context.
- Make dependencies explicit where possible.
- Refactor toward injection, parameters, or clear ownership.

### Divergent Change
- If one class changes for many different reasons, split responsibilities.
- Separate business logic, formatting, transport, persistence, and integration concerns.

### Shotgun Surgery
- If one change forces edits across many files, centralize the knowledge.
- Introduce a better boundary or clearer ownership.

### Feature Envy
- If a method mostly manipulates another object's data, move it or reshape the model.
- Put behavior near the data or concept it belongs to.

### Data Clumps and Primitive Obsession
- Replace repeated primitive bundles with meaningful types.
- Give recurring business concepts names and validation.

### Switch Statements and Conditionals
- Reduce repeated branching on type or mode when polymorphism, tables, strategies, or better data structures fit.
- Do not replace a single honest conditional with needless indirection.

### Temporary Fields and Weird Lifecycles
- Remove fields that exist only for unusual code paths when a separate object or clearer phase model is better.
- Prefer modeling states explicitly over half-initialized objects.

### Middle Man and Speculative Generality
- Remove forwarding layers that add no value.
- Delete abstractions created “just in case” if they are not earning their keep.

---

## Preferred Refactoring Moves

### Naming Refactorings
- Rename variables to reveal intent.
- Rename functions to describe behavior, not mechanism.
- Rename types and modules to align with problem-domain terminology.
- Rename before deeper refactoring when bad names block understanding.

### Extraction Refactorings
- Extract function when a block has a coherent purpose.
- Extract variable when an expression is hard to read.
- Extract class when one class has multiple reasons to change.
- Extract module when a file mixes unrelated concerns.

### Movement Refactorings
- Move function to the module or type where the data or concept lives.
- Move field when ownership is clearer elsewhere.
- Move statements to group related operations and reduce cognitive jumps.

### Simplification Refactorings
- Inline accidental abstractions.
- Collapse unnecessary layers.
- Replace nested conditionals with guard clauses where it improves clarity.
- Consolidate duplicate conditional fragments.

### Data Refactorings
- Encapsulate mutable state.
- Replace magic values with named constants or domain types.
- Introduce parameter objects for repeated argument groups.
- Replace raw collections with named abstractions when behavior accumulates around them.

---

## Refactoring Catalog Index

### Composing Methods
- USE Extract Method when a code fragment has a coherent purpose and a useful name.
- USE Inline Method when a method body is clearer than its indirection.
- USE Inline Temp when a temporary variable obscures a direct expression.
- USE Replace Temp with Query when a calculated value deserves a named query and can be reused safely.
- USE Introduce Explaining Variable when a complex expression needs named parts.
- USE Split Temporary Variable when one variable carries multiple meanings.
- USE Remove Assignments to Parameters when parameter mutation obscures input meaning.
- USE Replace Method with Method Object when local state prevents clean extraction.
- USE Substitute Algorithm when a clearer algorithm can replace a tangled one without changing behavior.

### Moving Features
- USE Move Method or Move Field when behavior or state belongs more naturally to another object.
- USE Extract Class when one class has more than one reason to change.
- USE Inline Class when a class no longer earns its existence.
- USE Hide Delegate when clients know too much about an object's collaborator.
- USE Remove Middle Man when a forwarding object no longer hides useful detail.
- USE Introduce Foreign Method only when you cannot edit the class that should own the behavior.
- USE Introduce Local Extension when repeated foreign methods need a local, coherent extension point.

### Organizing Data
- USE Self Encapsulate Field when direct field access blocks flexibility.
- USE Replace Data Value with Object when a primitive carries behavior, validation, or meaning.
- USE Change Value to Reference when identity and shared updates matter.
- USE Change Reference to Value when value semantics simplify ownership.
- USE Replace Array with Object when positions in a collection have names or rules.
- USE Duplicate Observed Data only when UI or framework synchronization forces it; keep synchronization explicit.
- USE Change Unidirectional Association to Bidirectional only when traversal is needed both ways.
- USE Change Bidirectional Association to Unidirectional when one direction is unnecessary coupling.
- USE Encapsulate Collection when external mutation can bypass invariants.
- USE Replace Record with Data Class when raw records need named access and behavior can grow safely.
- USE Replace Type Code with Class, Subclasses, or State/Strategy according to whether behavior varies by type.
- USE Replace Subclass with Fields when subclass variation is only data.

### Simplifying Calls and Conditionals
- USE Decompose Conditional, Consolidate Conditional Expression, and Consolidate Duplicate Conditional Fragments to make branching intent visible.
- USE Remove Control Flag when loop or conditional state can be expressed directly.
- USE Replace Nested Conditional with Guard Clauses when it clarifies the normal path.
- USE Replace Conditional with Polymorphism only when repeated type-based behavior justifies it.
- USE Introduce Null Object when repeated null behavior has a stable meaning.
- USE Introduce Assertion when an assumption should be explicit during development.
- USE Rename Method, Add Parameter, Remove Parameter, Parameterize Method, or Replace Parameter with Explicit Methods to make caller intent clearer.
- USE Preserve Whole Object when callers pass several values from the same object.
- USE Replace Parameter with Method when the receiver can obtain the value itself without hidden coupling.
- USE Remove Setting Method when post-construction mutation should not be allowed.
- USE Hide Method when public surface exposes unnecessary operations.
- USE Replace Constructor with Factory Method when creation intent or subtype selection needs a name.
- USE Encapsulate Downcast when callers should not own cast details.
- USE Replace Error Code with Exception or Replace Exception with Test according to the expected failure model.

### Generalization and Big Refactorings
- USE Pull Up Field, Pull Up Method, or Pull Up Constructor Body when duplicated superclass behavior is real.
- USE Push Down Method or Push Down Field when only some subclasses need the feature.
- USE Extract Subclass, Extract Superclass, or Extract Interface only when callers or variation points justify them.
- USE Collapse Hierarchy when inheritance no longer adds meaning.
- USE Form Template Method when similar algorithms differ in controlled steps.
- USE Replace Inheritance with Delegation when inheritance couples unrelated responsibilities.
- USE Replace Delegation with Inheritance only when the subtype relationship is genuine and stable.
- USE Tease Apart Inheritance when one hierarchy mixes multiple variation axes.
- USE Convert Procedural Design to Objects when data and behavior need clearer ownership.
- USE Separate Domain from Presentation when UI and policy are tangled.
- USE Extract Hierarchy when several types share behavior with meaningful variation.

---

## Function-Level Rules

1. One function should usually perform one coherent task.
2. Keep abstraction level consistent inside a function.
3. Remove hidden side effects unless the function's purpose is to cause them.
4. Prefer guard clauses over deeply nested conditionals when that clarifies the happy path.
5. Split phases like parsing, validation, computation, and I/O when they are mixed together.
6. Keep variable scope tight.
7. Delete dead code rather than comment it out.

---

## Class and Module Rules

1. A class or module should have a narrow reason to change.
2. Separate policy from presentation, I/O, persistence, and framework details.
3. Prefer composition of small focused units over god objects.
4. Delete or inline abstractions that no longer pay for themselves.
5. Do not create `utils`, `helpers`, or `common` modules as a default response to duplication.
6. Organize modules around concepts and behavior, not leftover convenience.

---

## Rules for Working with Conditionals

1. Replace repeated branching on type or status with stronger modeling when useful.
2. Use lookup tables for stable mapping logic.
3. Replace nested if/else pyramids with guard clauses, extracted predicates, or strategies when that reduces branching complexity.
4. Keep explicit conditionals when they are simple and honest.
5. Never introduce polymorphism merely to avoid a small local conditional.

---

## Data and Mutation Rules

1. Encapsulate mutation.
2. Narrow write access to the smallest useful surface.
3. Replace ad hoc mutations with intention-revealing operations.
4. Remove duplicated update logic by centralizing state transitions.
5. Prefer immutable intermediate values when that simplifies reasoning.

---

## Error Handling Rules

1. Refactor error handling to make the main path visible.
2. Keep cleanup, validation, and recovery logic from drowning core behavior.
3. Standardize similar error paths when they duplicate structure.
4. Preserve existing error semantics unless intentionally changing behavior.

---

## Review Rules

When reviewing or generating changes, actively look for:
- duplicated logic
- long functions
- long classes
- tangled control flow
- mixed abstraction levels
- feature envy
- shotgun surgery
- divergent change
- pass-through layers
- speculative generality
- hidden side effects
- global state reliance
- code that requires too much context to change safely

---

## Forbidden Patterns

Do not generate or keep these patterns unless explicitly required and justified.

### Big-Bang Rewrite
- replacing a working subsystem wholesale to “clean it up”
- rewriting before understanding current behavior
- changing structure and behavior in one giant move

### Mixed-Intent Patches
- feature work mixed with huge unrelated renames
- behavior changes hidden inside cleanup
- code motion that makes review impossible

### Abstracting Too Early
- introducing interfaces or strategy hierarchies before a second real need appears
- creating common libraries for one caller
- replacing understandable duplication with unclear shared code

### Refactoring Theater
- renaming things while deeper design problems remain untouched
- introducing patterns instead of removing complexity
- creating more files, layers, or wrappers without improving changeability

### Untested Structural Surgery
- large refactors without any safety net
- “cleanup” on fragile code with no verification strategy
- assuming behavior is obvious when it is not

---

## Code Generation Rules

When asked to modify existing code, use this default order:
1. understand current behavior
2. identify the friction for the requested change
3. add or improve the safety net if needed
4. perform preparatory refactoring
5. implement the behavioral change
6. perform follow-up cleanup
7. stop when the design is clearly better

Preferred first moves:
- rename badly named things
- extract coherent functions
- isolate side effects
- split mixed responsibilities
- move behavior closer to the owning concept
- remove duplication
- simplify conditionals

Preferred avoidance:
- unnecessary framework migrations
- gratuitous API redesign
- large hierarchy introduction
- replacing all old code with new code because the old code is ugly

---

## Testing Rules

1. Add characterization tests before risky edits when behavior is unclear.
2. Keep tests focused on externally visible behavior.
3. Update tests only when behavior intentionally changes.
4. Do not couple tests to private implementation details more than necessary.
5. Refactor tests too when they become noisy or duplicative.
6. Keep test data expressive and minimal.

---

## Stopping Rules

Stop refactoring when:
- the requested change is easy to implement
- the main smells blocking change are removed
- further cleanup would become speculative
- the next abstraction is not yet justified
- readability and local changeability are clearly improved

---

## Review Checklist

Before finalizing any change, verify:
- Did we preserve observable behavior during refactoring?
- Did we separate structural change from behavior change where practical?
- Did we remove at least one real source of friction?
- Is the code easier to read than before?
- Is the code easier to test or change than before?
- Did we reduce duplication or accidental complexity?
- Did we avoid speculative abstraction?
- Did we avoid a giant mixed patch?
- Did names improve?
- Did control flow become simpler?
- Did responsibilities become clearer?

If any answer is no, revise before shipping.

---

## Final Instruction

When uncertain, choose the next **small, behavior-preserving transformation**
that makes the requested change easier and the code easier to understand.
Reject approaches that gamble on large rewrites or mix too many intentions at once.
