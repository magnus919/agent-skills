# Code Review — judgment for real diffs, not comment quotas

Review a change for correctness, security, maintainability, and test adequacy, and
reach a verdict you can defend with evidence.

## Why Install This Skill

Most review advice is folklore: "keep PRs under 400 lines", "two reviewers", "use a
checklist". Some of it is well-founded and some of it is a vendor case study that
became a myth. This skill tells you which is which, and then gives you a working
method that fits the evidence.

After installing it, your agent can:

- scope a diff before reading it — effective size, risk-bearing paths, whether tests
  moved with the code, and a defensible attention budget;
- review in the order that finds problems: intent, contract, main path, boundaries,
  failure paths, tests, operability;
- write comments the author can act on, with severity labels, evidence, and a way
  to verify the fix;
- reach a verdict (`APPROVE`, `APPROVE WITH COMMENTS`, `REQUEST CHANGES`,
  `NEEDS MORE EVIDENCE`) that does not contradict its own findings, and record what
  it did *not* review;
- handle AI-generated and AI-reviewed changes without mistaking fluency for
  correctness.

The references are grounded in primary sources — Google's engineering practices,
the Microsoft and Google review studies, and recent AI-review deployments — with the
weak evidence labelled as weak. The scripts are deterministic and read-only: they
describe the diff, and never pretend to judge it.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | The review loop, verdict semantics, routing to specialist skills, and honest limits |
| `references/` | Eight focused references: evidence base, scoping and depth, defect taxonomy, comment quality, verdicts and evidence, AI-assisted review, metrics, source index |
| `templates/` | Five fillable artifacts: review record, review plan for oversized changes, comment set, risk-tiered checklist, AI pre-review brief |
| `scripts/review_scope.py` | Read-only diff scope: effective lines, risk flags by path, test mapping, attention budget, review order |
| `scripts/review_record_check.py` | Validates a review record: required sections, labeled findings, evidence and verification on blockers, verdict consistency |
| `scripts/test_*.py` | Tests against real temporary git repositories and against the shipped template |
| `evals/evals.json` | Eleven output-quality cases for agent runs (one fixture audits a flawed record) |

## Quick Start

No installation, no API keys, no network:

```bash
# What is actually in this change?
python3 scripts/review_scope.py --base origin/main --head HEAD --markdown

# Machine-readable, for an agent
python3 scripts/review_scope.py --base origin/main --head HEAD --json

# Reviewing the staged index before committing
python3 scripts/review_scope.py --staged --json

# Check a completed review record for contradictions and missing evidence
python3 scripts/review_record_check.py review.md
```

Example scope output for a real change:

```
# Review scope

- Range: `HEAD~2...HEAD`
- Tier: **oversized**
- Size: 27 files, +991/-13 (1004 effective lines, 0 generated)
- Budget: ~201 min across 4 session(s), capped at 60 min each

## Risk-bearing paths

- **authentication**: `app/auth/session.py`

## Attention order

1. `app/auth/session.py`
2. `app/service.py`
```

## Triggers

Load this skill when:

- a pull request, patch, or diff needs a verdict;
- a change is too large to review in one pass and needs scoping or splitting;
- review comments need triage, severity labels, or rewriting to be actionable;
- a team needs reviewer assignment, review policy, or latency norms;
- a defect reached production and you need to know what review missed;
- a model produced candidate review comments that a human must accept or discard;
- someone repeats review folklore and you need the evidence behind it.

Do not load it for fixing the defect, root-cause debugging, whole-system security
assessment, secure design of new code, or architecture review — those route to the
specialist skills named in `SKILL.md`.

## Requirements

- Python 3.10+ and `git` for the scripts (standard library only; no packages).
- `pytest` only if you want to run the bundled tests.
- No network access, credentials, or review platform integration.
