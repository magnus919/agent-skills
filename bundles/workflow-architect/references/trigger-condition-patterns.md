# Trigger Condition Patterns

This reference documents the canonical patterns for writing trigger conditions
in the output bundle's sub-skills. The bundle-builder uses these patterns when
generating each sub-skill's `description` field and "When to use" section.

Trigger conditions tell the agent loader *when* to activate a skill. The more
precise the trigger, the less friction the user experiences.

---

## Trigger Categories

### 1. Keyword-Based

The most common pattern. The skill activates when the user mentions specific
terms. Multiple keywords expand recall.

**Pattern:**
```yaml
description: >-
  Use when the user mentions [keyword], [keyword], or [keyword]. Also
  use when [context description].
```

**Examples:**
- "Use when the user says PR, review, approve, merge, or changes requested."
- "Use when the user mentions debug, bug, broken, error, traceback, or crash."
- "Use when the user says draft, article, write, publish, or blog post."

**Best practices:**
- Include 3-7 keywords — enough to trigger reliably, few enough to stay focused
- Lead with the most specific keyword first
- Use synonyms and common alternates (e.g., "debug" and "fix" for troubleshooting)

---

### 2. Context-Based

The skill activates based on session state, not just user messages.

**Pattern:**
```yaml
description: >-
  [Bare description of when it applies, since context-based triggers are
  agent-determined rather than keyword-driven.]
```

**Examples:**
- "Load this at the start of every first session of the day. It runs the
  morning intake routine."
- "Load this after a tool failure or error. It handles the diagnostics protocol."
- "Load this when a session has been running for 30+ minutes. It suggests a
  wrap-up routine."

**Best practices:**
- Context-based triggers are harder to specify in the Agent Skills format
  (which relies on `description` keywords). Document the context signal
  in the skill's "When to use" section.
- Pair with keyword triggers as fallback: "Use when the user says 'wrap up'
  or when the session has been running for 30+ minutes."

---

### 3. Signal-Based

The skill activates on behavioral patterns, not explicit keywords.

**Pattern:**
```yaml
description: >-
  Use when the user [behavior description]. Activates on [signal type].
```

**Examples:**
- "Use when the user switches tools or context rapidly (3+ distinct requests
  in 5 turns). Helps re-center after context switching."
- "Use when the user pauses for 60+ seconds mid-response. Offers to recap or
  re-establish focus."
- "Use when the user types a `/` command. Handles command dispatch."

**Best practices:**
- Signal-based triggers are the most fragile — they depend on the agent
  detecting patterns in real time
- Document the signal clearly in the body so the agent recognizes it
- Prefer keyword or context triggers when possible

---

### 4. Time-Based

The skill activates on a schedule, not in response to user input.

**Pattern (for cron/scheduled skills):**
```yaml
description: >-
  Cron skill. Runs [schedule] to [purpose]. Use when setting up recurring
  tasks or automated workflows.
```

**Examples:**
- "Runs every morning at 9am. Generates a daily standup summary from the
  previous day's work."
- "Runs every Friday at 5pm. Prompts the user to wrap up open items for the
  week."
- "Runs once per hour during active sessions. Checks for stalled work and
  suggests unblocking actions."

**Best practices:**
- Time-based triggers belong in the skill body, not the description
- The description should still support keyword activation (user might say
  "set up my daily standup")
- Cron scheduling is agent-specific — note compatibility requirements

---

## Writing Trigger Descriptions

Each generated sub-skill's `description` field should follow this formula:

```
Use when [who] [does what] [under what conditions].
[Optional: what the skill provides.]
```

**Examples:**
- "Use when the user starts their morning routine — checking notifications,
  reviewing overnight updates, or prioritizing tasks."
- "Use when the user shifts into building mode — writing code, drafting
  content, or designing. Provides focused work support."
- "Use when the user is wrapping up a session — summarizing decisions,
  filing issues, or saving state for next time."

### Keywords to Include

Pull from the phase's `typical_openers` and `typical_tools` discovered during
the interview:

- **Entry openers:** "check," "review," "what's new," "status," "start"
- **Build openers:** "build," "write," "create," "implement," "design"
- **Review openers:** "review," "look at," "check this," "approve"
- **Wrap openers:** "wrap," "done," "save," "summarize," "ship"

---

## Trigger Condition Manifest Format

The output bundle's `manifest.yaml` maps skills to their trigger conditions:

```yaml
# manifest.yaml
bundle_name: my-workflow
generated: 2026-05-29
archetype: morning-triage-deep-work

skills:
  - name: morning-triage
    file: skills/morning-triage.md
    trigger:
      type: keyword
      keywords: [check, review, overnight, what's new, start, morning]
      description: >-
        Loads when the user opens with status checks,
        review requests, or morning intake language.

  - name: deep-work
    file: skills/deep-work.md
    trigger:
      type: keyword+context
      keywords: [build, write, create, implement, focus]
      context: After morning triage is complete or user skips
                directly to a specific task
      description: >-
        Loads when the user shifts into building or creating mode,
        either after triage or as the session opener.

  - name: wrap
    file: skills/wrap.md
    trigger:
      type: keyword
      keywords: [wrap, done, save, close, ship, summarize]
      description: >-
        Loads when the user signals session completion or wraps up work.
```

Each trigger can have `type` one of: `keyword`, `context`, `signal`, `time`,
or a compound type like `keyword+context`.
