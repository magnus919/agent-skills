# Configuration, Interpolation, Profiles, and Overrides

## Interpolation

Supported forms include `$VAR`, `${VAR}`, `${VAR:-default}`, `${VAR-default}`, `${VAR:?error}`, `${VAR?error}`, `${VAR:+replacement}`, and `$$` for a literal dollar sign. Interpolation applies to YAML values before merge, not arbitrary mapping keys.

Precedence for interpolation is shell environment, then the file passed with `--env-file`, then the project `.env` file. Verify the actual inputs:

```bash
docker compose --env-file .env.test config --environment
docker compose --env-file .env.test config
```

Use required forms for values that must not silently become empty:

```yaml
image: example/api:${IMAGE_TAG:?IMAGE_TAG must be set}
environment:
  DATABASE_URL: ${DATABASE_URL:?DATABASE_URL is required}
```

Do not commit credentials in `.env`. `.env.example` is documentation, not a secret store.

## Profiles

Unprofiled services are always active. Profiled services start only when enabled, or when explicitly targeted. A dependency must be active and compatible with the target's profiles.

```bash
docker compose --profile debug up -d
COMPOSE_PROFILES=debug,ops docker compose up -d
docker compose --profile '*' config
```

Use profiles for optional tools, not for core services that every normal invocation needs.

## Multiple files

```bash
docker compose -f compose.yaml -f compose.dev.yaml config
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

Later files add or override earlier configuration. Relative paths are resolved from the first/base file, a common monorepo trap. Mappings merge; many sequences append; special resources such as ports, volumes, secrets, and configs have uniqueness rules. Use the Compose Specification's `!reset` and `!override` tags when you need to clear or fully replace values, then inspect the result.
