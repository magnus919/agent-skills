# Release Toolchain Cheatsheet

> One-liner per tool with a "pick when" note. Status reflects the 2025–2026 landscape; verify current vendor support before committing. This is a selection map, not an endorsement.

## CI/CD

| Tool | One-liner | Pick when |
|------|-----------|-----------|
| GitHub Actions | Cloud or self-hosted workflows with a huge ecosystem and native artifact attestation | You live on GitHub and want tight repo→CI coupling plus SLSA provenance out of the box |
| GitLab CI | Single-application CI/CD with built-in environments, review apps, and protected environments | You use GitLab and want CI + CD + security in one platform |
| Jenkins | Mature, plugin-driven automation server you self-host | Legacy estates, on-prem requirements, maximum plugin flexibility |
| CircleCI | Fast cloud CI with strong caching and parallelism | Small-to-mid teams wanting speed with minimal ops |
| Buildkite | Hybrid model: your infrastructure, their orchestration | You need your own runners for compliance/performance but want managed orchestration |
| Tekton | Kubernetes-native CI/CD building blocks | You are Kubernetes-native and want pipelines as CRDs |
| Dagger | CI/CD as code in your own language, runs anywhere | You want portable pipelines free of a single vendor |

## Release Automation

| Tool | One-liner | Pick when |
|------|-----------|-----------|
| semantic-release | Auto-version + auto-changelog from conventional commits | Single-package repos on GitHub; zero-touch semantic releases |
| release-please | Google-style release PRs; manifest mode for monorepos | Monorepos needing per-package versioning with a release train |
| changesets | Intentional, PR-driven version bumps for monorepos | You want humans to decide release content, not automagic |
| release-drafter | Drafts release notes from merged PR labels | You want fast GitHub release notes driven by PR labels |
| git-cliff | Changelog generator from conventional commits, highly configurable | You want a changelog generated locally or in any CI |

## Artifact Repositories

| Tool | One-liner | Pick when |
|------|-----------|-----------|
| Artifactory | Universal artifact manager with proxy, security, and promotion | Multi-format artifacts (containers, Maven, npm, PyPI) in one place |
| Nexus | Open-source artifact repository (Maven/npm/PyPI) | You want a self-hosted, budget-friendly repo, especially for JVM ecosystems |
| GHCR / ECR / GAR | Cloud-native container registries with IAM and signing | You are all-in on one cloud and want zero extra infrastructure |

## GitOps / Deployment

| Tool | One-liner | Pick when |
|------|-----------|-----------|
| Argo CD | Declarative GitOps for Kubernetes with sync, rollback, and SSO | You want Git as the single source of truth for cluster state |
| Flux | CNCF GitOps toolkit with automation and OCI support | You want GitOps + progressive delivery with strong multi-tenancy |
| Argo Rollouts | Advanced rollout strategies (canary/blue-green) for Kubernetes | You need canary with automated analysis on Kubernetes |
| Flagger | Progressive delivery operator that automates canary releases | You want metric-driven automated canary promotion |
| Harness | Enterprise CD / feature-flag / verification platform | You want a managed, approval-heavy enterprise platform |
| Spinnaker | Cloud-native CD with complex pipelines; declining maintenance | You inherited it; new projects should look elsewhere |

## Feature Flags

| Tool | One-liner | Pick when |
|------|-----------|-----------|
| LaunchDarkly | Enterprise feature management with targeting + experimentation | You need scale, audit, and kill-switch-grade reliability |
| Flagsmith | Open-core feature flags with remote config | You want a self-hostable, OSS-friendly option |
| Unleash | Open-source feature toggles, simple and fast | You want a lean OSS toggle server with good SDKs |
| OpenFeature | Vendor-neutral open standard for flag evaluation | You want to avoid lock-in and swap providers later |

## Security / Supply Chain

| Tool | One-liner | Pick when |
|------|-----------|-----------|
| Syft | Generates SBOMs from images/filesystems (SPDX, CycloneDX) | You need SBOM generation in every build |
| Trivy | Fast vulnerability scanner for images, repos, and SBOMs | You want one scanner for CI + registry + cluster |
| Cosign / sigstore | Keyless container signing + attestation | You want verifiable signatures without key management |
| slsa-github-generator | GitHub Actions producing SLSA L3 provenance | You want build provenance auditors accept |
| Dependabot / Renovate | Automated dependency-update PRs | You want dependency drift under control continuously |

## Observability

| Tool | One-liner | Pick when |
|------|-----------|-----------|
| Prometheus + Grafana | Open-source metrics + dashboards/alerting | You want the standard OSS monitoring stack |
| Datadog | SaaS APM, logs, metrics, and SLOs in one | You want a managed all-in-one with SLO/error-budget features |
| Sentry | Error tracking with release association | You want crash/exception tracking tied to releases |
| OpenTelemetry | Vendor-neutral telemetry standard (traces/metrics/logs) | You want to future-proof instrumentation |

## Sources and Further Reading

- Continuous Delivery Foundation: https://cd.foundation/
- GitHub Actions artifact attestations: https://docs.github.com/en/actions/security-for-github-actions
- Argo CD documentation: https://argo-cd.readthedocs.io/
- OpenFeature: https://openfeature.dev/
- SLSA framework: https://slsa.dev/
