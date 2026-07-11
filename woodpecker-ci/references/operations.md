# Operations: secrets, CLI, persistence, and observability

## Secret administration

Use the UI or CLI. Load values from files so line breaks are preserved:

```bash
woodpecker-cli repo secret add \
  --repository OWNER/REPO \
  --name ssh_key \
  --value @/path/to/id_rsa
```

Add image and event restrictions for deployment credentials. Never print the value or place it in a workflow file. Woodpecker masks secrets from its own store, but external secrets fetched by a pipeline can still appear in logs.

## Registry credentials

Use Woodpecker's registry settings or the backend's documented credential mechanism. For Kubernetes, pull credentials can be supplied as Kubernetes Secrets named through `WOODPECKER_BACKEND_K8S_PULL_SECRET_NAMES`. Verify the agent can pull the exact image before blaming the workflow.

## CLI workflow

The CLI documentation is version-sensitive. Start with:

```bash
woodpecker-cli --help
woodpecker-cli repo --help
woodpecker-cli pipeline --help
woodpecker-cli exec --help
```

Authenticate using the method documented for the installed release, then use the CLI for repository, pipeline, log, and secret operations. Prefer `--help` and `woodpecker-cli lint` over memorizing flags from an older release.

`exec` runs a workflow locally. It can validate commands and metadata, but server-managed secrets and forge event context may not be present. Do not use local success as proof that a server pipeline will succeed.

## Database, metrics, and health

Woodpecker automatically creates and migrates its database in normal upgrades unless release notes say otherwise. It does **not** perform backups. Back up the database and persistent server data before upgrades, test restoration, and use a SemVer image tag rather than a floating `latest` tag. Keep server and agent majors aligned.

SQLite is the default embedded database path. The server configuration also documents MySQL and PostgreSQL through `WOODPECKER_DATABASE_DRIVER` and `WOODPECKER_DATABASE_DATASOURCE`. Verify the exact connection string for the installed release and create an external database before pointing Woodpecker at it. Never delete the server volume during routine troubleshooting.

Woodpecker exposes Prometheus metrics when `WOODPECKER_PROMETHEUS_AUTH_TOKEN` is set. `WOODPECKER_METRICS_SERVER_ADDR` enables an unprotected metrics listener; an empty value disables it. Treat metrics as a deployment-specific surface: confirm the endpoint, bind address, authentication, and network policy before adding a monitor.

Useful checks:

```bash
docker compose ps
docker compose logs --tail=200 woodpecker-server
docker compose logs --tail=200 woodpecker-agent
python3 scripts/woodpecker-doctor.py --url https://ci.example.com --json
```

## Safe upgrade loop

1. Read the release notes for the current major and target tag.
2. Back up the database and persistent server data.
3. Render the new deployment configuration.
4. Upgrade server and agent together in a disposable or staging environment.
5. Confirm login, repository listing, webhook delivery, agent connection, a non-secret test pipeline, and metrics/health behavior.
6. Upgrade production and retain the previous image tag for rollback.

## Sources

See `references/source-index.md` for server configuration, CLI, Docker Compose, agent, and Helm documentation.