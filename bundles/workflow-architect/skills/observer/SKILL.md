---
name: observer
description: The passive observation sub-skill for workflow-architect. Loaded silently,
  it stays dormant until a trigger phrase activates it. On activation, it scans the
  current session context to infer the user's workflow from what actually happened.
license: MIT
compatibility: Hermes Agent — uses session_search and context scanning
metadata:
  tags: workflow, observation, discovery, passive
  spec-version: '1.0'
---

# Observer — Passive Workflow Discovery

This is the **passive observation mode** of workflow-architect. Unlike the
interviewer, which asks questions, the observer *watches and infers*.

## How It Works

1. The observer loads silently via `/workflow-architect passive`
2. It does nothing until a trigger phrase is detected
3. On trigger, it scans the current session's message history using a
   structured inference prompt
4. The output is a workflow state model (same structure as the interviewer
   produces), which feeds into the bundle-builder sub-skill

## Trigger Phrases

The observer activates when the user says any of these:
- "catalog my workflow"
- "what's my workflow"
- "analyze my process"
- "figure out what I do"
- "work it out from what I just did"

If none of these are detected in the user's message, the observer remains
dormant. Do not announce its presence — the user may not remember loading
it in passive mode.

## Activation Protocol

When a trigger phrase is detected:

1. **Check session depth.** Count substantive user messages (excluding
   greetings, meta-comments about the agent, and one-word replies). If
   fewer than 5 substantive messages, respond:

   ```
   "I don't have enough session context to work with yet. I've seen about
   [N] substantive turns, and I need more to find reliable patterns.
   Try active interrogation mode instead: /workflow-architect"
   ```

2. **If enough context exists, run inference.** Use the following structured
   prompt against the session context. You may use session_search or browser
   console to review the session transcript if needed.

   ```
   You are analyzing a session transcript to extract workflow patterns.
   Look at the user's messages and your responses. Identify:

   1. ENTRY PATTERNS — How did the session start? What was the user's
      first request? Was it a check-in, a specific task, a question?

   2. PHASES — Where did the session shift focus? What triggered each
      shift? (A new request, a status check, a tool output?)

   3. BRANCHING — Were there decision points where the user could have
      gone in different directions? What determined the direction taken?

   4. TOOLS — What tools did the user reach for? What commands did they
      ask you to run? What contexts did they reference?

   5. PAIN POINTS — Were there moments of friction? (Repeated corrections,
      stops-and-restarts, "no, not that" type corrections)

   6. EXIT — How did the session end (or approach ending)? Was it a
      natural completion, an interruption, or something else?

   Return your findings as a structured JSON document matching the
   workflow-architect state model format.
   ```

3. **If the session context is available via session_search**, also pull
   the 2-3 most recent related sessions for cross-session pattern detection.
   A single session may not reveal the full workflow; multiple sessions do.

4. **Present findings to the user:**

   ```
   "I looked through this session (and [N] recent related sessions) and
   found some patterns in how you work:

   [Summary of inferred workflow, similar to interviewer's convergence summary]

   Does this look right? If yes, I'll generate a bundle. If not, tell me
   what I got wrong — or switch to active mode for a more thorough conversation."
   ```

5. If the user confirms, load `skills/bundle-builder/SKILL.md` and follow
   its instructions to generate the output bundle.

## Limitations

- **Single-session bias:** One session may not represent your full workflow.
  The observer does its best work with multiple sessions of context.
- **Action-inference gap:** The observer only sees what *happened*, not
  what you *intended* or *considered and rejected*. Active interrogation
  captures richer intentional data.
- **Silent mode:** The observer does not announce itself when loading.
  This is intentional — passive mode is meant to be invisible until triggered.
