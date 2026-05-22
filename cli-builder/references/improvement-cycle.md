# CLI Improvement Cycle

After a CLI ships, real usage reveals what the tests didn't catch. This cycle captures feedback and prioritizes fixes systematically.

## The Flywheel

```
Traces → Feedback → Triage → Fix → Deploy
   ↑                              │
   └──────────────────────────────┘
```

## Structured Feedback Schema

When an agent session reveals a problem with a CLI tool, capture it as structured data — not a note-to-self. This makes patterns visible across multiple sessions:

```python
feedback = {
    "tool": "my-cli",
    "trace_id": "<session or run ID>",
    "theme": "ambiguous_error",
    # one of: missing_flag, silent_failure, wrong_output,
    #         unparseable_json, confusing_help
    "command": "my-cli deploy --env staging --tag v1.2",
    "observed": "Agent ran command with correct flags but got "
                "non-zero exit with no stderr output",
    "expected": "Non-zero exit should always include a stderr message "
                "explaining what went wrong",
    "frequency": "single_occurrence",
    # or "recurring" — if recurring, escalate to High priority
}
```

Review the feedback log before each new CLI build to identify recurring pain points.

## HALO-Style Prioritization

When the feedback log accumulates, triage findings by four tiers:

| Priority | Criteria | Action |
|----------|----------|--------|
| **Blocking** | Tool returns wrong output, errors on valid input, or crashes | Fix immediately, add regression test |
| **High** | Agent misuses a flag or pattern across multiple sessions (2+ feedback entries with same theme) | Fix this sprint, update help text |
| **Medium** | Missing `--json`, missing help examples, inconsistent naming | Schedule next sprint |
| **Low** | Stderr hygiene, edge-case idempotency, non-idiomatic flag names | Defer, log for next version |

**Triage rule:** Pattern frequency overrides tier. A "Medium" finding that appears in 3+ sessions is actually High. A "Blocking" finding that only appeared once with a workaround may be Medium.

The goal is not to fix everything — it's to have a defensible reason for what you're fixing now vs. deferring.

## Applying the Cycle

1. Collect traces from agent sessions using the tool
2. When a pattern emerges, write a structured feedback entry
3. Before the next development cycle, review the backlog
4. Fix the top priority items
5. Add regression tests for each fix
6. Deploy the updated tool
