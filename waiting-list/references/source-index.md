# Source index

Research checked 2026-09-15. These are evidence sources and examples, not
endorsements. Re-open vendor and repository documentation before making a
current implementation claim.

## Reference experience audit

| Public source | Checked | Verified scope and limitation |
| --- | --- | --- |
| [Monako homepage](https://www.monako.ai/) and [reserve route](https://www.monako.ai/order) | 2026-09-20 | Rendered DOM, interaction states, linked styles/media, and browser-observed requests informed `references/engagement-and-visual-system.md`. This was not a proprietary source-code or security audit, and it does not authorize copying the site's identity, assets, wording, product claims, or exact layout. |

## Default-path decisions

The owner approved TypeScript/Node.js on Vercel after reviewing the compiled
runtime tradeoff, and approved verification codes as an alternative to magic
links. The default is therefore static HTML + Alpine CSP + Vite, Node API,
Neon Postgres, Twilio Verify email/SMS codes (SendGrid for email), and a later
CRM connection. These are design choices, not claims that a portal has been
deployed or that every integration has been tested.

| Official source | Verified scope and limitation |
| --- | --- |
| [Vercel runtimes](https://vercel.com/docs/functions/runtimes) | Official runtime list; inspect individual runtime pages for maturity |
| [Node.js](https://vercel.com/docs/functions/runtimes/node-js) | Default JavaScript/TypeScript API path |
| [Go](https://vercel.com/docs/functions/runtimes/go), [Rust](https://vercel.com/docs/functions/runtimes/rust), [Bun](https://vercel.com/docs/functions/runtimes/bun) | Individual pages mark these runtimes beta at inspection |
| [Alpine CSP](https://alpinejs.dev/advanced/csp) | CSP-compatible build; test its supported expression subset |
| [Neon pooling](https://neon.com/docs/connect/connection-pooling) | Managed pooling; transaction-mode compatibility matters |
| [Twilio Verify email](https://www.twilio.com/docs/verify/email) | Email verification uses SendGrid setup and templates |
| [Verify consent](https://www.twilio.com/docs/verify/consent-opt-in) | Provider opt-in requirements; not a universal legal determination |
| [Canva exports](https://www.canva.dev/docs/connect/api-reference/exports/) | MP4 supported for compatible designs; not evidence of an installed connector |
| [Stytch email links](https://stytch.com/docs/consumer-auth/authentication/magic-links/overview) | Optional managed-link candidate; branding and user/session behavior require review |

No dependency from the open-source survey is a required default. Its evidence
below remains at the stated inspection level; no pinned-code security audit is
implied. Record resolved dependencies, versions, license and inspected files
when a generated project actually adopts one.

## Architecture and open-source examples

| Source | What it establishes | Limits |
| --- | --- | --- |
| [Open Waitlist](https://github.com/zaidazmi/open-waitlist) | A Next.js/Supabase/Resend implementation with full-app and backend-only modes, verification, referral links, dynamic ranking, and an own-frontend API path | Repository README is not a production-readiness audit; inspect current code, license, dependencies, and maintenance |
| [OpenLaunch](https://github.com/frockett/OpenLaunch) | A self-hostable Blazor app with subscribe/unsubscribe APIs, API keys, bulk email, bounce handling, and metrics; README says AWS SES is currently supported | Small project and provider scope; claims such as scale or security need independent validation |
| [revokslab/waitly](https://github.com/revokslab/waitly) | A Next.js template using Notion as CMS, Upstash Redis for rate limiting, and Resend | A template demonstrates a path, not a guarantee that Notion is a suitable system of record |
| [Vercel Labs nextjs-waiting-room](https://github.com/vercel-labs/nextjs-waiting-room) | FIFO waiting-room mechanics: monotonic tickets, signed admission tokens, atomic Redis admission, adaptive polling, and explicit production trade-offs | Example architecture; its fail-open and queue identity choices must be matched to the workload |
| [pleasehold.dev](https://github.com/PixelTowers/pleasehold.dev) | An API-first, self-hostable service shape with project-scoped API keys, deduplication, notifications, dashboard, and optional double opt-in | Current repository behavior and deployment posture still need inspection before adoption |

## Authoritative infrastructure guidance

| Source | Relevant finding |
| --- | --- |
| [Cloudflare Turnstile getting started](https://developers.cloudflare.com/turnstile/get-started/) | Embed a public sitekey, then validate the token server-side through Siteverify; client-side completion alone is incomplete |
| [Cloudflare Waiting Room JSON response](https://developers.cloudflare.com/waiting-room/how-to/json-response/) | Non-browser clients must preserve and update the waiting-room cookie; JSON responses still require periodic refresh to advance |
| [Resend webhook introduction](https://resend.com/docs/webhooks/introduction) | Webhooks report delivery events; delivery is at-least-once and unordered, so handlers should dedupe by `svix-id` and tolerate reordering |
| [Amazon SES sender reputation guidance](https://docs.aws.amazon.com/ses/latest/dg/tips-and-best-practices.html) | Double opt-in reduces hard bounces from typos; domain/authentication, list quality, and compliance also matter |
| [FTC CAN-SPAM compliance guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) | Commercial email requires a usable opt-out path; message purpose determines whether transactional/relationship treatment applies |
| [OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html) | URL tokens should be random, securely stored, single-use, expiring, and protected against brute force; responses should resist account enumeration |
| [Twilio Verify API](https://www.twilio.com/docs/verify/api/verification) | Managed verification supports SMS and email channels, E.164 phone numbers, provider status, and a verification-check step; standard SMS is code-based |
| [Twilio Messages resource](https://www.twilio.com/docs/messaging/api/message-resource) | A programmable SMS API can send application-authored message content and links; delivery is a message event, not ownership proof |
| [HubSpot Contacts API](https://developers.hubspot.com/docs/api-reference/latest/crm/objects/contacts/guide) | CRM contacts can be created, updated, associated, and upserted with scoped contact-write access and custom properties |

## Gemini-synthesis verification notes

- “Headless serverless pipeline,” “viral referral engine,” and “decoupled API”
  are useful architectural categories, but they are not the only patterns. The
  skill adds appointment backfill, allocation/lottery/preorder, and virtual
  waiting-room semantics because each manages a different scarce resource.
- `OpenLaunch` is directly verifiable as a public repository and is included as
  a self-hosted management example.
- `Waitly` is ambiguous: the research found a real `revokslab/waitly` template,
  a separate commercial reservation product, and other similarly named
  templates. Identify the exact repository before relying on its capabilities.
- `WaitBee` has a public beta landing page, but this research did not establish
  the specific open-source Next.js/PostgreSQL/Prisma feature set claimed in the
  synthesis. Treat those details as unverified until an authoritative source is
  available.
- No authoritative primary source was found for a project named
  `Headless-Waitlist` with the exact Drizzle/PostgreSQL/Resend/Arcjet stack.
  Treat it as an unverified lead, not a vetted dependency.
- “Always use double opt-in” is too absolute. It is a strong list-quality and
  consent pattern, especially for marketing or typo-sensitive lists, but the
  exact flow depends on message purpose, jurisdiction, UX, and operational
  requirements.
- “Keep the endpoint under 200 ms” is a useful performance hypothesis, not a
  universal contract. Measure the complete synchronous path, including bot
  checks, database writes, and failure behavior, for the chosen deployment.
- The stakeholder requirement changes the design: email and phone proof are
  optional, independent contact-channel assertions; CRM delivery is a runtime
  downstream projection after a configured eligibility gate, not a replacement
  for the local waitlist record.
