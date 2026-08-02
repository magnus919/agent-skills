# Security Testing

## Test Types by Phase

| Phase | Test Type | Tool Examples | Frequency |
|-------|-----------|---------------|-----------|
| Pre-commit | Secret scanning | gitleaks, trufflehog | Every commit |
| CI | SAST (static analysis) | Semgrep, CodeQL, bandit (Python), eslint-plugin-security | Every PR |
| CI | SCA (dependency audit) | `pip-audit`, `npm audit`, Dependabot, Snyk, Trivy | Every PR + daily |
| CI | Container scanning | Trivy, Grype | Every image build |
| Staging | DAST (dynamic) | OWASP ZAP, Burp Suite | Nightly or pre-release |
| Staging | API fuzzing | Schemathesis (OpenAPI), RESTler | Weekly |
| Pre-release | Pen test (manual) | External firm or red team | Quarterly / major release |

## OWASP Top 10:2025

The OWASP Top 10:2025 is the current standard awareness document. The 2025 edition restructured categories significantly — notably adding Software Supply Chain Failures (A03) and Mishandling of Exceptional Conditions (A10) as new entries.

| ID | Category | What to Test | How |
|----|----------|-------------|-----|
| A01 | Broken Access Control | IDOR, privilege escalation, path traversal | Access other users' resources by ID; test admin endpoints as regular user; fuzz path parameters with `../` |
| A02 | Security Misconfiguration | Default creds, verbose errors, open ports, debug endpoints | Banner grab; check `/debug`, `/admin`, `.env` exposure; verify CORS headers |
| A03 | Software Supply Chain Failures | Compromised dependencies, typosquatting, unsigned artifacts | SCA scans (Trivy, Snyk); verify lockfile integrity; check SBOM against known advisories |
| A04 | Cryptographic Failures | Weak algorithms, plaintext secrets, PII in logs | Grep logs for email/SSN patterns; verify TLS 1.2+ everywhere; audit key management |
| A05 | Injection | SQL, command, LDAP, XSS (reflected/stored/DOM) | Parameterized query audit; fuzz with `' OR 1=1`, `; rm -rf`, `<script>alert(1)</script>` |
| A06 | Insecure Design | Business logic flaws, missing rate limits, predictable IDs | Threat model review; abuse-case testing; verify rate limiting on sensitive operations |
| A07 | Authentication Failures | Session fixation, token expiry, brute force, credential stuffing | Attempt reuse of expired tokens; test rate limiting; verify MFA enforcement |
| A08 | Software or Data Integrity Failures | Unsigned updates, insecure deserialization, CI/CD pipeline tampering | Audit all `loads()`/`unserialize()` calls; verify artifact signatures; check auto-update channels |
| A09 | Security Logging and Alerting Failures | Missing audit trail, unmonitored auth failures, log injection | Verify login/logout/privilege-change events are logged; test that logs don't accept unescaped input |
| A10 | Mishandling of Exceptional Conditions | Verbose stack traces, fail-open on error, unhandled edge cases | Trigger error paths (timeout, malformed input, resource exhaustion); verify safe fallback behavior |

### Gotcha: Outdated OWASP Editions

The 2017 edition used different category names and groupings. Categories that existed as standalone entries in 2017 (such as data-exposure and XML-entity risks) are now subsumed under A04 (Cryptographic Failures) and A08 (Software or Data Integrity Failures) respectively. Do not build test plans around the retired 2017 taxonomy. Always cite the 2025 edition.

## Supply Chain Security and SBOM

Software supply chain attacks (A03) target the build and dependency pipeline rather than application code directly.

### SBOM (Software Bill of Materials)

| Tool | Format | Use |
|------|--------|-----|
| Syft | SPDX, CycloneDX | Generate SBOM from images, filesystems, archives |
| Trivy | CycloneDX | Generate SBOM + scan for vulnerabilities in one pass |
| `npm sbom` / `pip-audit --sbom` | SPDX / CycloneDX | Language-native SBOM generation |

### Supply Chain Controls

| Control | Implementation |
|---------|---------------|
| Dependency pinning | Lockfiles (`package-lock.json`, `uv.lock`, `Gemfile.lock`) committed to VCS |
| Artifact signing | Sigstore/cosign for container images; npm provenance for packages |
| CI/CD pipeline integrity | Branch protection, required reviews, pinned action SHAs (not `@main`) |
| Typosquat detection | Automated name-similarity checks on new dependencies |
| SBOM attestation | Generate and store SBOM per build; scan against advisory databases (OSV, NVD) |

### Container Security

```bash
# Scan image for OS + language CVEs and generate SBOM
trivy image --severity HIGH,CRITICAL myapp:latest
trivy sbom --output sbom.cdx.json myapp:latest

# Fail CI on critical findings
trivy image --exit-code 1 --severity CRITICAL myapp:latest
```

- Use distroless or alpine base images (smaller attack surface)
- Run as non-root (`USER 1000` in Dockerfile)
- No secrets in image layers — use runtime injection (Vault, SSM, k8s secrets)

## STRIDE Threat Modeling

STRIDE classifies threats by the property they violate. Use it during design review to enumerate attack surfaces before writing code.

| Threat | Property Violated | Example | Mitigation Pattern |
|--------|-------------------|---------|-------------------|
| **S**poofing | Authentication | Forged JWT, stolen session cookie | MFA, token binding, short expiry |
| **T**ampering | Integrity | Modified request body, altered DB record | HMAC signatures, input validation, audit logging |
| **R**epudiation | Non-repudiation | User denies performing action | Immutable audit logs with timestamps and user identity |
| **I**nformation Disclosure | Confidentiality | Verbose error leaks stack trace, PII in logs | Error sanitization, log redaction, encryption at rest |
| **D**enial of Service | Availability | Resource exhaustion, slowloris | Rate limiting, circuit breakers, autoscaling |
| **E**levation of Privilege | Authorization | IDOR grants admin access, role bypass | Least privilege, server-side authorization checks |

### When to Threat Model

- New service or API endpoint design
- Authentication or authorization flow changes
- Data flow changes (new storage, new integration)
- Before a major release (quarterly review cadence)

## SAST / DAST / SCA Tool Landscape

| Category | What It Does | Tools | When |
|----------|-------------|-------|------|
| **SAST** (Static Application Security Testing) | Analyzes source code for vulnerability patterns without executing | Semgrep, CodeQL, bandit, SonarQube, Checkmarx | Every PR — fast feedback |
| **DAST** (Dynamic Application Security Testing) | Attacks the running application from outside | OWASP ZAP, Burp Suite, Nuclei | Staging — needs a deployed instance |
| **SCA** (Software Composition Analysis) | Identifies vulnerable third-party dependencies and license issues | Snyk, Dependabot, Trivy, `pip-audit`, `npm audit` | Every PR + daily scheduled |

### SAST in CI (Semgrep Example)

```yaml
# .github/workflows/security.yml
- name: Semgrep
  uses: semgrep/semgrep-action@v1
  with:
    config: >-
      p/owasp-top-ten
      p/python
      p/security-audit
```

## Dependency Audit Discipline

| Severity | Action |
|----------|--------|
| Critical / High | Block merge; fix immediately |
| Medium | Create issue; fix within sprint |
| Low | Batch into maintenance window |

- Pin transitive deps with lockfiles
- Review Dependabot PRs weekly — don't let them accumulate

## Security Test Data

- Never test with real PII — use synthetic data (see [test-data-management.md](./test-data-management.md))
- Credential testing uses obviously-fake values: `AKIAIOSFODNN7EXAMPLE`
- If a test discovers a real vulnerability, stop and report — don't commit exploit code

## Gotchas

- **Outdated OWASP references** (2017 categories) produce misaligned test plans. Always use the 2025 edition.
- **SAST without DAST** misses runtime-only vulnerabilities (misconfiguration, CORS, auth bypass). Run both.
- **Ignoring supply chain** — most breaches in 2024–2025 exploited dependencies, not application code. SCA and SBOM are not optional.
- **Secret scanning only at pre-commit** misses secrets already in history. Run a full-history scan on onboarding and quarterly.

## Composition

- Deep secure-engineering lifecycle (secure design review, threat modeling workshops, incident response): [secure-software-engineering](../../secure-software-engineering/SKILL.md)
- Systematic debugging of security-related test failures: [systematic-debugging](../../systematic-debugging/SKILL.md)

*Sources: OWASP Top 10:2025 (owasp.org/Top10/2025), STRIDE (Microsoft Security Development Lifecycle), CycloneDX (OWASP), SLSA supply chain framework (slsa.dev), Semgrep docs (semgrep.dev), Trivy docs (trivy.dev), NIST SP 800-218 (SSDF).*
