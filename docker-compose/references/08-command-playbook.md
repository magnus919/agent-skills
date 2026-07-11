# Command Playbook

## Inspect and validate

```bash
docker compose version
docker compose ls
docker compose -f compose.yaml config --quiet
docker compose -f compose.yaml config --services
docker compose -f compose.yaml config --images
docker compose -f compose.yaml config --environment
```

## Lifecycle

```bash
docker compose up -d
docker compose up -d --build SERVICE
docker compose start SERVICE
docker compose stop SERVICE
docker compose restart SERVICE
docker compose pause SERVICE
docker compose unpause SERVICE
docker compose down
docker compose down --remove-orphans
```

## Runtime access

```bash
docker compose ps --all
docker compose logs -f --tail=100 SERVICE
docker compose exec SERVICE sh
docker compose run --rm SERVICE COMMAND
docker compose cp SERVICE:/path ./path
docker compose top SERVICE
docker compose port SERVICE 8080
```

## Images and data

```bash
docker compose pull
docker compose build --pull --no-cache SERVICE
docker compose images
docker compose volumes
docker volume inspect PROJECT_VOLUME
docker network inspect PROJECT_default
```

Use `--project-name` or `COMPOSE_PROJECT_NAME` to isolate concurrent projects. Prefer `--no-color --no-log-prefix` in CI logs. Confirm command availability with `docker compose COMMAND --help`; flags and implementation support evolve.
