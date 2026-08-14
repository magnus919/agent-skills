# promise-theory — trigger probes

Harness-specific activation tests for the `promise-theory` skill. These probes
evaluate whether a client should load the skill from its frontmatter
`description` alone (no `SKILL.md` body, no references). They live **only**
here, separate from `evals/evals.json`, which carries output-quality cases with
machine-parseable assertions.

## How to run

Give a fresh agent (with no prior promise-theory knowledge) **only** the
frontmatter `description` below plus the probe prompt, and ask it to decide
whether to load the skill. Record the decision; it must match the expected
decision stated for the probe. The expected decisions are grounded in the
description's trigger vocabulary and its negative boundary.

The skill `description` the probes are evaluated against:

> Design and diagnose coordination in hybrid human + AI agent workforces using
> promise theory (Burgess/Bergstra): model agents as autonomous, coordination
> as voluntary offers plus acceptance, and trust as calibrated assessment. Use
> for delegation modeling, capability manifests and agent contracts,
> coordination-failure diagnosis, trust/verification calibration, convergent
> self-healing systems, and converting obligation-based designs to
> promise-based. Do not use for enforceable centralized control, legal contract
> drafting (promise theory is not contract law), simple single-agent prompting,
> imperative push-based orchestration, or tool manuals — route those to the
> tool's own skill.

## Should-trigger probes

Prompts that must activate the skill. Each is an in-boundary coordination
task whose vocabulary matches the description's triggers (delegation modeling,
capability manifests, coordination-failure diagnosis, trust/verification
calibration, obligation-to-promise conversion).

### Probe ST-1 — delegation protocol design (should trigger)

- **Prompt:** "Design a delegation protocol for my agents — I have a researcher, a writer, and a reviewer, and I want each one to declare what it will do and record who accepts what before work starts."
- **Expected decision:** activate. The task asks each agent to declare what it will do and to record who accepts what — matching the description's trigger vocabulary ("delegation modeling", "capability manifests", "voluntary offers plus acceptance").

### Probe ST-2 — promise manifest drafting (should trigger)

- **Prompt:** "Draft a promise manifest for our 3-agent research team with human oversight."
- **Expected decision:** activate. Drafting a promise manifest is the description's core use case ("capability manifests and agent contracts", "delegation modeling").

### Probe ST-3 — coordination-failure diagnosis (should trigger)

- **Prompt:** "Diagnose why our two agents keep disagreeing about who writes the final summary."
- **Expected decision:** activate. This is a coordination failure between agents, which the description names explicitly ("coordination-failure diagnosis", "design and diagnose coordination in hybrid human + AI agent workforces").

### Probe ST-4 — trust calibration (should trigger)

- **Prompt:** "We are onboarding a new agent with no track record. How much should we trust it, and how often should we verify its output?"
- **Expected decision:** activate. The task asks for a starting trust level and a verification rate, matching the description's "trust as calibrated assessment" and "trust/verification calibration".

### Probe ST-5 — obligation-to-promise conversion (should trigger)

- **Prompt:** "Help me convert this obligation-based design into promises — right now we push tasks with mandates."
- **Expected decision:** activate. Converting obligation-based designs to promise-based ones is a named trigger in the description ("converting obligation-based designs to promise-based").

## Should-not-trigger probes (near-misses)

Prompts adjacent to the skill's territory that must **not** activate it. The
set collectively exercises the description's negative boundary: enforceable
centralized control, legal contract drafting, simple single-agent prompting,
imperative push-based orchestration / tool-manual routing, and sibling-overlap
deactivation.

### Probe SN-1 — deployment script near-miss (should not trigger)

- **Prompt:** "Write a bash script to deploy my server — just an imperative script that pushes the code and restarts the service."
- **Expected decision:** do not activate. The task is an imperative push-based orchestration script with no consent modeling — explicitly excluded by the description ("imperative push-based orchestration") — and a plain scripting task is better routed to a scripting or tool skill.

### Probe SN-2 — fully controlled fleet near-miss (should not trigger)

- **Prompt:** "I have a fleet I fully control; I just need the config pushed to all servers — no consent model needed."
- **Expected decision:** do not activate. Enforceable centralized control is a named anti-trigger ("Do not use for enforceable centralized control"); with direct command-and-verify authority, the promise machinery is overhead.

### Probe SN-3 — legal contract near-miss (should not trigger)

- **Prompt:** "Draft a legally binding services agreement between my company and a vendor."
- **Expected decision:** do not activate. Legal contract drafting is explicitly out of the description's boundary ("legal contract drafting (promise theory is not contract law)"); the task belongs to legal counsel or a contract-drafting skill.

### Probe SN-4 — single-agent prompting near-miss (should not trigger)

- **Prompt:** "Write me a single prompt for one LLM to summarize this meeting transcript."
- **Expected decision:** do not activate. This is simple single-agent prompting with no delegation graph to model, which the description excludes ("simple single-agent prompting").

### Probe SN-5 — tool-manual routing near-miss (should not trigger)

- **Prompt:** "Show me the helm CLI command to install a chart and list its flags and examples."
- **Expected decision:** do not activate. The user needs a specific tool manual, which the description routes away ("or tool manuals — route those to the tool's own skill"); the correct target is the `helm` / kubernetes tooling skill, not promise theory.

### Probe SN-6 — sibling-overlap deactivation (should not trigger)

- **Prompt:** "I want to build an eval set that gates our agent's releases and catches regressions — how should the datasets, graders, and release gate be designed?"
- **Expected decision:** do not activate. This is an evals/observability design question that belongs to the `agent-evals-and-observability` sibling skill; promise theory models promises and assessment, but the assessment-layer implementation routes to the sibling skill, so activating promise-theory here would be a false positive.

## Boundary coverage checklist

| Anti-trigger boundary | Probes exercising it |
|-----------------------|----------------------|
| Enforceable centralized control | SN-1, SN-2 |
| Legal contract drafting | SN-3 |
| Simple single-agent prompting | SN-4 |
| Imperative push-based orchestration / tool-manual routing | SN-1, SN-5 |
| Sibling-overlap deactivation | SN-6 |

Counts: 5 should-trigger probes (≥3 required) and 6 should-not-trigger
near-misses (≥4 required), each with an explicit expected decision.
