---
name: bundle-builder
description: >-
  The synthesis engine for workflow-architect. Reads accumulated workflow
  state from memory and renders it into a valid Agent Skills bundle directory
  with sub-skills, manifest, decision map, and optional kanban board. Loaded
  after the interviewer or observer achieves convergence.
license: MIT
compatibility: Hermes Agent — uses write_file for bundle output, shell_quote
metadata:
  tags: [workflow, generation, bundle, synthesis]
  spec-version: "1.0"
---

# Bundle Builder — Workflow Synthesis Engine

This sub-skill is loaded after the interviewer (active mode) or observer
(passive mode) achieves convergence. It reads the accumulated workflow
state from memory and generates an output bundle directory.

## Input

All `workflow-architect:state:*` memory entries. Read them all at once:

```
Read: workflow-architect:state:entry_points
Read: workflow-architect:state:phases
Read: workflow-architect:state:branching
Read: workflow-architect:state:pain_points
Read: workflow-architect:state:exit_criteria
```

If any required fields are missing (entry_points, phases, branching, exit_criteria),
abort with a clear message about what's missing.

## Output Structure

The bundle is written to `~/.hermes/skills/<category>/<bundle-name>/` with this layout:

```
<bundle-name>/
├── SKILL.md                # *** UMBRELLA ENTRY POINT *** — makes the bundle
│                           # loadable via skill_view() and discoverable by
│                           # the agent's skill scanner on trigger keywords.
│                           # CRITICAL: without this, the bundle is invisible.
├── README.md               # Summary of this bundle
├── manifest.yaml           # Skill-to-trigger mapping
├── skills/
│   ├── entry-skill.md      # One per discovered phase
│   ├── phase-two.md
│   └── ...
├── decision-map.md         # Mermaid flowchart
├── AGENTS.md               # Agent loading instructions for this bundle
├── kanban/
│   └── board-definition.yaml  # Only if kanban is appropriate
└── references/
    └── generated-from.md   # Metadata about how this bundle was created
```

**The `SKILL.md` umbrella is not optional.** Without it, individual sub-skills
may exist on disk but the agent's skill scanner has no entry point to match
trigger keywords against. The umbrella is how the agent discovers and enters
the bundle.

### Bundle naming

Ask the user for a bundle name at the start of synthesis:

```
"Before I generate the bundle — what should I call it?
Something short, lowercase with hyphens, like 'my-triage-workflow'
or 'dev-sprint-routine'."
```

Fallback if user doesn't provide one: `my-workflow-<archetype>-<date>`.

### Writing the files

For each file in the output bundle, use the templates in `templates/` as
starting points. Render them by substituting the state values.

**Step-by-step file creation order:**

0. **Umbrella SKILL.md** — **MANDATORY FIRST STEP.** This is the entry point
   that makes the bundle discoverable. Write it directly to the bundle directory
   as `SKILL.md`, then register it via `skill_manage(action='create')`.

   The umbrella must include:

   - `name: <bundle-name>` matching the bundle name
   - `description` with **broad trigger keywords** covering all common ways the
     user enters this workflow (e.g., "I want to write about X", "I read
     something interesting", "can you research this", "draft it", "ship it")
   - `compatibility: Hermes Agent`
   - `metadata.tags` including `workflow`, `bundle`, and domain-relevant tags

   Body content:

   ```markdown
   # <Bundle Name>

   A <N>-phase workflow covering <brief summary>.

   ## Pipeline

   <Phase 1> → <Phase 2> → <Phase 3> → ...

   (Include a Mermaid flowchart graph LR showing the phase sequence.)

   ## Sub-Skills

   | Phase | Skill | Trigger |
   |-------|-------|---------|
   | <name> | `<bundle-name>/<phase-file>` | <when to load> |
   | ... | ... | ... |

   ## Navigation

   When you load this umbrella, identify which phase the user is in,
   load the corresponding sub-skill via skill_view(), and follow its
   instructions. Use the transition signals in each sub-skill to know
   when to move to the next phase.

   ## Pipeline Heuristics

   - Can the user enter at any phase, or must they start at Phase 1?
   - Are any phases automatic (e.g., refine always follows draft)?
   - What's the relationship between phases (sequential, branching, optional)?
   ```

   **Category choice:** Place the bundle in a category that matches where its
   sub-skills live (e.g., `content` for blogging pipelines, `devops` for
   deployment workflows). Ask the user if unsure.

1. **manifest.yaml** — Use `templates/manifest.yaml.tmpl`. Substitute:
   - `{{BUNDLE_NAME}}` — the bundle name
   - `{{PHASES}}` — each phase with its trigger keywords, entry signals,
     typical tools, and exit signals
   - `{{HAS_KANBAN}}` — true/false based on kanban decision

2. **README.md** — Write from scratch (no template needed, it's prose).
   Structure:

   ```markdown
   # <Bundle Name>

   Generated by workflow-architect on <date>.

   This bundle covers a <archetype>-style workflow with <N> phases.

   ## Skills

   | Skill | Trigger | When it fires |
   |-------|---------|---------------|
   | <name> | <trigger description> | <when to load> |

   ## Loading

   Skills in this bundle are loaded automatically by trigger conditions.
   To load a specific skill: `skill_view(name='<bundle-name>/<skill-name>')`

   ## Kanban

   (Only if kanban exists) This workflow maps to a kanban board with <N> lanes.
   ```

3. **Sub-skills** — For each phase in `workflow-architect:state:phases`,
   generate a `.md` file in `skills/` using `templates/skill-skeleton.md`.

   Naming convention: `kebab-case-phase-name.md` (e.g., `morning-triage.md`).

   Each sub-skill file is a valid Agent Skills SKILL.md with:
   - `name` matching the filename (without .md)
   - `description` that includes trigger keywords from the phase's typical
     openers and tools
   - `compatibility: Compatible with any agent supporting the Agent Skills format`
   - Body sections:
     - **When to use** — the trigger condition in natural language
     - **What to do** — step-by-step instructions for the agent in this phase
     - **Transition signals** — what the user typically says or does that
       transitions out of this phase
     - **What to tell the user** — guidance on how the agent should communicate
       during this phase

4. **decision-map.md** — Use `templates/decision-map.md.tmpl`. Substitute:
   - `{{WORKFLOW_NAME}}` — bundle name
   - `{{PHASE_NODES}}` — phase names
   - `{{BRANCHING}}` — decision diamonds
   - `{{ENTRY}}` — how sessions start
   - `{{EXITS}}` — how sessions end

5. **AGENTS.md** — Standard agent loading instructions for this bundle.
   Short — just says which skills exist and when to load them.

6. **kanban/ directory** — Only if the kanban-decision-criteria.md reference
   indicates kanban is appropriate. Generates three files:

   a) **kanban/board-setup.sh** — Use `templates/kanban-board-setup.sh.tmpl`.
      Substitutes:
      - `{{BOARD_SLUG}}` — bundle name (kebab-case)
      - `{{BOARD_NAME}}` — title-case version or user-provided name
      - `{{FIRST_PHASE_SKILL}}` — skill file for the first phase
      - `{{FIRST_PHASE_PRIORITY}}` — priority for first-phase tasks
      - `{{GENERATION_DATE}}` — current date

      The setup script creates the board via `hermes kanban boards create`
      and prints instructions for adding work.

   b) **kanban/task-blueprints.yaml** — Use `templates/kanban-task-blueprints.yaml.tmpl`.
      Substitutes:
      - `{{BLUEPRINT_ENTRIES}}` — one blueprint entry per phase, each with:
        - `phase:` — phase name (kebab-case)
        - `title_template:` — e.g. "Build: {{feature}}"
        - `skill:` — path to the sub-skill file (e.g. `my-workflow/build`)
        - `default_priority:` — descending from first phase (highest) to last
        - `initial_status:` — first phase = `todo`, rest = `ready`
        - `body:` — instructions for the worker: what skill to load,
          definition of done, and transition to next phase

   c) **kanban/README.md** — Brief usage guide explaining how to set up and
      use the board. Structure:

      ```markdown
      # Kanban Board: <Bundle Name>

      This workflow maps to a Hermes Kanban board with <N> phases in sequence.

      ## Setup

      Run `kanban/board-setup.sh` to create the board:
      ```bash
      bash kanban/board-setup.sh
      ```

      The script creates the board and switches to it. If you prefer to set
      it up manually:
      ```bash
      hermes kanban boards create <bundle-name> --name "<Bundle Name>"
      ```

      ## Task Lifecycle

      <Phase 1> → <Phase 2> → <Phase 3>

      Each phase's task depends on the previous phase's task completing.
      When a task is done, the next phase's task auto-promotes to "ready"
      and the dispatcher picks it up.

      ## Adding Work

      Create a task for the first phase:
      ```bash
      hermes kanban create "Build: <feature description>" \\
        --skill <bundle-name>/<phase-1-skill> \\
        --priority 3
      ```

      Then create subsequent-phase tasks with `--parent` pointing to the
      first task's ID:
      ```bash
      hermes kanban create "Review: <feature>" \\
        --parent <task-id> \\
        --skill <bundle-name>/<phase-2-skill> \\
        --priority 2
      ```

      ## Task Blueprints

      See `kanban/task-blueprints.yaml` for template definitions of each
      phase's task, including default priorities, skill mappings, and
      worker instructions.
      ```

7. **references/generated-from.md** — Metadata about the generation process:

   ```markdown
   # Generated From

   - **Skill:** workflow-architect
   - **Mode:** active | passive
   - **Date:** <date>
   - **Archetype:** <archetype>
   - **Convergence Score:** <score>
   ```

8. **Register sub-skills with Hermes skill system** — For each sub-skill `.md`
   file written in step 3, register it so it appears in `skills_list()` and
   can be loaded with `skill_view()`. This is the critical step that makes
   generated skills actually usable by the agent.

   For each sub-skill file in `skills/<name>.md`:

   ```python
   skill_manage(action='create',
       name='<bundle-name>-<skill-name>',
       content=read_file('<bundle-path>/skills/<name>.md')['content'],
       category='generated')
   ```

   This creates a proper skill directory with `SKILL.md` entry point, making
   the sub-skill discoverable and loadable. The sub-skill's existing valid
   Agent Skills frontmatter (name, description, license, tags) is used as-is.

   **Why separate registration is needed:** The `skill_manage()` call also
   handles the skill directory structure (`SKILL.md` at root, not `<name>.md`
   in a `skills/` subdirectory). Without this step, the sub-skill files exist
   on disk but no Hermes mechanism discovers them. Only the umbrella SKILL.md
   (registered in step 0) would be loadable.

   **Verification:** After registering all sub-skills, verify at least one:
   ```python
   skill_view(name='<bundle-name>-<first-phase-name>')
   ```

   If it errors, the registration failed — check that the sub-skill file's
   frontmatter `name` field matches and the content has valid YAML.

## Kanban Decision

Before generating kanban files, consult `references/kanban-decision-criteria.md`
to decide whether a board is appropriate. The decision depends on the phases
and branching structure discovered:

- If phases form a clear linear sequence (A → B → C → D), kanban adds value
- If branching is emergent (session depends on context), kanban is likely inappropriate
- If the user mentioned waiting on others, hand-offs, or status tracking, kanban is a strong fit

Present the decision to the user:

```
"Your workflow has a [linear/emergent] structure. A kanban board [would/wouldn't]
add much value here because [reason]. [If yes: I'll add one to the bundle.]"
```

8. **Register sub-skills** — For each generated sub-skill `.md` file in
   `skills/`, register it so Hermes can discover it via `skill_view()` and
   `skills_list()`:

   ```
   For each sub-skill file `skills/<phase-name>.md`:
     Read the file content
     skill_manage(
       action='create',
       name='<bundle-name>/<phase-name>',
       content=file_content
     )
   ```

   This makes each sub-skill loadable as `skill_view('<bundle-name>/<phase-name>')`.
   The bundle name prefix prevents naming collisions with other skills.

   If `skill_manage` is not available in the agent's toolset, note this for
   the user and suggest they run the registration manually.

## Cleanup

After writing all files:

1. Remove all `workflow-architect:state:*` memory entries
   (`memory(action='remove', target='memory', old_text='workflow-architect:state:')`)
2. Tell the user where the bundle was written and what it contains
3. Verify the umbrella loads correctly with `skill_view(name='<bundle-name>')`
   — if it doesn't resolve, check that `skill_manage(action='create')` was run
   and the SKILL.md has valid frontmatter
4. Verify at least one registered sub-skill loads:
   `skill_view(name='<bundle-name>-<first-phase-name>')`
5. Suggest they enter the workflow via any trigger phrase covered by the
   umbrella's description, or by manually loading the umbrella skill
