---
title: "Infrastructure as Code Review Record: [Module / Project Name]"
doc_id: IACR-[MODULE-CODE]-[VERSION]
status: draft | in-review | approved | changes-requested
created: [YYYY-MM-DD]
last_modified: [YYYY-MM-DD]
reviewer: "[Reviewer Name]"
author: "[Module Author Name]"
---

# Infrastructure as Code Review Record — [Module / Project Name]

## 1. Review Metadata

| Field | Value |
|---|---|
| **Module / project** | [Name and path in Git] |
| **IaC tooling** | [e.g., Terraform, OpenTofu, Pulumi, Ansible, CloudFormation] |
| **Provider(s)** | [e.g., AWS, GCP, Azure, on-prem] |
| **Review scope** | [Full module / resource block / state change] |
| **Plan applied?** | [Yes/No — if yes, plan ID and date] |
| **Drift baseline** | [State of the environment before the change] |

## 2. Module Structure

| Check | Verdict | Notes |
|---|---|---|
| Single-purpose composition (no monolith root) | _[fill: pass / fail / n/a]_ | _[fill: what should be split into child modules]_ |
| Variables and defaults parameterize env specifics | _[fill: pass / fail / n/a]_ | _[fill: hardcoded IDs, account numbers, regions]_ |
| `for_each`/`count` used instead of copy-pasted blocks | _[fill: pass / fail / n/a]_ | _[fill: specific resources to convert]_ |
| Minimal output surface area | _[fill: pass / fail / n/a]_ | _[fill: outputs consumers actually need]_ |
| Version pinning of modules and providers | _[fill: pass / fail / n/a]_ | _[fill: constraints and locked versions]_ |

## 3. State and Drift

| Check | Verdict | Notes |
|---|---|---|
| Remote backend with locking configured | _[fill: pass / fail / n/a]_ | _[fill: backend type and lock mechanism]_ |
| No secrets material in state | _[fill: pass / fail / n/a]_ | _[fill: which attributes are sensitive and how they are handled]_ |
| Workspaces/environments isolated | _[fill: pass / fail / n/a]_ | _[fill: env separation approach]_ |
| Drift detection cadence defined | _[fill: pass / fail / n/a]_ | _[fill: scheduled plan or drift tooling]_ |
| State operations documented (`state mv`, `rm`, imports) | _[fill: pass / fail / n/a]_ | _[fill: any state surgery required]_ |

## 4. Security and Secrets

| Check | Verdict | Notes |
|---|---|---|
| Secrets come from a secret manager, not plaintext vars | _[fill: pass / fail / n/a]_ | _[fill: Vault / SOPS / cloud secret store reference]_ |
| Least-privilege IAM on created resources | _[fill: pass / fail / n/a]_ | _[fill: overly broad policies to tighten]_ |
| Network boundaries default to deny | _[fill: pass / fail / n/a]_ | _[fill: security groups, firewalls, network policies]_ |
| Sensitive outputs marked `sensitive = true` | _[fill: pass / fail / n/a]_ | _[fill: which outputs]_ |
| Resource naming and tagging consistent | _[fill: pass / fail / n/a]_ | _[fill: tag keys, cost center, owner, environment]_ |

## 5. Operational Readiness

| Check | Verdict | Notes |
|---|---|---|
| `plan` output reviewed for unintended changes | _[fill: pass / fail / n/a]_ | _[fill: resources that will be replaced vs updated]_ |
| `prevent_destroy` on irreplaceable resources | _[fill: pass / fail / n/a]_ | _[fill: database, state bucket, registry]_ |
| Lifecycle rules match intent (`create_before_destroy`) | _[fill: pass / fail / n/a]_ | _[fill: where ordering matters]_ |
| Rollback path defined | _[fill: pass / fail / n/a]_ | _[fill: revert commit, previous state, or forward fix]_ |

## 6. Findings

### Blocking Findings

| # | Severity | Finding | Location | Suggested Fix | Owner | Fixed? |
|---|---|---|---|---|---|---|
| 1 | [critical/high] | _[fill: what is wrong and why it blocks]_ | _[fill: file:line]_ | _[fill: concrete change]_ | _[fill: name]_ | _[fill: yes/no]_ |

### Non-Blocking Findings

| # | Severity | Finding | Location | Suggested Fix | Owner | Fixed? |
|---|---|---|---|---|---|---|
| 1 | [low/medium] | _[fill: what is suboptimal]_ | _[fill: file:line]_ | _[fill: concrete change]_ | _[fill: name]_ | _[fill: yes/no]_ |

## 7. Verdict

| Field | Value |
|---|---|
| **Verdict** | [approved / changes-requested] |
| **Blocking findings resolved** | [all / list of remaining] |
| **Re-review required** | [yes/no — and by when] |
| **Reviewer sign-off** | [Name, date] |
| **Author sign-off** | [Name, date] |

*File this record alongside the module and the applied plan output so the review is auditable.*
