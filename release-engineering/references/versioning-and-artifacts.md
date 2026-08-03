# Versioning and Artifacts

Version numbers are a **contract with every consumer** of your software — downstream teams, registries, release tooling, auditors, and users. Artifacts are the physical embodiment of a release: they must be **immutable once built**, **promotable** across environments, and **provably traceable** to the source and build that produced them. This reference covers version schemes (SemVer, CalVer), the commit conventions that drive automated bumps, changelog conventions, artifact immutability and promotion, naming/registry conventions, and provenance.

## Semantic Versioning (SemVer 2.0.0)

SemVer encodes API-compatibility intent in a three-part number: `MAJOR.MINOR.PATCH`, optionally followed by a `-prerelease` identifier and a `+build` metadata suffix.

| Component | Meaning | Example |
|-----------|---------|---------|
| **MAJOR** | Incompatible API change (consumers must change code) | `2.0.0` |
| **MINOR** | Backward-compatible addition of functionality | `1.4.0` |
| **PATCH** | Backward-compatible bug fix | `1.4.1` |
| **Prerelease** | Pre-release build, lower precedence than release | `1.4.0-rc.1` |
| **Build metadata** | Build-specific info; **ignored in precedence** | `1.4.0+20260801` |

### The Core Rules

- Once a version is published, its content **must not change**. Any modification requires a new, higher version.
- Version numbers must increment by the largest changed component: a MINOR change also resets PATCH to zero (`1.4.1` → `1.5.0`, not `1.5.1`); a MAJOR change resets MINOR and PATCH.
- Precedence is resolved left to right: `1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-beta < 1.0.0-rc.1 < 1.0.0`. Numeric identifiers compare numerically, alphanumeric identifiers lexically.
- Build metadata (`+sha.abc123`) is **not** part of precedence: `1.0.0+build1` and `1.0.0+build2` are equal in precedence, so two different builds of the same version are indistinguishable to dependency resolvers that sort by precedence.

> **Gotcha — Build metadata is invisible to precedence:** If you append a commit SHA as build metadata, semver-aware tools cannot tell two builds apart. Use prerelease identifiers (`1.0.0-alpha.1`) for ordered builds, or pin by **digest** (see Provenance) rather than by version string.

### Precedence in Practice

Precedence is a total order over releases and a partial order over prereleases of the same release:

| Version | Position |
|---------|----------|
| `1.0.0-alpha` | Earliest — fewer identifiers sorts before more (`alpha` < `alpha.1`) |
| `1.0.0-alpha.1` | |
| `1.0.0-beta` | |
| `1.0.0-rc.1` | |
| `1.0.0` | Latest — any prerelease sorts below its release |

Two rules that commonly surprise: numeric identifiers compare **numerically** (`alpha.10` > `alpha.9`), and a shorter identifier list sorts **below** a longer one sharing its prefix (`1.0.0-alpha` < `1.0.0-alpha.1`). Tooling such as `semver_check.py` in `scripts/` implements this ordering; get it wrong in your own sort and prerelease promotion logic will promote `1.0.0-rc.9` over `1.0.0-rc.10`.

### 0.x Semantics

`0.y.z` means **initial development**: the spec explicitly states that "anything may change at any time" and the public API should not be considered stable. Practical consequences:

- `0.1.0` → `0.2.0` usually signals breaking changes in pre-1.0 libraries — the `1.0.0` MAJOR convention is effectively deferred.
- This skill's default Release Please-compatible policy maps `feat` and breaking commits to MINOR in 0.x (`0.5.0` → `0.6.0`); fixes and other commit types remain PATCH (`0.5.0` → `0.5.1`). This keeps pre-1.0 release lines meaningful while preserving normal SemVer behavior at 1.0+.
- Consumers pinning `0.x` with caret ranges (`^0.3.1`) get **no automatic updates** in most package managers (npm, for example, treats caret on `0.x` as `>=0.3.1 <0.4.0`), which is exactly the behavior you want for a pre-stable API.

Declare a policy so both humans and automation agree on what a `0.x` bump means:

| Policy | Rule | Consequence |
|--------|------|-------------|
| **Strict** | Breaking changes bump MAJOR even in 0.x | Version jumps `0.3.0` → `1.0.0` early; signals commitment before the API is ready |
| **Deferred** (skill default) | Features and breaking changes bump MINOR until 1.0; fixes and other changes bump PATCH | `0.5.0` → `0.6.0` for `feat`, `0.5.0` → `0.5.1` for `fix`; 1.0 arrives when the API stabilizes |
| **Tooling-default** | Whatever your release tool computes from commits | Usually `feat`→MINOR; document that pre-1.0 MINOR may break |

> **Gotcha — The 0.x trap:** A 1.0.0 release is a promise about API stability. If your library has public consumers, treat 1.0.0 as a deliberate commitment — and conversely, do not stay in `0.x` forever because bumping to 1.0 feels risky; consumers already treat `0.x` as unstable either way.

### When SemVer Fits

SemVer is the right tool for **libraries, SDKs, and APIs** where consumers depend on compatibility contracts and need machine-readable signals for safe upgrades. It is a poor fit for applications or products that ship on a time cadence and whose "API" is a UI or an internal contract — see CalVer.

## Calendar Versioning (CalVer)

CalVer encodes **time** in the version, communicating freshness, support windows, and external-change-driven release schedules. Schemes combine date segments: `YYYY`, `YY`, `0M`, `MM`, `WW`, `DD` — plus an optional `.micro` or `.patch` suffix.

| Project | Scheme | Example |
|---------|--------|---------|
| Ubuntu | `YY.0M` | `26.04` |
| Twisted | `YY.MM.MICRO` | `24.7.0` |
| pip | `YY.MINOR.MICRO` | `24.2` |
| certifi | `YYYY.MM.DD` | `2025.01.01` |
| Stripe API | `YYYY-MM-DD` | `2025-07-15` |

The available date segments (per [CalVer](https://calver.org/)): `YYYY`/`YY` (year), `0M`/`MM` (month with/without zero-padding), `0W`/`WW` (ISO week), `0D`/`DD` (day with/without zero-padding) — combined with an optional `.micro`/`.patch` counter for multiple releases in the same period. Choosing `YYYY.MM.DD` buys maximum granularity but forces awkward micro-versions if you ever ship twice in a day; `YY.0M` (Ubuntu-style) is the common enterprise cadence.

### When CalVer Fits

- **Time-sensitive products** where "how fresh is this?" matters more than "what changed in the API?" — browsers, OS releases, compliance certificate bundles, data snapshots.
- **Large or frequently changing scope** where semantic bumps become meaningless (a browser's "minor" version says nothing about compatibility).
- **Externally driven releases** — e.g., a TLS certificate bundle that must be re-released when certificates rotate, or security tooling that tracks a moving threat landscape.
- **Applications** where the version is a support-window marker (Ubuntu LTS = "supported until YYYY.MM + N years").

### SemVer vs CalVer — Selection Guidance

| Dimension | SemVer | CalVer |
|-----------|--------|--------|
| Signal | API compatibility | Time / freshness |
| Best for | Libraries, SDKs, APIs | Applications, OSes, time-bound products |
| Consumers | Downstream code (automated resolution) | Humans, support contracts, infosec |
| Bump driven by | Commit semantics (Conventional Commits) | Calendar (plus manual patch bumps) |
| Common hybrid | SemVer for libraries, CalVer for the app that bundles them | — |

Many organizations run both: libraries version with SemVer while the product line uses CalVer (or a train name). The skill's `assets/versioning-decision-table.md` gives a structured comparison including fixed/one-version monorepo schemes (see [monorepo-polyrepo-release.md](./monorepo-polyrepo-release.md)).

## Conventional Commits

[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) is a lightweight specification for **machine-readable commit messages** that makes automated version bumps and changelog generation deterministic. Structure:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

The three types that map directly to SemVer:

| Commit | SemVer Effect | Example |
|--------|---------------|---------|
| `fix` | PATCH | `fix: correct retry backoff calculation` |
| `feat` | MINOR | `feat(api): add list-users endpoint` |
| `feat!` / `fix!` or **BREAKING CHANGE** footer | MAJOR | `feat!: drop support for v1 auth` |

- The **scope** is an optional noun in parentheses (`feat(api): ...`) that groups related changes for changelog and release-notes purposes; it does **not** change the bump.
- The **`!`** after the type/subject, or a footer line reading `BREAKING CHANGE: <description>`, both signal a MAJOR bump. Prefer the footer form: it forces you to write the migration note that changelogs and consumers need.
- Other types — `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `perf`, `test` — carry **no bump** by default (you can configure `perf` to bump PATCH). This is what keeps documentation-only PRs from inflating versions.
- A breaking change made without `!` or the footer is the most common source of **silent MAJOR drift** — the version bumps PATCH/MINOR while consumers break.

The full type set and its default bump effect:

| Type | Default bump | Typical use |
|------|--------------|-------------|
| `feat` | MINOR | New user-visible capability |
| `fix` | PATCH | Bug fix |
| `perf` | none (configurable) | Performance improvement |
| `refactor` | none | Internal restructuring, no behavior change |
| `docs` | none | Documentation only |
| `style` | none | Formatting, whitespace |
| `test` | none | Test additions/fixes |
| `build` | none | Build system changes |
| `ci` | none | CI configuration changes |
| `chore` | none | Maintenance, tooling |

Consistency matters more than the exact mapping: if `perf` bumps PATCH in one repo and nothing in another, consumers cannot predict release behavior from commit history. Choose a mapping once, encode it in the release tool config, and document it in `CONTRIBUTING`.

> **Gotcha — Squash-merge hygiene:** If you squash-merge, the PR title becomes the commit message. A PR titled `Update auth library` produces a commit with **no type**, which either fails the lint gate or defaults to no-bump, so the change ships inside whatever the last real bump was. Require conventional titles (via a lint action or merge-queue check) and keep the `BREAKING CHANGE:` footer in the squashed body.

Automated bump tooling reads this history: **semantic-release** analyzes commits and performs version + changelog + publish with no human gate; **release-please** generates a release PR (version bump + changelog) that a human merges; **git-cliff** generates the changelog from commits without publishing. For monorepo specifics (per-package vs combined releases), see [monorepo-polyrepo-release.md](./monorepo-polyrepo-release.md).

## Changelogs (Keep a Changelog and Release Please)

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) is the de-facto human changelog format, designed for **people, not machines** (machines read commits). Core conventions:

- **`## [Unreleased]`** section at the top for pending changes, replaced by a versioned header on release.
- Version headers linkable and date-stamped: `## [1.2.0] - 2026-08-01`, with a `[1.2.0]: https://...` reference link at the bottom.
- Change types grouped and consistent: **Added, Changed, Deprecated, Removed, Fixed, Security** — the same six groups in every entry.
- Latest version first; **`[YANKED]`** marks a version that must be pulled (e.g., `## [1.2.0] - 2026-08-01 [YANKED]`).
- Advertise SemVer adherence in the README or the changelog itself.

Anti-patterns: dumping the raw commit log as the changelog, ignoring deprecations, inconsistent date formats, and failing to link to diffs. If you use Conventional Commits, changelog sections can be generated automatically, but a human should review the "breaking changes and migration" entry for every MAJOR — that prose is what consumers actually read.

A minimal conforming structure:

```markdown
# Changelog

## [Unreleased]
### Added
- ... (pending changes)

## [2.1.0] - 2026-08-01
### Added
- ...
### Fixed
- ...

[Unreleased]: https://github.com/acme/app/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/acme/app/compare/v2.0.0...v2.1.0
```

The `scripts/changelog_check.py` in this skill validates this shape with `--format keep-a-changelog` (or safe `--format auto` detection). It also validates Release Please output with linked dated headers such as `## [0.6.0](https://github.com/example/proj/compare/v0.5.0...v0.6.0) (2026-08-03)`, conventional `###` sections such as `Features`, `Bug Fixes`, and `Reverts`, and `*` bullets with inline links. Release Please section labels are configurable. Release Please files do not use an `Unreleased` section; select that format explicitly in CI when auto-detection is not appropriate.

## Artifact Immutability and Promotion

The single most important artifact rule: **build once, promote the same artifact** through every environment. Never rebuild per environment — a rebuild introduces nondeterminism (time stamps, dependency drift, build-host state) and breaks the guarantee that what you tested is what you deployed.

- The artifact (image, package, binary) is **immutable** — identified by a content digest or a versioned tag that never changes.
- **Promotion** is a *pointer move*, not a rebuild: label the same artifact as `dev`, then `canary`, then `prod`. Google's internal package manager (MPM) does exactly this — content-hashed, versioned, **signed** packages with movable labels (`dev`, `canary`, `production`) pointing at immutable versions.
- This decouples "the build passed" from "the rollout reached production" and makes rollback trivial: point the label back at the previous known-good version (see [rollback-and-recovery.md](./rollback-and-recovery.md)).

### Movable Labels vs Immutable Tags

| Kind | Examples | Mutability | Use |
|------|----------|------------|-----|
| **Immutable** | `v1.2.3`, `sha-abc1234`, digest | Never rewritten | Point-in-time identity, provenance, rollback target |
| **Movable label** | `stable`, `latest`, `canary`, `prod` | Rewritten on promotion | "What should env X run now?" pointer |

> **Gotcha — Mutable tags in production manifests:** Pointing deployments at `latest` or `stable` means the running version is whoever promoted last, and rollback "to the previous version" is ambiguous. Reference the immutable tag or digest in your deployment manifests and GitOps repo; use the mutable label only for "current" semantics. Also see the supply-chain risk of digest drift in [supply-chain-security.md](./supply-chain-security.md).

### The Promotion Ledger

Every promotion is an auditable event. Record at minimum: the artifact digest, the version label moved, the source environment, the target environment, the actor (person or pipeline identity), the timestamp in UTC, and the pipeline run ID that authorized the move. This ledger is the same artifact an auditor samples under SOC 2 CC8.1 — a promotion with no ledger entry is indistinguishable from a manual deploy, which is an audit exception (see [change-governance-and-compliance.md](./change-governance-and-compliance.md)). GitOps systems (Argo CD, Flux) produce this record naturally: the promotion is a commit changing the environment's desired digest; anything that happens outside that commit is drift.

## Artifact Naming and Registry Conventions

### OCI (Container/Registry) Tags

- **Immutable tags:** git SHA (`sha-abc1234` or full SHA), SemVer (`v1.2.3`), or a monotonically increasing build number. These are the only tags safe to pin.
- **Mutable tags:** `latest`, `stable`, `canary`, `dev` — promoted as the label moves. Used for convenience and for environment pointers.
- **Promotion pattern:** build → tag with SHA + SemVer → test → promote the mutable label (`rc.1` → `stable`) without touching the immutable tag.
- **GitOps constraint:** Flux/GitLab-style operators can resolve semver ranges on tags (e.g., `>=1.0.0 <2.0.0`), but range resolution against *mutable* tags is a footgun — pin by digest in critical environments.
- **OCI convergence:** the OCI spec is absorbing every artifact type — container images, Helm charts, WASM modules, ML models, and SBOMs all publish as OCI artifacts, so a single registry with a single signing/scanning posture covers the whole catalog.

### Language-Registry Conventions

- **Maven/Gradle:** `1.0-SNAPSHOT` marks development; release versions are **immutable once deployed** to a central repository; a **BOM (Bill of Materials)** aligns dependency versions across modules.
- **npm/pnpm:** lockfiles (`package-lock.json`, `pnpm-lock.yaml`) pin the exact resolved tree; published versions are immutable (npm rejects republishing an identical version number with different content, though yanking is possible — avoid it).
- **Go modules:** `go.sum` pins module hashes; semantic import versioning (`/v2` suffix) is the convention for MAJOR breaks.
- **Python:** `uv`/pip lockfiles pin exact versions; `1.0-SNAPSHOT`-style pre-releases use PEP 440 prerelease tags (`1.0.0rc1`).

> **Gotcha — Version collisions:** Publishing a SemVer tag and a CalVer tag for the same artifact, or a mutable tag that shadows a SemVer tag (`latest` pointed at `v1.2.3` while `v2.0.0` ships), creates two "current" versions. Enforce one canonical identity per artifact: the digest is truth, tags are aliases.

## Provenance

Provenance answers "**what exactly is this artifact, and where did it come from?**" with machine-verifiable evidence:

- **Content digest** — the artifact's immutable identity (e.g., `sha256:...` for container images). Two artifacts with the same digest are byte-identical; promotion and rollback should operate on digests.
- **Build metadata** — commit SHA, build ID, source repo, build timestamp, build platform, build environment inputs. This connects the artifact to the exact code and pipeline run that produced it.
- **SBOM linkage** — an inventory of components (with versions and licenses) attached to or published alongside the artifact, enabling vulnerability queries after release (see [supply-chain-security.md](./supply-chain-security.md)).
- **SLSA provenance attestations** — signed statements (in-toto format) proving the artifact was built from a specific source commit by a specific workflow on a specific platform, enabling level-graded trust (see [supply-chain-security.md](./supply-chain-security.md)).

A provenance attestation is only as useful as the fields it carries. Minimum viable set:

| Field | Example | Why it matters |
|-------|---------|----------------|
| Subject digest | `sha256:9f86d08...` | Identifies the exact artifact being attested |
| Predicate type | SLSA provenance v1.0 | Says what the attestation claims |
| Builder identity | `https://github.com/acme/app/.github/workflows/release.yml@refs/heads/main` | Who built it (OIDC-verifiable) |
| Source location | `git+https://github.com/acme/app@<sha>` | Where the code came from |
| Materials | list of input digests (base images, deps) | What went into the build |
| Build invocation | command + env | How the build ran (hermeticity evidence) |

In practice: generate the SBOM **at build time** (not by scanning a running container), sign the image *and* the attestation with Cosign/sigstore, and record the digest + SBOM reference in the deployment record. This is also the evidence an auditor samples for SOC 2 CC8.1 — see [change-governance-and-compliance.md](./change-governance-and-compliance.md).

> **Gotcha — Provenance as an afterthought:** Attaching provenance after the artifact has been deployed means you are reconstructing evidence instead of producing it. Generate digests, SBOM, and attestations inside the build pipeline as steps, and fail the pipeline if they are missing — the same posture as [change-governance-and-compliance.md](./change-governance-and-compliance.md) takes toward audit evidence.

## Sources and Further Reading

- [Semantic Versioning 2.0.0](https://semver.org/) — the specification (CC BY 3.0)
- [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) — commit message spec driving automated bumps (CC BY 3.0)
- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) — changelog format conventions (MIT)
- [CalVer](https://calver.org/) — calendar versioning schemes and rationale
- [Google SRE Book — Chapter 8: Release Engineering](https://sre.google/sre-book/release-engineering/) — build-once, signed, labeled packages (CC BY-NC-ND: cite, do not copy)
- [semantic-release](https://github.com/semantic-release/semantic-release) — fully automated version + changelog + publish
- [googleapis/release-please](https://github.com/googleapis/release-please) — release-PR generation from conventional commits
- [pnpm Workspaces](https://pnpm.io/workspaces) — workspace protocol and monorepo publishing
