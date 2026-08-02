# Monorepo and Polyrepo Release Strategies

Where code lives determines how releases happen. Polyrepos isolate teams but make dependency change a **coordination problem**; monorepos make coordination cheap but push complexity into **build, versioning, and release tooling**. This reference covers the two models, the versioning schemes each enables, affected-build detection, the release tooling landscape, topological publishing, real-world anchors, and decision guidance.

## The Polyrepo Model

In a polyrepo architecture, each repository owns its own CI/CD pipeline, versioning strategy, and release cadence. Independence is the feature: teams get full autonomy over branching, deployment policy, and cadence, and access controls are enforced per project. The cost is that **dependencies must be created deliberately** — every shared library change requires a publish step to a registry, and every consumer must discover, evaluate, and adopt the new version.

### Registry-Mediated Dependency Propagation

Cross-repo coordination flows through registries (npm, PyPI, Maven Central, crates.io). Version pinning strategies — exact pins (`1.2.3`), caret ranges (`^1.2.3`), tilde ranges (`~1.2.3`) — determine how eagerly consumers adopt updates. Polyrepo workflows therefore lean heavily on **automated dependency-update bots**:

- **Renovate** (Mend): 90+ package managers, works across GitHub/GitLab/Bitbucket/Azure DevOps, monorepo-aware grouping and scheduling, auto-merge support.
- **Dependabot** (GitHub): zero-config for GitHub-hosted repos, security alerts and version updates, less flexible for complex or non-GitHub setups.

### Coordination Cost Scaling

The core polyrepo pain is **synchronizing deployments across repositories**. A breaking change to a shared library does not ship — it *cascades*:

- A breaking change in a shared lib triggers **N separate PRs** (one per consumer repo), each with its own review cycle — a process Renovate/Dependabot can generate but not approve for you.
- Update cascades form: service A updates and breaks service B, which blocks service C; the failure is a *topological* problem, not a per-repo one.
- Adoption timing diverges — some repos update immediately, others lag for months, so you permanently run a matrix of library versions in production.
- Atomic cross-service refactors are effectively impossible: there is no single commit that fixes all consumers.

A concrete example: library `auth-core@2.0.0` removes the legacy token format. With 50 consumer services across 50 repos, that is 50 update PRs (Renovate/Dependabot generate them), 50 review cycles, and 50 deployment windows — and service 17's team is on vacation, so for weeks the org runs 49 services on the new contract and one on the old, with the shared identity provider forced to serve both.

**Backporting** is the same problem in miniature: a security fix must be cherry-picked into each repo's stable branches independently. There is no shared stable branch to fix once. GitLab's patch process (backporting security fixes to multiple stable branches) is the canonical monorepo alternative to this per-repo chore.

### Coordination Patterns That Work in a Polyrepo

Polyrepo coordination is a discipline, not a tool. The patterns that keep it tractable:

| Pattern | How it works | Failure mode it prevents |
|----------|--------------|--------------------------|
| **Explicit version pinning policy** | Decide exact-pin vs caret/tilde per artifact class; document it | Silent adoption of breaking versions via loose ranges |
| **Compatibility windows** | Shared libs guarantee N-1 support; majors announce deprecation one cycle ahead | Consumers forced to upgrade on the library's schedule |
| **Dependency-update cadence** | Renovate/Dependabot batches by type (security immediate, minors weekly, majors monthly) | Update PR flood and last-minute major migrations |
| **Contract tests at the boundary** | Consumer-driven contract tests against the shared lib's published API | Cross-repo breakage discovered at deploy time, not CI time |
| **Shared release notes channel** | Every lib publish posts notes consumers can triage | Consumers learning about breaking changes from failing builds |

None of these eliminates the coordination cost — they bound it. If the cost keeps growing regardless, that is the signal that the affected packages belong in a shared repo.

## Monorepo Versioning Models

### Fixed / Synchronized Versioning — The "One Version Rule"

All packages share a **single version number**. Lerna's fixed mode (the default) operates on a single version line: any updated package is released at the new shared version, and `--force-publish` pushes all packages to version together, preventing drift. A major change in any package bumps **all** packages to a new major.

The philosophy's strongest form is Google's **one-version rule**: "There may only be one version of a package in //third_party." Rationale: (1) *maintenance* — multiple copies means multiple locations to keep updated; (2) *security* — vulnerability feeds omit older affected versions, and older versions accumulate latent vulnerabilities; (3) *diamond dependencies* — if two versions exist, eventually a build depends on both, and untangling the conflict can stop an unrelated project dead. Exceptions require formal approval (temporary <1 month auto-approved; >1 month needs director sign-off; permanent is rarely granted). This is the philosophical opposite of npm-style independent versioning.

### Independent Per-Package Versioning

Each package versions on its own SemVer line. **Changesets** is purpose-built for this: developers declare intent per package via small markdown changeset files, and the tool flattens the bump types into a single release per package while handling internal dependencies across a multi-package repository. Lerna's independent mode prompts per-package versions at publish time.

| Dimension | Fixed / one-version | Independent |
|-----------|---------------------|-------------|
| Version count | One for the whole repo | One per package |
| Upgrade story for consumers | Everything moves together; no version matrix | Per-package; consumers choose when to adopt |
| Atomicity | All packages release together | Packages release as they are ready |
| Fit | Google-style source-built monorepos, tight coupling, compliance | OSS libraries (npm ecosystem), decoupled lifecycles |
| Tooling | Lerna fixed mode, release-please `linked-versions` | Changesets, Lerna independent mode, release-please per-package |

### Release Trains

A release train is a **calendar-forced** release: everything merged and deployed by the cut date ships together, whether or not any single feature is "done" — the train leaves on time. GitLab is the canonical example: monthly releases on the third Thursday, with auto-deploy → release candidate (2 days before) → tag day → release day. Features ship only in monthly releases; patch releases carry only fixes; an MR must be merged, deployed to production, and stay deployed without rollback to be included. Trains trade feature timing for coordination cost and predictable dates — see [release-process-models.md](./release-process-models.md) and [release-operations-and-triage.md](./release-operations-and-triage.md).

The opposite end of the spectrum is **publish-on-merge**: every merged change that passes gates becomes part of a release immediately (what Changesets-enabled monorepos like Astro and SvelteKit effectively do per package). The two ends differ on cadence, not on quality gates:

| Dimension | Release train | Publish-on-merge |
|-----------|---------------|------------------|
| Cadence | Fixed calendar (monthly, weekly) | Every merge / every N merges |
| Feature timing | Fixed by the schedule | As soon as it is ready |
| Coordination cost | Low (everything rides the train) | Low per change, but version churn for consumers |
| Rollback | Whole train re-rolled or patch-released | Per-package version pin rollback |
| Fit | Enterprise, regulated, self-managed products | SaaS, libraries, fast-moving OSS |

Most organizations land between the extremes: continuous deployment to internal environments, plus a calendarized *customer-visible* release (train) for self-managed or on-prem consumers — which is exactly GitLab's model.

## Affected-Build Detection

The monorepo build problem: how do you know what to build and test for a given change, when the repo contains dozens or hundreds of projects? The answer is **affected-target analysis** — compute the minimal set of projects affected by a change:

| Tool | Mechanism | Notes |
|------|-----------|-------|
| **Nx** | `nx affected -t <task>`: git-diff changed files → map to projects via the project graph → transitive dependents | Configurable `--base`/`--head` SHAs; `projectsAffectedByDependencyUpdates` controls how dependency updates propagate |
| **Turborepo** | Content hashing of inputs (source, env vars, task dependencies) → cache hits skip unchanged packages | `dependsOn: ["^build"]` ensures dependency tasks run first; remote caching accelerates |
| **Bazel** | Build graph is a DAG of targets with explicit deps; changed-target transitive closure | Google's Piper/Blaze runs presubmit on affected targets only; the deepest form of the model |

> **Gotcha — Affected ≠ unaffected:** If you modify a widely used project, "affected" correctly expands to nearly the whole repo — running tasks for almost all projects is the tool telling you the truth about blast radius. Conversely, a known Nx limitation (nrwl/nx#33276) is that `nx release` has assumed all releaseable projects were built, which conflicts with the affected workflow — validate your release pipeline against the affected set explicitly.

**Changesets takes a different route:** developers *declare* which packages are affected via changeset files (human-declared intent) rather than the tool computing it — trading computation for explicit authorship. The Changesets GitHub Action aggregates pending changesets into a single "version PR" that bumps versions and updates changelogs. A changeset is a small markdown file:

```markdown
---
"@repo/analytics": minor
---

Add session-replay export to the analytics API.
```

The Changesets bot flags PRs that change a package without adding a changeset, keeping the declaration discipline automatic.

### Release-Pipeline Leverage

Affected detection feeds two release strategies:

- **Publish only changed packages** — Nx Release versions and publishes per project; Changesets publishes only packages with pending changesets. Efficient, but consumers must handle partial availability.
- **Release-all on a train** — GitLab ships everything deployed to production in the monthly train; Lerna `--force-publish` publishes all packages regardless of changes. Predictable, but noisy releases for unchanged packages.

The choice mirrors the versioning model: publish-only-changed pairs with independent versioning; release-all pairs with fixed/one-version.

## Release Tooling Fit

| Tool | Model | Best fit |
|------|-------|----------|
| **Changesets** | Human-declared intent (markdown files), version PR, publish | JS/TS monorepos, independent versioning (pnpm, Astro, SvelteKit, Chakra UI, Remix, Firebase JS SDK) |
| **Lerna** | Fixed (default) or independent mode; `lerna version`/`lerna publish`; `from-package` retry | Legacy JS monorepos; teams already on Lerna; task-running delegated to Nx/Turborepo |
| **semantic-release** | Fully automated from conventional commits (analyze → bump → changelog → publish) | Single repos; small monorepos via community plugins (`multi-semantic-release`, `semantic-release-monorepo`) |
| **release-please** | Manifest mode: combined Release PR across configured packages from two config files; plugins `node-workspace`, `cargo-workspace`, `maven-workspace`, `linked-versions`, `group-priority` | Multi-language monorepos, Google-style, hundreds of packages |
| **Nx Release** | Three phases (versioning, changelog, publishing); independent or grouped; npm/Docker/crates targets; programmatic API; `--dry-run` | Nx workspaces needing multi-target publishing |

Automation spectrum worth noting: **semantic-release** (fully automated, no human gate) → **release-please** (auto-generates a release PR, human merges) → **changesets** (developer declares intent per PR). Turborepo itself does not version or publish — its official recommendation is to pair it with Changesets (`turbo run build lint test && changeset version && changeset publish`). For the wider toolchain context (versioning, CI/CD, deployment), see [toolchain-landscape.md](./toolchain-landscape.md).

## Publishing Order and Failure Recovery

### Topological Publish Order

Packages must be published **dependencies-first**. If `@repo/ui` depends on `@repo/utils`, `@repo/utils` must reach the registry before `@repo/ui` publishes, or the registry resolves a version that does not exist. For a dependency chain `app → @repo/ui → @repo/utils → @repo/core`, the publish order is `@repo/core`, then `@repo/utils`, then `@repo/ui`, then `app` — each step's registry range resolving to an already-published version. pnpm recursive commands (`pnpm -r publish`) respect topological order by default; Lerna publishes topologically; Nx Release respects the project graph; release-please's `node-workspace` plugin updates the dependency references in each consumer's manifest as it walks the graph.

### The `workspace:` Protocol

During development, workspace packages reference each other locally via the `workspace:` protocol; at publish time pnpm rewrites it to registry ranges:

| Workspace spec | Published as |
|----------------|--------------|
| `workspace:*` | `1.5.0` (exact version) |
| `workspace:~` | `~1.5.0` |
| `workspace:^` | `^1.5.0` |
| `workspace:^1.5.0` | `^1.5.0` |

This lets you depend on local packages during development and publish without intermediate publish steps. Note `saveWorkspaceProtocol` defaults to `rolling` (saves `workspace:^`).

> **Gotcha — Leaked `workspace:` specifiers:** If a package publishes with an unreplaced `workspace:*` range, consumers cannot resolve it. Verify post-publish that registry metadata contains real versions, and make the rewrite a pipeline assertion, not an assumption.

### Partial-Publish Failure Recovery

A multi-package publish is **not atomic**: if package 3 of 10 fails, packages 1–2 are already on the registry and 4–10 are not. Recovery relies on idempotent retry:

- **Lerna `from-package`:** compares local vs registry versions and publishes only what is missing — re-running after a partial failure converges.
- **Changesets:** `changeset publish` is idempotent; re-running skips already-published versions.
- **release-please:** separates tag creation from publishing — if publish fails, tags exist and the publish step can be retried.
- **npm/pnpm:** `--access public` and OTP/2FA can fail mid-batch; plan for it in the retry loop.

**Cyclic dependencies** break topological ordering: pnpm cannot guarantee script order when workspace cycles exist (`disallowWorkspaceCycles` can make installation fail on cycles instead). Shopify built **Packwerk** specifically to detect and prevent circular dependencies between its monolith components.

## Real-World Anchors

- **Google (one-version monorepo):** ~35,000 developers, billions of lines of code, Piper VCS + Blaze/Bazel build system. One version of every dependency, enforced by policy; all code built from source at HEAD; presubmit on affected targets; large-scale changes via tooling (Rosie). External releases (Go, Angular) use separate processes.
- **GitLab (single repo, release train):** all code in one repository; monthly release train for 178+ consecutive months; auto-deploy daily, RC 2 days before release, tag Wednesday, release Thursday 13:00 UTC; patch releases for security/critical fixes from stable branches; features ship only in monthly releases.
- **Shopify (modular monolith):** a 2.8M+ line Ruby monolith with ~37 components (Rails Engines), Packwerk for dependency enforcement, Sorbet for contracts; selective extraction only for clear reasons (storefront rendering — high-throughput read-only; credit-card vaulting — sensitive data). New Rails apps are "componentized by default": a monorepo with internal modularity rather than npm-style publishing.

## Decision Guidance: Monorepo vs Polyrepo

| Choose monorepo when... | Choose polyrepo when... |
|------------------------|------------------------|
| Packages are tightly coupled and change together | Services are loosely coupled with independent lifecycles |
| Atomic cross-package changes are frequent | Teams need full autonomy over release cadence |
| Shared libraries have many internal consumers | Strict access-control / compliance boundaries per project |
| You want single-version consistency (Google model) | Different compliance/retention rules per product |
| A platform team manages many related packages | Repository size would exceed tooling limits |
| You need system-wide visibility into change impact | You need independent CI/CD scaling per service |

Monorepos excel at code sharing and consistent standards; polyrepos enforce strong per-project security boundaries at the cost of visibility and coordination. **Switching later is expensive and disruptive** — the migration cost argument cuts both ways, so the choice should be deliberate, not accidental.

### Migration Heuristics

- **Toward a monorepo:** if you spend more time coordinating library changes across repos than building features (the "50 PRs for one change" pattern), consolidating the *shared* packages first — while leaving genuinely independent services separate — captures most of the benefit without a big-bang migration. Shopify's modular monolith is the proof that internal modularity can substitute for package-publishing overhead.
- **Away from a monorepo:** if one component's compliance regime (SOX scope, data residency, customer-isolated tenancy) keeps colliding with the rest, extract that component first; the per-repo pipeline cost is a tax you pay to gain the boundary.
- **Never migrate for tooling novelty.** Nx, Turborepo, and Bazel make monorepos *tolerable*; they do not make a loosely coupled polyrepo system better. Measure the actual coordination pain before restructuring.

> **Gotcha — Monorepo ≠ single version:** Choosing a monorepo does not force you into one-version semantics. Independent versioning (Changesets/Lerna independent mode) gives you atomic cross-package *refactors* while keeping per-package *versions* — the two decisions (repo topology vs versioning model) are orthogonal and should be made separately.

## Sources and Further Reading

- [Google One-Version Rule](https://opensource.google/documentation/reference/thirdparty/oneversion) — the one-version philosophy and exception process
- [Changesets documentation](https://changesets-docs.vercel.app/readme.html) — intent-based publishing for JS/TS monorepos
- [Lerna version and publish](https://lerna.js.org/docs/features/version-and-publish) — fixed vs independent mode, `from-package` retry
- [Nx affected](https://nx.dev/docs/features/ci-features/affected) — git-diff + project-graph affected detection
- [release-please manifest mode](https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md) — combined release PRs across packages
- [GitLab monthly releases](https://handbook.gitlab.com/handbook/engineering/releases/monthly-releases/) — the canonical release train
- [Shopify's modular monolith](https://shopify.engineering/shopify-monolith) — 37-component Rails monolith with Packwerk
- [Why Google Stores Billions of Lines of Code in a Single Repository (Potvin & Levenberg, CACM 2016)](https://research.google/pubs/why-google-stores-billions-of-lines-of-code-in-a-single-repository) — the monorepo evidence base
