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

Generated bundles are written to `~/.hermes/skills/<bundle-name>/` via the
`write_file` tool. The user is told the exact path so they can inspect the
bundle and use the skills immediately.

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
| `templates/kanban-board.yaml.tmpl` | Template for kanban definition |
| `templates/decision-map.md.tmpl` | Template for Mermaid decision map |
