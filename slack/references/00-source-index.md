# Slack — Source Index

> **Last Updated:** 2026-08-03

This skill is a distilled operating layer over Slack's public developer documentation. Facts and method names in this skill are grounded in the sources below; refresh this index when Slack ships API changes.

| Topic | Source | URL |
|---|---|---|
| Web API overview and conventions | Slack Web API documentation | https://api.slack.com/web |
| Method catalog (conversations, chat, search, files) | Slack Method Reference | https://api.slack.com/methods |
| Scopes and tokens | Slack Token & Scopes docs | https://api.slack.com/authentication/token-types |
| Webhook signing (signature verification) | Verifying requests from Slack | https://api.slack.com/authentication/verifying-requests-from-slack |
| Pagination | Paging through collections | https://docs.slack.dev/web/using-the-web-api/#pagination |

## Refresh procedure

- Re-check the method reference when a call returns `method_not_supported` or a scope error for a documented method.
- Re-check the signing-verification page before changing anything in `webhook verify`; the `v0` signing scheme is a security boundary.
- Update `research_checked` in `SKILL.md` frontmatter and this file's `Last Updated` when you verify the sources again.
