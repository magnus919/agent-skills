# Data-Flow and Access Map

Template for mapping data flows across services, tenants, and geographic regions. Documents where data transits, where it resides, who can access it, and under what conditions.

## System boundary

| Field | Value |
|---|---|
| **System / feature** | |
| **Data categories mapped** | |
| **Trust boundaries crossed** | |
| **Owner** | |
| **Last updated** | |

## Service-level data flow

For each service that touches the data categories in scope:

| Service | Data received | Data stored | Data transmitted | Transmission destination | Transmission purpose |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |

## Cross-region data flow

| Data category | Source region | Destination region | Transfer mechanism | Legal basis for transfer | Encryption in transit |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |

## Access matrix

| Data category | Actor (user, service, role) | Access type (read, write, delete) | Access condition | Access logged? | Log retention |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |

## Tenant isolation

| Tenant boundary | Isolation mechanism | Cross-tenant query prevention | Verified? | Verification method |
|---|---|---|---|---|
| | | | | |

## Third-party and subprocessor flows

| Third party | Data shared | Purpose | DPA in place? | Data residency | Deletion commitment |
|---|---|---|---|---|---|
| | | | | | |

## Data stores inventory

| Store type | Data categories stored | Region | Encryption at rest | Backup region | Backup retention |
|---|---|---|---|---|---|
| Primary database | | | | | |
| Cache | | | | | |
| Read replica | | | | | |
| Object storage | | | | | |
| Search index | | | | | |
| Message queue | | | | | |
| Log store | | | | | |
| Analytics warehouse | | | | | |
| Archive | | | | | |

## Gaps and follow-up

| Gap | Severity | Owner | Due date |
|---|---|---|---|
| | | | |
