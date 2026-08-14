# Tailscale/Headscale Bundle — Agent Instructions

## Auto-Load Protocol

When the user's message matches trigger keywords (see umbrella SKILL.md), load the
corresponding sub-skill with `skill_view(name='tailscale/<sub-skill-name>')`.

For general "tailscale"/"headscale"/"tailnet" mentions, load this umbrella SKILL.md
first for navigation, then the relevant sub-skill.

## Shared Scripts

All scripts in the bundle root `scripts/` are available regardless of which sub-skill
is loaded. Reference them by relative path from the bundle root:

```
scripts/headscale-health-check.sh --json
scripts/headscale-backup.sh --dry-run
```

## Sub-Skill Scripts

Sub-skill scripts are in `skills/<sub-skill>/scripts/` and are documented in their
respective SKILL.md files.

## Environment

Set these env vars for non-interactive operation:

- `HEADSCALE_URL` — Headscale server URL
- `HEADSCALE_API_KEY` — API key from `headscale apikeys create`
- `TAILSCALE_AUTHKEY` — Pre-authenticated key for client setup

All scripts check these at runtime and show a helpful error if missing.
