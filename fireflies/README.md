# Fireflies.ai: meeting intelligence from the terminal

## Why Install This Skill

Turn Fireflies meetings into usable data without hand-copying notes. Search transcripts, inspect
summaries and action items, review analytics, and ask focused questions with AskFred from a single
dependency-free command line tool.

It also makes sensitive operations deliberate: every mutation requires an explicit confirmation,
and every mutation can be previewed locally before it is sent.

## What You Get

| Path | What it provides |
|---|---|
| `scripts/fireflies` | Python 3.9+ GraphQL CLI with safe reads, mutations, dry-runs, and webhook verification |
| `references/api-reference.md` | API model, operation families, limits, and source links |
| `references/cli-reference.md` | Complete CLI contract and examples |
| `references/workflows.md` | Transcript, analytics, upload, AskFred, and GraphQL recipes |
| `references/webhook-security.md` | Webhooks V2 verification guidance |
| `references/troubleshooting.md` | Failure diagnosis and escalation boundaries |

## Quick Start

```bash
export FIREFLIES_API_KEY='...'
python3 scripts/fireflies transcripts list --keyword roadmap --limit 10 --json
```

Output is the Fireflies GraphQL response, for example:

```json
{"data":{"transcripts":[{"id":"...","title":"Roadmap review"}]}}
```

Preview a change without calling the API:

```bash
python3 scripts/fireflies meetings rename transcript-id --title "Q3 roadmap" --dry-run --json
```

## Triggers

- Fireflies.ai transcripts, summaries, notes, contacts, channels, or analytics
- AskFred questions about meeting content
- Remote audio upload to Fireflies
- Fireflies Webhooks V2 signature verification

## Requirements

- Python 3.9 or newer
- A Fireflies API key in `FIREFLIES_API_KEY` for API calls
- Network access to `https://api.fireflies.ai/graphql`
- No third-party Python packages
