# Slack — Read and Post to Slack from the Terminal

Operate a Slack workspace without leaving your terminal or your agent's tool loop: list channels, read messages, follow threads, search history, find files, and verify that inbound webhook events are authentic.

## Why Install This Skill

Most agents have no way to answer the basic question "what did the team say about X in Slack?" — so they guess, or you paste screenshots. This skill gives your agent a real, bounded read path into a workspace (channels, messages, threads, search, files) plus a safe write path: sending a message is a guarded mutation that requires a preview and an explicit confirmation, so the agent can triage and answer without ever posting by accident.

It ships `slack-cli`, a small Python script that speaks the Slack Web API with no third-party dependencies. Reads are capped (`--limit`), output is clean JSON for the agent or readable text for you, and `--help` works with no token and no network. Webhook verification is built in: any event endpoint can prove a request really came from Slack using the standard HMAC-SHA256 signature check.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating contract, mutation gates, and verification boundaries |
| `references/` | Dated source index and a web API operations reference (methods, scopes, pagination, webhook verification) |
| `scripts/slack-cli` | Bounded, stdlib-only CLI: channels, messages, threads, search, files, webhook verify; `--json`, `--limit`, sends gated by `--dry-run`/`--yes` |
| `tests/` | 16 deterministic tests against a stub Slack API, covering the mutation gate and read-only contract |
| `evals/evals.json` | Six output-quality evaluation cases for agent runs |

## Quick Start

```bash
# Help works with no token and no network
slack/scripts/slack-cli --help

# Find the channel ID from a name (reads are capped at --limit)
SLACK_TOKEN=xoxb-... slack/scripts/slack-cli --json --limit 10 channels list

# Read the latest messages in a channel
SLACK_TOKEN=xoxb-... slack/scripts/slack-cli --json messages list --channel C12345

# Follow a thread (parent ts from the message list)
SLACK_TOKEN=xoxb-... slack/scripts/slack-cli --json threads list --channel C12345 --ts 1712345678.000001

# Search history, bounded
SLACK_TOKEN=xoxb-... slack/scripts/slack-cli --json search messages --query "incident"

# Send only with a preview first, then explicit confirmation
SLACK_TOKEN=xoxb-... slack/scripts/slack-cli messages send --channel C12345 --text "on it" --dry-run
SLACK_TOKEN=xoxb-... slack/scripts/slack-cli messages send --channel C12345 --text "on it" --yes

# Verify an inbound webhook before trusting it
slack/scripts/slack-cli webhook verify --body-file body.json --signature "v0=..." --timestamp 1712345678
```

## Triggers

Load this skill for `slack` operations: "what was said in #channel", reading or listing messages and channels, following or summarizing threads, searching Slack history, finding shared files, posting a message or thread reply (with confirmation), and verifying `X-Slack-Signature` webhook events. Do not load it for building Slack apps or bots, workspace administration (user provisioning, org settings), or other chat platforms like Discord or Teams.

## Requirements

- Python 3.9+ for `slack-cli` (stdlib only; `--help` and webhook verification need nothing else).
- A Slack bot or user token (`SLACK_TOKEN`) with the scopes the read needs: `channels:read`, `channels:history`, `groups:read`, `groups:history`, `search:read`, `files:read`, and `chat:write` for sending. For `webhook verify`, the app signing secret (`SLACK_WEBHOOK_SECRET`).
- Network access to `api.slack.com` for live reads and sends.
