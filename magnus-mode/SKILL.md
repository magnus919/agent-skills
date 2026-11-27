---
name: magnus-mode
description: Assess and route technology-project work when the user explicitly invokes Magnus Mode. Use it to find the next evidenced step across discovery, planning, delivery, or operations. Do not auto-invoke it for ordinary coding, single-skill requests, or unrelated catalog work.
license: MIT
metadata:
  attribution: Inspired by Lauren Tan's P-stack and Addy Osmani's lifecycle routing.
---

# Magnus Mode

Start only on an explicit request to use Magnus Mode. This skill maps a technology project to the next evidence-bearing steps. It does not replace the selected specialist's process, create a second delivery state machine, or grant authority to execute.

1. Establish the outcome, affected surface, requested stopping point, and existing authority. If intent or acceptance is unsettled, route to discovery or shaping first. Read-only exploration can answer a question; it does not approve a design or a change.
2. Read the relevant sections of [the lifecycle map](references/lifecycle.md). Use the minimum available project evidence needed to place the work: accepted brief, decision record, delivery packet, tracker, candidate revision, CI/review records, or authorized environment observations. Use Neckbeard's position assessment and evidence rules for engineering journeys; don't recreate its packet.
3. Mark relevant steps **verified**, **reported/unverified**, **missing**, **stale or contradicted**, or **not applicable** with a reason. Cite the evidence and revision it covers. A filename, convincing handoff, green CI, or merged PR does not prove a different milestone. Preserve valid evidence and reopen only the decisions or checks affected by a change.
4. Identify the **ready set**: applicable steps with hard predecessors satisfied and within the requested stop. Name what is blocked and the exact prerequisite or decision owner. Independent read-only assessment can continue while a decision is blocked. Run steps in parallel only if they do not contend for a shared contract, write surface, environment, budget, or decision; join on all relevant evidence.
5. Recommend the next owning skill. Use the catalog identity to load just that skill and any complementary skills needed now. If a skill is unavailable, say which one; use an available equivalent only if it preserves the required evidence and authority. Never silently treat a missing skill as a passed gate.

## Report

Give the current position, material evidence, first blocking prerequisite (or none), what can proceed in parallel, and the next skill and stop. Keep assessment read-only by default. If later action is authorized, follow the selected skill and project rules. Clarify the smallest missing decision rather than restarting an evidenced project. A scoped typo may use the lightweight path; an authoritative runbook change may need recovery evidence even if the diff is Markdown only.

## When not to use

Use the product, engineering, or operations specialist directly when the user hasn't asked for Magnus Mode, or the task already has a clear owner and no lifecycle assessment is requested. Follow incident command during an active incident; do not turn it into a planning exercise. Do not route personal or unrelated work, load the whole catalog, or promise a universal slash command.

See [examples and source attribution](references/examples.md).
