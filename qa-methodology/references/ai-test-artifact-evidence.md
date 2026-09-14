# AI-assisted test artifact evidence

Use this reference when AI generates or transforms tests, fixtures, review comments, test plans, or QA summaries. It supplements the independent-verification and mutation gates in `ai-code-quality-gates.md`; it does not authorize self-review or replace security, release, statistical, or repository-policy owners.

## Provenance without unnecessary retention

Classify the artifact (production code, test, fixture, mock, charter, review comment, summary, or documentation), link it to the spec/AC and risk tier, and record the AI role (generate, transform, summarize, suggest). For consequential artifacts retain the tool/model identifier, relevant context boundary, date, output or commit hash, human edits, assumptions accepted/rejected, verifier, and evidence location. Redact secrets and unnecessary personal/customer data; QA needs reproducibility metadata, while retention and privacy policy belong to the relevant security/observability owner.

## Spec-first oracle review

Before reading implementation-coupled tests, derive expected behavior from the specification: normal, invalid, boundary, state-transition, failure, permission/security, concurrency, and recovery cases as applicable. Inspect each generated test for a behavioral oracle, independent expected value, fixture isolation, meaningful failure, and the ability to detect a plausible defect. Reject line-execution tests, mock-only assertions, mirrored assumptions, tautologies, vacuous assertions, and exact-string checks where the output is nondeterministic. Add a hand-built negative case, differential check, property, or bounded mutation to show the test can fail for the wrong behavior.

## Review comments are hypotheses

Treat an AI review comment as a triage signal, never as approval evidence. Check it against the spec, diff, actual API/tool contract, and domain context. Label it substantiated, unsubstantiated, duplicate, context-dependent, or requires domain review. Large diffs, generated migrations, authentication/authorization changes, data-loss paths, and comments dependent on unavailable context require human or domain escalation. Record review queue delay and unresolved high-impact findings; do not reward comment volume or model confidence.

## Workflow-level evidence

When claiming that AI improved QA, compare against a named baseline. Report meaningful defect detection or escape rate, behavioral/mutation evidence, flake rate, coverage by risk/capability slice, review time or queue burden, security findings, and rework. Generated-test count, lines changed, passing self-tests, and a successful demo are activity signals, not proof of quality. Preserve inconclusive and infrastructure-failure outcomes separately.

## Emergency exceptions

An emergency may shorten review time, but it does not waive independent verification for a high-impact change. Record the incident/change reason, risk owner, temporary scope, checks completed, missing evidence, compensating monitoring, approver, expiry, and post-incident review date. Reconcile the exception with the normal gate and add follow-up tests or decomposition work. Release promotion and incident response remain owned by their sibling skills.

## Exit gate

The QA evidence is complete when artifact provenance is sufficient and privacy-safe, every applicable AC has a spec-derived oracle review, an independent verifier has checked the artifact, generated comments have dispositions, workflow claims have baseline metrics, and any exception has an owner, expiry, and follow-up.
