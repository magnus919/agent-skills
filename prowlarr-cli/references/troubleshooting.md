---
name: prowlarr-cli/troubleshooting
description: "Common pitfalls and FAQs for prowlarr-cli."
---

# Troubleshooting & FAQs

## Common Pitfalls

### Prowlarr is infrastructure, not media

Unlike radarr-cli, sonarr-cli, and lidarr-cli, prowlarr-cli doesn't browse or
add media. It manages the indexer layer that those apps use to find content.

### Indexer statistics may be empty on new setups

If Prowlarr was just set up or has few queries, `indexer-stats` may return
minimal data. This is normal — stats accumulate over time as searches run.

### Test all runs asynchronously

`prowlarr-cli test-all` triggers the command and returns immediately. The actual
tests run in the background. Check `prowlarr-cli indexer-status` to see results.

### Port 9696

Prowlarr defaults to port 9696 (not 7878, 8989, or 8686 like the other arrs).

## When Not to Use

- **Media search/download** — Prowlarr feeds indexers to other arrs but doesn't download media.
- **First-time Prowlarr setup** — install and configure Prowlarr first (prowlarr.com).

## FAQ

**Q: What's the difference between indexer-stats and indexer-status?**
A: `indexer-stats` shows cumulative query/grabs counts. `indexer-status` shows
current health (which indexers are disabled, when they'll retry).

**Q: Can I add or remove indexers with this CLI?**
A: Not yet. This CLI is read-only for now (list, inspect, test). Use the
Prowlarr web UI for adding/editing indexers.

**Q: How do I find an indexer's ID?**
A: Run `prowlarr-cli --json indexers | jq '.indexers[] | {name, id}'`
