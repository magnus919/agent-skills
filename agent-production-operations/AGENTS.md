# AGENTS.md — agent-production-operations bundle

This bundle follows the Agent Skills format. The discoverable entry point is
[SKILL.md](SKILL.md), which is a thin umbrella that routes to reference files
and specialist skills.

## Loading behavior

- The bundle does **not** ship nested sub-skills. All content is in
  `references/` files loaded on trigger.
- [SKILL.md](SKILL.md) is the only file that appears in generated catalogs.
- Reference files are loaded only when their trigger condition matches (see
  the loading protocol table in SKILL.md).

## Nested-skill loading note

This bundle is a composition of existing specialist skills. When the active
concern falls within a specialist's domain, load that specialist's SKILL.md
directly rather than re-deriving its method from the bundle. The routing table
in [SKILL.md](SKILL.md) defines which specialist to load for each concern.

## Validation

This bundle is validated by the repository's standard toolchain:
- `ruby scripts/validate-skills.rb`
- `.venv/bin/python scripts/validate-evals.py`
- `ruby scripts/validate-skill-quality.rb --base origin/main`
