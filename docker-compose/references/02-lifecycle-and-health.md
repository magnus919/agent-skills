# Lifecycle, Readiness, and Jobs

Compose creates and removes services in dependency order, but startup order is not readiness. `depends_on` without a condition only establishes ordering.

## Readiness pattern

```yaml
services:
  api:
    image: example/api:1.2
    depends_on:
      db:
        condition: service_healthy
        restart: true
      migrate:
        condition: service_completed_successfully
  db:
    image: postgres:18
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
  migrate:
    image: example/api:1.2
    command: ["./app", "migrate"]
    depends_on:
      db:
        condition: service_healthy
    restart: "no"
    profiles: [ops]
```

Use a healthcheck that tests actual readiness, not merely that a process exists. Ensure the image contains the probe executable (`curl`, `wget`, `pg_isready`, or an application-specific probe). Use `start_period` for slow initialization. A healthcheck provides a signal; it does not repair the service.

## Safe lifecycle

```bash
docker compose up -d
docker compose up -d --build SERVICE
docker compose restart SERVICE
docker compose stop
docker compose down
docker compose down --remove-orphans
```

`down` removes project containers and networks. Named volumes normally remain. Treat `down -v`, `volume rm`, and host-directory deletion as data-loss operations.

## One-off work

Use `docker compose run --rm SERVICE COMMAND` for migrations, administration, and probes. Use `docker compose exec SERVICE COMMAND` when the service is already running and you need its live environment. Prefer a dedicated job service for repeatable migrations over ad-hoc commands in application startup.
