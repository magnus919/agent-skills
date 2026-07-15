# Troubleshooting

- **Missing key:** set `FIREFLIES_API_KEY`, pass `--api-key`, or use `--dry-run`. Help and local webhook checks need no key.
- **Authentication failure:** verify `Authorization: Bearer <key>` and regenerate/check the key in Fireflies Integrations.
- **GraphQL error:** inspect JSON `errors`, especially `code` and `extensions.helpUrls`; do not retry malformed documents unchanged.
- **`too_many_requests`:** honor `retryAfter` when present and reduce request rate.
- **Permission or plan restriction:** audit events/rule executions can require Enterprise/admin access; AskFred mutations need AI credits. Escalate access, do not infer it.
- **Pagination:** use transcript `limit` (50 or less) and `skip`; use documented cursors for audit/rule queries.
- **Webhook verification failure:** compare the raw body, unmodified signature header, and the correct shared secret. Do not verify re-serialized JSON.
- **Safe escalation:** capture the command (without credentials), exit code, response error code, and help URL; provide these to Fireflies support.
