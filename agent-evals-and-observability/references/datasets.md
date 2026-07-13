# Datasets and Fixtures

Freeze each evaluated dataset version as an immutable artifact under the repository's chosen naming scheme. Record a changelog rather than prescribing a particular version-label convention. Preserve the exact case, fixture, configuration boundary, and manifest needed to reproduce a run.

The manifest must state provenance; rights and consent; creation and review owners; task taxonomy; slices; source class; expected outcomes; fixtures and reset method; expected side effects; contamination and leakage risk; limitations; access; retention; deletion handling; and change history.

Use isolated sandboxes or resettable fixtures for stateful tools. Inspect actual environment state to grade idempotency or side effects; identical text is not sufficient evidence. Treat production-derived data as a controlled source: verify rights, minimize and transform it, redact before storage, limit access, define deletion, and prevent it from entering prompts or training/evaluation targets where it would contaminate comparisons.

Report prevalence-oriented samples separately from deliberately risk-enriched or adversarial cases. Slices should expose meaningful differences such as task class, tool availability, locale, policy path, or input condition; they are not a license to infer outcomes for unrepresented groups.
