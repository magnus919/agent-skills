# Workflows

## List, Filter, and Read a Transcript

Use this to locate meetings and then inspect their content.

```bash
scripts/fireflies transcripts list --keyword roadmap --organizers owner@example.com --limit 10 --json
scripts/fireflies transcripts get transcript-id --json
```

The detailed query includes summary, speakers, sentences, and analytics.

## Extract Actions and Summary

Use this for a currently live meeting or for a completed transcript.

```bash
scripts/fireflies live-action-items meeting-id --json
scripts/fireflies transcripts get transcript-id --json
```

## Team Analytics

Use a bounded time range for trend reporting.

```bash
scripts/fireflies analytics --start 2026-01-01 --end 2026-01-31 --json
```

## Upload Audio with Webhook Correlation

Use a publicly retrievable HTTPS media URL and a webhook endpoint you control. Preview first.

```bash
scripts/fireflies audio upload --url https://media.example/call.mp3 --webhook https://app.example/fireflies --client-reference-id import-42 --dry-run --json
scripts/fireflies audio upload --url https://media.example/call.mp3 --webhook https://app.example/fireflies --client-reference-id import-42 --confirm --json
```

## AskFred Conversation

Use AskFred for natural-language analysis when the account has AI credits.

```bash
scripts/fireflies askfred create --question 'What decisions were made?' --transcript-id transcript-id --confirm --json
scripts/fireflies askfred continue thread-id --question 'Who owns the follow-up?' --confirm --json
```

## Generic GraphQL

Use this when a documented operation is newer than the CLI's ergonomic commands. Copy the document
from Fireflies primary documentation, pass variables as JSON, and preview mutations before confirmation.

```bash
scripts/fireflies query --document 'query { user { name } }' --json
scripts/fireflies mutation --document 'mutation Example($input: SomeInput!) { someMutation(input: $input) { success } }' --variables '{"input":{}}' --dry-run --json
```
