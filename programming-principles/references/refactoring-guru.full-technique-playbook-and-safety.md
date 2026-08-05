# Refactoring.Guru: Technique Playbook and Safety

> Part of the Refactoring.Guru full reference — technique playbook, decision anti-patterns, execution safety, tradeoff rules, agent workflow, and review checklist. Index: [refactoring-guru.full.md](refactoring-guru.full.md)

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
