# Binary Analysis — Agent Skill

Give your AI agent the ability to analyze unknown binary files through a deterministic, read-only CLI backed by Ghidra's static-analysis engine.

## Why Install This Skill

You have a binary file and you need to know what it does — but you don't have a
reverse engineer on call. Maybe it's a vendor-supplied library without source
code, a suspicious download, an embedded firmware image, or a legacy executable
your team inherited. You want to answer questions like: What APIs does it call?
Are there any suspicious capabilities? What does this specific function do?

This skill teaches AI agents how to use the `binary` CLI — a non-interactive,
flag-driven analysis harness — to answer those questions systematically. The
agent learns when to run a fast triage versus a deep function-level dive, how to
separate deterministic evidence from interpretation, and how to produce
structured, auditable reports.

After installing this skill, your agent can:
- **Triage unknown binaries** — identify suspicious API imports, assess
  capabilities, and produce evidence-backed reports in under a minute.
- **Decompile and disassemble** specific functions to understand logic without
  source code.
- **Map call graphs and cross-references** to trace how functions relate to each
  other.
- **Extract structural data** — sections, entry points, imports, exports,
  symbols, and strings — with cursor-based pagination.
- **Generate auditable reports** in Markdown, JSON, HTML, or PDF with full
  provenance (binary SHA-256, adapter version, analysis profile).

## What You Get

| Directory | What It Provides |
|-----------|-----------------|
| `SKILL.md` | Agent instructions: trigger rules, workflow phases, safety boundaries, evidence standards, and reference routing. |
| `README.md` | This file — human-facing documentation. |
| `scripts/binary` | The CLI entrypoint — 37 commands across 14 functional groups. Thin argparse wrapper, no network listeners. |
| `scripts/binary_analysis/` | Python package with CLI command implementations, canonical domain model (21 entities, 9 enums), project lifecycle, backend adapters (abstract + fake + Ghidra), reporting engine, rule engine, and optional worker daemon. |
| `references/` | Deep reference docs loaded on demand: installation, CLI reference, binary formats, triage workflow, function analysis, evidence methodology, security rules, packed binaries, firmware, troubleshooting, and reporting. |
| `tests/` | Unit, contract, integration, security, and golden tests with a fake backend for offline testing. |
| `assets/` | Report templates and rule sets. |
| `evals/` | Agent evaluation cases for output-quality verification. |

## Quick Start

### 1. Check your environment

```bash
cd skills/binary-analysis
scripts/binary doctor --json
```

If anything reports `severity: "ERROR"`, the output will include remediation
hints. The bootstrap command can automate setup for PyGhidra:

```bash
scripts/binary bootstrap --apply --json
```

For Java and Ghidra, follow the manual install steps in the doctor output.

### 2. Confirm everything is ready

```bash
scripts/binary version --json
```

Expected output includes `cli_version`, `adapter`, `backend`, and `platform`.

### 3. Run your first triage

```bash
scripts/binary project create my-first-triage --json
scripts/binary import /path/to/suspicious.exe --project my-first-triage --json
scripts/binary analyze --project my-first-triage --json
scripts/binary triage --project my-first-triage --json
```

The triage output separates observations (deterministic facts), heuristics
(rule-derived with confidence scores), and unknowns (unresolved questions).

## Triggers

Your agent will load this skill when you say things like:

- "Analyze this binary" or "What does this executable do?"
- "Decompile this function" or "Show me the pseudocode for..."
- "Is this binary suspicious?" or "What APIs does it import?"
- "Trace the call path from main to socket"
- "Generate a triage report for this firmware image"
- "Check if Ghidra is set up correctly" or "Install the binary analysis tools"

The skill does **not** load for source-code analysis, runtime debugging, binary
patching, or network forensics — those are different domains with their own
skills.

## Requirements

| Dependency | Version | Purpose | Install |
|-----------|---------|---------|---------|
| Python | 3.12+ | CLI runtime and analysis package | System or pyenv |
| Java JDK | 21+ | Ghidra runtime | [Adoptium](https://adoptium.net/) or system package |
| Ghidra | 12.1+ | Static-analysis backend | [ghidra-sre.org](https://ghidra-sre.org/) |
| PyGhidra | 3.1+ | Python bridge to Ghidra | `pip install pyghidra` or `binary bootstrap --apply` |

Set these environment variables before running Ghidra-backed commands:

```bash
export JAVA_HOME="/path/to/jdk-21"
export GHIDRA_INSTALL_DIR="/path/to/ghidra_12.1.2_PUBLIC"
```

Use `scripts/binary doctor --json` to verify your installation at any time.
Commands that don't require Ghidra (project management, fake-backend tests) work
without these variables.
