---
name: verification-methodology
description: Verify work against explicit criteria using evidence, reproducible checks, and clear pass, conditional, or blocked verdicts. Use before declaring an artifact, implementation, or claim complete.
license: MIT
compatibility: No runtime dependency.
metadata:
  source_repo: https://github.com/magnus919/hermes-profiles
  source_commit: 867a555
---


# Verification Methodology

Pass/fail assessment against pre-defined criteria.

## The Verification Protocol

1. **Receive** — restate the artifact, claim, or implementation being verified and the decision it will support.
2. **Assess criteria** — convert requirements into observable pass/fail conditions; identify what would disprove each claim.
3. **Investigate** — collect direct, reproducible evidence and record commands, source locations, or source URLs.
4. **Decide** — mark each criterion passed, failed, blocked, or not applicable. Do not convert missing evidence into a pass.
5. **Report** — use the verdict template to distinguish verified facts, assumptions, and remaining work.

Stop when every criterion has direct evidence or an explicit blocked/not-applicable verdict. Escalate when the criterion is ambiguous, evidence conflicts, or the required access is unavailable.

## Reference Files

| Reference | When to load |
|-----------|-------------|
| `references/criteria-assessment.md` | You need to evaluate whether work meets completion criteria |
| `references/evidence-standards.md` | You need to judge whether evidence supports the claims made |
| `references/verdict-template.md` | You need to produce a structured pass/fail/hold verdict |

## Portability

This skill is intentionally host-neutral. Use your agent's normal mechanisms to load the references, templates, and scripts listed here. Do not assume a particular profile system, task orchestrator, memory service, or response-handoff format.
