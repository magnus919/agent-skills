---
name: interviewer
description: The active interrogation sub-skill for workflow-architect. Guides the
  user through 8-15 adaptive questions to discover their workflow phases, branching
  signals, tool preferences, and friction points. Loaded by the umbrella workflow-architect
  skill when running in active mode.
license: MIT
compatibility: Hermes Agent — uses memory tool for state persistence
metadata:
  tags: workflow, interview, discovery, process
  spec-version: '1.0'
---

# Interviewer — Active Workflow Discovery

This is the core of workflow-architect's **active interrogation mode**. It runs
a structured but adaptive conversation with the user to discover how they work.

## State Model

The interview builds a structured representation of the user's workflow.
State is stored via the memory tool with the prefix
`workflow-architect:state:` so it survives across turns.

```yaml
state:
  entry_points: []          # How sessions start
  phases: []                # Distinct phases discovered
    - name: string
      description: string
      typical_tools: []
      typical_openers: []   # What user says to enter this phase
      typical_exits: []     # What user says to leave this phase
  branching: []             # Decisions and what drives them
  pain_points: []
  exit_criteria: []         # How sessions end
  archetype: null           # Best match from workflow-archetypes
  convergence_score: 0      # 0.0 to 1.0 — enough to generate bundle?
```

## Question Progression

The interview follows a branching script. Each answer feeds the state model
and determines the next probe. Do not ask all questions sequentially — adapt
based on what the user has already told you.

### Phase 1: Session Opener (1-2 questions)

Start broad. The goal is to understand the user's self-model of their workflow.

```
Agent: "Walk me through a typical session from the very start.
        What's the first thing you do when you open this agent?"

User:  "I usually check my task list, see what's urgent, and jump into the
        most pressing issue."

Agent: [Records entry point: "check task list, prioritize by urgency"]
       [Probes for structure: "After that initial triage — what happens
        next? Does the session settle into a rhythm?"]
```

**Alternative openers** (pick one based on the user's stated context):
- "Describe a session that went really well. What did it look like from start to finish?"
- "What does a typical day look like, broken into sessions?"
- "If I looked at your last 10 sessions, what patterns would I see?"

### Phase 2: Phase Discovery (2-4 questions)

Probe for distinct modes or stages. Listen for transition language.

Key probes (use as follow-ups, not a checklist):
- "After that first step — what determines what you do next?"
- "Are there different *modes* you shift between? Like triage mode vs building mode vs research mode?"
- "What does a deep work session look like vs a quick check-in session?"
- "Do you find yourself switching between types of work within a single session?"

**Branching detection — listen for these signals:**
- "If X, then Y" — conditional logic in the workflow
- "Depends on whether..." — branching signal
- "Usually I do A, but sometimes I do B" — mode distinction
- "After that I always..." — deterministic phase transition

When you hear a branching signal, probe it:
```
User:  "If there are open PRs assigned to me, I review those first.
        Otherwise I look at my kanban board."
Agent: [Records branching signal: "pending PRs → review mode,
        otherwise → kanban triage"]
       "Got it. After you finish the PR review — what's the signal
        that tells you you're done with that and ready to move on?"
```

### Phase 3: Tool & Context Probe (2-3 questions)

Map tools, context needs, and environmental patterns.

- "In each of those modes — what tools do you reach for? Any commands you type over and over?"
- "Are there specific files, boards, or dashboards you check first thing?"
- "Do you work better in certain contexts? (Morning vs afternoon, quiet vs busy, alone vs paired)"

### Phase 4: Pain Point & Flow Probe (1-2 questions)

The most valuable output of this skill is identifying where the workflow
breaks down. Be patient here — users often haven't articulated this.

- "Is there a step in this flow that consistently feels harder than it should be?"
- "If you could wave a wand and fix one thing about how you work, what would it be?"
- "Is there a hand-off or transition that always feels clunky?"

### Phase 5: Exit & Rhythm Probe (1-2 questions)

- "How do most of your sessions end? Do you have a wind-down routine?"
- "Do you ever leave sessions abruptly? What causes that — interruption, fatigue, task completion?"

### Phase 6: Convergence Check

After each answer, evaluate whether you have enough to generate a useful bundle.

**Minimum convergence criteria:**
- At least 3 phases identified (can include entry as a phase)
- Entry points documented
- At least one branching signal
- Tools mapped to at least 2 phases
- Exit criteria identified
- Convergence score >= 0.6

**Convergence scoring:**
| Criteria met | Score contribution |
|---|---|
| 3+ phases | 0.3 |
| Entry points known | 0.15 |
| Branching signals found | 0.2 |
| Tools mapped to 2+ phases | 0.15 |
| Exit criteria known | 0.1 |
| Pain points identified | 0.1 |

When convergence score >= 0.6, present a summary to the user:

```
"I think I have enough to generate your workflow bundle. Here's what
I've mapped out so far:

[Summary of phases, branching, tools, and pain points]

Does this look like an accurate picture of how you work?
If yes, I'll generate the bundle. If not, tell me what I got wrong
and I'll refine it."
```

If the user confirms, load `skills/bundle-builder/SKILL.md` and follow its
instructions to generate the output bundle.

If the user corrects or refines, update the state and re-check convergence.

## State Persistence

Use the memory tool to persist state across turns:

```
memory(action='add', target='memory',
       content='workflow-architect:state:entry_points=["check task list, prioritize"]')
```

Use a known key prefix per dimension so the bundle-builder can read all
state entries:

| Key | Value type |
|-----|------------|
| `workflow-architect:state:entry_points` | JSON array |
| `workflow-architect:state:phases` | JSON array of phase objects |
| `workflow-architect:state:branching` | JSON array of signal objects |
| `workflow-architect:state:pain_points` | JSON array |
| `workflow-architect:state:exit_criteria` | JSON array |
| `workflow-architect:state:convergence_score` | Float 0-1 |
| `workflow-architect:state:archetype` | String or null |

**Important:** On the final turn (after bundle generation), clean up these
memory entries so they don't pollute future sessions:
```
memory(action='remove', target='memory',
       old_text='workflow-architect:state:')
```

The bundle-builder sub-skill handles reading all `workflow-architect:state:*`
entries from memory and writing the output bundle files.

## Archetype Matching

After each answer, check the shared `../../references/workflow-archetypes.md` file to see
if the user's answers match a known archetype. If they do, note it in state
and use it to seed better follow-up questions (e.g., "For a morning triage
workflow, people often have a 'stale items bucket' — do you have something
like that?")
