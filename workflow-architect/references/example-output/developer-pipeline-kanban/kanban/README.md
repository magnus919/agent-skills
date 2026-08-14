# Kanban Board: Developer Pipeline Kanban

This workflow maps to a Hermes Kanban board with **3 phases** in sequence:
**Build → Review → Deploy**

## Setup

Run `kanban/board-setup.sh` to create the board:

```bash
bash kanban/board-setup.sh
```

The script creates the board and switches to it. If you prefer to set it up
manually:

```bash
hermes kanban boards create developer-pipeline-kanban \
  --name "Developer Pipeline Kanban"
```

## Task Lifecycle

```
Build → Review → Deploy
```

Each phase's task depends on the previous phase's task completing. When a
Build task is marked `done`, its linked Review task auto-promotes from `todo`
to `ready`. The dispatcher picks it up on the next tick and spawns a worker.

## Adding Work

Create a Build task:

```bash
hermes kanban create "Build: rate limiting middleware" \
  --skill developer-pipeline-kanban/build \
  --priority 3
```

Note the returned task ID. Chain Review and Deploy:

```bash
hermes kanban create "Review: rate limiting middleware" \
  --parent <build-task-id> \
  --skill developer-pipeline-kanban/review \
  --priority 2

hermes kanban create "Deploy: rate limiting middleware" \
  --parent <review-task-id> \
  --skill developer-pipeline-kanban/deploy \
  --priority 1
```

## Concurrent Features

To work on multiple features simultaneously, create independent Build tasks
for each. Each spawns its own Review → Deploy chain. The dispatcher handles
concurrency — set WIP by not creating too many Build tasks at once.

## Task Blueprints

See `kanban/task-blueprints.yaml` for template definitions of each phase's
task, including default priorities, skill mappings, and worker instructions.
