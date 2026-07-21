# OBEY The Pragmatic Programmer by Andrew Hunt and David Thomas

## When to use

Use as a general engineering operating style when the goal is accountable delivery, adaptability, fast feedback, and code that remains easy to change.

## Primary bias to correct

Do not optimize only for the local edit, requested feature, or familiar ritual. Own the outcome by reducing duplicated knowledge, keeping concerns independent, proving assumptions early, and automating repeated work.

## Decision rules

- Be pragmatic, not dogmatic. Choose the practice that improves real outcomes.
- Own the result. Surface tradeoffs, risks, and avoidable design costs.
- Keep one authoritative representation for each piece of system knowledge. Derive or trace everything else.
- Preserve orthogonality: independent components, narrow interfaces, separated concerns.
- Keep volatile decisions reversible. Do not hard-code vendors or environments before evidence justifies commitment.
- Use domain vocabulary and small domain languages when they make rules clearer.
- Prefer thin end-to-end tracer bullets over piles of isolated pieces.
- Use prototypes to learn, not to pretend the work is done.
- Dig for real requirements. Separate durable needs from current proposed solutions.
- Automate repetitive, error-prone, easy-to-forget work. Builds, tests, linting, deployment.
- Shorten feedback loops with relevant tests, automated checks, cheap early signals.
- Make contracts, assumptions, invariants, and obligations explicit and close to the abstraction.
- Distinguish programmer errors, contract violations, expected failures, retryable failures, permanent failures.
- Treat resource ownership as a contract. Release every acquired allocation on success and failure paths.
- Use tooling as leverage, but understand generated code and tool output before relying on it.
- Debug from reproduced facts: observe, isolate, explain, fix, verify.
- Communicate through code, names, docs, comments, commit messages, scripts, and tests.
- Apply the broken windows rule: fix or visibly contain small quality decay before it normalizes.

## Trigger rules

- When the same fact appears in multiple artifacts, choose one owner and derive the rest.
- When one change requires edits in many unrelated places, repair the missing boundary.
- When uncertainty is high, reduce risk with tracer feedback or a prototype.
- When hidden assumptions live only in comments or tribal setup steps, move them into code or tests.
- When repeated manual steps appear, automate and version them.
- When a human finds a bug, add an automatic regression test.

## Final checklist

- One authoritative owner for each system fact?
- Unrelated concerns independent and volatile choices reversible?
- Working feedback exists for risky assumptions?
- Repeatable work automated and versioned?
- Tests automatic, relevant, and run before done?
