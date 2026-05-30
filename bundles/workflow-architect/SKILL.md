---
name: workflow-architect
description: >-
  Discover your actual workflow through conversation or observation, then generate
  a tailored skills bundle that encodes it as loadable agent skills with trigger
  conditions. Use when you want to understand your own process, formalize it, or
  share it with collaborators. Also use when a session feels aimless — this skill
  gives it structure.
license: MIT
compatibility: >-
  Hermes Agent — uses skill_view(), memory tool, session context scanning,
  and write_file for bundle generation. Output bundles are standard Agent Skills.
metadata:
  tags: [workflow, meta, productivity, skills-bundle, onboarding, process]
  spec-version: "1.0"
---

# Workflow Architect

A meta-skill that helps you (and your agent) understand how you actually work. It
discovers your workflow patterns through either active interrogation or passive
observation, then generates a **skills bundle** — a set of loadable skills, each
with trigger conditions, that encode your workflow so your agent can meet you
where you are in every session.

## What You Get

After running workflow-architect, you'll have a new bundle in your agent's skill
directory containing:

- **Sub-skills** — one per phase of your workflow, each with a `description`
  that tells the agent when to load it (e.g., "load this when the user starts
  their morning triage routine" or "use this when the user shifts into deep work
  mode")
- **A manifest** — maps skill names to their trigger conditions, entry points,
  and transition signals
- **A decision map** — Mermaid flowchart visualizing your workflow as the agent
  sees it
- **A kanban board** (optional) — only included if your workflow follows a
  predictable linear path where WIP limits and lane transitions add value

The generated bundle lives in `~/.hermes/skills/` and is immediately loadable
in future sessions.

## Two Modes

Workflow-architect adapts to how you want to engage with it.

### Mode 1: Active Interrogation (One-Shot)

**When to use:** You have a few minutes to talk through your process. This is
the most thorough mode — the agent asks guided questions, branches based on your
answers, and builds a model of your workflow turn by turn.

**How to invoke:**
```
/workflow-architect
```

The agent will guide you through a conversation of about 8-15 questions.
Answer naturally — the skill adapts its probes based on what you say.

### Mode 2: Passive Observation

**When to use:** You're already in a session doing real work and don't want to
stop and reflect. Let this mode watch what you actually do, then infer the
workflow pattern from your actions.

**How to invoke:**
```
/workflow-architect passive
```

The agent loads the observer skill silently. It does nothing until you say one
of the trigger phrases below, at which point it scans the current session's
message history and reconstructs your workflow from what happened.

**Trigger phrases (say any of these to activate observation analysis):**
- "catalog my workflow"
- "what's my workflow"
- "analyze my process"
- "figure out what I do"
- "work it out from what I just did"

> **Limitation:** Observation mode works best after a session with at least
> 20+ turns of substantive work. If the session context is too thin, the
> observer will suggest switching to active interrogation mode instead.

## Loading Protocol

1. Read this umbrella SKILL.md for context
2. If active: load `skills/interviewer/SKILL.md`
3. If passive: load `skills/observer/SKILL.md`
4. After convergence: load `skills/bundle-builder/SKILL.md` to synthesize
   and write the output bundle
5. The bundle is written to `~/.hermes/skills/<bundle-name>/` — tell the
   user where it landed and what skills it contains

## What the Interview Builds

The interviewer (and observer, through inference) builds a structured model
with these dimensions:

| Dimension | What it captures |
|-----------|------------------|
| **Entry points** | How your sessions typically start |
| **Phases** | The distinct modes or stages in your workflow |
| **Branching signals** | What makes you go left vs right at each fork |
| **Tool preferences** | What you reach for in each phase |
| **Loop conditions** | What keeps you in a mode vs what kicks you out |
| **Exit criteria** | How you know a session is done |
| **Pain points** | What feels frictionful or inefficient |

## Environment

No environment variables required. State is stored via memory tool
with the prefix `workflow-architect:state:` so it persists across turns
during multi-turn interviews.
