# Slack Web API Operations

> **Last Updated:** 2026-08-03

Operational detail for the Slack Web API surface the skill owns: methods, scopes, pagination, error handling, and webhook signature verification. The bundled `slack-cli` implements this reference; use this document when a call behaves unexpectedly or you need the exact scope/method contract.

## Method surface

All calls POST form-encoded fields to `https://slack.com/api/<method>` with the token as `Authorization: Bearer` and read the JSON response; `ok: false` plus `error` is the error shape.

| Operation | Method | Required scopes | Notes |
|---|---|---|---|
| List channels | `conversations.list` | `channels:read`, `groups:read` | `types` selects public/private/IM/MPIM; `exclude_archived` filters |
| Read history | `conversations.history` | `channels:history`, `groups:history` | Newest first; returns `messages` + `response_metadata.next_cursor` |
| Thread replies | `conversations.replies` | `channels:history`, `groups:history` | Parent message is the first result; `ts` is the parent timestamp |
| Post message | `chat.postMessage` | `chat:write` | Guarded mutation; `thread_ts` replies in a thread |
| Search messages | `search.messages` | `search:read` | Supports `in:`, `from:`, `before:`/`after:`, quoted phrases |
| List files | `files.list` | `files:read` | Optionally filter by channel or user |

## Pagination and bounded reads

- Every listing method returns at most `limit` results per page (max 100 for most) plus `response_metadata.next_cursor`.
- **Bounded-read rule:** request only what the task needs; `slack-cli --limit` caps at the request level. If a task needs more, page explicitly with `--cursor`, and stop when the question is answered.
- Search returns `total` (total matches) alongside the bounded `matches` array — report the total, return only the cap.

## Error handling

- `ok: false` with an `error` string: `invalid_auth` (token bad/expired), `missing_scope` (token lacks the scope — the exact scope is in the response `needed`/`provided` fields), `channel_not_found`, `not_in_channel`, `ratelimited` (429 — back off and retry with `Retry-After`).
- `is_ratelimited: true` in a 200 response: the method was throttled; slow down.
- Never retry a failed send blindly: `chat.postMessage` can be retried with the same `text` (it is not idempotent in the strict sense), so confirm state via `conversations.history` before re-sending.

## Webhook signature verification

Slack signs every outbound HTTP request to your endpoints (events, slash commands, interactivity). Algorithm per [Verifying requests from Slack](https://api.slack.com/authentication/verifying-requests-from-slack):

1. Take the **exact raw request body** bytes — any re-encoding (JSON pretty-print, charset change) breaks the signature.
2. Reject if `|now - X-Slack-Request-Timestamp| > 300` seconds (replay window).
3. Compute `v0=HMAC_SHA256(signing_secret, "v0:" + timestamp + ":" + body)`.
4. Compare with `X-Slack-Signature` using a constant-time comparison (`hmac.compare_digest`).

The app signing secret lives in the Slack app settings (Basic Information → App Credentials → Signing Secret) and is distinct from the bot token. Never log the secret, the signature comparison, or full webhook bodies; `slack-cli webhook verify` reports a boolean result.

## Token and scope hygiene

- Bot tokens (`xoxb-`) act as the app; user tokens (`xoxp-`) act as a user. Scope needs differ: reading public channels needs `channels:history`; reading private channels needs `groups:history` on a bot that has been added to the channel.
- Store tokens in the environment (`SLACK_TOKEN`), never in code, chat, or commit messages. Revoke and rotate a token that leaks — it is a credential, not a config value.
