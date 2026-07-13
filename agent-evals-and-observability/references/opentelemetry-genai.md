# Optional OpenTelemetry GenAI Interoperability

OpenTelemetry GenAI semantic conventions are an optional interoperability layer, not this skill's canonical data model or a prerequisite for evaluation. The `open-telemetry/semantic-conventions-genai` repository was checked at commit `63f8200eee093730ce845d26ce2aafb621b0807e` on 2026-07-13 and labeled Development. Verify current status and canonical names before adopting any convention.

If useful, map local concepts such as agent invocation, model request, tool execution, workflow step, evaluator result, duration, token/resource use, and correlation to the then-current conventions. Keep an internal event contract that works without OTel and avoid copied example hostnames, paths, prompts, model names, or histogram bucket boundaries.

Prompt and output content are opt-in and sensitive under this guidance. Do not enable content capture by default; apply the minimization, redaction, access, retention, deletion, and incident controls in [production observability](production-observability.md) first.
