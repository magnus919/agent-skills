# The default implementation path

Use for ordinary branded prelaunch capture. This selection favors a small
number of managed services and a static page that a marketing team can revise.
The choices below are project defaults, with documented provider facts checked
2026-09-15. Recheck versions and plan limits when generating an application.

## Fixed choices unless the campaign supplies a reason to change

| Concern | Default | Reason |
| --- | --- | --- |
| Page | One `index.html`, semantic HTML and custom CSS | Content renders without a server framework |
| Dynamic behavior | Alpine.js CSP build, bundled locally | Forms and status live in ordinary HTML; avoids requiring unsafe-eval |
| Build | Vite with pinned dependencies and lockfile | Produces static assets; Node is a build tool as well as the API runtime |
| API | Small TypeScript functions on Node.js, Vercel | One host, same-origin requests, supported default runtime |
| Persistence | Neon managed Postgres, pooled connection, `pg` driver | Durable relational state without database server operations |
| Verification | Twilio Verify; SendGrid integration for email | Managed code generation, delivery and checking for email and SMS |
| Hosting | Vercel | Static delivery, API functions, previews and domain management together |
| Async work | Postgres outbox, authenticated bounded Vercel Cron drain | Durable effects without a second queue product for a small launch |
| CRM | Runtime-selected adapter; connection pending until chosen | Fits an existing CRM without imposing another sales system |
| Bot checks | Server validation, shared rate limits; Turnstile when needed | Controls protect actual send/write operations |
| Brand media | Versioned uploaded/exported assets with poster fallback | Reliable publication with optional Canva sourcing |

Use a currently supported Node LTS and matching TypeScript/tool versions; pin
the choice in the generated project after checking Vercel compatibility. Do not
introduce Next.js, a React app, an SSR server, or a custom account dashboard just
to serve the one-page campaign. Vite's development server is not production.

Use Alpine's CSP-compatible package and external component registration. Test
the expressions used against that build; its expression support differs from
the default package. Bundle dependencies rather than relying on a floating CDN
URL. Keep a strict script policy and explicit allowed verification/challenge
origins. Only public fields may be exposed through Vite's client environment.

## Generated project layout

```text
index.html                Static campaign content and accessible form
src/main.js               Alpine components and API calls
src/styles.css            Brand variables, layout and motion
public/                   Approved logos, imagery, posters and media
campaign.public.json      Copy and presentation only; no credentials
api/                      Thin TypeScript request handlers
server/                   Domain rules, DB access and provider adapters
migrations/               Versioned SQL; never run on every request
tests/                    API/domain/provider contract and browser tests
vercel.json               Routing, headers, function and cron settings
package.json              Build, test, typecheck and migration commands
.env.example              Names and purpose only; no real secrets
```

Use explicit API paths and exclude them from any page fallback rewrite. Vite
outputs `dist`; ensure Vercel also discovers the API functions. Smoke-test both
the static document and API in the actual preview deployment. Run migrations
as a controlled release step with a separate migration credential. Preview
deployments use separate databases/provider test accounts and never inherit
production recipients or CRM credentials. Do not put live contact data in seeds.

Keep one database region near the API region, TLS on, small bounded connection
pools, request timeouts, and parameterized SQL. Use Neon's pooled connection for
normal API traffic; verify migration and transaction-pooling compatibility.
No browser database credentials or direct browser writes to Postgres.

## Verification default

Default to required email confirmation by code, with phone collection off.
When phone is enabled, default to a managed SMS code; campaign policy determines
whether phone proof is optional or required. Codes keep both flows on the page.
Use Twilio Verify's email integration with a SendGrid account, authenticated
sending domain and configured template. Sender setup is real work: expose it
as a connection card, not a promise of zero setup. Provider accepts the code
check; the API binds that result to the exact pending contact and updates local
state. Record verified channel, destination version, method and timestamp.

Twilio Verify does not establish CRM permission. Do not add marketing material
to verification messages. Marketing SMS remains separately selected and consented.
Read current provider opt-in, allowed-country, sender and fraud-protection
requirements before enabling real sends. Set a budget ceiling and destination
limits. A missing required verifier blocks production readiness, not preview.

Magic links remain an extension. If requested, prefer a provider with a
documented managed email-link flow (Stytch is one candidate), retaining its
scanner protection and testing destination binding. Do not equate a Verify
code example with a native SMS-link product. Custom links require the lifecycle
in the implementation contract. Existing user approval of codes removes the
need to preserve a link requirement for this default path.

## Worker execution and plan selection

Store outbound intent with the entry. An authenticated cron endpoint claims a
bounded batch, calls providers and records outcomes, stopping before the
function deadline. Never start an unawaited promise or background timer after
returning the request and assume it will finish. Cron is a wake-up, not the
durable queue; Postgres is the queue of pending work.

For verification latency, after commit the request may attempt one bounded send
through the same leased dispatcher. Failure leaves the item for the worker;
success is recorded before the browser says the message was sent. A frontend
status request may poll briefly with backoff, then offer resend/help. Polling
does not itself authorize another send. Provider timeout can have an unknown
outcome; obey provider reconciliation and resend limits before retrying.

Check the selected Vercel plan's allowed cron frequency, timing accuracy,
commercial-use terms, function duration, and cost. Budget for a plan supporting
the required worker cadence; do not sell a commercial launch on an assumed
free tier. If the cadence cannot meet confirmation/CRM targets, use a managed
authenticated scheduler or queue and document the extra service. Protect worker
endpoints with a server secret; prevent overlapping jobs with database leases.

## Runtime CRM configuration

The owner selects their existing CRM during connection. Default adapter example
is HubSpot, not an automatic account purchase or a claim that every CRM works.
Read credentials from the host's secret store, and the versioned mapping and
provider selection from server configuration. A runtime change may require a
function restart/redeployment; it must not require editing public HTML.

Read `templates/campaign-config.example.json` for the configuration shape.
Validate it before activating the campaign. Refuse unknown adapters and missing
required credentials. Keep a disabled adapter distinct from a configured adapter
that is failing. Backfill current eligible records after connection through the
outbox. Pending verification and pending CRM are separate operator states.

## Explicit alternatives

Preserve a working existing stack or provider when it meets the contract.
If a compiled service is specifically chosen, keep the static page on Vercel
and deploy Go to an appropriate managed service; specify its cost, region,
worker model, and routing. Vercel currently labels Go and Rust runtimes beta;
do not switch languages to solve that limitation without checking the target.
The approved general default is Node.js, not a beta compiled runtime.

Traffic gating, lotteries, inventory and appointment scheduling are separate
patterns. Do not claim this capture architecture can safely serialize checkout
at a mass launch; use the appropriate admission or capacity authority.

## Primary sources

- [Alpine CSP build](https://alpinejs.dev/advanced/csp)
- [Vite static deployment](https://vite.dev/guide/static-deploy)
- [Vercel Node.js](https://vercel.com/docs/functions/runtimes/node-js)
- [Vercel Go](https://vercel.com/docs/functions/runtimes/go) and [Rust](https://vercel.com/docs/functions/runtimes/rust)
- [Vercel cron plan limits](https://vercel.com/docs/cron-jobs/usage-and-pricing)
- [Neon connection pooling](https://neon.com/docs/connect/connection-pooling)
- [Twilio Verify email with SendGrid](https://www.twilio.com/docs/verify/email)
- [Twilio Verify consent](https://www.twilio.com/docs/verify/consent-opt-in)
