# Component context maps

A component context map is a compact, source-linked handoff for one existing subsystem. It helps a reviewer or implementer orient to the code that matters for a bounded decision. It is not a repository-wide inventory, a substitute for reading critical paths, or an architecture verdict.

## When to make one

Create a map when a task crosses an unfamiliar boundary, review needs a concise source pack, ownership or side effects are easy to miss, or the same subsystem context will be reused across a design and implementation handoff. Skip it for a trivial isolated edit whose relevant code and behavior are already clear.

State the decision the map supports and set a boundary before exploring. Include only the caller, component, dependencies, data, and tests needed to answer that decision. Stop when each relevant responsibility has an evidence trail or is marked unknown; do not expand the map to make it look comprehensive.

## Record evidence at the right level

Use the component context contract in templates/component-context-contract.md. For each claim:

- Link to a repository path and, where possible, a symbol, test, configuration key, or trace.
- Label it observed, inferred, reported, or unknown. Separate owner statements from repository evidence.
- Record the source revision or commit. A link to a moving branch is not a stable source identity.
- Describe behavior and boundaries in your own words. Keep copied source excerpts short and necessary.
- Capture public interfaces, invariants, side effects, data ownership, external dependencies, and verification paths that matter to the decision.
- Identify unknowns and the smallest observation that could resolve each one.

An interface is more than a function signature: include callers, input/output meaning, error behavior, and lifecycle or transaction assumptions when evidence supports it. An invariant should name the state or rule that must hold and the evidence that enforces it. Side effects include writes, emitted events, network calls, permissions, background work, and observability changes.

## Check for drift

When the source revision changes, compare the relevant files and symbols with the map. Re-open evidence for changed claims, remove obsolete statements, and preserve a note of what was checked. File changes are a signal to inspect, not proof that a contract changed. Likewise, an unchanged hash does not prove runtime behavior is unchanged.

Keep the map useful to its named decision. If evidence is missing, report the gap rather than filling it with a plausible design. For a system-wide health assessment, coupling analysis, or clean-room redesign, continue through the main workflow in this skill. For a design that is already approved and needs delivery sequencing, use implementation-planning.
