# Release Evidence

## Make The Decision Now

Decide what release claims matter, who owns them, and which artifacts can support or refute each claim. Typical claims concern the source revision, build identity, dependency inventory, test results, approval, deployment configuration, rollback readiness, and known-risk exceptions.

## Build An Evidence Bundle

- Link the release to an immutable source revision and reproducible build inputs where feasible.
- Generate and retain an SBOM in the consumer-agreed CycloneDX 1.7 or SPDX 3.0.1 format.
- Retain provenance attestation and signature verification results when the supply-chain policy calls for them; validate issuer and predicate against policy.
- Record security tests, threat-model changes, review approvals, deployment checks, accountable exceptions, expiry or review dates, rollback path, and incident-response contact.
- Include AI model, retrieval corpus, prompt or policy version, tool configuration, evaluation results, and human-approval gates where they affect release behavior.

## What It Proves And Does Not Prove

An SBOM supports an inventory claim at its generation scope and time. Provenance supports a claim about an identified build process. Test results support only the behavior exercised in the stated environment. None proves absence of vulnerabilities, secure deployment configuration, or safe AI behavior. CISA Secure by Design joint guidance encourages transparency and manufacturer accountability; publish or share artifacts according to the product's data-handling and disclosure policy.

## Exceptions And Verification

An exception needs a named owner, rationale, affected scope, compensating controls, expiry or review date, and rollback or response path. Independently retrieve and validate artifacts, verify deployment identity against the approved revision, and rehearse a rollback or containment action appropriate to release risk.
