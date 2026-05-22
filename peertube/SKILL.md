---
name: peertube
description: >-
  Browse PeerTube federated video from the terminal: view videos and
  channels, search across instances, check server stats, and manage your
  account. Uses OAuth2 authentication with token persistence. Use when the
  user mentions PeerTube, federated video, decentralized video platforms,
  or browsing/uploading to a PeerTube instance.
license: MIT
compatibility: Requires PEERTUBE_SERVER env var (set to your instance URL,
  e.g. https://watch.nousresearch.com), Python 3.8+, and the `requests`
  library. OAuth2 tokens persisted to ~/.config/peertube-cli/token.json.
metadata:
  tags: [peertube, federated-video, video-platform, activitypub, api-client]
  sources:
    - https://joinpeertube.org/
    - https://docs.joinpeertube.org/api/reference
---

# peertube-cli — PeerTube Federated Video

Browse videos, channels, and server info on any PeerTube instance. Search across the fediverse, list channels, check your account stats, and manage authentication — all from the terminal.

## Setup

1. Set the PeerTube instance URL:

```bash
export PEERTUBE_SERVER="https://your-instance.example.com"
```

2. (Optional) Log in for authenticated operations:

```bash
peertube-cli auth login --username "your-username" --password "your-password"
```

The OAuth2 token is persisted to `~/.config/peertube-cli/token.json` and automatically reused. `--dry-run` works without authentication.

## Essential Commands

### auth login — Authenticate to a PeerTube instance

```bash
peertube-cli auth login --username "myuser" --password "mypassword"   # login
```

Token is saved to `~/.config/peertube-cli/token.json` and reused on subsequent calls. Tokens expire after the server-configured lifetime (typically 24h).

### server — Instance information

```bash
peertube-cli server                                # instance name, description, stats
peertube-cli server --json                         # machine-readable
```

Shows: instance name, short description, total users, total videos, total views.

### videos — Browse recent videos

```bash
peertube-cli videos                                # last 12 videos
peertube-cli videos --limit 24                     # more results
peertube-cli videos --json                         # machine-readable
```

Shows: title, duration, views, author/channel, publish date.

### search — Search videos across the fediverse

```bash
peertube-cli search --query "linux tutorial"       # search videos
peertube-cli search -q "peer" --limit 24           # more results
peertube-cli search -q "docker" --json             # machine-readable
```

### channels — List video channels

```bash
peertube-cli channels                              # all channels on the instance
peertube-cli channels --json                       # machine-readable with subscriber counts
```

Shows: display name, channel handle (@name), video count, subscriber count.

### me — Your profile

```bash
peertube-cli me                                    # your account stats
peertube-cli me --json                             # machine-readable
```

Shows: username, role, video count, view count. Requires authentication.

## Global Flags

All flags work in any position:

```bash
peertube-cli --json videos                         # flag before subcommand
peertube-cli videos --json                         # flag after subcommand
peertube-cli --dry-run search --query "test"       # preview (no API call)
peertube-cli --quiet videos                        # suppress non-essential output
peertube-cli --verbose channels                    # detailed logging
```

## Known Gotchas

- **Set PEERTUBE_SERVER first** — Without this env var, the CLI defaults to `https://your-instance.example.com` (which won't resolve). Always export the correct instance URL.
- **Authentication is required for most commands** — `server` and public video browsing work without auth. `me`, `channels`, and personal video lists require a valid OAuth token. Use `--dry-run` to preview without auth.
- **Token is persisted automatically** — After `auth login`, the token is saved to `~/.config/peertube-cli/token.json`. No need to login again unless the token expires. Delete this file to force re-login.
- **Token expiry** — PeerTube OAuth2 tokens have a configurable expiry (default ~24h). Expired tokens cause 401 errors. Re-run `auth login` to refresh.
- **Cross-instance search** — `search --query` searches across the fediverse, not just the local instance. Results may include videos from remote instances.
- **API pagination** — PeerTube uses offset-based pagination. The `--limit` flag controls the page size (default: 12 for videos, 15 for channels).
- **Rate limits** — PeerTube instances have configurable rate limits. The CLI does not auto-retry on 429 responses.

## References

- [scripts/peertube-cli](scripts/peertube-cli) — The CLI binary. Built following the cli-builder patterns: `--json`, `--dry-run`, `--quiet`, `--verbose`, dual-output via `emit()`, lazy auth, config file persistence.
- [PeerTube API Reference](https://docs.joinpeertube.org/api/reference) — Official API reference.
- [JoinPeerTube.org](https://joinpeertube.org/) — Find instances and learn about the federated video platform.
