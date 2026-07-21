# OBEY Refactoring.Guru

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

## Technique Playbook

Each named technique MUST be applied with a symptom, a use condition, an avoid condition, safe steps, and verification. The entries below are intentionally compact; they are for agent decision-making, not tutorial prose.

### Composing Methods Playbook

- `Extract Method`: Symptom: a fragment has a coherent purpose, needs a comment, duplicates another fragment, or blocks local reasoning. Use when a name can explain the fragment better than inline detail. Do not use when the fragment hides required side effects or depends on too much changing local state. Safe steps: identify inputs, outputs, mutated variables, extract, name by purpose, replace old fragment with the call. Verify by running tests around the caller and checking changed state flow.
- `Inline Method`: Symptom: a method name adds no clarity beyond its body. Use when indirection obscures the caller. Do not use when the method is an override point, public contract, or useful concept name. Safe steps: inspect all callers, substitute body, remove only when no caller remains. Verify by checking dispatch/interface usage and tests around callers.
- `Extract Variable`: Symptom: an expression is hard to understand in place. Use when a temporary name reveals intent. Do not use when the variable merely repeats the expression mechanically. Safe steps: introduce an immutable local value close to use, name the concept, keep evaluation order. Verify by tests and by checking no side effect was evaluated earlier or later.
- `Inline Temp`: Symptom: a temporary variable gets in the way of another refactoring or hides a simple expression. Use when the expression is cheap and clear. Do not use when the name explains a non-obvious concept or prevents repeated side effects. Safe steps: replace references with the expression, then delete the temp. Verify evaluation count and order.
- `Replace Temp with Query`: Symptom: a temporary value blocks extraction or repeats a meaningful calculation. Use when a named query can compute the same value without mutation. Do not use when the calculation is expensive, stateful, or order-dependent without caching policy. Safe steps: create query, replace temp reads, remove temp. Verify result equivalence and performance-sensitive paths.
- `Split Temporary Variable`: Symptom: one variable has multiple meanings across assignments. Use when assignments represent separate concepts. Do not use when the variable is an intentional accumulator. Safe steps: create one variable per meaning and update uses. Verify each use points to the intended value.
- `Remove Assignments to Parameters`: Symptom: a parameter is reused as scratch state. Use when mutation obscures caller intent. Do not use when language semantics intentionally model output parameters and callers rely on it. Safe steps: introduce a local variable, replace assignments, keep parameter read-only. Verify caller-visible behavior.
- `Replace Method with Method Object`: Symptom: a method is too tangled with locals to extract smaller methods. Use when a dedicated object can hold algorithm state and enable smaller methods. Do not use for a simple long method that `Extract Method` can handle. Safe steps: create method object, move locals to fields, move algorithm, split internal steps. Verify algorithm output and side effects.
- `Substitute Algorithm`: Symptom: an algorithm is confusing and a clearer equivalent exists. Use only after behavior is well protected. Do not use to change semantics, performance guarantees, or edge-case behavior silently. Safe steps: capture current behavior, replace algorithm, compare results on edge cases. Verify with broad tests around expected and boundary inputs.

### Moving Features Playbook

- `Move Method`: Symptom: a method uses another class more than its own. Use when behavior belongs with the data it changes. Do not use when separation is deliberate for interchangeable behavior. Safe steps: inspect data usage, extract partial fragment if needed, add method to target, redirect callers, remove old method. Verify callers and access visibility.
- `Move Field`: Symptom: a field is used more by another class or concept. Use when ownership is clearer elsewhere. Do not use when moving it creates circular knowledge or breaks lifecycle ownership. Safe steps: add field to target, migrate reads/writes, preserve initialization, delete old field. Verify construction, serialization, persistence, and mutation behavior.
- `Extract Class`: Symptom: one class does two jobs. Use when fields and methods form a stable separate responsibility. Do not use for arbitrary size reduction. Safe steps: create class, move data and behavior together, delegate temporarily, update clients gradually. Verify behavior and that responsibility boundaries are clearer.
- `Inline Class`: Symptom: a class no longer earns its maintenance cost. Use when its behavior fits naturally in another class. Do not use when it marks a real boundary or extension point. Safe steps: move members to target, replace references, delete empty class. Verify construction and public API usage.
- `Hide Delegate`: Symptom: clients navigate collaborator structure. Use when the current object can shield clients from that structure. Do not use if it creates a pure pass-through layer without reducing knowledge. Safe steps: add forwarding method with meaningful policy, update clients, keep collaborator private. Verify clients no longer know the path.
- `Remove Middle Man`: Symptom: a class mostly forwards calls. Use when direct collaboration is clearer. Do not use when the middle layer protects volatility or policy. Safe steps: replace forwarding calls with direct calls, remove forwarding methods, then reassess the class. Verify callers still have appropriate dependency.
- `Introduce Foreign Method`: Symptom: a library class lacks one small operation. Use for a narrow missing method you cannot add to the library. Do not use when many operations are missing. Safe steps: create local helper near usage, name it as if it belonged to the library type, replace duplicates. Verify behavior against library edge cases.
- `Introduce Local Extension`: Symptom: a library class repeatedly lacks substantial behavior. Use when a local wrapper/subclass reduces duplicated workarounds. Do not use for one small helper. Safe steps: create extension type, move repeated behavior, migrate callers deliberately. Verify compatibility with library construction and updates.

### Organizing Data Playbook

- `Self Encapsulate Field`: Symptom: direct field access prevents controlled access behavior. Use when access may need validation, lazy behavior, or override. Do not use when direct field access is intentionally simple and local. Safe steps: add access methods, replace internal reads/writes, then route future access through methods. Verify no recursive access or initialization breakage.
- `Replace Data Value with Object`: Symptom: a primitive carries domain meaning or validation. Use when behavior or constraints belong with the value. Do not use for a wrapper without added meaning. Safe steps: create value object, migrate construction, move validation/behavior, replace primitive usage. Verify equality, serialization, and boundary conversion.
- `Change Value to Reference`: Symptom: many equal objects should represent one mutable entity. Use when shared identity and current state matter. Do not use for naturally immutable values. Safe steps: introduce factory or repository lookup, return canonical instances, update creation paths. Verify identity sharing and missing-object handling.
- `Change Reference to Value`: Symptom: reference lifecycle is heavier than the object deserves. Use when immutable value semantics fit. Do not use when identity or shared mutation matters. Safe steps: make object immutable, define equality, simplify construction. Verify comparisons and update flows.
- `Replace Array with Object`: Symptom: array indexes have hidden names. Use when positions represent fields. Do not use for true homogeneous sequences. Safe steps: create object with named fields, replace index access, add behavior if needed. Verify all index semantics are preserved.
- `Duplicate Observed Data`: Symptom: GUI classes hold domain data. Use when domain state should live outside the UI with synchronization. Do not use when UI-only state has no domain meaning. Safe steps: create domain object, move domain data, synchronize UI/domain updates. Verify two-way update behavior.
- `Change Unidirectional Association to Bidirectional`: Symptom: both classes genuinely need navigation. Use when reverse lookup is complex or frequent. Do not use for convenience alone. Safe steps: choose dominant owner, add reverse field, centralize association updates. Verify add/remove consistency.
- `Change Bidirectional Association to Unidirectional`: Symptom: one side does not use the other. Use to reduce dependency and maintenance code. Do not use when reverse navigation is required by behavior. Safe steps: replace reads with parameters/lookups if needed, remove update code, delete unused field. Verify navigation callers.
- `Replace Magic Number with Symbolic Constant`: Symptom: a literal has hidden meaning. Use when a name explains the value. Do not use for obvious local literals. Safe steps: introduce named constant near owner, replace uses. Verify no unrelated same-value literals were captured.
- `Encapsulate Field`: Symptom: public field exposes representation. Use when access needs control. Do not stop at trivial accessors if behavior belongs inside. Safe steps: add accessor, migrate reads/writes, make field private. Verify callers and invariants.
- `Encapsulate Collection`: Symptom: callers mutate internal collection directly. Use when owner must preserve invariants. Do not expose a settable mutable collection as a replacement. Safe steps: return read-only view/copy, add add/remove methods, migrate callers. Verify mutation paths.
- `Replace Type Code with Class`: Symptom: a code needs type safety or behavior but not polymorphic variants. Use for meaningful codes. Do not use for trivial constants. Safe steps: create class for code, replace primitives, centralize validation. Verify persistence and comparisons.
- `Replace Type Code with Subclasses`: Symptom: type code drives stable variant behavior. Use when behavior differs by type and type does not change often at runtime. Do not use for volatile states. Safe steps: create subclasses, move variant behavior, replace creation. Verify dispatch and construction.
- `Replace Type Code with State/Strategy`: Symptom: type or state controls behavior and may change at runtime. Use when runtime switching matters. Do not use when a simple class code is enough. Safe steps: create state/strategy objects, move behavior, route transitions explicitly. Verify state transitions.
- `Replace Subclass with Fields`: Symptom: subclasses differ only by constant data. Use when hierarchy adds no behavior. Do not use when subclasses have distinct logic. Safe steps: add fields to superclass, replace subclass construction, remove empty subclasses. Verify type checks and serialization.

### Conditional and Method Call Playbook

- `Decompose Conditional`: Symptom: condition or branches require mental parsing. Use when names can clarify condition, then, or else parts. Do not use if extraction hides side effects. Safe steps: extract condition and branches into named methods. Verify branch behavior.
- `Consolidate Conditional Expression`: Symptom: multiple checks lead to one action. Use when checks are side-effect free. Do not use if checks differ in timing or side effects. Safe steps: combine expression, extract named query. Verify truth table.
- `Consolidate Duplicate Conditional Fragments`: Symptom: all branches repeat code. Use when repeated code can move before or after the conditional without changing order. Do not use if branch-specific side effects change ordering. Safe steps: move common fragment, extract if longer. Verify branch outputs.
- `Remove Control Flag`: Symptom: a flag variable only directs loop or branch flow. Use when direct break/return/continue is clearer. Do not use if the flag represents durable domain state. Safe steps: replace flag checks with direct control flow. Verify loop exit behavior.
- `Replace Nested Conditional with Guard Clauses`: Symptom: special cases obscure the normal path. Use when early exits make normal flow obvious. Do not use when nesting communicates required transaction or cleanup scope. Safe steps: identify special cases, move them first, keep normal path last. Verify all branches.
- `Replace Conditional with Polymorphism`: Symptom: behavior varies by stable type/state and conditionals repeat. Use after variation ownership is clear. Do not use for simple one-off conditionals or factory selection. Safe steps: create type/state structure, move variant behavior, replace conditional dispatch. Verify each variant.
- `Introduce Null Object`: Symptom: null checks dominate behavior. Use when a neutral object can obey the same interface. Do not use when absence is an error that should be explicit. Safe steps: create null object, replace null branches, preserve observable absence behavior. Verify absent and present cases.
- `Introduce Assertion`: Symptom: code depends on hidden state assumptions. Use to make invariants explicit. Do not use for normal validation or recoverable user errors. Safe steps: add assertion at boundary of assumption. Verify tests fail clearly when invariant is violated.
- `Rename Method`: Symptom: a method name hides intent. Use when callers should understand behavior without reading the body. Do not use if rename churn is unrelated to the change. Safe steps: rename definition and callers atomically. Verify references and public compatibility.
- `Add Parameter`: Symptom: a method lacks data needed for its job. Use when passing occasional data is better than storing it. Do not use if the method should own or derive the data. Safe steps: add compatible signature, migrate callers, remove old signature when safe. Verify callers.
- `Remove Parameter`: Symptom: a parameter no longer affects behavior. Use after confirming it is unused. Do not use if the parameter is part of public compatibility. Safe steps: remove uses, migrate signatures, preserve compatibility path if needed. Verify callers.
- `Separate Query from Modifier`: Symptom: a method both returns data and mutates state. Use when callers need clear intent. Do not use if atomic read-modify behavior is the public contract. Safe steps: split query and command, update callers. Verify state changes and return values.
- `Parameterize Method`: Symptom: similar methods differ only by values. Use when one method with a parameter keeps intent clear. Do not use when the parameter selects different behavior. Safe steps: create parameterized method, redirect old methods, remove duplicates if safe. Verify all value cases.
- `Replace Parameter with Explicit Methods`: Symptom: a parameter selects distinct behavior. Use when separate names are clearer than flags or modes. Do not use for ordinary data. Safe steps: create explicit methods, route callers, remove selector parameter. Verify each behavior.
- `Preserve Whole Object`: Symptom: callers pass several values from one object. Use when the callee naturally depends on the whole concept. Do not use if it creates an oversized dependency. Safe steps: change signature to object, update field reads, migrate callers. Verify dependency direction.
- `Replace Parameter with Method Call`: Symptom: caller passes data the callee can obtain. Use to reduce redundant caller work. Do not use if it hides an expensive or surprising dependency. Safe steps: move lookup to callee, remove parameter, update callers. Verify lookup behavior.
- `Introduce Parameter Object`: Symptom: parameters repeatedly travel together. Use when they form one concept. Do not use for a random bag of unrelated arguments. Safe steps: create object, migrate signature, move related behavior. Verify construction and validation.
- `Remove Setting Method`: Symptom: a field should not change after initialization. Use when immutability or lifecycle clarity matters. Do not use when mutation is valid domain behavior. Safe steps: set through constructor/factory, remove setter, update initialization. Verify object creation.
- `Hide Method`: Symptom: public method is not intended for clients. Use to reduce interface surface. Do not use if external callers need it. Safe steps: check callers, reduce visibility, update tests. Verify public API.
- `Replace Constructor with Factory Method`: Symptom: creation needs naming, selection, caching, or controlled reference lookup. Use when `new` hides important creation policy. Do not use for simple construction. Safe steps: add factory, redirect construction, restrict constructor if safe. Verify creation paths.
- `Replace Error Code with Exception`: Symptom: exceptional failure is represented by status codes callers must inspect. Use when failure should interrupt normal flow. Do not use for ordinary expected branch choices. Safe steps: throw exception, update callers, remove code checks. Verify failure handling.
- `Replace Exception with Test`: Symptom: callers use exceptions for avoidable expected conditions. Use when a cheap pre-check exists. Do not use when failure is exceptional or race-prone. Safe steps: add query/test, update callers, keep exception for true violations. Verify normal and failure paths.

### Generalization Playbook

- `Pull Up Field`, `Pull Up Method`, `Pull Up Constructor Body`: Symptom: siblings duplicate members or setup. Use when the superclass can honestly own the shared part. Do not use when duplication is accidental or variants will diverge. Safe steps: move shared member up, update subclasses, remove duplicates. Verify all subclasses.
- `Push Down Field`, `Push Down Method`: Symptom: superclass member is used only by some subclasses. Use when superclass contract is too broad. Do not use if callers rely on the superclass member. Safe steps: move member down, update references, narrow contract. Verify affected subtype callers.
- `Extract Subclass`: Symptom: only some instances need special behavior. Use when variation is stable and meaningful. Do not use for temporary flags or speculative categories. Safe steps: create subclass, move variant behavior, update construction. Verify base and variant behavior.
- `Extract Superclass`: Symptom: classes share real behavior or data. Use when a common owner simplifies duplication. Do not use for coincidental method names. Safe steps: create superclass, pull up shared members, update inheritance. Verify all subclasses.
- `Extract Interface`: Symptom: clients use only a common subset. Use when the subset is a real client contract. Do not use as a generic abstraction habit. Safe steps: define interface, type clients to it, keep implementers honest. Verify client compilation and behavior.
- `Collapse Hierarchy`: Symptom: subclass and superclass are practically identical. Use when hierarchy adds no distinction. Do not use if remaining subclasses would violate substitutability. Safe steps: choose survivor, move members, replace references, delete empty type. Verify type expectations.
- `Form Template Method`: Symptom: similar algorithms share structure but vary steps. Use when skeleton and steps are stable. Do not use when algorithms are only superficially similar. Safe steps: align method names, pull up skeleton, push variant steps down. Verify all algorithms.
- `Replace Inheritance with Delegation`: Symptom: inheritance causes refused bequest or excessive coupling. Use when object uses another object rather than is that object. Do not use if subtype substitution is central. Safe steps: add delegate, forward needed behavior, replace inherited access. Verify public behavior.
- `Replace Delegation with Inheritance`: Symptom: a class delegates nearly everything to an object it truly is. Use rarely when subtype relation is honest. Do not use if inheritance would create unused behavior. Safe steps: inherit, remove redundant delegate, update construction. Verify substitutability.

---

## Decision Anti-Patterns

- MUST NOT apply a refactoring because its name sounds modern; apply it because it treats a diagnosed smell.
- MUST NOT turn a simple conditional into polymorphism unless variation is stable, repeated, and owned by type/state.
- MUST NOT create a parameter object from unrelated arguments just to shorten a signature.
- MUST NOT introduce a superclass or interface from coincidental method names without a real client or shared behavior.
- MUST NOT replace duplication with an abstraction that has a worse name than the duplicated code.
- MUST NOT stop at getters and setters when the real smell is behavior living outside the data.
- MUST NOT hide feature work inside a refactoring sequence.
- MUST NOT preserve a forwarding class merely because deleting it requires caller updates.
- MUST NOT use bidirectional association as a convenience shortcut when one side can receive the collaborator as a parameter or lookup.
- MUST NOT delete speculative or dead-looking code until generated, reflected, serialized, plugin-facing, and public usages are checked.
- MUST NOT add assertions for normal user input, expected absence, or recoverable errors.
- MUST NOT use exceptions as routine tests when callers can cheaply check the condition first.
- MUST NOT inline names that explain business intent even when the body is short.
- MUST NOT move behavior away from its data if doing so creates feature envy in the opposite direction.
- MUST NOT continue cleanup after the diagnosed smell is fixed unless the next smell blocks the requested change.

---

## Technique Execution Safety

### Extraction Safety

- Before `Extract Method`, MUST identify every variable read, written, or returned by the fragment.
- SHOULD leave variables local to the extracted method when they are declared and used only inside the fragment.
- SHOULD pass prior values as parameters only when the extracted fragment genuinely needs them.
- MUST double-check any variable modified inside the fragment; if later code needs the changed value, return it explicitly or choose a safer refactoring.
- SHOULD use `Replace Temp with Query` before extraction when temporary variables are blocking a clean method boundary.
- MUST name the extracted method after its purpose, not after the mechanical steps it performs.
- MUST NOT extract a fragment that hides an important side effect behind a harmless-sounding name.

### Inlining Safety

- Before `Inline Method`, MUST confirm the method adds no useful name, abstraction, override point, or public contract.
- SHOULD inline only after checking all callers, especially when dynamic dispatch, inheritance, or interface calls may be involved.
- MUST NOT inline a method if callers depend on it as part of a public or test-facing API.
- Before `Inline Class`, MUST move all useful behavior and data to the target class and update all references.
- MUST delete the emptied class only after references, construction sites, tests, and documentation no longer require it.

### Moving Safety

- Before `Move Method`, MUST inspect which class owns most of the data used by the method.
- SHOULD extract the moved fragment first when only part of a method belongs elsewhere.
- MUST update all callers and preserve visibility intentionally; do not widen access just to make the move compile.
- Before `Move Field`, MUST migrate reads and writes through accessors or direct replacements in a small sequence.
- MUST NOT move behavior away from its data if the separation was deliberate and supports interchangeable behavior.

### Encapsulation Safety

- Before `Encapsulate Field`, SHOULD add access methods, migrate all direct readers and writers, then make the field private.
- SHOULD review accessor callers after encapsulation; behavior may belong inside the owning class rather than outside it.
- Before `Encapsulate Collection`, MUST prevent callers from mutating the internal collection directly.
- SHOULD expose add/remove operations that preserve invariants instead of exposing a settable collection.
- MUST NOT add trivial getters and setters as the final design if they merely preserve public data under different names.

### Conditional Safety

- Before `Consolidate Conditional Expression`, MUST verify that the conditions are side-effect free.
- SHOULD extract the consolidated condition into a named query when the expression is complex.
- Before `Consolidate Duplicate Conditional Fragments`, SHOULD move duplicate code before or after the conditional only when doing so preserves execution order.
- Before `Replace Nested Conditional with Guard Clauses`, MUST identify the normal path and preserve special-case behavior.
- Before `Replace Conditional with Polymorphism`, MUST confirm that the conditional varies by stable type, state, or strategy; otherwise prefer explicit methods or a simpler conditional.
- MUST NOT introduce polymorphism for a simple conditional that is easier to read in place.

### Method Call Safety

- Before `Add Parameter`, MUST check whether the method should instead own the data as a field or obtain it through an existing collaborator.
- SHOULD preserve compatibility by creating a new method or transition path before deleting the old signature when callers are numerous or public.
- Before `Remove Parameter`, MUST confirm the parameter is unused or no longer changes behavior.
- Before `Separate Query from Modifier`, MUST split state mutation from returned information and update callers to use the right method for each intent.
- Before `Replace Parameter with Explicit Methods`, MUST confirm the parameter selects distinct behavior rather than ordinary data.
- Before `Introduce Parameter Object`, MUST confirm the grouped parameters represent one concept and not an arbitrary bag.
- MUST NOT simplify a method call if the simplification creates hidden dependencies between classes.

### Data Reorganization Safety

- Before `Replace Data Value with Object`, MUST define the object's meaning, equality, validation, and allowed behavior.
- Before changing value/reference semantics, MUST decide whether identity, mutability, sharing, and lifecycle management are required.
- SHOULD make value objects immutable before replacing references with values.
- SHOULD use factory creation when replacing values with references so callers receive the canonical object.
- Before changing association direction, MUST identify which side owns updates and how consistency is maintained.
- MUST remove a bidirectional association when one side does not need navigation.
- MUST NOT add a bidirectional association unless both sides genuinely need it and consistency logic is explicit.

### Generalization Safety

- Before pulling members up, MUST confirm sibling duplication is real and the superclass contract can honestly own the member.
- Before pushing members down, MUST confirm the superclass no longer promises or needs the member.
- Before extracting a superclass or interface, MUST identify real shared behavior or a real client-facing subset.
- MUST NOT extract an interface only because two classes happen to share method names.
- Before collapsing a hierarchy, MUST check remaining subclasses for substitutability and public type expectations.
- Before replacing inheritance with delegation, MUST preserve the delegated behavior and update construction and forwarding paths deliberately.
- MUST NOT replace delegation with inheritance unless the delegating class truly is a subtype and the inheritance will not create refused bequest.

---

## Safety and Tradeoff Rules

- MUST choose a treatment based on the smell, not on a preferred pattern.
- MUST NOT introduce polymorphism, inheritance, bidirectional links, or new classes when a simpler extraction or rename solves the problem.
- MUST NOT remove parameters, associations, or abstractions if doing so creates worse coupling or hides required variation.
- SHOULD prefer local simplification before hierarchy changes.
- SHOULD prefer names and extracted methods before comments.
- SHOULD prefer deleting unused structure before extending it.
- SHOULD preserve domain meaning when replacing primitives or arrays with objects.
- SHOULD keep behavior with the data it changes unless a deliberate interchangeable behavior model is needed.
- SHOULD use assertions for invariants, not as substitutes for normal validation or recoverable error handling.
- MUST preserve public compatibility or provide a transition path when refactoring public interfaces.

---

## Refactoring Workflow for Agents

Before editing:

1. Identify the requested behavior change or maintenance goal.
2. Scan the touched area for smells using the catalog above.
3. Name the primary smell, its cost, and the smallest useful refactoring.
4. Identify the expected cleaner end state and the stop condition.
5. Identify tests or checks that prove behavior is preserved.
6. Decide whether the refactoring belongs before, after, or separate from feature work.

During editing:

1. Apply one named transformation at a time.
2. Keep the code runnable after each meaningful step.
3. Rename, extract, move, inline, or encapsulate before introducing larger design structures.
4. Re-run relevant tests after risky movement, public interface changes, or changed state flow.
5. Re-check whether the chosen technique is still the smallest treatment.
6. Stop if the refactoring exposes a different, larger problem and report the new scope.

After editing:

1. Confirm behavior preservation.
2. Confirm the original smell is reduced or removed.
3. Confirm no broader feature change was hidden in the refactor.
4. Confirm no new smell was introduced, especially middle-man, speculative generality, or inappropriate intimacy.
5. Confirm that any intentionally untreated smell has a reason.
6. Report the refactoring technique used, the stop condition reached, and the validation performed.

---

## Review Checklist

- Is the change a refactoring, a feature, or a bug fix, and is that boundary clear?
- Did the code become cleaner in the touched area?
- Is there a named smell that justified the transformation?
- Was the smallest suitable technique used?
- Did all relevant tests pass?
- Did any public interface change receive compatibility handling?
- Did the change reduce duplication, bloat, coupling, or unclear control flow?
- Did it avoid speculative abstractions?
- Did it avoid needless polymorphism, inheritance, or bidirectional associations?
- Is any remaining smell explicitly deferred rather than hidden?
