# Dependency Update Policy

This document defines the policy for adopting new dependency releases in the agent-skills repository.

## Minimum Release Age

New dependency releases must be at least **7 days old** before adoption. This waiting period mitigates supply chain attacks where a compromised release is published and adopted before it can be detected and removed.

### Rationale

Supply chain attacks increasingly target the window between a malicious release publication and its discovery. By requiring a 7-day minimum age, we ensure:

1. **Community scrutiny**: The release has been available for review by the broader community for at least a week.
2. **Detection window**: Automated scanning tools and security researchers have had time to flag issues.
3. **Revocation opportunity**: If a release is compromised and later yanked from PyPI, our delay prevents us from adopting it before removal.

## Enforcement

This policy is enforced automatically in CI via `scripts/check-dependency-age.py`, which:

1. Parses `requirements-dev.txt` for `==`-pinned dependencies.
2. Queries the PyPI JSON API for each package's release date.
3. Fails CI if any pinned dependency was released less than 7 days ago.

### Exceptions

- **Non-pinned dependencies** (using `>=` without `==`): Not checked, as the resolver chooses the version. These should eventually be pinned.
- **Pre-release versions**: Should not be adopted. If pre-releases are needed for testing, they should be in a separate requirements file.
- **Emergency security fixes**: If a critical CVE requires a same-day update, the policy can be bypassed with an explicit justification in the PR description. The CI check can be temporarily skipped.

## Dependabot Updates

Dependabot runs weekly for pip dependencies and monthly for GitHub Actions. PRs from Dependabot are subject to the same minimum release age check as manual updates.

## Related

- [scripts/check-dependency-age.py](../scripts/check-dependency-age.py) — CI enforcement script
- [.github/dependabot.yml](../.github/dependabot.yml) — Automated update configuration
- [docs/runbooks.md](./runbooks.md) — Incident response procedures
