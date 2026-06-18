# OKF v0.1 — Specification Summary

The full specification lives at [GoogleCloudPlatform/knowledge-catalog/okf/SPEC.md](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md). This reference covers the key structural rules, conformance criteria, and design decisions.

## Goals

1. Define a universal format that **enrichment agents** can write into
2. Inform how **consumption agents** should read and traverse it
3. Facilitate **exchange** of knowledge across systems and organizations
4. Standardize the small number of **required** fields for meaningful consumption

## Non-goals

- Defining a fixed taxonomy of concept types
- Prescribing storage, serving, or query infrastructure
- Replacing domain-specific schemas (Avro, Protobuf, OpenAPI) — OKF references them, does not subsume them

## Terminology

| Term | Definition |
|------|------------|
| **Knowledge Bundle** | Self-contained, hierarchical collection of knowledge documents. The unit of distribution. |
| **Concept** | A single unit of knowledge within a bundle. One markdown document. |
| **Concept ID** | The path of the concept's file within the bundle, with `.md` suffix removed. E.g. `tables/users.md` has ID `tables/users`. |
| **Frontmatter** | YAML metadata block delimited by `---` at the top of a markdown file |
| **Body** | Everything in the file after the frontmatter |
| **Link** | Standard markdown link from one concept to another |
| **Citation** | A link from a concept to an external source supporting a claim |

## Bundle Structure Rules

```
bundle/
├── index.md           # Reserved — directory listing (optional)
├── log.md             # Reserved — update history (optional)
├── <concept>.md       # Any other .md file is a concept
└── <subdirectory>/
    ├── index.md
    └── …
```

### Reserved filenames

| Filename | Purpose |
|----------|---------|
| `index.md` | Directory listing. Optional. No frontmatter (except at bundle root for `okf_version`). |
| `log.md` | Update history. Optional. ISO 8601 date headings, newest first. |

All other `.md` files are concept documents.

## Frontmatter Specification

```yaml
---
type: <Type name>                  # REQUIRED
title: <Optional display name>
description: <Optional one-line summary>
resource: <Optional canonical URI>
tags: [<tag>, …]                   # Optional
timestamp: <ISO 8601 datetime>     # Optional
---
```

### `type` field — REQUIRED

A short string identifying the kind of concept. Examples: `BigQuery Table`, `BigQuery Dataset`, `API Endpoint`, `Metric`, `Playbook`, `Reference`.

- Types are NOT registered centrally
- Producers SHOULD pick descriptive, self-explanatory values
- Consumers MUST tolerate unknown types gracefully (treat as generic concept)

### Recommended fields (priority order)

1. `title` — Human-readable display name. If omitted, consumers may derive from filename
2. `description` — Single sentence summary. Used by index generators, search snippets, previews
3. `resource` — URI identifying the underlying asset. Absent for abstract ideas
4. `tags` — YAML list of short strings for cross-cutting categorization
5. `timestamp` — ISO 8601 datetime of last meaningful change

### Extensions

Producers MAY include any additional keys. Consumers SHOULD preserve unknown keys on round-trip and SHOULD NOT reject unrecognized fields.

## Conventional Body Sections

| Heading | Purpose |
|---------|---------|
| `# Schema` | Structured column/field descriptions |
| `# Examples` | Usage examples, often fenced code blocks |
| `# Citations` | External sources backing claims |

These are **conventions**, not requirements. Any markdown content is valid.

## Cross-linking Rules

Two forms of links:

1. **Absolute (bundle-relative):** Start with `/`, interpreted relative to bundle root. Recommended form.
2. **Relative:** Standard markdown relative paths.

A link from concept A to concept B asserts a relationship. The specific kind (parent/child, references, joins-with, depends-on) is conveyed by surrounding prose, not by the link itself. Graph consumers treat all links as directed edges of an untyped relationship.

**Consumers MUST tolerate broken links** — a link whose target does not exist in the bundle is not malformed; it may represent not-yet-written knowledge.

## Index Files (`index.md`)

May appear in any directory. Contains no frontmatter (except optionally at bundle root):

```markdown
# Section Heading

* [Title 1](relative-url-1) - short description
* [Title 2](relative-url-2) - short description
```

Entries SHOULD include the `description` from the linked concept's frontmatter. Producers MAY generate `index.md` automatically; consumers MAY synthesize one on the fly.

## Log Files (`log.md`)

Flat list of date-grouped entries, newest first:

```markdown
## 2026-05-22
* **Update**: Added [Customer Metrics](/tables/customer-metrics.md).
* **Creation**: Established the [Playbook](/playbooks/dataplex.md).
```

Date headings MUST use ISO 8601 `YYYY-MM-DD` form. Leading bold word (`**Update**`, `**Creation**`, `**Deprecation**`) is a convention, not a requirement.

## Citations

Sources listed under `# Citations` at the bottom of a document, numbered:

```markdown
# Citations

[1] [Source title](https://...)
[2] [Source title](path/to/reference.md)
```

Citation links may be absolute URLs, bundle-relative paths, or paths into a `references/` subdirectory.

## Conformance Criteria

A bundle is **conformant** with OKF v0.1 if:

1. Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter block
2. Every frontmatter block contains a non-empty `type` field
3. Every reserved filename follows its defined structure when present

Consumers MUST NOT reject a bundle because of:
- Missing optional frontmatter fields
- Unknown `type` values
- Unknown additional frontmatter keys
- Broken cross-links
- Missing `index.md` files

## Versioning

Format: `<major>.<minor>`

- **Minor bump:** Backward-compatible additions (new optional fields, new conventional headings)
- **Major bump:** Breaking changes (renaming required fields, changing reserved filenames)

Bundles MAY declare their target version via `okf_version: "0.1"` in a bundle-root `index.md` frontmatter block (the only place frontmatter is permitted in `index.md`). Consumers that don't understand the declared version SHOULD attempt best-effort consumption.
