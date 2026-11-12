# Component context map eval challenges

These examples challenge the context map cases in evals.json. They are rubric probes authored for review, not model runs or evidence that the skill improves outcomes.

| Case | Satisfying evidence | Contradictory near miss | Evidence omitted |
|---|---|---|---|
| bounded-subsystem-context-map | The map names one subsystem and decision, cites the source revision and relevant paths/symbols, records an observed interface and side effect, labels a missing invariant unknown, and lists a focused verification gap. | It generates a repository-wide component inventory, presents inferred ownership as observed, or calls an invariant enforced without a test or code path. | It describes responsibilities in prose but gives no revision, source links, evidence classifications, or unknowns. |
| documentation-drift-triage | The report compares the documented retry limit with the implementation and test at a fixed revision, calls out the contradiction, and leaves the owner to choose a documentation or code change. | It silently edits the specification to match the code, or declares the code defective solely because it differs from the document. | It reports drift but does not cite either side or distinguish missing evidence from contradiction. |

Each case should be distinguishable as met, contradicted, or not shown from the answer. Prose assertions remain subject to appropriate human or validated grading.
