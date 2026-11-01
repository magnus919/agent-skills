# Risk-tiered review checklist

<!-- Use this to decide what to look at, not to prove the change is safe.
     A ticked box means the question was asked and answered by the cited
     evidence. An unticked box is an open question, not a pass.
     Tier the change first; low-tier changes do not need the high-tier rows. -->

## Tier the change

| Tier | Trigger | Minimum review |
|---|---|---|
| **T1 — routine** | Docs, tests only, isolated internal rename, dependency patch with no behavior change | One reviewer, single pass, evidence that tests run |
| **T2 — standard** | New feature path, behavior change in a bounded module, config default change | One reviewer with domain knowledge, plus CI evidence; negative-path test expected |
| **T3 — sensitive** | Auth, authorization, crypto, payments, PII, data deletion, migrations, public contract, dependency major bump, CI/build change | Two reviewers, one owning the sensitive area; threat-model or compatibility note; rollback evidence |
| **T4 — critical** | Money movement, tenant isolation boundary, irreversible data operation, safety-critical or regulated path, release-blocking hotfix | Named accountable reviewer plus a second independent reviewer; rehearsal or dry-run evidence; explicit rollback plan and owner |

Tiering is a claim about blast radius, not about how hard the diff is to read.
A 40-line auth change is T3; a 900-line test refactor may be T1.

## Every tier

| Question | Evidence that answers it | Where to look |
|---|---|---|
| Does the change do what its description says? | Diff read against the stated intent; the mismatch is the finding | PR description, issue, spec |
| Does it build and pass its own tests? | Command and output, not "CI is green" | CI log or local run |
| Is the new behavior tested, including the failure path? | A test that fails before and passes after | Test diff |
| Do the tests assert behavior or just execute code? | Assertions on outcomes, not on mocks calling through | Test diff |
| Is there anything in the diff that does not belong to this change? | Diff scope matches stated intent | Diff |

## T2 and above

| Question | Evidence that answers it | Where to look |
|---|---|---|
| What happens on invalid, empty, huge, or concurrent input? | Error-path tests or explicit reasoning about the guard | Code and tests |
| What happens when the dependency it calls fails, times out, or retries? | Timeout, retry, and fallback code plus a test | Code |
| Is the change backward compatible for existing callers and stored data? | Consumer list, contract test, or migration plan | API schema, migration files |
| Does it add a log line someone can act on, and no secret? | Log statements reviewed for content and level | Diff |
| Is the change observable when it fails in production? | Metric, log, or trace that distinguishes failure from success | Diff, dashboards |
| Can it be rolled back without data loss? | Rollback command or feature-flag path | Release notes, flags |

## T3 and above

| Question | Evidence that answers it | Where to look |
|---|---|---|
| Does every new entry point check identity **and** authorization on the object it touches? | Denial test: authenticated-but-unauthorized request fails | Handler and policy code |
| Can tenant or user context cross a boundary? | Cross-tenant test; explicit tenant parameter threading | Repository and query layer |
| Are secrets, tokens, and PII kept out of logs, errors, and URLs? | Redaction test or code inspection | Error handlers, logging |
| Does the migration run forward, backward, and on representative data volume? | Dry run output and timing; rollback drill | Migration scripts |
| Does a dependency change bring new transitive packages or licenses? | Lockfile diff and license check | Lockfile, SBOM |
| Does the CI or build change alter what gets deployed? | Diff of pipeline steps; artifact provenance | CI config |

## T4 additions

| Question | Evidence that answers it | Where to look |
|---|---|---|
| Who is accountable for this decision, by name? | Named reviewer in the record | Review record |
| What is the blast radius if this is wrong, and who is affected? | Written impact statement | Risk section of the record |
| What is the rollback, who executes it, and how is it verified? | Rehearsed rollback or documented drill | Runbook |
| What compensating control exists while the risk is live? | Flag, rate limit, manual approval, monitoring threshold | Release plan |

## Checklist limits — read before trusting a filled sheet

- A checked box records that a question was asked. It does not record that the answer was right.
- Checklists catch omissions of known categories. They do not find unknown failure modes, and reviewers who work from a list find fewer *unlisted* problems.
- The dangerous rows are the ones marked "N/A" without a reason. Require a reason.
- If the sheet is longer than the diff deserves, the sheet is the problem: delete rows rather than ritualizing them.
