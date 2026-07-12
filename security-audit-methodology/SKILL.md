---
name: security-audit-methodology
description: Plan authorized security reviews with threat modeling, architecture and dependency audits, and vulnerability classification. Use for scoped defensive security assessment.
license: MIT
compatibility: Authorization for the target system is required. This skill provides defensive methodology, not a substitute for qualified security review.
metadata:
  source_repo: https://github.com/magnus919/hermes-profiles
  source_commit: 867a555
---


# Security Audit Methodology

## Authorization and safety boundary

Before any assessment, confirm the target, scope, permitted techniques, data-handling rules, and escalation contact. Do not probe systems, access accounts, exploit findings, or alter production state without explicit authorization. Record findings as evidence for the responsible owner; this skill does not certify compliance or replace qualified security review.

Security is not a checklist — it's a posture. This methodology covers systematic evaluation of code, architecture, dependencies, and operational practices for security weaknesses.

## The Security Engineer's Domain

| You own | You don't own |
|---------|--------------|
| Threat modeling — STRIDE, attack trees, trust boundaries | General code review — that's the reviewer |
| Vulnerability assessment — classification, severity, reproduction | Performance analysis — that's the debugger |
| Security architecture review — authn/authz, data flow, secrets management | Operational reliability — that's SRE |
| Dependency analysis — supply chain, known vulnerabilities, license risk | Compliance certification — that's legal |
| Security testing guidance — fuzzing, SAST/DAST integration | Incident response execution — that's SRE/on-call |

## Reference Files

| Reference | When to load |
|-----------|-------------|
| `references/threat-modeling.md` | Evaluating a system's attack surface — STRIDE per component, trust boundaries, data flow analysis |
| `references/vulnerability-classification.md` | Assessing a finding — CVSS scoring, CWE mapping, severity triage, exploitability assessment |
| `references/security-architecture-dependency-audit.md` | Reviewing authentication (OAuth 2.0, OIDC, SAML, mTLS), authorization (RBAC/ABAC/ReBAC), session management, secrets management, and dependency/supply chain security (SBOM, CVE matching, license analysis, SLSA framework) |

## Core Principles

**Trust nothing, verify everything** — Every input, every boundary, every assumption is a potential attack surface. Default deny, explicit allow.

**Defense in depth** — No single control is sufficient. Authentication without rate limiting, encryption without key management, input validation without output encoding — each is a vulnerability waiting to chain.

**Least privilege** — Every component, every user, every process should have exactly the permissions it needs and no more. Over-privilege is the most common security debt.

**Understand the attacker's perspective** — The question isn't "can this be exploited?" It's "how would an attacker think about this system?" Model their incentives, constraints, and capabilities.

**Fix the class, not the instance** — One SQL injection means you need parameterized queries everywhere, not just at that one endpoint. A single XSS means review the entire rendering pipeline.

## Portability

This skill is intentionally host-neutral. Use your agent's normal mechanisms to load the references, templates, and scripts listed here. Do not assume a particular profile system, task orchestrator, memory service, or response-handoff format.
