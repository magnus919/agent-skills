# Bundle Manifest Design — Issue #203

This note records the design decision for the bundle-manifest contract and the
lifecycle capability matrix introduced for issue #203
("chore: define bundle manifests and lifecycle capability matrix"). It is the
bounded design note required by acceptance criterion AC1: it surveys the
repository's existing bundle metadata, records the chosen schema, and explains
why the chosen field set is the smallest set that still covers the required
contract. It deliberately does **not** propose a second skill format, does not
require top-level skills to join bundles, and does not expand into unrelated
repository refactors (see [Non-goals](#non-goals)).

## 1. Problem statement

The repository has eight canonical bundles — top-level directories with a
`SKILL.md` entrypoint: `product-lifecycle`, `production-excellence`,
`agent-production-operations`, `forward-deployed-engineering`, `neckbeard`,
`workflow-architect`, `tailscale`, and `research-and-vault`. Only
`workflow-architect` carries a bundle-metadata
concept today, and that concept is generation-time configuration for its own
builder — not a common, machine-readable composition contract. Users and agents
cannot consistently discover, from metadata alone, what a bundle is for, which
lifecycle stages it covers, which skills it composes, what it requires, what it
produces, where it hands off, where it overlaps other bundles, and how it is
evaluated.

## 2. Survey of existing bundle metadata

### 2.1 `workflow-architect/templates/manifest.yaml.tmpl`

The template defines a generation-time manifest with the following fields:

| Field | Meaning |
|---|---|
| `bundle_name` | Bundle identity for the generator |
| `generated` | Generation date (timestamp) |
| `archetype` | Builder archetype (e.g. `morning-triage-deep-work`) |
| `kanban` (optional) | Kanban board metadata (`board_slug`, `phases`) |
| `skills` | Ordered list of `{name, file, trigger{type, keywords, description, context}}` |

Its purpose is to drive the workflow-architect generator (morning-triage /
deep-work archetypes, kanban boards). The `skills` entries describe **loading
triggers** (keyword → nested skill) for that specific builder — not a general
capability contract.

### 2.2 `workflow-architect/references/example-output/developer-triage/manifest.yaml` (and `developer-pipeline-kanban`)

Concrete instances of the template: `bundle_name`, `generated` (e.g.
`2026-05-29`), `archetype` (`morning-triage-deep-work`,
`build-review-deploy`), optional `kanban` (`developer-pipeline-kanban` only),
and `skills` entries with `trigger` metadata (`type: keyword` /
`keyword+context`, `keywords`, `description`, optional `context`). These
confirm that the existing manifest concept is **workflow-architect-specific
generation configuration** — no bundle outside workflow-architect consumes it.

### 2.3 Bundles that carry no manifest today

`neckbeard/`, `research-and-vault/`, and `tailscale/`
carry no manifest of any kind. Their capability description lives only in the
`SKILL.md` frontmatter `description` field. `product-lifecycle`,
`production-excellence`, and `agent-production-operations` (the three new
milestone bundles) also carry no manifest today; they ship one with this issue.

### 2.4 `open-knowledge-format/references/bundle-architecture.md`

OKF's bundle-architecture describes **organizational guidance** for knowledge
bundles: flat vs. hierarchical directory layouts, `index.md` design,
cross-linking patterns, and tagging conventions. It is not a machine-readable
manifest format and defines no schema; it informs *how bundles are organized*,
not *how their capabilities are declared*.

### 2.5 Survey conclusion

The existing "manifest" concept is (a) workflow-architect-specific, (b)
generation-time configuration rather than a capability contract, and (c) not
consumed by any other bundle or tool. OKF contributes structure guidance but no
schema. No existing artifact exposes the discovery contract this issue needs
(purpose, audience, stages, included skills, prerequisites, outputs, handoffs,
conflicts, eval suite) in a machine-readable form. A new, small, versioned
schema is therefore warranted — it reuses the repository's schema conventions
(`schemas/evals-v1.schema.json`: JSON Schema, versioned filename
`*-v1.schema.json`) rather than inventing a parallel mechanism.

## 3. Chosen schema

The contract is `schemas/bundle-manifest-v1.schema.json` (JSON Schema,
draft 2020-12, `additionalProperties: false`, versioned filename following the
`evals-v1.schema.json` convention). A manifest lives at `<name>/manifest.yaml`
and is validated by `scripts/validate-bundles.rb`.

### 3.1 Fields preserved, dropped, and renamed vs. the existing manifest concept

| Existing concept (workflow-architect) | Disposition | Rationale |
|---|---|---|
| `bundle_name` | **Preserved** (renamed semantics: now must equal the bundle directory name) | Bundle identity is required for cross-references and the matrix |
| `skills` list | **Renamed → `included_skills`** | Entries become relative SKILL.md paths (catalog references or nested helpers) instead of trigger configurations; a machine-checkable composition list |
| `trigger {type, keywords, ...}` | **Dropped** | Loading triggers remain human-authored prose in each bundle's `SKILL.md` / `AGENTS.md`, where they are read; the manifest is a capability contract, not a loader config |
| `generated` (timestamp) | **Dropped** | Generation-time metadata; a timestamp would make the generated matrix non-deterministic |
| `archetype` | **Dropped** | workflow-architect-specific concept with no meaning for the other bundles |
| `kanban {board_slug, phases}` | **Dropped** | Pipeline-board-specific concept owned by workflow-architect's builder |
| *(new)* `purpose`, `audience`, `stages`, `prerequisites`, `outputs`, `handoffs`, `conflicts`, `eval_suite`, `schema_version` | **Added** | The nine contract fields + version pin, below |

### 3.2 The nine contract fields and the minimalism rationale

The issue contract names nine fields. Each maps to exactly one discoverability
question a user or agent must be able to answer from metadata alone; no field
can be derived from another, and dropping any one leaves a question
unanswerable:

| # | Field | Question it answers | Consumer |
|---|---|---|---|
| 1 | `purpose` | What does this bundle do? | Human readers, matrix, catalog |
| 2 | `audience` | Who is this for? | Human readers, matrix |
| 3 | `stages` | What lifecycle span does it cover, and which skill serves each stage? | Lifecycle discovery (VAL-MNF-018) |
| 4 | `included_skills` | Which skills does it compose? (paths resolve to SKILL.md files) | Composition boundary, catalog-exactness (VAL-MNF-020) |
| 5 | `prerequisites` | What inputs/artifacts must exist before use, and from which skills? | Readiness-path discovery (VAL-MNF-019) |
| 6 | `outputs` | What artifacts does it produce? | Handoff validation (VAL-MNF-014) |
| 7 | `handoffs` | Where do its outputs go next? | Composition navigation, conflict analysis |
| 8 | `conflicts` | Where does it overlap another bundle/skill, and how should overlap route? | Conflict resolution (VAL-MNF-021) |
| 9 | `eval_suite` | How is it evaluated, and where is the eval manifest? | Eval discovery (VAL-MNF-017) |

**Why this is the smallest set:** every field is either (a) an irreducible
answer to a discovery question the issue explicitly requires, or (b) a
reference used by the validators to reject contradictory metadata. The schema
adds only `schema_version` and `bundle_name` (identity + version pin, mirroring
`evals-v1`). It deliberately excludes workflow-architect's trigger/archetype/
kanban machinery, excludes free-form "tags" (already present in `SKILL.md`
frontmatter `metadata`), and excludes per-skill methodology content (owned by
the skills themselves). Each field has a defined type (strings, ordered stage
lists, path lists) chosen so that a validator can machine-check completeness
and consistency without a second toolchain.

## 4. Migration path

Per the milestone-4 mission boundary, the four pre-existing canonical bundles
are **off-limits** in this issue — their metadata belongs to their owning
areas and must not be changed here. They are therefore listed in this migration
path with a stated reason and future sequencing:

| Bundle | Status this issue | Reason (mission boundary) | Future sequencing |
|---|---|---|---|
| `workflow-architect` | No manifest added | Already owns a manifest concept (generation config for its builder); converting it to the new contract would require migrating the builder and its example-output fixtures, which is out of scope for #203 | Convert after its builder tooling and example-output fixtures are stable; preserve `trigger` semantics in `SKILL.md`/`AGENTS.md` prose |
| `neckbeard` | No manifest added | Ships its own evaluation harness (`eval/`) and delivery-packet lifecycle; belongs to the neckbeard maintenance track | Add a manifest on its next substantive change, deriving `stages` from its journey phases |
| `tailscale` | No manifest added | Complex multi-skill bundle with its own `skills/` hierarchy and scripts; belongs to the tailscale maintenance track | Add a manifest when its nested-skill boundary is next documented, listing nested helpers under `skills/` |
| `research-and-vault` | No manifest added | Minimal bundle (SKILL.md + README only) with no composition surface yet | Add a manifest when it gains references/helpers |

The **three new milestone bundles** — `product-lifecycle`, `production-excellence`,
and `agent-production-operations` — and `forward-deployed-engineering` ship
schema-conformant `manifest.yaml` files now (`<name>/manifest.yaml`), each resolving
`eval_suite` to its own `<name>/evals/evals.json`.

For the matrix, bundles without a manifest are rendered with a purpose derived
from their `SKILL.md` frontmatter `description` and the remaining cells set to
the documented deferral marker `migration deferred — see docs/bundle-manifest-design.md §Migration path`
(never blank; see VAL-MNF-010/011).

## 5. Non-goals

- **No second skill format.** The manifest contract does not alter the
  top-level `SKILL.md` format: `validate-skills.rb`'s `ALLOWED_FIELDS`
  (`name description license compatibility metadata allowed-tools`) is
  unchanged, and no validator requires a manifest for a top-level
  `<skill>/SKILL.md`. Manifests are not registered as standalone skills in any
  catalog.
- **No mandatory bundle membership.** Bundles remain optional composition
  layers. Top-level skills that belong to no bundle continue to validate,
  appear in catalogs, and are never flagged for lacking a manifest or bundle
  membership. No validator contains an error path of the form "must belong to
  a bundle".
- **Capability descriptions stay in source.** Each bundle's human-readable
  capability description remains discoverable from source metadata (the
  `SKILL.md` `description` field and/or the manifest `purpose` field),
  independent of the generated matrix. Deleting the generated matrix loses no
  capability description.
- **No unrelated refactors.** This issue touches only the changed surface
  listed in the PR: `{product-lifecycle,production-excellence,
  agent-production-operations}/**` (additive manifest + doc rows), `schemas/`,
  `scripts/`, `docs/`, and `.github/workflows/validate.yml`.

## 6. Validation and generation

- `scripts/validate-bundles.rb` — rejects incomplete manifests (missing
  required field, naming the file and field), contradictory manifests
  (unresolvable `included_skills`, handoff naming an undeclared output/stage,
  conflict naming a non-catalog skill), dangling `eval_suite` references, and
  undeclared cross-bundle overlaps on included skills (naming both manifests).
- `scripts/gen-lifecycle-matrix.rb` — deterministically generates
  `docs/lifecycle-capability-matrix.md` (one row per canonical bundle) and
  `docs/lifecycle-capability-matrix.json` (machine-readable, per-cell source
  provenance), reusing the `gen-*.rb` generator conventions (`ROOT`,
  `PUBLIC_SKILLS`, `YAML.safe_load` frontmatter parsing, `--write` mode, check
  mode with a `Run: ruby scripts/gen-lifecycle-matrix.rb --write` hint).
- `scripts/validate-lifecycle-matrix.rb` — verifies the JSON artifact covers
  every canonical bundle, every populated cell traces to its source, the
  artifact is current, and nested bundle helpers never leak into the four
  generated catalogs.
- `scripts/test-validate-bundles.rb` — deterministic positive/negative test
  coverage for the validator, generator, and matrix validator.
- `.github/workflows/validate.yml` — runs the new validator, tests, generator
  check, and matrix validator as part of the repository gate suite.
