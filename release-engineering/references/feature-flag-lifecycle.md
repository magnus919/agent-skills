# Feature Flag Lifecycle

Feature flags are **runtime control points** that decouple deployment from release: code ships to production, but behavior is exposed deliberately and reversibly. A flag that is treated as a one-off `if` statement is a liability; a flag managed through a deliberate lifecycle is the fastest rollback mechanism in your toolkit and the backbone of progressive delivery. This reference covers the flag taxonomy, the seven-stage lifecycle, naming and ownership, flag debt, testing, tooling and the OpenFeature standard, SDK key security, anti-patterns, and the precise limits of flags as a rollback lever.

## Flag Taxonomy

Pete Hodgson's canonical taxonomy (martinfowler.com, 2017) classifies flags along two axes — **longevity** (how long the flag lives) and **dynamism** (how often and for whom the value changes):

| Category | Purpose | Typical Lifetime | Dynamism | Cleanup |
|----------|---------|------------------|----------|---------|
| **Release toggles** | Hide incomplete code; enable trunk-based development; decouple deploy from release | Days to weeks (transient) | Static (same for all users per release) | Remove within 1–2 weeks; add a removal task at creation |
| **Experiment toggles** | A/B and multivariate testing; statistically significant cohorts | Hours to weeks (until significance) | High (per-user, per-request) | Remove when the experiment concludes; never let linger past significance |
| **Ops toggles** | Operational control: kill switches, circuit breakers, load shedding | Mostly short-lived; a few permanent kill switches | Very high (reconfigure in seconds, no redeploy) | Retire once confidence is gained; review permanent kill switches quarterly |
| **Permission toggles** | Entitlements, premium features, alpha/beta access | Very long-lived (years) | High (per-user, per-request) | Treat as permanent; review annually; never auto-expire |

A simpler operational split — **temporary vs permanent** — maps directly onto the taxonomy: temporary flags are release, experiment, and interop-testing toggles (created to be removed); permanent flags are entitlements, load shedding, custom branding, and accessibility toggles (created to persist). The two halves have opposite governance: temporary flags demand expiry enforcement; permanent flags demand annual review and careful change control.

## The Seven-Stage Lifecycle

Each stage has distinct best practices. Treat every flag as passing through: **create → guard → evaluate → rollout → verify → remove → expire**.

### 1. Create

- Assign an **owner** at creation — the person responsible for cleanup.
- Choose the category (temporary vs permanent) and set an **expiry date** for temporary flags.
- Follow the naming convention `{type}-{team}-{feature}-{context}` (see below).
- **Create the companion removal PR at the same time** as the feature PR — a documented practice that converts "we'll clean up later" into a scheduled task.
- Keep scope minimal: one flag per feature unit. For multi-part features (e.g., a dashboard plus three widgets), use **prerequisite flags** — a parent flag plus child flags — rather than one sprawling flag or four independent ones.

### 2. Guard (Implement)

- Decouple *toggle points* from *toggle logic* with a centralized abstraction — e.g., `featureDecisions.showNewCheckout()` instead of scattered `flags.isEnabled("next-gen-ecomm")` calls. A single wrapper function means cleanup touches one file, and the code reads as intent, not plumbing.

```python
# One module owns every flag decision for this service.
# Cleanup = delete the wrapper + its tests, then archive the flag key.
class FeatureDecisions:
    def show_new_checkout(self, user) -> bool:
        return self._flags.get_boolean("release-payments-new-checkout-web",
                                       default=False, context=user)
```

- Convention: **OFF = legacy/old behavior, ON = new behavior**. Inverting this per-feature is how stale flags become dangerous.
- Place **per-user toggles at the edge** (UI layer) and **technical toggles in the core** service; avoid spreading the same flag across layers where a partial rollout can desync the experience.
- For kill switches, use **inverted logic**: kill-switch *disabled* = feature ON (default safe); kill-switch *enabled* = feature OFF. The safe default is the feature on, not off, so a misconfigured switch fails open for users.

### 3. Evaluate

- **Targeting rules** combine attributes (plan, region, cohort) with AND/OR logic.
- **Percentage rollouts** must use **deterministic/consistent hashing** on a stable identifier (user ID) so the same user always lands in the same bucket — otherwise users see the new and old state on alternating refreshes ("flickering"). This is sticky bucketing; no server-side session storage required.
- **Prerequisite flags** define valid dependency chains: the parent must be enabled before children are meaningful, and the SDK short-circuits children when the parent is off. Example: `release-analytics-dashboard` (parent) gates `release-analytics-dashboard-chart-a`, `...-chart-b`, and `...-export` (children); rolling the parent to 10% automatically scopes all three children to that same 10%.
- For experiments, bucket by user ID modulo so cohorts are stable across requests and can be analyzed later.

### 4. Rollout

- Progress through **tiers**: internal testers → beta/canary cohort → full production, and through **percentages**: 1% → 5% → 10% → 50% → 100%.
- Tie every step to **guardrail metrics** (error rate, latency, conversion). Roll back the flag, not the deploy, when guardrails trip. This is the same logic as canary analysis in [progressive-delivery.md](./progressive-delivery.md).
- Pause long enough at each step for the metrics window to be meaningful; a 1% canary for 30 seconds proves nothing.

A concrete rollout gate might look like:

| Step | Exposure | Gate to proceed | On gate failure |
|------|----------|-----------------|-----------------|
| 1 | Internal testers | No new errors in dogfood | Hold |
| 2 | 1% of traffic | Error rate ≤ baseline + 0.5% for 15 min | Toggle off, alert |
| 3 | 10% | P95 latency ≤ baseline + 10% for 30 min | Toggle back to 1% |
| 4 | 50% | Conversion within statistical bounds | Toggle back to 10% |
| 5 | 100% | Stable for 24h; then schedule removal | — |

Each step is a separate, logged event in the flag platform — the audit trail that makes flag rollback defensible to an auditor (see [change-governance-and-compliance.md](./change-governance-and-compliance.md)).

### 5. Verify

- **Test both flag states (ON and OFF)** in CI, plus the production-intended configuration and the fallback. With N flags, exhaustive combinatorial testing is impossible — focus on the flags changed in this release and their known interactions.
- Periodically verify the fallback values of *permanent* flags — a kill switch nobody has exercised in a year is a claim, not a capability.

### 6. Remove (Cleanup)

- Remove **all code references first**, then archive the flag in the flag platform. Deleting the key first strands the code; deleting after code removal is the safe order.
- Use **code-reference scanning** (LaunchDarkly code references, Uber's Piranha) to find every usage — including string literals in non-source files.
- **Archive, do not delete.** A deleted flag key can be recreated later, silently re-enabling old behavior (see Knight Capital below). Archival preserves history and prevents key reuse.

### 7. Expire

- **"Time bombs"** — tests or CI checks that fail if a flag outlives its expiry date — enforce removal mechanically.
- Detect stale flags continuously (GrowthBook auto-flags stale rules; a common target is **stale rate < 15%**, while most orgs run well above 40%).
- General guidance: **archive temporary flags quarterly (90–120 days)**. A healthy project has a high ratio of archived to unarchived flags.

## Naming and Ownership Conventions

| Practice | Convention | Why |
|----------|------------|-----|
| **Naming** | `{type}-{team}-{feature}-{context}`, e.g., `release-payments-new-checkout-web` | Self-documenting; a stale flag's type and owner are visible in its name |
| **Ownership** | Assigned at creation; owner responsible for cleanup | Prevents orphan flags; the flag registry shows who to page |
| **RBAC** | Limit who can toggle sensitive flags (prod kill switches) | A wrong toggle is an incident; scope the blast radius of the button |
| **Expiry** | Set at creation for temporary flags; enforced by time bombs | Removes the "we'll get to it" failure mode |
| **Definition of done** | "A feature is done when the flag is archived" | Pushes cleanup into the feature's own completion criteria, not a later debt cycle |

## Flag Debt and Cleanup

Unremoved flags are **technical debt with a unique compounding cost**: every stale flag doubles the combination space that tests must cover, masks dead code that developers fear to touch, and — in the worst case — becomes a live grenade.

- **Knight Capital (2012):** a reused flag name reactivated an obsolete trading algorithm; the firm lost **$460M in 45 minutes** and was sold days later. The mechanism: an old flag was repurposed, and its previous semantics came back alive. Never reuse flag keys; archive, don't delete.
- **Uber (Piranha):** built automated flag-removal tooling and deleted **2,000 stale flags** that had outlived their purpose. Piranha demonstrates that removal can be mechanized: find references, delete the toggle, migrate the test.
- **LaunchDarkly guidance:** target a 90–120 day time-to-archive for temporary flags; treat deletion of a key as a dangerous operation; use code references and "extinction events" to force cleanup of entire flag cohorts.

> **Gotcha — Flag debt is invisible until it bites:** A flag that has been ON for a year is not "working as intended" — it is dead code plus a test burden plus a future Knight Capital. If a flag's state has not changed in two quarters and it is not a permission/entitlement flag, it should be archived by default and defended on review.

## Testing Both Flag States

Every flag-gated code path must be exercised **ON and OFF** in CI, because the OFF path is what ships if the flag rolls back. Practical guidance:

- Test the production-intended configuration *and* the fallback configuration.
- Focus combinatorial effort on flags changed in the current release plus their prerequisite chains; do not attempt exhaustive N-flag matrix testing.
- For kill switches, include a scheduled drill: toggle, verify the feature actually disappears, toggle back.
- Add the flag-state matrix to the release checklist so a rollout that flips two interacting flags is caught before production.

## Tooling and the OpenFeature Standard

**OpenFeature** (CNCF, incubating since December 2023) is a vendor-neutral SDK standard. It standardizes the *application-facing* surface and deliberately leaves the *platform* surface vendor-specific:

| OpenFeature standardizes | OpenFeature does NOT standardize |
|--------------------------|----------------------------------|
| **Evaluation API** — vendor-agnostic `getBooleanValue("flag", false, context)` | Flag creation UI and admin workflows |
| **Evaluation Context** — key-value container (static global + dynamic per-request) | Targeting rule syntax |
| **Provider interface** — translates API calls to any vendor SDK (LaunchDarkly, Flagsmith, Unleash, ConfigCat, GrowthBook, or a local file) | Percentage rollout algorithms |
| **Hooks** — lifecycle interceptors for logging, telemetry, validation | Flag storage and audit trails |
| **Events** — provider readiness, error, config-change notifications | — |
| **OFREP** — Remote Evaluation Protocol for network evaluation | — |

SDK architecture splits into two evaluation models:

- **Server-side SDKs:** cache the full ruleset locally and evaluate in-process — **sub-millisecond** evaluation, thousands of evals/sec without per-request network cost.
- **Client-side SDKs:** evaluation is delegated to the vendor server per context; the full ruleset (including targeting rules that may embed PII) is **never** downloaded to clients.

### Platform Selection

| Platform | Type | Notable |
|----------|------|---------|
| **LaunchDarkly** | Commercial SaaS | Market leader; code references; flag lifecycle automation; engineering insights |
| **Flagsmith** | Open-source + SaaS | Self-hostable; OpenFeature provider |
| **Unleash** | Open-source + SaaS | 25+ SDKs; dependent flags; kill-switch patterns; GitLab integration |
| **ConfigCat** | SaaS | Budget-friendly; OpenFeature provider |
| **GrowthBook** | Open-source + SaaS | Warehouse-native; experimentation built in; feature evaluation diagnostics |
| **DevCycle / Statsig / Harness** | Commercial | Experimentation-first platforms; governance tooling |
| **GO Feature Flag** | Open-source | Built on OpenFeature; OFREP support |

**Build vs buy:** a config file or environment variable is genuinely enough when you have fewer than ~10 flags, no targeting needs, and no runtime toggling requirement — or in air-gapped environments where no SaaS is acceptable. Beyond that, the operational burden (admin UI, audit trails, RBAC, code-reference scanning, stale detection) makes a dedicated platform — or an OpenFeature-backed integration layer — the cheaper long-term choice. See [toolchain-landscape.md](./toolchain-landscape.md) for the wider deployment/observability tooling context.

### SDK Key Security

The LaunchDarkly key model is representative of the industry:

| Key type | Used by | Security posture | Prefix |
|----------|---------|------------------|--------|
| **SDK key** | Server-side SDKs | **Secret** — grants read access to the full ruleset; rotate if exposed | `sdk-` |
| **Mobile key** | Mobile SDKs (Android, iOS, React Native) | Not secret — only flags marked "available on mobile SDKs" | `mob-` |
| **Client-side ID** | JS client-side SDKs, edge SDKs | Not secret — only flags toggled for client-side use | alphanumeric |

> **Gotcha — SDK key in a client:** Embedding a server-side SDK key in a web or mobile app exposes the full ruleset, including targeting rules and potentially PII-bearing attributes. Client-side IDs exist precisely so you never ship a secret. Rotate any `sdk-` key that appears in a client bundle or a public repo.

Mobile specifics: streaming updates in the foreground, hourly polling in the background (battery/data), cached values served offline, and — critically — **iOS SDKs do not background-fetch**. App store review also treats flag-gated features as live: a hidden-but-functional feature in the binary can trigger review rejection.

## Anti-Patterns

| Anti-pattern | Description | Mitigation |
|--------------|-------------|------------|
| **Flag hell / sprawl** | Hundreds of unowned flags; combinatorial test explosion; nobody knows who owns what | Ownership, naming, expiry, stale detection (<15%), WIP limits on flag count |
| **Flags as permanent config** | Using release flags for static config that rarely changes; using flags as a database or secrets store | Use proper config management and secrets tooling; flags are for runtime behavioral control |
| **Flags masking dead code** | Unremoved flags hide unreachable paths; developers fear removal | Code-reference scanning, extinction events, Piranha-style automated removal |
| **Reused flag keys** | The Knight Capital scenario — old semantics come back alive | Never reuse keys; unique namespacing; archive not delete |
| **Non-sticky percent rollouts** | No consistent hashing → users flicker between states on refresh | Deterministic hashing on stable ID (all major platforms do this) |
| **Remote evaluation latency** | Per-request evaluation from a remote server compounds at thousands of evals/sec | Local/in-process evaluation, CDN caching, edge SDKs; sub-millisecond target |
| **Nested/conflicting flags** | Two flags control overlapping behavior; invalid state combinations | Prerequisite flags; single-purpose flags; document the dependency graph |
| **Client payload leaks** | Full rulesets (and their targeting PII) shipped to clients | Client-side IDs only; mark PII attributes private; never send rulesets to clients |
| **Interaction blindness** | Cannot answer "what does user X see?" across dozens of flags | Per-user flag previews and evaluation diagnostics in the flag platform |

## Flags as the Primary Rollback Lever — and Its Limits

For **code-level behavioral regressions**, a flag rollback beats an artifact rollback on every axis that matters in an incident:

| Dimension | Flag rollback | Artifact rollback |
|-----------|---------------|-------------------|
| Speed | Sub-second (toggle) | Minutes to tens of minutes (redeploy previous version) |
| Scope | Per-feature, per-user-segment | Entire deployment unit |
| Risk | Low — only the toggled feature is affected | Higher — reverts all changes in the artifact |
| Reversibility | Instant re-enable | Requires another deploy |
| Audit | Flag change logged in the flag platform | Deployment logged in CI/CD |

**But flags cannot undo reality.** They are a lever over *code paths*, not over *state*:

1. **Database schema changes** — a flag cannot un-alter a table. Use the **expand/contract pattern**: (a) add the new column additively, (b) deploy code behind a flag that uses the new column, (c) roll the flag out, (d) once stable, deploy code that stops reading the old column, (e) contract — drop the old column in a separate migration. **Wrap flags around code, never around DDL.** See [rollback-and-recovery.md](./rollback-and-recovery.md).
2. **Infrastructure changes** — flags do not control load balancers, DNS, or network policy. Use blue/green, canary infrastructure, or IaC rollback for those.
3. **Data mutations** — if flag-gated code writes data in a new format, toggling off does not undo the writes. Requires dual-write, backfill scripts, or compensating migrations.
4. **External side effects** — emails sent, payments processed, API calls made. Flags prevent future occurrences; they cannot reverse past ones.
5. **Multi-service contracts** — if service A's flag-gated change requires service B to change in lockstep, toggling one without the other breaks the contract. Requires coordinated rollout or API versioning.
6. **Mobile store review** — a flag can gate a feature, but the feature is still *in the binary* and reviewed as live; kill-switch-grade removal of a harmful feature may still require an app update.

> **Gotcha — The flag-rollback reflex:** Toggling a flag off does not "roll back" schema migrations, background jobs that already ran, or writes already committed. Before you tell an incident team "just flip the flag," check what the flag actually guards: code paths (safe to flip) or data/infra state (needs a complementary mechanism).

## Sources and Further Reading

- [Feature Toggles (aka Feature Flags) — Pete Hodgson, martinfowler.com](https://martinfowler.com/articles/feature-toggles.html) — the canonical taxonomy and lifecycle
- [Reducing technical debt from feature flags — LaunchDarkly](https://launchdarkly.com/docs/guides/flags/technical-debt) — lifecycle stages, archival, code references
- [OpenFeature Introduction](https://openfeature.dev/docs/reference/intro) — what the CNCF standard does and does not cover
- [Choosing an SDK type — LaunchDarkly](https://launchdarkly.com/docs/sdk/concepts/client-side-server-side) — SDK key types, client vs server evaluation, mobile behavior
- [4 Types of Feature Flags — Octopus Deploy](https://octopus.com/devops/feature-flags/) — taxonomy confirmation, management best practices
- [How to Implement Feature Flags at Scale — GrowthBook](https://www.growthbook.io/blog/how-to-implement-feature-flags-at-scale) — governance, stale detection, Knight Capital and Piranha case studies
- [Kill Switches Best Practice — Unleash](https://www.getunleash.io/blog/kill-switches-best-practice) — inverted-logic kill switch design
- [Database Migrations with Feature Flags — Harness](https://www.harness.io/blog/database-migration-with-feature-flags) — expand/contract, flags around code not DDL
