# AGENTS.md — Agent Guide for agent-skills

This file tells AI agents how to load and use skills from this repository. Skills in this repo follow the [Agent Skills open format](https://agentskills.io) — a standardized way to give agents new capabilities through structured markdown files.

## Format Compliance

Every skill in this repository conforms to the [Agent Skills specification](https://agentskills.io/specification.md):

| Requirement | Rule |
|-------------|------|
| Directory | Each skill in its own directory named by the skill |
| Entry point | `SKILL.md` with YAML frontmatter + markdown body |
| `name` field | Lowercase, hyphens only, matches parent directory name |
| `description` field | Trigger-oriented, describes what and when |
| Progressive disclosure | Core instructions in `SKILL.md` (< 500 lines, < 5,000 tokens), supporting material in `references/`, `templates/`, `scripts/` |
| File references | Relative paths from skill root, one level deep |
| **Human-readable README** | **`README.md`** in skill root — required for every skill. See [README Format](#readme-format) below |

## README Format

Every skill directory **MUST** contain a `README.md` written for a **human audience** (not an AI agent). The README explains what the skill does and why someone would want to install it. It is the public face of the skill — the first thing a human sees when browsing the repository.

### Required Sections

| Section | Purpose |
|---------|---------|
| **Title** | Skill name + one-line summary of what it does |
| **Why Install This Skill** | 2-3 paragraph pitch answering "what problem does this solve for me?" and "what can my agent do after installing this?" — written in plain language, not format docs |
| **What You Get** | Table listing directory contents (scripts, references, templates, assets) and what each provides |
| **Quick Start** | Minimal setup: env vars to export, first command to run (omit for reference-only skills) |
| **Triggers** | List of trigger conditions that tell someone when to load this skill |
| **Requirements** | Dependencies, API keys, Python version, system tools |

### Style Guidance

- **Lead with benefit, not implementation.** Answer "what does this do for me?" before "what tech is it built on?"
- **Be concrete.** Show real command examples with expected output. Avoid abstract descriptions.
- **Assume the reader is human.** No agent instructions, no JSON schemas, no progressive disclosure notes. Those go in `SKILL.md`.
- **Keep it scannable.** Use tables, code blocks, and bullet lists. A human should grasp the skill's purpose in 10 seconds.
- **One page or less.** A README that takes more than a minute to read is too long. Save depth for `SKILL.md`.

### Example

See [data-scientist/README.md](data-scientist/README.md) or any skill in this repository for the canonical format.

## State-Modifying Skills

Skills that change external state must say so explicitly and use this gate before the first mutation:

> Confirm the target, scope, and rollback path before acting. Read-only discovery may proceed without confirmation.

Destructive operations still require an explicit user directive; this convention does not authorize deletion, privilege changes, or irreversible cleanup.

## Failure-Mode Routing

For problem-pattern routing, start with [FAILURE-MODE-INDEX.md](FAILURE-MODE-INDEX.md).

## How to Load Skills

Skills are loaded progressively in three stages:

### Stage 1 — Metadata

At session start, read each skill's `name` and `description` from frontmatter. This takes ~100 tokens per skill and lets you know what's available without loading full content.

```yaml
# Example metadata (from cli-builder/SKILL.md)
name: cli-builder
description: >-
  Build or refactor CLI tools designed for AI agent consumption: non-interactive,
  flag-driven, idempotent, with --json output and --dry-run preview.
```

### Stage 2 — Full Instructions

When a user's request matches a skill's description keywords, load the full `SKILL.md`. The body contains step-by-step instructions, examples, and gotchas. Do not load skills preemptively — only load when triggered.

### Stage 3 — Supporting Files

Reference files (`references/`, `templates/`, `scripts/`) are loaded on demand. The `SKILL.md` tells you when to read each one. Do not load all references at activation time — following the triggers preserves context.

## Reading Order

If this is your first session with this repo, read these in order:

1. [agent-skills/SKILL.md](agent-skills/SKILL.md) — The Agent Skills format reference. Read this first to understand the format.
2. [README.md](README.md) — Skill index with descriptions. Use to discover which skill to load.
3. Individual skill `SKILL.md` files as triggered by the user's task.

## Skill Loading by Trigger

When the user mentions these keywords, load the corresponding skill:

| User says... | Load skill |
|---|---|
| "API design", "design an API", "API contract", "OpenAPI", "AsyncAPI", "GraphQL schema", "REST API", "RPC API", "webhook design", "event schema", "streaming API", "API versioning", "API deprecation", "API migration", "API compatibility", "idempotency key", "pagination design", "API error taxonomy" | [api-design-and-evolution](api-design-and-evolution/SKILL.md) |
| "build a CLI", "make a CLI tool", "agent-friendly CLI", "add --json flag" | [cli-builder](cli-builder/SKILL.md) |
| "SDD", "spec-driven development", "specification driven", "software factory", "spec first", "spec as code", "SPEC.md template", "write a spec for AI", "AI code generation pipeline", "acceptance criteria", "quality gates", "phase gate review", "BDD for AI", "OpenAPI first", "executable specification" | [spec-driven-development](spec-driven-development/SKILL.md) |
| "debug this", "root cause", "why is this broken", "fix this bug" | [systematic-debugging](systematic-debugging/SKILL.md) |
| "Docker Compose", "docker compose", "compose.yaml", "multi-container", "healthcheck", "Compose Watch", "Compose profiles", "Compose networks", "Compose volumes", "Compose secrets", "Compose override" | [docker-compose](docker-compose/SKILL.md) |
| "Woodpecker CI", "woodpecker", ".woodpecker.yml", ".woodpecker/", "Woodpecker agent", "Woodpecker pipeline", "Woodpecker secrets", "Woodpecker plugin", "Woodpecker backend", "Woodpecker build failure" | [woodpecker-ci](woodpecker-ci/SKILL.md) |
| "epub", "ebook", "EPUB file", "ebook format", "read epub", "write epub", "create ebook", "extract from epub", "epub to text", "edit epub", "repair epub", "convert epub2", "epub images", "batch epub", "ebook metadata" | [epub](epub/SKILL.md) |
| "gutenberg", "public domain", "download a book", "classic literature", "free ebook", "gutenberg.org", "project gutenberg", "PG", "gutendex" | [gutenberg](gutenberg/SKILL.md) |
| "self-hosted runner", "github actions runner", "CI runner", "set up a runner", "runner registration", "runner won't register", "autoscaling runners", "runner security", "runner group", "ARC", "Actions Runner Controller", "runner scale set", "myoung34/github-runner", "ephemeral runner", "just-in-time runner", "runner container image", "runner custom image", "runner network", "runner troubleshooting", "runner monitoring" | [github-runner](github-runner/SKILL.md) |
| "hugo theme", "hugo cms", "accessible theme", "wcag theme", "theme design", "theme accessibility", "theme UX", "design tokens", "css theme", "theme contrast", "responsive theme", "hugo template", "hugo pipes", "hugo module", "hugo shortcode", "render hook", "tailwindcss hugo", "hugo i18n", "hugo seo", "hugo output format", "hugo site", "hugo static site" | [hugo-theme](hugo-theme/SKILL.md) |
| "weather", "forecast", "temperature", "is it raining", "Tempest" | [tempest-cli](tempest-cli/SKILL.md) |
| "traefik", "reverse proxy", "load balancer", "API gateway", "Let's Encrypt", "ACME", "Docker routing", "traefik.yml", "entry point", "middleware", "TLS termination", "forward auth", "rate limit" | [traefik](traefik/SKILL.md) |
| "reverse-engineer", "understand this codebase", "PRD from code", "architecture document" | [software-architecture-analysis](software-architecture-analysis/SKILL.md) |
| "data architecture", "data platform", "data strategy", "data mesh", "governance" | [data-architect](data-architect/SKILL.md) |
| "daily check-in", "day debrief", "conversational journaling", "grill me", "interview me about my life", "learn how I work", "what could an AI help me with", "personal AI boundaries", "proactive check-in", "daily life" | [daily-life-discovery](daily-life-discovery/SKILL.md) |
| "financial modeling", "unit economics", "CAC", "LTV", "CAC payback", "pricing strategy", "fundraising", "cap table", "term sheet", "ARR", "MRR", "churn", "NDR", "Rule of 40", "Magic Number" | [financial-modeling](financial-modeling/SKILL.md) |
| "statistical analysis", "experimental design", "A/B test", "hypothesis test", "power analysis", "causal inference", "regression", "Bayesian", "p-value", "effect size", "model selection", "machine learning methodology" | [data-scientist](data-scientist/SKILL.md) |
| "brand identity", "brand guidelines", "style guide", "brand card", "brand strategy", "visual identity", "brand documentation", "color palette", "brand book" | [brand-designer](brand-designer/SKILL.md) |
| "kanban", "WIP", "cycle time", "flow metrics", "Scrum to Kanban", "multi-portfolio", "throughput", "classes of service" | [kanban-guru](kanban-guru/SKILL.md) |
| "kubernetes", "k8s", "kubectl", "k3s", "RKE2", "MicroK8s", "k0s", "Talos", "OpenShift", "EKS", "AKS", "GKE", "Pod", "Deployment", "StatefulSet", "CRD", "RBAC", "NetworkPolicy", "Helm on Kubernetes", "cluster upgrade", "Kubernetes troubleshooting" | [kubernetes](kubernetes/SKILL.md) |
| "langgraph", "multi-agent", "state machine", "graph-based workflow", "LangGraph", "supervisor pattern", "swarm pattern", "agent orchestration", "graph state", "subgraph", "agent routing", "tool-calling loop", "agent loop", "stateful agent", "durable execution", "human in the loop langgraph", "checkpointer", "langgraph persistence" | [langgraph](langgraph/SKILL.md) |
| "debate", "council", "multi-perspective", "structured debate", "get multiple perspectives", "expert panel", "decision landscape", "what would experts say", "what are we missing", "convergence", "false consensus", "agent-council", "pre-mortem" | [agent-council](agent-council/SKILL.md) |
| "skill format", "how do I make a skill", "agentskills.io" | [agent-skills](agent-skills/SKILL.md) |
| "flaresolverr-cli", "FlareSolverr session", "request.get", "request.post", "return-only-cookies" | [flaresolverr-cli](flaresolverr-cli/SKILL.md) |
| "Cloudflare challenge", "DDoS-GUARD", "browser-backed request" | [flaresolverr](flaresolverr/SKILL.md) |
| "Three.js", "three.js", "WebGL", "3D scene", "GLTF", "browser 3D" | [three](three/SKILL.md) |
| "last.fm", "scrobble", "music discovery", "listening history", "similar artists", "lastfm", "weekly top artists", "genre charts" | [lastfm](lastfm/SKILL.md) |
| "MeshCore Companion", "meshcore-packet-capture", "MeshCore packet capture", "BLE radio capture", "serial radio capture", "MeshCore MQTT", "LetsMesh", "PACKETCAPTURE_", "meshcore-packet-capture Docker", "MeshCore NixOS" | [meshcore-packet-capture](meshcore-packet-capture/SKILL.md) |
| "nous", "theia", "hermes brand", "brand identity", "style guide", "mascot", "anime style", "cyber-classical", "color palette reference" | [nous-branding](nous-branding/SKILL.md) |
| "okf", "open knowledge format", "knowledge bundle", "LLM wiki", "agent knowledge", "Google knowledge format", "markdown knowledge", "vendor-neutral knowledge", "create an OKF bundle", "validate OKF", "concept document", "knowledge format" | [open-knowledge-format](open-knowledge-format/SKILL.md) |
| "raleigh", "open data", "city of raleigh", "raleigh data", "crime data", "food inspections", "building permits", "arcgis", "public data", "raleighnc" | [raleigh](raleigh/SKILL.md) |
| "color management", "ICC profile", "sRGB", "CIELAB", "color space", "gamut", "working space", "well-behaved profile", "ArgyllCMS", "xicclu", "color difference", "dE", "soft proof", "display referred", "scene referred" | [color-management](color-management/SKILL.md) |
| "crowdsec", "CrowdSec", "IPS", "IDPS", "WAF", "intrusion prevention", "bouncer", "cscli", "appsec", "LAPI", "remediation component", "community blocklist", "fail2ban", "security engine" | [crowdsec](crowdsec/SKILL.md) |
| "open source", "contributing", "how to contribute", "submit a PR", "file an issue", "CONTRIBUTING.md", "bug report template", "PR template" | [opensource-contributions](opensource-contributions/SKILL.md) |
| "agent eval", "agent evaluation", "LLM eval", "LLM evals", "evaluation dataset", "grader calibration", "model judge", "trajectory review", "agent observability", "agent traces", "agent telemetry", "agent regression", "agent release gate", "privacy-aware telemetry", "prompt evaluation", "model testing" | [agent-evals-and-observability](agent-evals-and-observability/SKILL.md) |
| "pydanticai", "pydantic AI", "pydantic graph", "AI agent", "LLM agent", "agent framework", "function tool", "tool-using agent", "agent with tools", "agent with dependencies", "structured output", "streaming agent", "agent graph", "state machine graph", "GraphBuilder", "BaseNode", "multi-agent", "agent delegation", "TestModel", "FunctionModel", "capabilities" | [pydanticai](pydanticai/SKILL.md) |
| "product discovery", "stakeholder interview", "requirements discovery", "user research", "customer interview", "requirements gathering", "discovery phase", "stakeholder mapping", "interview guide", "discovery conversation", "transcript to spec", "requirements conflict", "what would have to be true", "pre-mortem", "laddering", "assumption busting" | [product-discovery](product-discovery/SKILL.md) |
| "product UX", "product design", "interaction design", "information architecture", "task flow", "user flow", "state model", "recovery path", "interface contract", "UX handoff", "usability study plan" | [product-design-and-ux](product-design-and-ux/SKILL.md) |
| "prioritize", "RICE", "MoSCoW", "opportunity solution tree", "decision log", "write a spec", "product spec", "PRD", "stakeholder communication", "executive brief", "feature prioritization", "backlog ranking", "release scope", "build vs buy", "product decision" | [product-methodology](product-methodology/SKILL.md) |
| "workflow", "figure out my workflow", "analyze my process", "what do I actually do", "catalog my workflow", "formalize my process", "workflow architect", "onboard me to my own process" | [workflow-architect](bundles/workflow-architect/SKILL.md) |
| "default alive", "default dead", "runway", "burn rate", "burn multiple", "financial projection", "startup finances", "cash on hand", "breakeven", "how long until", "profitability" | [yc-default-alive-calculator](yc-default-alive-calculator/SKILL.md) |
| "growth rate", "weekly growth", "monthly growth", "startup growth", "compound growth", "traction", "are we growing", "growth benchmark", "how fast should we grow", "YC growth", "product-market fit", "acceleration", "growth trajectory" | [yc-weekly-growth-compass](yc-weekly-growth-compass/SKILL.md) |
| "artifact-pyramids", "artifact pyramids" | [artifact-pyramids](artifact-pyramids/SKILL.md) |
| "chief of staff", "CoS", "executive office", "gatekeeping", "triage", "decision memo", "executive briefing", "board materials", "force multiplication", "leader effectiveness", "organizational sensing", "organizational radar", "team health", "institutional memory", "leadership transition", "calendar triage", "meeting audit", "strategic time", "attention allocation" | [chief-of-staff-methodology](chief-of-staff-methodology/SKILL.md) |
| "site-reliability-engineering", "site reliability engineering" | [site-reliability-engineering](site-reliability-engineering/SKILL.md) |
| "research and vault", "research-to-notes", "research to durable note", "research extraction and vault", "research-to-note pipeline" | [research-and-vault](bundles/research-and-vault/SKILL.md) |
| "research-methodology", "research methodology" | [research-methodology](research-methodology/SKILL.md) |
| "remote system administration", "remote administration", "remote SSH", "SSH administration", "Ansible administration", "Paramiko automation", "remote Linux", "remote FreeBSD", "remote NetBSD", "remote OpenBSD", "remote macOS", "remote service", "remote firewall", "remote package update", "fleet administration", "fleet rollout", "remote launchctl", "remote rcctl", "remote systemctl" | [remote-systems-administration](remote-systems-administration/SKILL.md) |
| "technical-documentation", "technical documentation" | [technical-documentation](technical-documentation/SKILL.md) |
| "secure software engineering", "build securely", "secure by design", "security requirements", "security acceptance criteria", "threat model this design", "secure code review", "secure defaults", "authorization design", "multi-tenant isolation", "release evidence", "SBOM", "software supply chain", "AI security", "LLM security", "prompt injection", "tool authorization", "RAG security" | [secure-software-engineering](secure-software-engineering/SKILL.md) |
| "security-audit-methodology", "security audit methodology" | [security-audit-methodology](security-audit-methodology/SKILL.md) |
| "mermaid-diagrams", "mermaid diagrams" | [mermaid-diagrams](mermaid-diagrams/SKILL.md) |
| "adr-authoring", "adr authoring" | [adr-authoring](adr-authoring/SKILL.md) |
| "c4-diagramming", "c4 diagramming" | [c4-diagramming](c4-diagramming/SKILL.md) |
| "technology-radar", "technology radar" | [technology-radar](technology-radar/SKILL.md) |
| "strategy", "strategic planning", "OKRs", "strategic narrative", "Five Forces", "Blue Ocean", "competitive positioning", "moat", "Ansoff", "Three Horizons", "market entry", "capital allocation", "M&A evaluation", "BCG Matrix", "portfolio management" | [strategy-frameworks](strategy-frameworks/SKILL.md) |
| "verification-methodology", "verification methodology" | [verification-methodology](verification-methodology/SKILL.md) |
| "accessibility", "a11y", "WCAG", "ARIA", "accessible name", "screen reader", "keyboard navigation", "focus management", "focus trap", "dialog", "modal", "combobox", "listbox", "accessible form", "form validation", "error recovery", "accessible authentication", "color contrast", "reduced motion", "target size", "accessibility testing" | [web-accessibility](web-accessibility/SKILL.md) |
| "seo-audit", "seo audit" | [seo-audit](seo-audit/SKILL.md) |
## Use-When Sections

Every skill description must identify when to load it. Skills with meaningful overlap should also include a `## When not to use` section naming the nearest alternative or prerequisite. Keep these sections trigger-oriented and concise; implementation details belong in references.

## Best Practices

### Do Load by Trigger

The `description` field is the trigger mechanism. If the user's request contains keywords matching a skill's description, load that skill. If multiple skills match, load the most specific one.

### Don't Load Everything at Startup

Loading every skill at session start wastes context. Let the conversation trigger loading. Skills load in ~100 tokens (metadata) and only expand when needed.

### Follow Progressive Disclosure

When a skill body tells you to read a reference file only under specific conditions ("Read this if the API returns a 500"), do not read it proactively. Reference files are for specific edge cases, not general instruction.

### Completion and Exit Conditions

Skills that perform diagnosis, planning, or multi-step work must state when they are complete and when to stop. A valid exit condition is an observable artifact or a bounded escalation, such as: deliver the requested file, confirm the current setup is adequate, or stop after three non-converging diagnostic passes and report the evidence.

## Validate Your Output

When creating or modifying a skill in this repo, validate against the format:
- `name` matches parent directory name
- `description` is 1-1024 chars, non-empty
- Body under 500 lines and 5,000 tokens
- All file references use relative paths from skill root
- Frontmatter YAML is valid
- **`README.md` exists in the skill root** with all required sections (see [README Format](#readme-format) above)
- **README is written for humans** — no agent instructions, JSON schemas, or progressive disclosure notes in the README. Those belong in `SKILL.md`.

### Respect Attribution

Some skills in this repo are adapted from other open-source projects. Attribution is maintained in the source field. Do not remove or modify attribution.

## Troubleshooting

**Skill not loading when expected:** The `description` field may need trigger keyword updates. Check that the user's phrasing overlaps with the skill's description vocabulary.

**Skill body too large:** The agent's context window may be full. The spec recommends under 5,000 tokens per skill. If a skill is exceeding this, its content can be further split into references.

**Reference file not found:** All file references use relative paths from the skill's directory root. If a reference is missing, check that the file exists at the path specified.
