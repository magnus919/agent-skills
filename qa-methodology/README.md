# QA Methodology

Senior-to-principal QA and SDET methodology for software teams that ship with confidence.

## Why Install This Skill

Shipping software without a test strategy means discovering failures in production instead of in CI. This skill gives your agent the methodology of a senior QA engineer: risk-based prioritization that tells you what to test first, regression suites that catch breakage without becoming brittle, and quality gates that block merges on evidence rather than vibes.

Beyond traditional QA, the bundle covers the agentic era: independent verification of AI-generated code, mutation-guided test hardening for changed behavior, acceptance-criteria testability review for Spec-Driven Development pipelines, and eval dataset design with judge-bias mitigation for AI agents. Whether your team is a two-person startup or a multi-team platform, the references scale from task-level test design to org-level quality engineering strategy.

Install once and your agent designs test strategies, triages CI failures by exit code, writes exploratory charters, scores risks on a 5x5 grid, reviews AI-generated PRs with independence, and maps QA career growth from Senior through Principal.

## What You Get

| Directory | Contents |
|-----------|----------|
| `references/` | 16 deep-dive files: test-strategy, test-automation, quality-gates-and-metrics, regression-testing, test-data-management, performance-testing, security-testing, ci-failure-triage, test-debugging, risk-based-testing, exploratory-testing, test-design-techniques, qa-career-levels, sdet-engineering, ai-code-quality-gates, agentic-eval-design |
| `templates/` | 6 fillable templates, including mutation-review for reproducible survivor triage and evidence |
| `assets/` | 3 quick-reference assets: risk-matrix-grid, test-design-techniques-checklist, qa-definition-of-done |
| `scripts/` | 2 Python CLIs: risk-prioritize (P×I ranking with --json output), check-ac-testability (vague-AC scanner) |
| `evals/` | Schema-v1 output-quality eval manifest (10 cases) |

## Quick Start

Score and rank risk items from a JSON file:

```bash
python3 qa-methodology/scripts/risk-prioritize.py --json risk-items.json
```

Check acceptance criteria for testability before a gate review:

```bash
python3 qa-methodology/scripts/check-ac-testability.py spec.md
```

## Triggers

- Test strategy design or review
- Regression suite building, selection, or evolution
- CI failure triage (exit codes, flake classification, bisect)
- Test automation framework selection and flaky management
- Quality gate design and metrics (DORA, targeted mutation review evidence)
- Mutation-guided test hardening (surviving mutants, weak assertions, diff-aware scope)
- Risk-based testing (P×I scoring, workshops, registers)
- Exploratory testing (SBTM charters, heuristics)
- Agentic eval design (datasets, judge bias, flaky-eval discipline)
- SDD gate review (AC testability, independent verification)
- SDET engineering and QA career leveling

## Requirements

- Python 3.8+ for scripts (standard library only, no third-party packages)
- No specific CI platform, test framework, or AI agent required
- Works with any language or stack (examples reference pytest, Playwright, k6, and others as illustrations)
