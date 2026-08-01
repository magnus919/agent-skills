# Bug Report

> File one report per defect. Provide enough detail for any engineer to reproduce without asking questions.

## Title

<One-line summary: [Component] Observed behavior under specific condition>

## Classification

| Field | Value |
|-------|-------|
| Severity | Critical / High / Medium / Low |
| Priority | P1 (Immediate) / P2 (This sprint) / P3 (Backlog) / P4 (Won't fix) |
| Component | <affected module or service> |
| Discovered In | <test type: unit / integration / E2E / exploratory / production> |
| Charter / Test ID | <link to exploratory charter or test case, if applicable> |

### Severity Definitions

| Severity | Meaning |
|----------|---------|
| Critical | Data loss, security breach, system down, revenue stoppage |
| High | Major feature broken, no workaround, SLA breach |
| Medium | Feature impaired but workaround exists |
| Low | Cosmetic, minor inconvenience, documentation error |

## Environment

| Field | Value |
|-------|-------|
| OS / Platform | <e.g., macOS 15, Ubuntu 24.04, iOS 18> |
| Browser / Client | <e.g., Chrome 131, API client v2.3> |
| Application Version | <commit SHA, release tag, or build number> |
| Environment | <local / CI / staging / production> |
| Relevant Config | <feature flags, env vars, tenant settings> |

## Reproduction Steps

1. <Step 1 — starting state or navigation>
2. <Step 2 — action taken>
3. <Step 3 — action taken>
4. <...add steps as needed>

**Reproducibility:** Always / Sometimes (___ in ___ attempts) / Once (not yet reproduced)

## Expected vs Actual

| | Description |
|---|-------------|
| **Expected** | <What should happen according to spec, docs, or reasonable behavior> |
| **Actual** | <What actually happens — be specific about the observed behavior> |

## Evidence

Attach or link:

- [ ] Screenshot / screen recording: <path or URL>
- [ ] Error message / stack trace: <paste below or link>
- [ ] Logs: <path or link>
- [ ] Network capture: <path or link>
- [ ] Test output: <CI link or local path>

```
<paste error output or stack trace here>
```

## Additional Context

<Anything that helps triage: recent changes, related issues, suspected root cause, whether it blocks release.>

## Escalation

| Condition | Action |
|-----------|--------|
| Severity = Critical | Blocks release; escalate to engineering leadership within 1 hour |
| Severity = High + Priority = P1 | Escalate to team lead within 4 hours |
| Unreproducible after 3 attempts | Add to investigation backlog with environment capture |
