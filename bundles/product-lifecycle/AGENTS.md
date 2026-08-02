# Product Lifecycle Bundle — Agent Instructions

## Loading

### Lifecycle routing
1. Load `product-lifecycle` umbrella SKILL.md for the phase routing table
2. Identify the current lifecycle phase from the table
3. Load `references/phases.md` for detailed phase contracts
4. Load the specialist skill(s) named in the phase row
5. Follow the specialist's method; do not re-derive it from the umbrella

### Capability lookup
1. Load `references/capability-map.md` for capability → owning skill mapping
2. Load the owning skill directly

### Nested skill loading
This bundle does not contain nested sub-skills. It composes specialist skills
from the catalog. Each specialist skill is loaded on trigger when its phase is
entered. The umbrella documents which skills load at which phase; it does not
auto-load them.

## Lifecycle evidence ledger

Every phase writes to a shared lifecycle evidence ledger. The ledger is the
cross-phase handoff contract. Phase N+1 reads what phase N wrote and does not
re-derive it. Ledger fields and conventions are defined in
`references/phases.md`.

## Stop and escalation

Every phase has explicit escalation behavior. A stopped/escalated lifecycle is a
legitimate outcome — the ledger preserves what was learned. Stop conditions
include: no viable problem (Phase 1), no strategic fit (Phase 2), experiment
disproves hypothesis (Phase 5), readiness returns No-go (Phase 6), adoption
fails (Phase 7), and justified retirement (Phase 9).

## Reference files

| File | Purpose |
|---|---|
| `references/phases.md` | Per-phase contracts with entry evidence, output artifacts, escalation behavior, completion criteria, and ledger spec |
| `references/discovery-brief.md` | Bundle boundary, comparison with existing bundles, surveyed skills, non-ownership statement |
| `references/capability-map.md` | Capability area → owning skill lookup table |

## Environment

No environment variables required. No API keys, no services, no network
dependencies.
