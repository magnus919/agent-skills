# Failure signatures and evidence-first diagnosis

| Symptom | First checks | Avoid |
|---|---|---|
| No pipeline after a push | Repository activation, forge webhook delivery, public `WOODPECKER_HOST`, matching workflow event | Rewriting steps before proving the webhook arrived |
| Pipeline queued indefinitely | Connected agent, matching labels, backend, `WOODPECKER_MAX_WORKFLOWS`, agent logs | Assuming the application image is broken before the agent receives work |
| Agent cannot connect | `WOODPECKER_SERVER` host/port, Docker DNS, gRPC port, shared secret, TLS mode | Changing workflow YAML |
| OAuth redirect loop | Public host, exact callback URL, provider URL, client/secret, clock/TLS | Regenerating pipeline files |
| Clone authentication failure | Forge reachability from agent, repository visibility, clone plugin trust, `WOODPECKER_AUTHENTICATE_PUBLIC_REPOS` | Printing credentials into a diagnostic step |
| Docker socket permission denied | Socket mount, Docker daemon, SELinux labels/policy, agent user | Permanently disabling SELinux as the first fix |
| Service hostname resolves but tests fail | Native readiness probe, service port, credentials, retry/backoff | Treating container creation as readiness |
| Kubernetes pod never starts | Namespace, RBAC, ServiceAccount, PVC/storage class, image pull secret, pod events | Enabling workflow-controlled service accounts without a trust review |
| Secret is empty | Scope precedence, event filter, plugin-image filter, `from_secret`, `$${VAR}` escaping | Broadening secret exposure to all pull requests |
| Logs are missing or truncated | Server/agent gRPC stability, log store setting, database limits, pipeline log commands | Deleting the database or volumes |
| Upgrade starts but old data is unavailable | Backup restore test, migration log, image tag alignment, file ownership | Downgrading binaries without restoring a pre-migration database |

## Evidence collection

```bash
docker compose ps
docker compose logs --tail=200 woodpecker-server
docker compose logs --tail=200 woodpecker-agent
woodpecker-cli lint --help
python3 scripts/woodpecker-doctor.py --url https://ci.example.com --server woodpecker-server:9000 --json
```

For clone failures, use `skip_clone: true` only in a temporary diagnostic workflow, verify network and forge API access from the same backend, then remove the diagnostic pause. Capture the first error and the exact installed version in the incident record.

## Sources

- https://woodpecker-ci.org/docs/usage/troubleshooting
- https://woodpecker-ci.org/docs/administration/configuration/agent
- https://woodpecker-ci.org/docs/administration/configuration/backends/docker
- https://woodpecker-ci.org/docs/administration/configuration/backends/kubernetes
- https://woodpecker-ci.org/docs/administration/configuration/server
- https://woodpecker-ci.org/docs/usage/secrets
- https://woodpecker-ci.org/docs/usage/project-settings