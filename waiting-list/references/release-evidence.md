# Release evidence and operations

Read when testing a generated portal or deciding whether it can launch.
Keep evidence per revision with date, environment, provider versions, commands,
results, screenshots, and unresolved limitations. A skill eval manifest checks
output quality; it is not evidence that a generated portal works.

## Implementation sequence

1. Build the branded static page and every form state with deterministic fake
   responses. Mark preview mode. Retain mobile/desktop and motion-off captures.
2. Implement migrations and API; run against disposable Postgres, not an
   in-memory substitute for concurrency tests. Verify durable registration.
3. Add a fake verification adapter for expiry, failures, and race tests, then
   use the selected provider's test environment and controlled destinations.
4. Add fake CRM responses, then the chosen CRM's test tenant. Exercise upsert,
   retry, withdrawal, and reconciliation. Preserve unrelated CRM properties.
5. Deploy a preview using isolated secrets/database/provider environments.
   Verify actual routes, callbacks, headers, assets, cookies, and worker wakeups.
6. Complete campaign-owner review and production connection checks. Publishing
   uses the authorized domain and account; record a rollback deployment and a
   way to pause signup/outbound work independently.

## Required evidence for the default capture path

| Test | Observable result |
| --- | --- |
| 20 concurrent submissions of the same contact | One canonical entry and no multiplied verification/CRM effects |
| Retry after committed response is lost | Same safe acknowledgement, no duplicate entry |
| Provider outage during send | Entry persists, pending state is honest, eventual retry or actionable failure |
| Wrong/expired code and exhausted attempts | No verified contact, no eligible CRM payload |
| Email verified while required phone is pending | Membership/CRM gate stays closed |
| Optional phone remains unverified | Eligible email can sync; phone is absent from CRM payload |
| Contact changes while proof check is in flight | Old destination cannot become current verified contact |
| Callback replay, scanner GET, forged provider event | No additional activation, CRM write, or unauthorized disclosure |
| CRM returns 429 or times out after write | Retry/lookup converges on one remote identity |
| Withdrawal races with CRM write | Local sends stop and compensating remote suppression completes |
| Two workers claim the same batch | Leases/idempotency prevent conflicting effects; expired leases recover |
| Deployment preview | No production DB writes, messages, or CRM records |
| Background video fails, motion disabled, JS disabled | Readable campaign and truthful usable fallback remain |

For enabled queue/referral/booking/allocation modes add that mode's invariants;
do not demand inventory tests for a simple email interest list. API tests also
cover body limits, Origin/CSRF, unauthorized status access, admin authorization,
webhook signatures, log redaction, and configuration rejecting browser secrets.

## Starting operational targets

These are proposed initial targets to test and adjust, not provider guarantees:

- Valid accepted submissions: at least 99.9% durable acknowledgements over the
  campaign's measured window; exclude explicitly classified input/abuse errors.
- Registration API: p95 under 1 second at expected peak, including cold starts.
- Verification: 95% provider-accepted sends within 60 seconds; record delivery
  separately because provider acceptance does not prove inbox/handset receipt.
- CRM: 99% of eligible changes applied within 5 minutes during healthy service;
  oldest pending age above 10 minutes for two checks alerts the operator.
- Zero leaked credentials or raw proof tokens in browser bundles/log captures.

Measure registration errors, committed entries, provider send latency, proof
success/expiry, rate-limit denials, CRM pending age/retries/dead letters,
suppression age, and worker last-success time. Avoid email/phone/token values
as metric labels. Correlate opaque request/event IDs. Alert on database failures,
missing worker heartbeats, authentication errors, persistent suppression delay,
or the messaging spend ceiling; verification conversion is a funnel metric,
not by itself an availability incident.

Test the expected peak and a 2x burst, noting duration and workload. Compute
rough worker capacity as batch size / measured batch time; ensure it exceeds
peak event generation with headroom. Include database connection limits and
provider quotas. Avoid unsupported global scale claims from a local benchmark.

## Operator recovery

Show “Email confirmation delayed,” “CRM connection needs attention,” and “New
registrations paused” with a concrete action. Keep raw provider diagnostics in
restricted logs. On outage, retain durable work, stop uncontrolled resend loops,
repair the connection, preview replay scope, and replay through the same worker.
Reconcile local version and remote ID afterward; do not bulk re-create contacts.

Pause new entries and outbound work independently. Rolling back the static
deployment does not roll back database migrations or delete provider messages.
Use additive compatible migrations first, retain the old deployment's compatible
schema, and document a forward repair for irreversible data changes.

## Research and skill evaluation

For dependency recommendations retain official source URL, date, version or
commit, license, relevant inspected files, maintenance signal, and observed
limitations. A README-only observation stays explicitly README-only. Never turn
the unverified Gemini examples into mandatory dependencies.

Run portable output cases with this skill and a baseline in fresh contexts.
Retain actual outputs and per-assertion evidence; use observable behavior for
API tests and human review for brand quality. Run the separate trigger queries
through a client that records skill loading. Report manifest/schema validity,
behavioral runs, and production connection checks as separate evidence levels.
