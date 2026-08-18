---
name: data-cleaning
description: >-
  Clean, profile, validate, reshape, and document messy tabular, text, JSON, and
  relational data through an evidence-first, reproducible workflow. Use when
  preparing data for analysis, reporting, modeling, ingestion, migration, or
  matching. Do not use for statistical modeling, dashboard design, or operating
  a named data platform; route those tasks to data-scientist, data-engineering,
  or the relevant tool skill.
license: MIT
compatibility: Works with any Agent Skills client. The bundled profiler requires Python 3.9+ and the standard library; ecosystem tools are optional.
metadata:
  domain: data-quality-and-cleaning
  source: primary-docs-plus-orientation-article
---

# Data cleaning

Treat cleaning as a controlled transformation of an observed dataset, not cosmetic editing. Preserve raw input, state the target use and grain, make every lossy decision explicit, and prove that the cleaned output satisfies a contract.

## Route by task

| Need | Read next |
|---|---|
| End-to-end method, scope, and stopping rules | `references/methodology.md` |
| Choose a library or platform | `references/tool-selection.md` |
| Missingness, duplicates, types, ranges, categories, dates, joins | `references/operations.md` |
| Text, identifiers, Unicode, and entity resolution | `references/text-and-entity.md` |
| Schemas, contracts, validation, drift, scale | `references/validation-and-scale.md` |
| CLI, OpenRefine, monitoring, and interactive remediation | `references/cli-and-interactive-tools.md` |
| Source claims and version-sensitive caveats | `references/sources.md` |
| Plan, logs, exceptions, contracts, or reports | `templates/cleaning-plan.md`, `templates/transformation-log.jsonl`, `templates/exception-register.csv`, `templates/schema-contract.yml`, `templates/quality-report.md` |
| Lightweight profile or reconciliation | Run `python3 scripts/profile_dataset.py --help` or `python3 scripts/reconcile_dataset.py --help` |

## Default workflow

1. **Frame:** identify the decision, owner, source, privacy constraints, unit of observation, keys, expected grain, time window, and acceptance threshold. Do not silently infer a business rule from a suspicious value.
2. **Freeze evidence:** record source path/URI, retrieval time, file size/hash where feasible, encoding, delimiter, schema, row/column counts, and software versions. Keep raw data read-only and write to a new output.
3. **Profile before changing:** inspect missingness, sentinel values, duplicates, cardinality, type candidates, ranges, invalid dates, whitespace/Unicode anomalies, cross-field relationships, and drift. Use the bundled profiler for a dependency-free first pass.
4. **Design decisions:** classify each finding as preserve, standardize, repair, impute, quarantine, reject, or escalate. Record rationale, rule, affected rows, confidence, reversibility, and owner.
5. **Transform in layers:** prefer deterministic named steps: parse → canonicalize → type/coerce → validate → deduplicate → resolve entities → impute/quarantine → reshape. Keep raw, staged, rejected, and final datasets distinct.
6. **Validate twice:** run structural checks before and after transformation. Validate row/grain preservation, key uniqueness, referential integrity, allowed values, units, bounds, null policy, and expected distributions. Tests should identify failing records.
7. **Review and release:** compare before/after metrics, inspect samples of every changed class, obtain domain approval for semantic or lossy changes, publish the report and provenance, and make the run reproducible.

## Non-negotiable controls

- Never overwrite raw data or silently drop rows, columns, categories, outliers, or unmatched entities.
- Separate invalid, missing, not applicable, not collected, and withheld when the domain distinguishes them.
- Parse dates and numbers with an explicit locale, timezone, unit, and error policy. Count parse failures; do not silently turn them into nulls.
- Normalize text conservatively. Retain original and normalized values plus confidence when matching or repairing.
- Fit imputers, encoders, normalization parameters, and deduplication rules only on the permitted training/reference partition. Avoid leakage across time or evaluation boundaries.
- Treat profiling as evidence for investigation, not permission to auto-fix. An anomaly can be a real event.
- Use quarantine for records that cannot be repaired safely. “Clean” means accepted by a stated contract, not “no rows remain.”

## Completion gate

A cleaning task is complete only when the output, transformation/decision log, validation evidence, provenance, and unresolved issues exist; raw data remains intact; acceptance checks pass; and a reviewer can reproduce or audit the result. If semantic ambiguity remains, stop at quarantine or escalation rather than inventing a value.

## When not to use

Do not use this skill for inferential statistics or model selection, which belong to `data-scientist`; for ETL orchestration, storage, or production data-quality operations, route to `data-engineering`; or for operating a named validation or database platform, route to that tool's skill. This skill supplies cleaning judgment and artifacts those workflows consume.
