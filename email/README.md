# Email — Send and Diagnose Transactional Email (SendGrid)

Send transactional email through Twilio SendGrid from your terminal or agent: send with confirmation, check deliverability (bounces and spam reports), and verify that inbound webhook events are authentically signed by SendGrid.

## Why Install This Skill

Transactional email is how services talk to users — password resets, receipts, alerts — and agents have had no bounded way to send or diagnose it. This skill gives your agent a real send path that is safe by design: every send is a guarded mutation requiring a preview (`--dry-run`) and an explicit confirmation (`--yes`), so no mail goes out by accident. It also gives a read path for the two signals that matter for delivery health: bounces and spam complaints.

It ships `email-cli`, a small Python script that speaks the SendGrid v3 API with no third-party dependencies. The webhook verifier is fully self-contained: it validates SendGrid's Signed Event Webhook (ECDSA P-256 signatures) using only the Python standard library, with a replay-window timestamp check, so your event handler can prove a delivery or bounce event really came from SendGrid.

## What You Get

| Directory | Purpose |
|---|---|
| `SKILL.md` | Agent-facing operating contract, mutation gates, and verification boundaries |
| `references/` | Dated source index and a SendGrid operations reference (API surface, deliverability semantics, webhook verification) |
| `scripts/email-cli` | Bounded, stdlib-only CLI: send, deliverability bounces/spam-reports, webhook verify (self-contained ECDSA P-256); `--json`, `--limit`, sends gated by `--dry-run`/`--yes` |
| `tests/` | 15 deterministic tests against a stub SendGrid API plus OpenSSL-generated ECDSA vectors cross-checking the verifier |
| `evals/evals.json` | Six output-quality evaluation cases for agent runs |

## Quick Start

```bash
# Help works with no API key and no network
email/scripts/email-cli --help

# Who bounced recently? (capped at 20)
SENDGRID_API_KEY=SG.xxx email/scripts/email-cli --json --limit 20 deliverability bounces

# Spam complaints
SENDGRID_API_KEY=SG.xxx email/scripts/email-cli --json --limit 20 deliverability spam-reports

# Send only with a preview first, then explicit confirmation
SENDGRID_API_KEY=SG.xxx email/scripts/email-cli send --to user@example.com \
  --from no-reply@example.com --subject "Password reset" --body "Click the link" --dry-run
SENDGRID_API_KEY=SG.xxx email/scripts/email-cli send --to user@example.com \
  --from no-reply@example.com --subject "Password reset" --body "Click the link" --yes

# Verify an inbound Signed Event Webhook before trusting it
email/scripts/email-cli webhook verify --body-file body.json \
  --signature "MEUC..." --timestamp 1712345678 --public-key-file public-key.pem
```

## Triggers

Load this skill for `email` operations: sending a transactional email (with confirmation), checking why mail bounced, looking up spam complaints and suppressions, or verifying a SendGrid `X-Twilio-Email-Event-Webhook-Signature`. Do not load it for marketing campaigns, other email providers (Postmark, SES, Mailgun), or building an email feature inside an application.

## Requirements

- Python 3.9+ for `email-cli` (stdlib only; `--help`, deliverability reads, and webhook verification need nothing else).
- A SendGrid API key (`SENDGRID_API_KEY`) with `mail.send` access to send and suppression read access for deliverability checks.
- A verified sender identity for the from-address you use.
- For webhook verification: the webhook public key (shown in Event Webhook settings when Signed Webhook is enabled) saved as a PEM file.
- Network access to `api.sendgrid.com` for live sends and deliverability reads.
