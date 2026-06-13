# Workflow Architect Bundle — Agent Instructions

## Loading

### Active Mode (Interview)
1. Load `workflow-architect` umbrella SKILL.md for context
2. Then load `skills/interviewer/SKILL.md` — the interview protocol
3. After convergence, load `skills/bundle-builder/SKILL.md` to generate the bundle
4. Clean up `workflow-architect:state:*` memory entries after generation

### Passive Mode (Observation)
1. Load `workflow-architect` umbrella SKILL.md for context
2. Then load `skills/observer/SKILL.md` — the observation protocol
3. Wait for trigger phrase before taking any action
4. On trigger, scan session context and infer workflow
5. Load `skills/bundle-builder/SKILL.md` to generate the bundle
6. Clean up `workflow-architect:state:*` memory entries after generation

## Output Location

Generated bundles are written to `~/.hermes/skills/<category>/<bundle-name>/` via the
`write_file` tool. The umbrella SKILL.md is registered via `skill_manage(action='create')`
and sub-skills are registered individually so they appear in `skills_list()` and can be
loaded with `skill_view()`.

## Registration

The umbrella SKILL.md is registered with `skill_manage(action='create')` in step 0 of the
bundle-builder. Each generated sub-skill is also registered (step 8) so it's immediately
discoverable by the agent's skill system. Verify with `skill_view(name='<bundle-name>')`
and `skill_view(name='<bundle-name>-<first-phase-name>')`.

## Registration

Both the umbrella `SKILL.md` and each sub-skill `.md` file in the generated
bundle are registered via `skill_manage(action="create")` so they appear in
`skills_list()` and are discoverable by the agent. Registration happens
during generation — no manual step required.

- **Umbrella** — registered under `<bundle-name>` (the bundle root skill)
- **Sub-skills** — registered under `<bundle-name>/<phase-name>`

The umbrella's `description` frontmatter contains broad trigger conditions
that let the agent auto-detect the bundle in future sessions when the user's
conversation cues match a known workflow phase.

## Environment

No environment variables required. State is stored via memory tool with
the prefix `workflow-architect:state:`.

## Reference Files

| File | Purpose |
|------|---------|
| `references/workflow-archetypes.md` | Pattern library for convergence detection |
| `references/trigger-condition-patterns.md` | Trigger condition format spec |
| `references/kanban-decision-criteria.md` | When to include kanban |
| `references/example-output/developer-triage/` | Worked example of a generated bundle |
| `templates/skill-skeleton.md` | Template for generated sub-skills |
| `templates/manifest.yaml.tmpl` | Template for bundle manifest |
| `templates/kanban-board-setup.sh.tmpl` | Template for board creation script |
| `templates/kanban-task-blueprints.yaml.tmpl` | Template for phase-to-task mappings |
| `templates/decision-map.md.tmpl` | Template for Mermaid decision map |
