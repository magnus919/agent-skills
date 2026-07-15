# Webhook Security

Webhooks V2 events are `meeting.transcribed`, `meeting.summarized`, and `meeting.bot_joined`.
Fireflies sends `X-Hub-Signature: sha256=<hex>`, an HMAC-SHA256 over the exact raw request body.
Verify it before parsing or acting on the event. Use timing-safe comparison.

```bash
scripts/fireflies webhook verify --secret "$WEBHOOK_SECRET" --signature "$X_HUB_SIGNATURE" --body request-body.json --json
```

Use `--body -` to read raw bytes from stdin. This command is a local verifier, never makes a
network call, and does not print the secret. A receiving endpoint should return a 2xx response
within 10 seconds. Persist or queue work after verification; handle retries idempotently and avoid
assuming delivery order. Test valid and invalid signatures before deployment.
