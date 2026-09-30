# Tools, environment, and lifecycle

A custom runtime needs an explicit action loop: assemble context, call model,
validate the requested action, authorize, execute, observe, checkpoint, and decide
continue/stop/escalate. Keep the model's proposal separate from execution authority.

## Tool affordances

Use bounded typed inputs, structured results, timeouts, cancellation, and errors
that distinguish denial, bad input, unavailable dependency, and execution failure.
Report enough context to correct a call without leaking secrets. A tool that hides
stderr or truncates a decisive error makes feedback unreliable.

Classify concurrency per call and resource, not merely by tool name. Two reads may
be safe; a read during a migration or two writes to one file may not be. Keep
permission decisions tied to target, identity, current scope, and exact operation.
Do not cache an authorization result across changed arguments or state.

Fail closed on sensitive actions and enforce controls outside the prompt. Sandbox
untrusted code and treat retrieved instructions as data. Log minimal redacted
operation/decision references, not unrestricted command output or personal data.

## Reproducible environment

Inspect lockfiles, runtime pins, CI, service health, credentials handling, and
network assumptions. Split setup/readiness from verification: installing packages
on every check can mutate lockfiles and consume time. Use an isolated checkout for
concurrent work, and explicit service teardown ownership. A process being alive
is weaker evidence than readiness for the requested task.

## Lifecycle

Startup reads authoritative intent/state, checks the current revision and dirty
work, validates environment, and picks bounded work. End-of-session records what
actually happened, incomplete checks, and recovery instructions. Clean means
restartable with known state; it does not authorize git reset, deleting files, or
committing someone else's work.

Test denial, dependency failure, timeout, partial write, cancellation, and resume.
Hooks must use the runtime's actual trust and failure semantics; product-specific
claims need pinned primary documentation or source before implementation.
