# Development, Builds, CI, and Production

## Compose Watch

Watch services built from local source:

```yaml
services:
  web:
    build: .
    command: npm start
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src
          ignore:
            - node_modules/
        - action: rebuild
          path: package.json
```

Run `docker compose up --watch` or `docker compose watch`. `sync` is for hot-reloadable source, `sync+restart` for changed configuration, and `rebuild` for dependencies or image inputs. The image needs `stat`, `mkdir`, and `rmdir`, and the runtime user must be able to write to the target path. Do not sync host-native dependency trees such as `node_modules` across architectures.

## Build and CI loop

```bash
docker compose build --pull
docker compose config --quiet
docker compose up -d --wait
docker compose ps
docker compose logs --no-color --tail=200
docker compose down --volumes --remove-orphans
```

Use an isolated project name and deterministic image tags in CI. Do not use destructive volume cleanup against shared environments.

## Production baseline

- Deploy immutable image tags or digests.
- Define healthchecks and graceful `stop_grace_period`.
- Set restart policy deliberately (`unless-stopped` for long-running services, `on-failure` for jobs).
- Bound memory/CPU only after measuring and verifying target implementation support.
- Configure log rotation or a centralized logging driver.
- Run as non-root where supported; use `read_only: true` plus explicit writable mounts when practical.
- Keep databases off public host ports unless required.
- Back up and restore-test named volumes; Compose does not create a backup strategy.
- Verify externally reachable endpoints after deployment. `config` passing is not deployment verification.
