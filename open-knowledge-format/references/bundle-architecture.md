# OKF Bundle Architecture

How to structure, organize, and distribute OKF knowledge bundles effectively.

## Bundle Distribution

A bundle MAY be distributed as:

- **A git repository** (recommended) — provides history, attribution, diffs
- **A tarball or zip archive** of the directory
- **A subdirectory** within a larger repository

## Directory Organization Strategies

### Flat structure (small bundles)

For fewer than 10 concepts, a flat directory works:

```
bundle/
├── index.md
├── customers.md
├── orders.md
├── weekly-active-users.md
└── incident-response.md
```

### Hierarchical structure (medium bundles)

Group by domain or type for bundles with 10-100 concepts:

```
bundle/
├── index.md
├── tables/
│   ├── index.md
│   ├── customers.md
│   ├── orders.md
│   └── products.md
├── metrics/
│   ├── index.md
│   ├── wau.md
│   └── revenue.md
└── playbooks/
    ├── index.md
    ├── incident-response.md
    └── data-freshness-alert.md
```

### Deeply nested structure (large bundles)

For 100+ concepts, use subdirectories that mirror organizational or system boundaries:

```
bundle/
├── index.md
├── log.md
├── sales/
│   ├── index.md
│   ├── tables/
│   │   ├── orders.md
│   │   └── customers.md
│   └── metrics/
│       └── revenue.md
└── marketing/
    ├── index.md
    ├── tables/
    │   └── campaigns.md
    └── metrics/
        └── cac.md
```

## Cross-linking Patterns

### Linking to a specific concept

```markdown
See the [customers table](/tables/customers.md) for the join key.
```

### Linking to a subdirectory index

```markdown
Browse available [metrics](/metrics/index.md).
```

### Linking to an external resource

```markdown
Defined in the [OpenAPI spec](https://example.com/openapi.yaml).
```

### Linking from a dataset to its constituent tables

```markdown
The sales dataset contains [orders](/tables/orders.md) and [customers](/tables/customers.md).
```

## Index File Design

An `index.md` provides progressive disclosure — letting an agent or human see what's available without opening every document.

### Root index pattern

```markdown
# <Bundle Name> Knowledge Base

* [Tables](/tables/index.md) - Database tables reference
* [Metrics](/metrics/index.md) - Business metrics definitions
* [Playbooks](/playbooks/index.md) - Incident response and operational guides
```

### Subdirectory index pattern

```markdown
# Tables

* [Customers](customers.md) - Customer profile data
* [Orders](orders.md) - Completed customer orders
* [Products](products.md) - Product catalog
```

## Log File Conventions

A `log.md` records history at any level of the hierarchy:

```markdown
# Change Log

## 2026-06-18
* **Creation**: Established the sales dataset documentation.
* **Update**: Added revenue metrics with cross-links to orders table.

## 2026-06-15
* **Initialization**: Created bundle structure and index files.
```

## Tips for Agent-Friendly Bundles

1. **Always include `index.md` at the bundle root.** Agents use it as an entry point for progressive loading.
2. **Prefer absolute (bundle-relative) links** starting with `/`. They survive document moves within subdirectories.
3. **Use consistent `type` values across your bundle.** While the spec doesn't require a registry, consistency helps agents route and filter.
4. **Write descriptions for every concept.** These are what `index.md` entries and search snippets use.
5. **Bundle complementary domains separately.** A bundle about "sales data" and one about "incident response" are better as separate bundles than a single flat one.
6. **Tag liberally.** Tags are the primary cross-cutting categorization mechanism. They enable agent filtering without directory reorganization.
