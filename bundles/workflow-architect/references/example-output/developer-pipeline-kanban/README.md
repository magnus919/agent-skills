# Developer Pipeline Kanban — Example Output (kanban-enabled)

This directory is a **worked example** of what workflow-architect produces
when the discovered workflow is linear enough for kanban. It represents a
fictional developer who follows a strict **build → review → deploy** pipeline.

**This workflow uses kanban** because the phases are strictly sequential,
each has clear entry/exit criteria, and the user tracks multiple features
through the pipeline concurrently.

## What's in here

| File | Purpose |
|------|---------|
| `manifest.yaml` | Maps skills to trigger conditions, includes kanban metadata |
| `skills/build.md` | Build phase — implement the feature |
| `skills/review.md` | Review phase — code review and approval |
| `skills/deploy.md` | Deploy phase — ship to production |
| `kanban/board-setup.sh` | Hermes CLI script to create the kanban board |
| `kanban/task-blueprints.yaml` | Phase-to-kanban-task definitions |
| `kanban/README.md` | Usage guide for the kanban board |
| `decision-map.md` | Mermaid flowchart of the linear pipeline |

## Comparison with developer-triage

| Aspect | developer-triage (no kanban) | developer-pipeline-kanban |
|--------|------|------|
| Workflow shape | Emergent — depends on what's pending | Linear — build → review → deploy |
| Kanban fit | Low — branching is context-dependent | High — strict sequence, hand-offs, concurrent items |
| Branching | Yes — PR check determines direction | No — fixed pipeline |
| What's in the bundle | Skills only | Skills + kanban board + task blueprints |
