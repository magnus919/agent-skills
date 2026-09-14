# spring-ai — Diagnose Spring AI projects before they surprise you

## Why Install This Skill

Spring AI projects combine fast-moving framework APIs with model providers, retrieval stores, memory, tools, and streaming. A project can compile while leaking conversation context, logging prompts, executing an unauthorized tool, or treating partial output as complete.

This skill gives your agent a read-only diagnostic workflow for actual Maven and Gradle projects. It reports build versions, configuration hazards, source-level integration clues, and actionable findings as machine-readable JSON so you can retain evidence with a commit or incident record.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Version posture, workflow, boundaries, and recovery expectations. |
| `scripts/spring_ai_check.py` | Stdlib-only Maven/Gradle/config/source diagnostic CLI. |
| `scripts/test_spring_ai_check.py` | Offline tests for parsing, findings, JSON, and error behavior. |
| `references/compatibility-and-setup.md` | Current setup checks and version-sensitive API notes. |
| `references/integration-boundaries.md` | ChatClient, memory, retrieval, tools/MCP, streaming, and observability checks. |
| `references/source-index.md` | Official Spring AI and Spring Boot URLs with verification date. |
| `examples/minimal-project/` | Static diagnostic fixture used by the tests; not a runnable application. |
| `evals/evals.json` | Seven schema-v1 output-quality cases. |

## Quick Start

No API key is required for diagnostics:

```sh
python3 spring-ai/scripts/spring_ai_check.py --root ./my-spring-app --json
```

Use `--strict` in CI when warnings should fail the check. The tool never contacts a model provider.

## Triggers

- Diagnose Spring AI Maven or Gradle compatibility and configuration.
- Inspect ChatClient/advisor, retrieval, memory, tool/MCP, streaming, or observability integration.
- Prepare a local Spring AI smoke-test or troubleshoot a failed integration.

## Requirements

- Python 3.8+ standard library.
- A Maven or Gradle project directory for useful results.
- Maven/Gradle and provider credentials only when running the project’s own tests; the diagnostic CLI does not need them.
- Re-check official documentation for upgrades; supported documentation posture is Spring AI 2.0.1 current stable and 1.0.9 maintenance reference as verified 2026-09-14.
