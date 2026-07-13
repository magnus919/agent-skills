# Secrets Lifecycle

## Make The Decision Now

For each credential, key, token, certificate, or signing material, decide its owner, purpose, scope, acquisition method, storage boundary, delivery path, revocation path, and event- or risk-driven rotation conditions. Do not add a secret merely to avoid designing identity or authorization.

## Design The Lifecycle

- Prefer workload or user identity with short-lived, scoped credentials over distributed static material when the environment supports it.
- Store secrets in an access-controlled secret system or platform mechanism; inject them only where needed and avoid source control, images, build logs, command lines, crash reports, and client bundles.
- Separate environments and duties. Limit who can read, change, deploy, or audit each secret.
- Define detection and response for exposure: revoke or disable, replace dependent material, identify affected use, and preserve minimum necessary evidence.
- Rotate when compromise, staff or vendor changes, cryptographic policy, expiry, or risk warrants it. Routine rotation without safe rollout, rollback, and dependency inventory can create outages without reducing material risk.

## Evidence And Verification

Maintain a non-secret inventory with owner, scope, expiry, and rotation trigger. Test least-privilege retrieval, redaction, revocation, and replacement in a non-production path. Review repository history and generated artifacts for accidental exposure without printing sensitive values.

## Misuse To Avoid

- Hardcoding credentials in examples, configuration defaults, tests, or AI prompts.
- Logging authorization headers, raw tokens, request bodies, or model context that can contain secrets.
- Calling an encrypted value "managed" while broad identities can still retrieve it.
