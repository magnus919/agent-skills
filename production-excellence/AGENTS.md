# AGENTS.md — Production Excellence Bundle

This bundle is a thin composition layer that assembles cross-domain production
evidence into a launch or operational decision. It is the discoverable entry
point; all routed skills are top-level catalog skills, not nested sub-skills.

## Loading behavior

- The umbrella `SKILL.md` is the single discoverable entry point. Harnesses that
  respect Agent Skills progressive disclosure will discover this bundle through
  its frontmatter (`name: production-excellence`).
- This bundle does not contain nested skills under a `skills/` directory. All
  specialist skills are referenced via relative markdown links
  (`../../<skill>/SKILL.md`) and are resolved by the harness from the catalog.
- When a production concern maps to a single specialist (e.g., a migration plan
  is needed), load that specialist directly. Use this bundle when cross-domain
  assembly and a gate decision are required.
- The bundle's reference files (`references/`) are loaded on demand per the
  file map in `SKILL.md`. Do not load all references at activation time.

## Harness notes

- Compatible harnesses are guaranteed to see this bundle's `SKILL.md`. Nested
  sub-skill auto-loading is not applicable (no nested skills exist).
- The bundle's routing table in `SKILL.md` uses relative links from the bundle
  root (`production-excellence/`) to top-level skill directories
  (`../<skill>/SKILL.md`). Harnesses must resolve these relative to the
  repository root.
