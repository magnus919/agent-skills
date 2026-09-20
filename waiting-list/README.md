# waiting-list

Design and build honest, resilient waitlist portals for anticipated goods and services.

## Why Install This Skill

“Waitlist” can mean an email interest list, a fair queue, a virtual waiting room, a booking backfill, or a scarce-inventory allocation. Those systems have different promises and failure modes. This skill helps an agent identify the real one before it reaches for a familiar landing-page template.

Give your agent a brand guide, logos, campaign goals, and optional background video. It follows a simple path: preview your page, choose contact confirmation, connect your services, and prepare for launch. The default is a single HTML page with Alpine.js, TypeScript APIs on Vercel, Neon Postgres, and managed email/SMS codes. CRM connects when you choose it.

## What You Get

| Path | Purpose |
|---|---|
| `SKILL.md` | Core classification, design workflow, contracts, controls, and completion criteria |
| `references/architecture-patterns.md` | Pattern comparison, headless API shape, queue mechanics, and referral policy guidance |
| `references/operations-and-abuse.md` | Bot controls, email lifecycle, privacy, administration, and incident behavior |
| `references/contact-verification-and-crm.md` | Optional email/phone proof flows and runtime CRM outbox/adapters |
| `references/default-stack.md` | Chosen stack, providers, hosting, setup and alternatives |
| `references/brand-and-marketer-workflow.md` | Brand intake, Canva/video, preview and accessible form experience |
| `references/engagement-and-visual-system.md` | Monako-derived visual narrative, state-aware conversion, motion, media, and performance wishlist |
| `references/implementation-contract.md` | API, database, verification and CRM behavior to implement |
| `references/release-evidence.md` | Functional, visual and operational launch checks |
| `references/source-index.md` | Dated primary-source index and verification notes for the supplied synthesis |
| `templates/waitlist-decision-record.md` | Fillable architecture and delivery decision record |
| `templates/campaign-brief.md` | Plain-language campaign worksheet |
| `templates/campaign-config.example.json` | Configuration example for the implementing agent |
| `evals/` | Output-quality scenarios and separate skill-trigger probes |

## Quick Start

Ask: “Use waiting-list to build our launch page. Here are our logo and brand guide. Collect confirmed emails and connect our CRM when ready. Show me a preview first.” Your agent handles the engineering choices and keeps you focused on the campaign. This package guides building a portal; it is not an already hosted app.

## Triggers

Use for prelaunch signup pages, early-access or beta programs, product launches, scarce goods, appointment backfills, reservations, referral waitlists, high-traffic waiting rooms, and premium or cinematic campaign experiences.

Do not use for standalone landing-page copy, ordinary CRM/email administration, or checkout, inventory, and scheduling work without a waitlist-specific decision.

## Requirements

- An Agent Skills-compatible client
- For a live default deployment: Vercel, Neon, Twilio Verify and SendGrid accounts, a sending domain, and your chosen CRM; the agent handles build tools and configuration
- Qualified privacy/legal review when the program involves regulated data, commercial email, incentives, payments, allocation, or jurisdiction-specific obligations
