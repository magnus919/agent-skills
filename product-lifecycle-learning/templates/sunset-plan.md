# Sunset Plan

Plan the full retirement lifecycle for a feature or capability: deprecation communication,
migration path, customer treatment during sunset, and internal cleanup. Use when the lifecycle
decision is Retire. See [../references/retirement-lifecycle.md](../references/retirement-lifecycle.md).

## Feature Identity

| Field | Value |
|---|---|
| Feature / capability name | |
| Retirement decision date | |
| Sunset plan author | |
| Sunset plan date | |

## Deprecation Communication

| Field | Value |
|---|---|
| Deprecation announcement date | |
| Rationale for retirement (evidence-backed) | |
| Replacement or alternative | |
| Affected user segments | |
| Communication channels | |

**Announcement draft / key messages:**

## Timeline

| Milestone | Date | Description |
|---|---|---|
| Announcement | | Public deprecation notice |
| End-of-life (EOL) | | Last day of full support |
| End-of-support (EOS) | | Last day of limited support; no new bug fixes |
| Removal | | Feature removed from the product |
| Data export deadline | | Last day users can export data |
| Internal cleanup complete | | All flags, code, docs, monitoring removed |

## Migration Path

| Field | Value |
|---|---|
| Recommended replacement | |
| Migration guide location | |
| Data export format | |
| Data export instructions | |
| Migration tooling available | Yes / No — describe |
| Compatibility window | (how long the old and new coexist) |

**Step-by-step migration instructions for users:**

## Customer Treatment

| Field | Value |
|---|---|
| Support SLA during sunset | |
| Grace period duration | |
| Data export guarantee | Yes / No — describe |
| Refund or credit policy | |
| Escalation contact for exceptions | |
| Enterprise / B2B extended support | Yes / No — describe |

**Customer communication plan:** (coordinate with `conditional-customer-success` for
account-level execution — prose reference, skill not yet landed)

## Internal Cleanup Checklist

- [ ] Feature flags removed
- [ ] Kill switches and toggles removed
- [ ] Code archived (not deleted — archived for reference)
- [ ] Dead code paths removed from active codebase
- [ ] Documentation removed or archived
- [ ] Documentation cross-references updated
- [ ] Monitoring dashboards retired
- [ ] Alerting rules removed
- [ ] SLOs / SLIs updated or removed
- [ ] Runbooks archived
- [ ] Infrastructure decommissioned
- [ ] Third-party dependencies removed (if feature-specific)
- [ ] Database tables / schemas cleaned up (after data export window closes)
- [ ] API endpoints deprecated and removed
- [ ] On-call rotations updated
- [ ] Support knowledge base updated

## Learning Closure

- [ ] Retained learning record completed
- [ ] Assumption ledger finalized
- [ ] Learning routed to roadmap, analytics, adoption, experimentation, specifications
