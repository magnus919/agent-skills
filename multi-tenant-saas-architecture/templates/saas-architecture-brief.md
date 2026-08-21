# SaaS Architecture Brief

## Decision
- **Product/service:**
- **Decision owner:**
- **Review date or trigger:**
- **Status:** draft | decided | superseded

## Service promise and context
- Customer and tenant promise:
- Users, operators, and support actors:
- Subscription and region assumptions:
- Data classes and lifecycle constraints:
- Scale, skew, and recovery facts:
- Unknowns requiring evidence:

## Domain authorities
| Concept | Meaning | Authoritative owner | States and transitions | Cross-tenant rule |
|---|---|---|---|---|
| Tenant | | | | |
| Account/subscription | | | | |
| User/membership | | | | |
| Entitlement/resource | | | | |

## Planes and flows
- Control-plane responsibilities:
- Application-plane responsibilities:
- Provisioning and configuration handoff:
- Entitlement and usage handoff:
- Billing and suspension handoff:
- Retry, stale state, reconciliation, and support behavior:

## Tenancy choices
| Resource | Shape | Why it fits the promise | Failure blast radius | Cost/fairness concern | Revisit trigger |
|---|---|---|---|---|---|
| Primary data | | | | | |
| Runtime compute | | | | | |
| Cache/queue/search | | | | | |
| Backup/restore | | | | | |

## Lifecycle and operations
- Onboarding and deprovisioning:
- Hot-tenant/noisy-neighbor behavior:
- Restore, export, and deletion scope:
- Tenant-aware observability and privacy constraints:

## Decisions and handoffs
| Decision or open question | Owner | Evidence or gap | Handoff |
|---|---|---|---|
| | | | |

## Verification
- Cross-tenant negative cases:
- Lifecycle idempotency and retry cases:
- Entitlement/billing disagreement:
- Restore and deletion evidence:
- Capacity/noisy-neighbor evidence:
