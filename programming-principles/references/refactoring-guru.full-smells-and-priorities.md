# Refactoring.Guru: Smells and Priorities

> Part of the Refactoring.Guru full reference — smell catalog, detection process, and the smell-to-treatment priority map. Index: [refactoring-guru.full.md](refactoring-guru.full.md)


## Source and Scope

This rule set is derived from the public Refactoring.Guru refactoring material:

- <https://refactoring.guru/refactoring>
- <https://refactoring.guru/refactoring/what-is-refactoring>
- <https://refactoring.guru/refactoring/technical-debt>
- <https://refactoring.guru/refactoring/when>
- <https://refactoring.guru/refactoring/how-to>
- <https://refactoring.guru/refactoring/smells>
- <https://refactoring.guru/refactoring/catalog>
- <https://refactoring.guru/refactoring/techniques>

The crawl intentionally excluded example code, images, premium course pages, design pattern pages, legal pages, and non-refactoring navigation.

This file is not a copy of the site. It is an operational rule set for AI coding agents, paraphrased from the refactoring process, code-smell catalog, and refactoring technique catalog.

This file is binding engineering policy: `MUST` is binding, `SHOULD` is a strong default, and `MUST NOT` is forbidden.

---

## Purpose

Refactoring is the controlled process of improving code structure without adding new functionality.

Use these rules to:

- identify code smells before and during a change
- decide whether refactoring is justified now
- select the smallest technique that addresses the smell
- keep each transformation behavior-preserving
- leave code simpler, clearer, and cheaper to change

Clean code in this rule set means code that:

- is obvious to other programmers
- avoids duplicated knowledge and duplicated control flow
- has a minimal number of moving parts
- passes the relevant tests
- is easier and cheaper to maintain than the code it replaced

---

## Primary Directive

When changing existing code, first diagnose the smell that makes the change hard.

Then choose the smallest refactoring that removes or isolates that smell while preserving behavior.

Never treat refactoring as a vague cleanup pass. Every refactoring MUST have:

- a specific smell, friction, or maintenance cost it addresses
- a bounded transformation
- a verification path
- no hidden feature change

---

## Refactoring Process

### Keep Refactoring Separate

- MUST NOT mix direct feature development and refactoring in one indistinguishable edit.
- SHOULD separate refactoring and behavior changes at least by commit, patch section, or clearly labeled step.
- MUST preserve existing behavior during refactoring.
- MUST call out any behavior change as feature work or bug fixing, not as refactoring.
- SHOULD refactor before feature work when dirty code blocks understanding or makes the feature awkward.
- SHOULD refactor after feature work when the feature leaves new duplication, awkward names, or unnecessary structure.

### Work in Small Steps

- MUST apply refactoring as a sequence of small changes.
- MUST keep the program in working order after each meaningful step when practical.
- SHOULD run relevant tests after each risky structural change.
- MUST stop and reduce scope when a refactoring becomes too large to reason about locally.
- SHOULD prefer several named transformations over one broad rewrite.
- MUST NOT use refactoring as cover for uncontrolled redesign.

### Verify Continuously

- MUST identify the relevant test or check before risky refactoring.
- MUST run all relevant existing tests after refactoring.
- If tests fail, MUST decide whether the refactoring changed behavior or the tests were too coupled to implementation details.
- MUST fix refactoring mistakes before continuing.
- SHOULD replace or lift brittle low-level tests when they block behavior-preserving structure changes.
- MUST NOT delete failing tests to make a refactoring appear successful.

### Keep the Result Cleaner

- Refactoring is successful only if the code becomes cleaner in the area touched.
- MUST NOT perform a refactoring that leaves the code just as unclear, duplicated, or bloated.
- SHOULD pause and re-diagnose when a chain of small edits is not improving clarity.
- SHOULD consider a planned rewrite only when the code is extremely sloppy, tests exist or are added first, and enough time is explicitly allocated.

---

## When to Refactor

### Rule of Three

- MAY implement a first occurrence directly.
- SHOULD tolerate a second similar occurrence when the abstraction is still uncertain.
- MUST consider refactoring on the third similar occurrence.
- MUST NOT abstract coincidental similarity before the repeated responsibility is clear.

### While Adding a Feature

- SHOULD refactor first when existing code is too dirty to understand the change safely.
- SHOULD reshape the local structure so the feature becomes straightforward.
- MUST keep preparatory refactoring separate from the feature behavior.
- SHOULD use the feature request as an opportunity to pay down the specific debt that blocks it.

### While Fixing a Bug

- SHOULD inspect the area around the bug for hidden complexity, duplication, and unclear ownership.
- SHOULD clean the structure that allowed the bug to hide when the cleanup is small and local.
- MUST preserve the observed bug fix as a separate behavior change from the supporting refactor.

### During Code Review

- SHOULD use review as the last chance to catch smells before code becomes public.
- SHOULD fix simple smells immediately when review context and ownership allow it.
- SHOULD estimate and isolate larger smells instead of smuggling them into the reviewed change.
- SHOULD collaborate with the author when a smell needs judgment about intent.

---

## Technical Debt Rules

- Treat technical debt as a cost that compounds by slowing future development.
- MUST NOT justify patches, kludges, missing tests, or unclear structure as harmless if they make later changes slower or riskier.
- SHOULD expose the debt source when it comes from business pressure, missing tests, weak modularity, delayed refactoring, poor documentation, isolated branches, or inconsistent standards.
- MUST prioritize debt that affects current change speed, correctness, or team understanding.
- SHOULD reduce debt incrementally through ordinary feature and bug work.
- MUST NOT delay all refactoring until a future cleanup project unless the current change cannot safely absorb it.

---

## Smell Detection Process

When touching existing code, scan in this order:

1. Bloaters: code grew too large to understand or change.
2. Object-orientation abusers: inheritance, type codes, or conditionals are misusing the object model.
3. Change preventers: one change forces edits in too many places, or one class changes for unrelated reasons.
4. Dispensables: code exists without earning its maintenance cost.
5. Couplers: classes know too much about each other or delegate so much that responsibility disappears.
6. Library gaps: external classes force duplicated workarounds.

For each smell:

- identify the symptom
- identify why it makes change harder
- choose the matching treatment
- check whether the suggested treatment creates worse coupling or unnecessary abstraction
- apply the smallest useful refactoring

### Diagnose, Treat, Verify, Stop

Use this workflow for every non-trivial refactoring:

1. Diagnose the smell:
   - name the visible symptom
   - name the maintenance cost it creates
   - identify whether the smell is local, repeated, or architectural
   - check whether the smell is real or only a style preference
2. Choose treatment:
   - pick the catalog technique that directly addresses the smell
   - prefer a smaller technique before a larger structural move
   - note the expected cleaner end state before editing
   - reject a treatment if its own tradeoff is worse than the smell
3. Verify behavior:
   - identify existing tests, characterization checks, type checks, or manual checks before moving code
   - run the relevant check after each risky step
   - if behavior changes, stop treating the change as refactoring and isolate the behavior change
4. Decide the stop condition:
   - stop when the named smell is gone or materially reduced
   - stop when the next improvement requires a different smell diagnosis
   - stop when the refactoring would cross ownership, public API, or feature scope without explicit approval
   - stop when the code is cleaner enough for the requested change and further cleanup is speculative

MUST NOT continue refactoring just because another smell was discovered. Record the next smell separately unless it blocks the current change.

### Smell Exception Rules

- MUST NOT treat every smell mechanically; confirm that the treatment improves clarity for this codebase.
- MAY leave a simple conditional alone when replacing it with polymorphism would obscure a direct rule.
- MAY leave duplicate fragments separate when the shared abstraction would be less obvious than the duplication.
- MAY keep comments that explain why, external constraints, or algorithms that have already resisted simpler structure.
- MAY keep a small class when it communicates a real extension point or boundary.
- MAY keep behavior separate from data when the design intentionally supports interchangeable behavior.
- MAY keep long parameter lists temporarily when removing parameters would create stronger unwanted dependencies.
- MUST document or report intentional non-treatment when a visible smell is left in touched code.

---

## Bloaters

### Long Method

- Trigger: a method is long enough that understanding it requires scrolling, comments, or mental bookkeeping.
- MUST ask questions once a method is noticeably long; ten lines is a warning threshold, not a mechanical limit.
- SHOULD extract a method when a code fragment needs a comment to explain what it does.
- SHOULD extract loops, conditional branches, and coherent phases into named methods.
- SHOULD use `Replace Temp with Query`, `Introduce Parameter Object`, or `Preserve Whole Object` when locals block extraction.
- SHOULD use `Replace Method with Method Object` when extraction is blocked by many locals or a tightly coupled algorithm.
- MUST NOT avoid extraction only because a method call might have negligible performance cost.

### Large Class

- Trigger: a class has too many fields, methods, responsibilities, or lines to understand as one concept.
- SHOULD split a class that wears multiple functional hats.
- SHOULD use `Extract Class` when a subset of fields and methods forms a separate responsibility.
- SHOULD use `Extract Subclass` when rare or variant behavior bloats the main class.
- SHOULD use `Extract Interface` when clients need only a stable subset of behavior.
- SHOULD move GUI-held domain data into domain classes when interface objects are carrying business state.
- MUST NOT split a class only because it is large if the extracted part has no stable responsibility.

### Primitive Obsession

- Trigger: primitives, strings, numbers, constants, or arrays are standing in for meaningful concepts.
- SHOULD replace repeated primitive values with small objects that carry meaning and validation.
- SHOULD use `Replace Data Value with Object` for a single primitive that has domain behavior or constraints.
- SHOULD use `Replace Type Code with Class`, subclasses, or state/strategy when codes control behavior.
- SHOULD use `Replace Array with Object` when array positions have named meaning.
- SHOULD use `Replace Magic Number with Symbolic Constant` when a literal value carries domain meaning.
- MUST NOT wrap primitives in new types when the wrapper adds no name, validation, behavior, or error prevention.

### Long Parameter List

- Trigger: a method needs more than three or four parameters, or callers must memorize argument order.
- SHOULD replace derived arguments with `Replace Parameter with Method Call`.
- SHOULD pass an existing object with `Preserve Whole Object` when the callee needs several values from it.
- SHOULD introduce a parameter object when parameters form a recurring concept.
- MUST NOT remove parameters if doing so creates an unwanted dependency between classes.

### Data Clumps

- Trigger: the same group of values appears in multiple fields, signatures, or calls.
- SHOULD test whether the values still make sense if one member is removed; if not, model the group.
- SHOULD use `Extract Class` for repeated field groups.
- SHOULD use `Introduce Parameter Object` for repeated parameter groups.
- SHOULD pass the whole object when methods keep receiving pieces of the same concept.
- SHOULD move behavior that uses the clump onto the new object when appropriate.
- MUST NOT pass a whole object if that creates an undesirable dependency on a much larger collaborator.

---

## Object-Orientation Abusers

### Switch Statements

- Trigger: complex `switch` or repeated `if` chains branch on type, mode, or category.
- SHOULD suspect missing polymorphism when adding a new case requires edits in multiple switch sites.
- SHOULD extract and move switch logic to the class that owns the decision.
- SHOULD replace type-code branching with subclasses or state/strategy when behavior varies by type.
- SHOULD replace conditional dispatch with polymorphism once the structure is explicit.
- SHOULD use explicit methods instead of polymorphism when there are only a few simple parameter variations.
- SHOULD use a null object when a branch exists only for null handling.
- MUST NOT replace a simple honest conditional or factory selection with unnecessary polymorphism.

### Temporary Field

- Trigger: fields are meaningful only in special circumstances and are empty or invalid otherwise.
- SHOULD extract the algorithm and its temporary state into a separate class.
- SHOULD use a method object when a method needs temporary fields only to carry many intermediate values.
- SHOULD use a null object when conditional checks around absent state dominate the code.
- MUST NOT normalize half-initialized objects as ordinary design.

### Refused Bequest

- Trigger: a subclass inherits behavior or data that it does not use or cannot honor.
- SHOULD push unused methods or fields down to the subclasses that actually need them.
- SHOULD replace inheritance with delegation when the subclass relationship is misleading.
- SHOULD preserve inheritance only when the unused inherited behavior is harmless and does not confuse clients.

### Alternative Classes with Different Interfaces

- Trigger: two classes do the same job but expose different method names or signatures.
- SHOULD align names with `Rename Method`.
- SHOULD align signatures with `Move Method`, `Add Parameter`, or `Parameterize Method`.
- SHOULD extract a superclass when duplicated behavior is only partial but real.
- SHOULD delete one alternative after the common interface and behavior make it redundant.
- MAY leave alternatives separate when they live in separate external libraries and unification is impractical.

---

## Change Preventers

### Divergent Change

- Trigger: one class must change for many unrelated reasons.
- SHOULD split unrelated responsibilities with `Extract Class`.
- SHOULD separate product behavior, display behavior, persistence behavior, and integration behavior when they evolve independently.
- SHOULD use superclass or subclass extraction only when the shared behavior is genuine.

### Shotgun Surgery

- Trigger: one conceptual change forces many small edits across many classes.
- SHOULD centralize the scattered responsibility.
- SHOULD move methods and fields to the owner of the changing concept.
- SHOULD inline or extract classes to put related changes in one place.
- MUST NOT leave knowledge scattered after the pattern is visible.

### Parallel Inheritance Hierarchies

- Trigger: adding a subclass in one hierarchy requires adding a matching subclass in another.
- SHOULD merge the duplicated hierarchy pressure by moving methods and fields so one hierarchy owns the variation.
- SHOULD collapse or replace parallel structures when they exist only to mirror each other.
- MUST avoid creating new parallel hierarchies during extension work.

---

## Dispensables

### Comments

- Trigger: comments explain what unclear code does rather than why it exists.
- SHOULD replace explanatory comments with better names, extracted variables, extracted methods, or assertions.
- SHOULD keep comments for rationale, non-obvious constraints, external contracts, and algorithms that resisted simplification.
- MUST NOT use comments as deodorant for confusing structure.

### Duplicate Code

- Trigger: two fragments are identical or perform the same job under slightly different wording.
- SHOULD use `Extract Method` for duplicates in the same class.
- SHOULD use pull-up or extract-superclass techniques for duplicates across sibling classes.
- SHOULD use `Extract Class` when duplicate behavior belongs to a separate concept.
- SHOULD remove accidental duplication even when the fragments are not textually identical.
- MAY leave duplication when merging would make the code less intuitive or create the wrong abstraction.
- MUST NOT merge duplicates that are only coincidentally similar and likely to diverge for different reasons.

### Lazy Class

- Trigger: a class no longer does enough to justify its maintenance cost.
- SHOULD inline a near-useless class.
- SHOULD collapse a hierarchy when subclasses or superclasses no longer carry distinct behavior.
- MAY keep a small class when it clearly communicates an intended extension point and earns that clarity.

### Data Class

- Trigger: a class only stores data and exposes crude getters or setters while clients perform the behavior.
- SHOULD encapsulate public fields.
- SHOULD encapsulate collections rather than exposing mutable collection internals.
- SHOULD move client behavior onto the data class when the behavior operates on that data.
- SHOULD remove broad setters or accessors after meaningful behavior exists.

### Dead Code

- Trigger: unused variables, parameters, fields, methods, classes, files, or unreachable branches.
- SHOULD use IDE and compiler feedback to find dead code.
- MUST delete unused code and files when no compatibility reason remains.
- SHOULD inline or collapse empty classes or hierarchies before deletion when needed.
- SHOULD remove unused parameters from methods.
- MUST NOT delete public, serialized, reflected, or plugin-facing code without checking external compatibility.

### Speculative Generality

- Trigger: abstractions, parameters, hooks, fields, or classes exist only for imagined future needs.
- SHOULD inline unused abstractions.
- SHOULD remove unused parameters, methods, fields, and classes.
- SHOULD collapse unused hierarchies.
- MAY keep framework extension points only when real users need them.
- MUST check tests before deleting a member that exists only for test access.

---

## Couplers

### Feature Envy

- Trigger: a method uses another object's data more than its own.
- SHOULD move behavior to the class that owns the data it mainly uses.
- SHOULD extract the envying fragment before moving it when only part of a method envies another object.
- SHOULD split a method across owners when it uses several data sources for separable purposes.
- MAY keep behavior separate when the separation is intentional, such as interchangeable strategy-like behavior.

### Inappropriate Intimacy

- Trigger: classes rely on each other's internals or spend too much time together.
- SHOULD move methods and fields to reduce private knowledge crossing boundaries.
- SHOULD extract or hide delegates to reduce unnecessary knowledge of collaborator structure.
- SHOULD replace inheritance with delegation when intimacy comes from an overexposed subclass relationship.

### Message Chains

- Trigger: client code navigates through a chain of objects to reach data or behavior.
- SHOULD hide the delegate behind the object the client already knows.
- SHOULD move behavior closer to the data instead of making clients navigate structure.
- MUST NOT expose object graph topology as a routine calling convention.

### Middle Man

- Trigger: a class mostly forwards calls and adds no policy, coordination, or protection.
- SHOULD remove the middle man when direct collaboration is clearer.
- SHOULD inline a class that exists only as pass-through.
- SHOULD keep a delegating layer when it protects a boundary, hides volatile structure, or provides useful policy.

### Incomplete Library Class

- Trigger: an external library class lacks methods you need and cannot be changed directly.
- SHOULD use a foreign method for one or two missing operations.
- SHOULD use a local extension when the missing behavior is substantial.
- MUST NOT scatter repeated library workarounds throughout the codebase.
- MUST NOT fork or wrap a library broadly when one narrow foreign method would solve the gap.

---

## Technique Selection Rules

### Composing Methods

- Use `Extract Method` when a fragment has a coherent purpose or needs explanation.
- Use `Inline Method` when a method body is clearer than its name or the indirection adds no value.
- Use `Extract Variable` when an expression needs a name to reveal intent.
- Use `Inline Temp` when a temporary variable obscures a simple expression or blocks another refactoring.
- Use `Replace Temp with Query` when a temporary value should be recomputable by a named query.
- Use `Split Temporary Variable` when one variable is assigned different meanings over time.
- Use `Remove Assignments to Parameters` when a method mutates parameters as local scratch space.
- Use `Replace Method with Method Object` when a method is too entangled with locals to extract cleanly.
- Use `Substitute Algorithm` when a clearer algorithm can replace a confusing one after behavior is protected.

### Moving Features Between Objects

- Use `Move Method` when a method uses another class more than its current class.
- Use `Move Field` when a field is used more by another class or concept.
- Use `Extract Class` when one class contains separable responsibilities.
- Use `Inline Class` when a class no longer earns its existence.
- Use `Hide Delegate` when clients know too much about an object's collaborators.
- Use `Remove Middle Man` when delegation no longer hides useful complexity.
- Use `Introduce Foreign Method` when a library class needs a small missing operation.
- Use `Introduce Local Extension` when a library class needs substantial local behavior.

### Organizing Data

- Use `Self Encapsulate Field` when direct field access prevents adding behavior around access.
- Use `Replace Data Value with Object` when a primitive needs meaning, validation, or behavior.
- Use `Change Value to Reference` when many equal objects should represent one mutable real-world entity.
- Use `Change Reference to Value` when lifecycle management is not worth it and immutable value semantics fit.
- Use `Replace Array with Object` when array positions have domain meaning.
- Use `Duplicate Observed Data` when GUI-held domain data should be split into domain data with synchronization.
- Use `Change Unidirectional Association to Bidirectional` only when both sides genuinely need navigation.
- Use `Change Bidirectional Association to Unidirectional` when one side does not use the other.
- Use `Replace Magic Number with Symbolic Constant` when a literal carries meaning.
- Use `Encapsulate Field` when a public field exposes representation.
- Use `Encapsulate Collection` when callers can mutate internal collections directly.
- Use `Replace Type Code with Class` when a code needs type safety or behavior.
- Use `Replace Type Code with Subclasses` when type code drives stable variant behavior.
- Use `Replace Type Code with State/Strategy` when runtime state or algorithm variation changes behavior.
- Use `Replace Subclass with Fields` when subclasses differ only by constant data.

### Simplifying Conditional Expressions

- Use `Decompose Conditional` when conditions or branches are hard to read.
- Use `Consolidate Conditional Expression` when multiple checks lead to one action.
- Use `Consolidate Duplicate Conditional Fragments` when all branches contain the same code.
- Use `Remove Control Flag` when a variable is used only to break or direct control flow.
- Use `Replace Nested Conditional with Guard Clauses` when special cases obscure the normal path.
- Use `Replace Conditional with Polymorphism` when conditional behavior varies by type.
- Use `Introduce Null Object` when null checks dominate behavior.
- Use `Introduce Assertion` when hidden assumptions about state should be explicit.

### Simplifying Method Calls

- Use `Rename Method` when a method name does not reveal behavior.
- Use `Add Parameter` only when a method truly needs additional data and a field would be worse.
- Use `Remove Parameter` when a parameter is unused or no longer affects behavior.
- Use `Separate Query from Modifier` when a method both returns information and changes state.
- Use `Parameterize Method` when several similar methods differ only by values.
- Use `Replace Parameter with Explicit Methods` when a parameter selects distinct behavior.
- Use `Preserve Whole Object` when callers pass several values from one object.
- Use `Replace Parameter with Method Call` when a parameter can be obtained by the callee.
- Use `Introduce Parameter Object` when parameters repeatedly travel together.
- Use `Remove Setting Method` when objects should not be changed after creation or after initialization.
- Use `Hide Method` when public methods are not part of the intended interface.
- Use `Replace Constructor with Factory Method` when construction needs naming, selection, caching, or controlled creation.
- Use `Replace Error Code with Exception` when callers should not manually inspect status codes for exceptional failure.
- Use `Replace Exception with Test` when callers can cheaply check a condition before invoking an operation.

### Dealing With Generalization

- Use `Pull Up Field` or `Pull Up Method` when siblings duplicate data or behavior.
- Use `Pull Up Constructor Body` when subclass constructors duplicate setup.
- Use `Push Down Field` or `Push Down Method` when a superclass member is used only by some subclasses.
- Use `Extract Subclass` when a subset of instances has distinct behavior.
- Use `Extract Superclass` when classes share real behavior or data.
- Use `Extract Interface` when clients need only a shared subset of behavior.
- Use `Collapse Hierarchy` when subclass and superclass are no longer meaningfully different.
- Use `Form Template Method` when similar algorithms share structure but vary in steps.
- Use `Replace Inheritance with Delegation` when inheritance creates refused bequest or excess coupling.
- Use `Replace Delegation with Inheritance` only when a delegating class truly is a subtype and delegation is pointless.

---

## Smell-to-Treatment Priority Map

Use this map after diagnosing the smell. Start with the preferred treatment, move to fallback only when the preferred treatment is blocked, and treat risky options as requiring stronger tests and explicit justification.

- `Long Method`: prefer `Extract Method`; fallback to `Replace Temp with Query`, `Introduce Parameter Object`, or `Preserve Whole Object` when locals block extraction; risky treatment is `Replace Method with Method Object` because it creates a new object and changes the shape of the algorithm.
- `Large Class`: prefer `Extract Class`; fallback to `Extract Subclass` for rare or variant behavior or `Extract Interface` for client-facing subsets; risky treatment is broad hierarchy extraction before responsibilities are stable.
- `Primitive Obsession`: prefer `Replace Data Value with Object`, `Replace Magic Number with Symbolic Constant`, or `Replace Array with Object`; fallback to type-code refactorings when behavior varies by code; risky treatment is replacing type code with subclasses or state/strategy before variation is stable.
- `Long Parameter List`: prefer `Replace Parameter with Method Call` or `Preserve Whole Object`; fallback to `Introduce Parameter Object`; risky treatment is removing parameters by creating hidden object dependencies.
- `Data Clumps`: prefer `Extract Class` or `Introduce Parameter Object`; fallback to `Preserve Whole Object`; risky treatment is passing a large owner object merely to avoid a parameter list.
- `Switch Statements`: prefer `Extract Method` and `Move Method` to isolate the decision; fallback to type-code replacement; risky treatment is `Replace Conditional with Polymorphism` when the conditional is simple or not based on stable variation.
- `Temporary Field`: prefer `Extract Class` or `Replace Method with Method Object`; fallback to `Introduce Null Object` for absence checks; risky treatment is spreading optional half-state through more conditionals.
- `Refused Bequest`: prefer `Push Down Method` or `Push Down Field`; fallback to `Replace Inheritance with Delegation`; risky treatment is preserving inheritance only to avoid changing callers.
- `Alternative Classes with Different Interfaces`: prefer `Rename Method` and signature alignment; fallback to `Extract Superclass`; risky treatment is merging classes across library or ownership boundaries.
- `Divergent Change`: prefer `Extract Class`; fallback to `Extract Superclass` or `Extract Subclass` for genuine shared behavior; risky treatment is inheritance used to avoid clear responsibility splits.
- `Shotgun Surgery`: prefer `Move Method` and `Move Field` to centralize ownership; fallback to `Inline Class` or `Extract Class`; risky treatment is adding more forwarding layers without reducing edit sites.
- `Parallel Inheritance Hierarchies`: prefer moving methods and fields to collapse mirrored variation; fallback to hierarchy collapse; risky treatment is adding the next paired subclass without redesigning ownership.
- `Comments`: prefer `Extract Variable`, `Extract Method`, or `Rename Method`; fallback to `Introduce Assertion` for hidden state assumptions; risky treatment is deleting comments before the code has become self-explanatory.
- `Duplicate Code`: prefer `Extract Method`; fallback to pull-up or `Extract Superclass` for sibling duplication or `Extract Class` for a separate concept; risky treatment is merging coincidental similarity.
- `Lazy Class`: prefer `Inline Class`; fallback to `Collapse Hierarchy`; risky treatment is keeping a class only because future work might need it.
- `Data Class`: prefer `Encapsulate Field` and `Encapsulate Collection`; fallback to `Move Method` and `Extract Method` to bring behavior to the data; risky treatment is stopping after trivial accessors.
- `Dead Code`: prefer deletion after usage checks; fallback to `Inline Class`, `Collapse Hierarchy`, or `Remove Parameter`; risky treatment is deleting externally reachable API.
- `Speculative Generality`: prefer `Inline Method`, `Inline Class`, `Remove Parameter`, and field deletion; fallback to `Collapse Hierarchy`; risky treatment is removing framework extension points without checking users.
- `Feature Envy`: prefer `Move Method`; fallback to `Extract Method` before moving an envying fragment; risky treatment is moving behavior that was deliberately separated for interchangeable strategy-like use.
- `Inappropriate Intimacy`: prefer `Move Method` and `Move Field`; fallback to `Hide Delegate` or `Replace Inheritance with Delegation`; risky treatment is widening visibility to preserve the intimacy.
- `Message Chains`: prefer `Hide Delegate`; fallback to `Move Method` closer to the data; risky treatment is adding a middle man that merely forwards without reducing knowledge.
- `Middle Man`: prefer `Remove Middle Man`; fallback to `Inline Class`; risky treatment is removing a boundary that hides volatile structure or policy.
- `Incomplete Library Class`: prefer `Introduce Foreign Method` for a narrow missing operation; fallback to `Introduce Local Extension` for repeated substantial missing behavior; risky treatment is broad library wrapping or forking.

---

