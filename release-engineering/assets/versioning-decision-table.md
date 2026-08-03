# Versioning Decision Table

> Choose a versioning scheme, then encode the rules in your release tooling. Canonical definitions: SemVer 2.0.0, CalVer, and Conventional Commits.

## Scheme Selection

| Question | If yes → |
|----------|----------|
| Do you have a public API or installable library where consumers depend on compatibility guarantees? | **SemVer** — each version carries semantic meaning |
| Is the product time-bound (releases must be date-identifiable) or driven by external events (regulatory, compliance)? | **CalVer** — date-based |
| Do multiple components ship on the same train with a shared promise (product suite, mobile app)? | **Fixed / one-version** — a single version for the product |
| Do components evolve independently and integrate via registries? | **Independent versioning** — per-component SemVer |

| Scheme | Format | Best for | Example |
|--------|--------|----------|---------|
| SemVer | MAJOR.MINOR.PATCH[-prerelease][+build] | Libraries, APIs, anything with consumers | 2.4.0, 2.4.0-rc.1 |
| CalVer | Date segments + optional modifier | Products with time-based releases | Ubuntu 24.04, pip 24.3 |
| Fixed / one-version | One version across all components | Release trains, product suites, mobile apps | 2026.08.1 |
| Independent | Per-component versions | Microservices, monorepo packages | api 3.2.1, web 1.9.0 |

## SemVer Rules

| Component | Rule |
|-----------|------|
| MAJOR | Incompatible API change |
| MINOR | Backward-compatible new functionality |
| PATCH | Backward-compatible bug fix |
| 0.y.z | Initial development: anything may change; consumers should pin |
| Prerelease | `-alpha.1`, `-beta.2`, `-rc.1` — lower precedence than the final release |
| Build metadata | `+build.123`, `+exp.sha.5114f85` — ignored in precedence, useful for provenance |

## Bump Rules from Conventional Commits

| Commit type | Bump | Example |
|-------------|------|---------|
| `BREAKING CHANGE:` footer, or `feat!` / `fix!` | MAJOR | `feat!: drop v1 API` |
| `feat` | MINOR | `feat(auth): add refresh tokens` |
| `fix` | PATCH | `fix(api): retry on 429` |
| `perf`, `refactor`, `docs`, `test`, `chore`, `ci`, `build`, `style` | PATCH in this skill | `docs: update readme` |

For `0.y.z`, this skill's Release Please-compatible policy maps both
`feat` and breaking changes to MINOR (`0.5.0` -> `0.6.0`), while fixes and
other changes remain PATCH. At `1.0.0` and later, normal SemVer priority
applies.

> **Gotcha —** the bump is decided by the highest-priority type in the release range: one `BREAKING CHANGE` forces a MAJOR at 1.0.0+, or a MINOR bump in 0.x, even if the rest are fixes. Automate with the `version_bump.py` script.

## Prerelease and Build Metadata Rules

- Prerelease identifiers: dot-separated alphanumerics + hyphens; numeric identifiers have no leading zeros (`rc.1`, not `rc.01`).
- Prerelease precedence: `1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-beta < 1.0.0-rc.1 < 1.0.0`.
- Build metadata (`+...`) does not affect precedence: `1.0.0+001 == 1.0.0+002`.
- Promotion pattern: build once, record the digest, tag with SemVer, promote the same immutable artifact through environments — never rebuild for promotion.

## Sources and Further Reading

- Semantic Versioning 2.0.0: https://semver.org/
- Conventional Commits 1.0.0: https://www.conventionalcommits.org/en/v1.0.0/
- CalVer: https://calver.org/
- Keep a Changelog: https://keepachangelog.com/en/1.1.0/
- Changesets (independent versioning in monorepos): https://github.com/changesets/changesets
