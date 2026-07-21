# Security Testing

## Test Types by Phase

| Phase | Test Type | Tool | Frequency |
|-------|-----------|------|-----------|
| Pre-commit | Secret scanning | gitleaks, trufflehog | Every commit |
| CI | SAST (static analysis) | Semgrep, CodeQL, bandit (Python), eslint-security | Every PR |
| CI | Dependency audit | `npm audit`, `pip-audit`, Dependabot, Snyk | Every PR + daily |
| CI | Container scanning | Trivy, Grype | Every image build |
| Staging | DAST (dynamic) | OWASP ZAP, Burp Suite | Nightly or pre-release |
| Staging | API fuzzing | Schemathesis (OpenAPI), RESTler | Weekly |
| Pre-release | Pen test (manual) | External firm or red team | Quarterly / major release |

## OWASP Top 10 — Test Patterns

| Risk | What to Test | How |
|------|-------------|-----|
| Injection (SQL, command, LDAP) | All user input reaches DB/shell | Parameterized query audit; fuzz with `' OR 1=1`, `; rm -rf` |
| Broken auth | Session fixation, token expiry, brute force | Attempt reuse of expired tokens; test rate limiting |
| Sensitive data exposure | PII in logs, unencrypted transit | Grep logs for email/SSN patterns; verify TLS everywhere |
| XXE | XML parsers accept external entities | Send `<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>` |
| Broken access control | IDOR, privilege escalation | Access other users' resources by ID; test admin endpoints as regular user |
| Security misconfiguration | Default creds, verbose errors, open ports | Banner grab; check `/debug`, `/admin`, `.env` exposure |
| XSS | Reflected/stored/DOM | Inject `<script>alert(1)</script>` in every input field |
| Insecure deserialization | Pickle, YAML.load, Java ObjectInputStream | Audit all `loads()`/`unserialize()` calls for untrusted input |
| Known vulnerabilities | CVEs in dependencies | `pip-audit`, `npm audit`, Trivy |
| SSRF | Server fetches user-supplied URLs | Provide `http://169.254.169.254/` (cloud metadata), `http://localhost:6379` |

## SAST in CI (Semgrep Example)

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

- Block merges on **critical** and **high** severity findings
- **Medium**: create issue, fix within sprint
- **Low**: batch into maintenance window
- Pin transitive deps with lockfiles (`package-lock.json`, `uv.lock`, `Gemfile.lock`)
- Review Dependabot PRs weekly — don't let them accumulate

## Container Security

```bash
# Scan image for OS + language CVEs
trivy image --severity HIGH,CRITICAL myapp:latest

# Fail CI on critical findings
trivy image --exit-code 1 --severity CRITICAL myapp:latest
```

- Use distroless or alpine base images (smaller attack surface)
- Run as non-root (`USER 1000` in Dockerfile)
- No secrets in image layers — use runtime injection (Vault, SSM, k8s secrets)

## Security Test Data

- Never test with real PII — use synthetic data (see test-data-management.md)
- Credential testing uses obviously-fake values: `AKIAIOSFODNN7EXAMPLE`
- If a test discovers a real vulnerability, stop and report — don't commit exploit code
