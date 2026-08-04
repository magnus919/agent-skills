# SendGrid Operations

> **Last Updated:** 2026-08-03

Operational detail for the Twilio SendGrid surface the skill owns: the Mail Send API, suppression endpoints for deliverability, and Signed Event Webhook verification. The bundled `email-cli` implements this reference; use this document when a call behaves unexpectedly.

## API conventions

- Base URL: `https://api.sendgrid.com/v3`. Every request carries `Authorization: Bearer <API_KEY>` and JSON bodies.
- The API key scope matters: `mail.send` is needed to send; suppression reads need access to the Suppression endpoints (`suppression.read`/suppression access on the key). An unauthorized call returns 401 with an error body.
- `email-cli` honors `SENDGRID_API_BASE` (test/stub override); production default is the v3 base.

## Sending (POST /v3/mail/send)

- Payload: `{"from": {"email": ...}, "personalizations": [{"to": [{"email": ...}], "subject": ...}], "content": [{"type": "text/plain", "value": ...}]}` plus an optional `text/html` content part.
- The from-address must be a **verified sender identity** on the account; unverified senders are rejected.
- Success is **HTTP 202 Accepted with an empty body** and the message id in the `X-Message-Id` response header — the email is queued, not delivered. Acceptance ≠ delivery; confirm with bounce events, spam reports, or the activity feed.
- Failure is an HTTP 4xx/5xx with an `errors` array naming the field (e.g. invalid `from`, missing content).

## Deliverability surface (read-only)

| Signal | Endpoint | What it means |
|---|---|---|
| Bounces | `GET /suppression/bounces?limit=N` | Recipients whose mail bounced, with `reason`, `status`, `created` |
| Spam reports | `GET /suppression/spam_reports?limit=N` | Recipients who marked mail as spam, with `ip` and `reason` |

- Suppression endpoints return plain arrays (not paginated objects); `limit` caps them (max 500). **Bounded-read rule:** request only what the task needs; `email-cli --limit` caps at the request level.
- Hard bounces (permanent, 5.x.x) indicate invalid addresses — do not re-send to them. Spam complaints indicate content or targeting problems — review before the next send.

## Signed Event Webhook verification

SendGrid signs each webhook POST when "Signed Webhook" is enabled. Algorithm (mirrors the official `sendgrid-python` `EventWebhook.verify_signature` helper):

1. **Raw body bytes**: use the exact request body; re-encoding (pretty-print, charset change) breaks verification.
2. **Timestamp**: `X-Twilio-Email-Event-Webhook-Timestamp` (Unix seconds). Reject if `|now - ts| > 300s` (default replay window; `--max-age 0` disables for historical verification).
3. **Data**: SHA-256 digest over `timestamp + raw body` — bytes concatenated with **no separator** (`timestamped_payload = (timestamp + payload).encode('utf-8')`).
4. **Signature**: `X-Twilio-Email-Event-Webhook-Signature`, base64-decoded ASN.1 DER `(r, s)`, verified as an ECDSA signature over the P-256 (secp256r1) curve with the webhook public key.
5. Constant-time semantics: compare by performing the mathematical verification; never string-compare signatures.

The public key is displayed in the Event Webhook settings dialog when Signed Webhook is enabled and can also be fetched via the Event Webhook API. Store it as a PEM file, never in code. `email-cli webhook verify` implements steps 1–5 with a self-contained stdlib P-256 verifier (no `cryptography` dependency).

## Error handling

- 401 `unauthorized`: API key invalid or missing scope — rotate/regrant, never retry blindly.
- 400 `errors[]`: payload problem; the message names the offending field (e.g. from-address not verified).
- 429 `rate_limited`: slow down and retry with backoff.
- `email-cli` exit 1 with `Email API HTTP <code>: <detail>` (human) or `{"ok": false, "error": "..."}` (JSON). Exit 2 is a usage error.

## Credential hygiene

- API keys are full-account credentials: store in `SENDGRID_API_KEY`, never in code, chat, or commits. Scope keys narrowly (`mail.send` only, or a separate key for suppression reads) and rotate on leak.
- Webhook public keys are public material; webhook *secrets* do not exist in this scheme (signature verification is the security boundary).
