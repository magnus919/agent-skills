# Email (SendGrid) — Source Index

> **Last Updated:** 2026-08-03

This skill is a distilled operating layer over Twilio SendGrid's public developer documentation. Facts and endpoint names in this skill are grounded in the sources below; refresh this index when SendGrid ships API changes.

| Topic | Source | URL |
|---|---|---|
| SendGrid v3 API reference | Twilio SendGrid API v3 reference | https://www.twilio.com/docs/sendgrid/api-reference |
| Send email | Send Mail API | https://www.twilio.com/docs/sendgrid/api-reference/mail-send/mail-send |
| Suppressions (bounces, spam reports) | Suppressions API | https://www.twilio.com/docs/sendgrid/api-reference/suppressions |
| Signed Event Webhook (signature verification) | Event Webhook security features | https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/getting-started-event-webhook-security-features |
| Event Webhook payload reference | Event webhook reference | https://www.twilio.com/docs/sendgrid/for-developers/tracking-events/event |
| Official Python verification helper | sendgrid-python eventwebhook | https://github.com/sendgrid/sendgrid-python/tree/main/sendgrid/helpers/eventwebhook |

## Refresh procedure

- Re-check the signed-webhook security page before changing anything in `webhook verify`; the ECDSA signing scheme is a security boundary and the official Python helper is the reference implementation this skill mirrors.
- Re-check the Mail Send API when SendGrid announces breaking changes to the `/v3/mail/send` payload.
- Update `research_checked` in `SKILL.md` frontmatter and this file's `Last Updated` when you verify the sources again.
