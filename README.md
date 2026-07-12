# agent-skills

A collection of AI agent skills — reusable workflows, protocols, and knowledge packs for agentic systems. Skills follow the [Agent Skills open format](https://agentskills.io), making them compatible with any agent framework that supports the standard.

## Skills

### [adr-authoring](adr-authoring/SKILL.md)

Preserve the reasoning behind consequential architecture choices so later contributors can understand, revisit, or supersede them responsibly.

### [agent-council](agent-council/SKILL.md)

Multi-agent structured debate system — spawn a panel of expert agents to debate any question with convergence-aware iteration. Produces a decision landscape with confidence diagnostics, shared risks, remaining disagreements, and a principal's path narrative. Ships as a pip-installable Python package built on PydanticAI + PydanticGraph. `pip install pydantic-ai && pip install agent-council` and one API key to run your first debate.

### [agent-skills](agent-skills/SKILL.md)

Reference for the Agent Skills open format itself — directory structure, frontmatter schema, naming conventions, and progressive disclosure model. Use this meta-skill when creating or reviewing any other skill in this repository.

### [arr-cli](arr-cli/SKILL.md)

Radarr and Sonarr media library management. Two CLIs (`radarr-cli` for movies, `sonarr-cli` for TV series) with one shared skill wrapper. List movies and series, search for additions, check calendars and wanted/missing episodes. Separate API keys per app.

### [artifact-pyramids](artifact-pyramids/SKILL.md)

Structure durable research work so people and agents can start with conclusions, then inspect the analysis and underlying evidence only when needed.

### [autogen](autogen/SKILL.md)

An expert-level skill for building **conversational multi-agent systems** with Microsoft's AutoGen framework. Unlike graph-based or role-based orchestration, AutoGen uses **agent-to-agent conversations** as the orchestration primitive.

### [brand-designer](brand-designer/SKILL.md)

Create comprehensive brand identity documentation for any brand. Guides you through documenting strategy, visual identity (logo, color, typography, imagery), voice and tone, application guidelines, governance, and asset inventory. Produces markdown specs, compiled brand books, and brand-compliant images via reference-image-aware generation. Ships 7 templates, a brand-book CLI for validation/compilation, and a generate script for brand card and mockup imagery.

### [cli-builder](cli-builder/SKILL.md)

Build and refactor CLI tools for AI agent consumption. 10 universal patterns (non-interactive, `--json`, `--dry-run`, idempotent, lazy auth, progressive help), an agent-compatibility test suite, a Python API client pattern, and a bash scaffold template. Principles grounded in real failures from building 15+ agent-facing CLIs.

### [color-management](color-management/SKILL.md)

Expert-level ICC profile color management for open-source workflows. Covers color science fundamentals (CIELAB, xyY, chromaticity), working space selection (sRGB, ProPhotoRGB, ACEScg, Rec.2020), ICC profile operations (convert, assign, extract, embed), gamut analysis, sRGB variant comparison, and color difference (dE) computation. Ships 6 Python scripts that wrap ImageMagick, ArgyllCMS, Exiftool, and LittleCMS; 5 reference files covering overview, operations, tool commands, working space data, and a full glossary. Distilled from Elle Stone's ninedegreesbelow.com and Bruce Lindbloom's color science resources.

### [confluence-cli](confluence-cli/SKILL.md)

Atlassian Confluence from the terminal. List spaces, browse pages, view content with body extraction, search with CQL, and create pages. Same API token as Jira.

### [crewai](crewai/SKILL.md)

An expert-level skill for building **role-based multi-agent teams** with CrewAI. Agents are defined as Roles with Goals and Backstories; crews are composed with sequential or hierarchical workflows.

### [crowdsec](crowdsec/SKILL.md)

Deploy, configure, and manage CrowdSec — the open-source, collaborative IPS/IDPS/WAF. Covers Security Engine installation (Linux, Docker), cscli hub management, remediation components (firewall, Traefik, Nginx), AppSec WAF, profiles, notifications, blocklists, CTI, metrics, and production best practices. Ships 7 reference files for deep dives into config, AppSec, Docker, Traefik integration, database backends, hub collections, and troubleshooting.

### [data-architect](data-architect/SKILL.md)

Act as a virtual data architect. Discover data assets, assess maturity, evaluate platforms, design architectures, establish governance, and create migration plans. Covers modern data patterns (data mesh, data lakehouse, streaming, real-time analytics) with vendor evaluation frameworks and maturity models.

### [data-scientist](data-scientist/SKILL.md)

PhD-level expertise in data science, statistics, and machine learning. Rigorous statistical methodology, experimental design, causal inference, Bayesian analysis, model selection and diagnostics, and research-grade communication. Ships five analysis scripts (power analysis, assumption diagnostics, model comparison, effect size calculator, experimental design generator) with Python + R dual-language support.

### [docker-compose](docker-compose/SKILL.md)
Define, run, debug, and harden multi-container applications with Docker Compose. Covers the Compose Specification, lifecycle and healthchecks, service networking, volumes, secrets, profiles, interpolation, overrides, Compose Watch, CI, production patterns, and troubleshooting. Ships 9 references, 5 templates, and a portable diagnostics script.

### [dspy](dspy/SKILL.md)

An expert-level skill for **programmatic prompt optimization** with Stanford's DSPy framework. You write Python programs with typed signatures; DSPy optimizes the prompts automatically. This is the framework for prompt engineering that doesn't feel like engineering.

### [epub](epub/SKILL.md)

EPUB file format expert — read, write, edit, convert, and repair EPUB2/EPUB3 ebooks.
Ten CLI scripts: structure inspection, text extraction, knowledge extraction (LLM mode
via env vars), scaffold creation, surgical editing, image extraction, batch processing,
EPUB2→3 conversion, repair, and validation. Eight reference files covering format
internals, Python libraries, spec/validation, tutorials, capability discovery,
fixed-layout, accessibility, and media overlays. Portable across any AgentSkills harness.

### [forgejo-cli](forgejo-cli/SKILL.md)

Safe Forgejo API v1 CLI for issues, pull requests, repositories, file contents, metadata, webhooks, and user settings. Includes a guarded generic `/api/v1/` route for version-specific endpoints such as Actions and admin APIs.

### [flaresolverr](flaresolverr/SKILL.md)

Use a private FlareSolverr service through a dependency-free JSON CLI when ordinary HTTP retrieval is blocked by a browser challenge.

### [ghost-cli](ghost-cli/SKILL.md)

Ghost CMS from the terminal. Manage posts and pages, list tags, and check site info. Admin API key from Ghost Integrations. JWT authentication handled automatically.

### [github-runner](github-runner/SKILL.md)

Deploy, manage, and troubleshoot self-hosted GitHub Actions runners. Covers systemd, Docker, Kubernetes (ARC), and Scale Set Client deployments.

### [gutenberg](gutenberg/SKILL.md)

Search, download, and extract public-domain books from Project Gutenberg. Look up books by ID or keyword via gutendex, download plain-text and EPUB editions, strip licensing boilerplate, and classify fiction vs non-fiction. Ships a portable Python CLI with zero external dependencies.

### [haystack](haystack/SKILL.md)

An expert-level skill for building **production search and NLP pipelines** with Haystack. Pipelines are validated DAGs with typed components and explicit connections.

### [hugo-theme](hugo-theme/SKILL.md)

Build, customize, and debug advanced Hugo CMS themes. Covers template architecture, asset pipeline (Hugo Pipes, Tailwind CSS, PostCSS, images), shortcodes and render hooks, page bundles and content adapters, Hugo Modules, performance optimization, SEO/structured data, design/UX/accessibility, custom output formats, and CI/CD. Ships 7 reference files covering each topic area.

### [jellyfin-cli](jellyfin-cli/SKILL.md)

Jellyfin media server from the terminal. Check server info, browse recently added, search your library by type, list libraries, and view statistics.

### [jira-cli](jira-cli/SKILL.md)

Atlassian Jira from the terminal. Search issues with JQL, view details, create issues, add comments, list projects, and transition status. API token from id.atlassian.com.

### [jira-jql](jira-jql/SKILL.md)

Expert-level Jira Query Language reference covering all operators, functions (date/time, user, sprint/version, issue, custom field, JSM), history operators (WAS/CHANGED), relative dates, performance best practices, role-based ready queries, REST API usage, and troubleshooting. Three companion references: complete function catalog, role-specific query bank (dev, scrum master, PO, power user, admin), and gotchas/troubleshooting guide.

### [kanban-guru](kanban-guru/SKILL.md)

A virtual Kanban expert for engineering teams. Diagnose flow problems, design board configurations, calibrate WIP limits, establish service level expectations, set up multi-portfolio operating models, and navigate Scrum-to-Kanban transitions. Covers all seven cadences, classes of service, Little's Law, flow metrics, and the full practitioner's playbook with rich reference material.

### [kubernetes](kubernetes/SKILL.md)

Operate and troubleshoot Kubernetes safely across upstream Kubernetes, k3s, RKE2, MicroK8s, k0s, Talos, OpenShift/OKD, kind, Minikube, Rancher, EKS, AKS, and GKE. Covers workloads, APIs, version skew, networking, storage, scheduling, autoscaling, security, policy, backups, upgrades, observability, and evidence-first diagnosis. Ships the agent-first `k8s-cli` wrapper, diagnostic scripts, templates, and dated source references.

### [langchain](langchain/SKILL.md)

An expert-level skill for building LLM-powered applications with LangChain — the most widely adopted LLM orchestration framework. LCEL chains, RAG pipelines, agents, LangSmith observability, and LangServe deployment.

### [langgraph](langgraph/SKILL.md)

Build multi-agent AI systems with LangGraph — the low-level orchestration framework for stateful, graph-based agent workflows using directed graphs. Covers all major patterns: supervisor (centralized routing node, ~94% accuracy), swarm (direct agent-to-agent handoffs, ~40% fewer LLM calls), and hierarchical teams (subgraph composition with nested state). Includes state management (checkpointers/stores), persistence, production debugging, and evaluation methodology. Ships 3 Python scripts (supervisor scaffold, swarm scaffold, eval generator), 3 runnable templates, and 8 reference files covering architecture, each pattern in depth, evals, production failures, and troubleshooting.

### [lastfm](lastfm/SKILL.md)

Last.fm music data API from the terminal. Lookup user listening history, get artist/album/track metadata, discover similar music via collaborative filtering, explore global and per-country charts, search, manage tags, and scrobble listening events. API key from last.fm/api/account/create (free). Includes a music discovery pipeline for turning liked tracks into recommendations.

### [lidarr-cli](lidarr-cli/SKILL.md)

Manage your Lidarr music library from the terminal — search and browse artists and albums, add new artists, check calendars, view queue and download history.

### [llamaindex](llamaindex/SKILL.md)

An expert-level skill for building LLM applications over your data with LlamaIndex. RAG pipelines, multi-agent orchestration, event-driven workflows, knowledge graph construction, and production deployment.

### [mermaid-diagrams](mermaid-diagrams/SKILL.md)

Create maintainable diagrams that render reliably in the documentation surfaces where readers actually encounter them.

### [meshcore-packet-capture](meshcore-packet-capture/SKILL.md)

Operate MeshCore Companion radio packet capture over BLE, serial, or TCP. Covers MQTT publishing, TOML and environment configuration, token authentication, Docker, systemd, launchd, NixOS, and evidence-first troubleshooting.

### [nous-branding](nous-branding/SKILL.md)

Generate images and content consistent with the Nous Research brand identity.
Ships four reference images (color palette card, official high-res mascot,
brand collage) that can be used as img2img inputs. Covers the Nous Girl
mascot specs, cyber-classical art style, texture system (risograph grain,
CRT scan lines, photocopy noise), hex-accurate color palette, and image
prompt templates for text-only and reference-image-driven workflows.

> **Cross-pollination note:** This skill was developed in parallel with [plntrprotocol/nous-branding](https://github.com/plntrprotocol/nous-branding) — a sibling project created independently, in friendship, for the same purpose. We've been learning from each other's approaches throughout development, and each repo has strengths the other doesn't. If you're using ours, go check out theirs too.

### [open-knowledge-format](open-knowledge-format/SKILL.md)

Google's Open Knowledge Format (OKF) v0.1 — create, validate, and consume vendor-neutral AI agent knowledge bundles. Markdown files with YAML frontmatter, organized in directory hierarchies with cross-links and progressive disclosure. Ships a validation script, concept template, example bundle, and detailed references covering the spec, bundle architecture, and real-world use cases.

### [openlibrary-cli](openlibrary-cli/SKILL.md)

Open Library book metadata from the terminal. Search books and authors, get work and edition details, lookup by ISBN. No API key required — the public Open Library API is free for everyone.

### [opensource-contributions](opensource-contributions/SKILL.md)

Comprehensive open source contribution guidance — from reading CONTRIBUTING.md and filing good bug reports through branching, committing, PR creation, and the release cycle. Covers both contributor and maintainer workflows with progressive disclosure: a concise orchestrator SKILL.md loads detailed phase references on demand. Includes a portable PR template compliance checker script. Agent disclosure template for AI-assisted contributions.

### [peertube](peertube/SKILL.md)

PeerTube federated video platform from the terminal. Browse videos and channels, search across instances, view server info. OAuth2 login with token persistence. Set PEERTUBE_SERVER to point at any instance.

### [product-discovery](product-discovery/SKILL.md)

Discover product requirements from human stakeholders — map who to talk to, ask questions that surface hidden assumptions, detect gaps in real time, resolve conflicts, and translate conversations into structured specs. Phase 0 upstream of any spec-driven pipeline. Ships 8 reference files covering stakeholder mapping, question patterns, gap detection, conflict resolution, transcript-to-spec distillation, AI-conducted discovery, power dynamics, and time-constrained discovery; plus 5 templates (discovery plan, interview guide, distillation worksheet, gap register, interpretation log).

### [prowlarr-cli](prowlarr-cli/SKILL.md)

Manage your Prowlarr indexer hub from the terminal — list and inspect indexers, view query/grab statistics, check health, manage connected *arr applications, and test indexer connectivity.

### [pydanticai](pydanticai/SKILL.md)

Build production-grade AI agents and graph-based state machines with PydanticAI and PydanticGraph. Covers agent creation, function tools with RunContext dependencies, structured output validation, streaming (text/events/graph nodes), a 20+ capability plugin system with on-demand loading (Thinking, WebSearch, MCP, Hooks, etc.), 16 model providers with FallbackModel and concurrency limiting, multi-agent delegation and programmatic hand-off, comprehensive testing with TestModel/FunctionModel, and the PydanticEvals evaluation framework. Includes the full PydanticGraph API — both BaseNode (class-based) and GraphBuilder (function-based) with parallel map/broadcast operations, joins with reducers, decisions, Mermaid rendering, and step-by-step execution. Ships 8 reference files covering core agents, capabilities/hooks, graph, models/output, patterns/integrations, testing/evals, worked examples, and an API surface quick reference.

### [raleigh](raleigh/SKILL.md)

Query, search, and download public datasets from the City of Raleigh Open Data portal. Wraps the ArcGIS REST API to access 170+ datasets — crime reports, food inspections, building permits, bike lanes, parks, zoning, traffic, budgets, and more. No API key needed. Ships a Python CLI with catalog, search, info, query, download, and categories commands.

### [research-methodology](research-methodology/SKILL.md)

Turn an open question into a bounded, evidence-led investigation rather than a plausible-sounding synthesis.

### [security-audit-methodology](security-audit-methodology/SKILL.md)

Give authorized teams a disciplined way to identify and prioritize security risks without mistaking a checklist for a security guarantee.

### [site-reliability-engineering](site-reliability-engineering/SKILL.md)

Build practical reliability practices around the work teams actually perform: measurable service objectives, useful alerts, incident response, and learning-oriented follow-up.

### [software-architecture-analysis](software-architecture-analysis/SKILL.md)

Reverse-engineer a software codebase to understand its architecture, data flow, privacy posture, and feature surface — then produce a clean-room design document, PRD, or migration plan under new constraints (local-first, privacy-first, self-hosted). Includes an interface extraction pattern for designing swappable storage provider abstractions.

### [spec-driven-development](spec-driven-development/SKILL.md)

Spec-Driven Development (SDD) methodology for AI software factories — where structured specifications are the input, AI agents generate the code, and quality gates enforce correctness at each pipeline phase. Covers the 5-phase pipeline (SPECIFY → DECOMPOSE → IMPLEMENT → VERIFY → DELIVER), 4 phase gates with APPROVED/CONDITIONS/REJECTED verdicts, 7 spec quality gates, a methodology selection matrix (BDD, OpenAPI, AsyncAPI, DbC, TLA+, ADRs, C4), NFR encoding patterns, format translation (PRD → SPEC.md → Gherkin → OpenAPI), gate recovery and revision workflows, and a worked example SPEC.md. Ships 4 templates, 9 reference files, and 2 validation scripts. Tool-agnostic — works with Claude Code, Cursor, Hermes Agent, Devin, OpenHands, and droid.

### [systematic-debugging](systematic-debugging/SKILL.md)

4-phase root cause debugging protocol: understand bugs before fixing. Covers schema/environment divergence, exception type specificity in fallback chains, progressive characterization grids for API/retrieval failures, dependency source detection (editable dev forks), macOS sandboxed application debugging, and the Rule of Three for recognizing architectural problems. Adapted from [obra/superpowers](https://github.com/obra/superpowers) (MIT) with significant expansion from real-world use.

### [technical-documentation](technical-documentation/SKILL.md)

Make documentation useful at the moment someone needs to install, operate, extend, or troubleshoot a system.

### [three](three/SKILL.md)

Build browser-based Three.js and WebGL scenes, animations, and interactive 3D visualizations.

### [tempest-cli](tempest-cli/SKILL.md)

Hyper-local weather from a WeatherFlow Tempest station. Query current conditions, 7-day forecast, historical observations, and real-time UDP broadcasts. A complete reference implementation of the cli-builder patterns in a working, testable project — including the CLI binary and full API field layout reference.

### [tmdb-cli](tmdb-cli/SKILL.md)

The Movie Database API from the terminal. Search and discover movies and TV by genre, certification, rating, and date range. Check trending, upcoming, and now playing. Free API key from themoviedb.org.

### [traefik](traefik/SKILL.md)

Deploy, configure, secure, and maintain Traefik v3 reverse proxy — Docker provider, HTTP/TCP/UDP routing, TLS/ACME (Let's Encrypt), middlewares, observability, API, and production deployment. Covers the full static config schema, all 25+ built-in middlewares with YAML config, ACME certificate resolvers with DNS-01/HTTP-01/TLS-ALPN-01 challenges, Docker label reference for routers/services/middlewares, TCP/UDP routing with SNI matching, Prometheus/OpenTelemetry metrics and access logs, and production-ready Docker Compose deployments with security hardening. Ships 10 reference files covering every major feature area.

### [trakt](trakt/SKILL.md)

Trakt.tv media discovery from the terminal. Browse trending, anticipated, and popular movies and TV shows. Read-only — uses only a Client ID, no OAuth required.

### [transistor](transistor/SKILL.md)

Transistor.fm podcast hosting from the terminal. Manage shows and episodes, view subscriber analytics. API key from transistor.fm settings.

### [woodpecker-ci](woodpecker-ci/SKILL.md)
Operate self-hosted Woodpecker CI from installation through production troubleshooting. Covers Forgejo/Gitea integration, server and agent setup, Docker and Kubernetes backends, workflow syntax, secrets, plugins, matrices, CLI/local execution, upgrades, security, and incident response.

### [yc-default-alive-calculator](yc-default-alive-calculator/SKILL.md)

Paul Graham's "Default Alive / Default Dead" framework as a deterministic CLI tool. Given revenue, burn rate, cash on hand, and growth rate, compute whether a startup will reach profitability before running out of money. Ships a month-by-month projection engine, burn multiple analysis, lever identification, and actionable verdict (ALIVE / DEAD / MARGINAL). Python 3.9+ with zero external dependencies.

### [yc-weekly-growth-compass](yc-weekly-growth-compass/SKILL.md)

Paul Graham's "Startup = Growth" framework as an operational weekly practice. Computes growth rates from single-period or time-series data, benchmarks against YC tiers (1% concerning → 10%+ outstanding), projects compound growth, and frames every decision through the compass question: "Does this serve your target growth rate?" Python 3.9+ with zero external dependencies.

## Bundles

Bundles organize related skills under a single umbrella with shared reference material and auto-loading by trigger context.

### [tailscale](bundles/tailscale/SKILL.md)

Self-hosted Tailscale/Headscale VPN ecosystem. Seven sub-skills covering Headscale server deployment, ACL/tailnet policy authoring, Tailscale client configuration, node lifecycle (auth keys, registration, tagging, decommissioning), subnet routing and exit nodes, DERP relay infrastructure, and backup/migration. Ships 23 scripts with `--json` and `--dry-run` support, 8 reference documents, and 6 templates.

### [workflow-architect](bundles/workflow-architect/SKILL.md)

Discover your actual workflow through conversation or passive observation, then generate a tailored skills bundle that encodes it as loadable agent skills with trigger conditions. Dual mode: active interrogation (guided 8-15 question interview) or passive observation (analyzes session context from what you actually did). Output includes sub-skills per workflow phase, a manifest with trigger conditions, a Mermaid decision map, and optionally a kanban board if the workflow is linear. Ships 3 sub-skills, 3 reference documents, 4 templates, and a worked example output bundle.

---

## Installation

Skills don't require installation in the traditional sense. They are loaded by your AI agent when triggered. Each agent framework documents its own skill directory path and loading mechanism — follow the links below for the authoritative setup guide for your harness.

| Harness | Setup Guide |
|---------|-------------|
| **Claude Code** | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) |
| **OpenCode** | [opencode.ai/docs/skills](https://opencode.ai/docs/skills) |
| **OpenAI Codex** | [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills) |
| **GitHub Copilot** | [docs.github.com/en/copilot/concepts/agents/about-agent-skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) |
| **Cursor** | [cursor.com/docs/context/skills](https://cursor.com/docs/context/skills) |
| **Gemini CLI** | [geminicli.com/docs/cli/skills](https://geminicli.com/docs/cli/skills) |
| **Hermes Agent** | See below |

### Hermes Agent

Hermes Agent loads skills from `~/.hermes/skills/`, organized by category subdirectory:

```bash
cp -r cli-builder ~/.hermes/skills/devops/
cp -r systematic-debugging ~/.hermes/skills/software-development/
cp -r tempest-cli ~/.hermes/skills/devops/
```

Hermes loads skill metadata at session start. Use the `/skills` command to list available skills, and `skill_view(name)` to load a specific skill's full instructions. Skills can also be pinned for persistent availability.

### Generic / Other Frameworks

The [agentskills.io clients page](https://agentskills.io/clients) maintains an up-to-date list of every agent framework that supports the Agent Skills format, with links to each one's setup instructions. Any framework listed there can load these skills — follow that framework's specific documentation for the correct directory path and loading mechanism.

For frameworks without built-in skill loading, the format is intentionally simple:

1. Place the skill directory in your agent's accessible file path
2. The agent reads `SKILL.md` when triggered by keywords in the task
3. Supporting files in `references/`, `templates/`, and `scripts/` are loaded on demand

You can also instruct your agent to read specific `SKILL.md` files at session start, or reference skills in your agent's system prompt or CLAUDE.md/AGENTS.md.

---

## Contributing

Skills follow the [Agent Skills specification](https://agentskills.io/specification.md). See [CONTRIBUTING.md](CONTRIBUTING.md) for the contributor workflow, [the Code of Conduct](CODE_OF_CONDUCT.md) for community expectations, and `AGENTS.md` for agent-specific loading and compliance guidance.

Before submitting a new skill:
1. Ensure `SKILL.md` has valid YAML frontmatter (required: `name`, `description`)
2. The `name` field must match the parent directory name
3. Keep `SKILL.md` under 500 lines and 5,000 tokens
4. Move detailed reference material to `references/` for progressive disclosure
5. Run the canonical-skill validator: `ruby scripts/validate-skills.rb` (vendored `agent-council/profiles/skills/` content is intentionally excluded)
6. Validate with `skills-ref validate ./my-skill` if available

---

## License

MIT — see [LICENSE.md](LICENSE.md) for full terms.
