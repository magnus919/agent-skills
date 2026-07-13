# Production Observability and Privacy

Observability provides diagnostic context, not an automatic evaluation verdict. Correlate minimized traces, structured logs, metrics, deployment/configuration identity, and user feedback with a non-identifying invocation identifier. Record sampling rules and bias: errors, high-cost paths, and opted-out traffic may be under- or over-represented.

Default to metadata such as operation class, outcome category, duration, resource counters, and redacted error class. Treat prompt/output text, tool arguments/results, retrieved content, intermediate state, credentials, and personal data as sensitive opt-in data. Minimize before export; use structured allowlists and redaction at the earliest boundary; test redaction; enforce least-privilege access; set purpose-bound retention; support deletion; and maintain incident response and access-audit procedures.

Sampling, retention, access, and alert conditions are local risk decisions. Record their rationale, limitations, failure behavior, and how a privacy incident is contained without expanding collection indiscriminately.

## Telemetry Contract

Define the question before the signal. For each trace, log, metric, or feedback field, record purpose, producer, schema/version, sensitivity, cardinality, sampling, redaction/minimization, access, retention/deletion, correlation, owner, and what happens if collection or export fails. Keep high-cardinality identifiers out of metric labels; use restricted traces or logs for case-level diagnosis.

Useful backend-neutral signals can include:

- invocation/workflow/step outcome and bounded duration;
- model/tool/policy/configuration version identifiers;
- error and stop categories, retry/loop/escalation counts, and tool outcome class;
- resource or billed-usage counters from their authoritative source;
- committed/rolled-back side-effect category; and
- evaluator name/version/result linked by an opaque non-identifying run ID.

Do not synthesize user, conversation, or tenant identity from content. Do not expose chain-of-thought as telemetry. If content is genuinely required for a bounded investigation, use an approved opt-in path with purpose limitation, field allowlists, transformation/redaction before export, restricted access, deletion, and auditable shutdown.

## Alerts, Feedback, And Incident Learning

Alerts should point to an actionable operational condition and owner; they do not establish why quality changed. Define the population, sampling path, expected delay, missing-data behavior, and false-positive/false-negative costs. User feedback, support tickets, judge scores, and anomaly detectors are candidate signals with selection and measurement bias, not automatic labels.

For an incident: contain harm; preserve the smallest authorized evidence; record deployment/configuration and sampling gaps; reproduce in a safe fixture; distinguish agent, tool, data, policy, infrastructure, grader, and telemetry failures; correct the system; then add a transformed regression case only after rights/privacy/contamination review. Verify the fix offline and at the deployed boundary without broadening production capture merely to make diagnosis easier.
