# Model and File Design

## Canonical shape

Use `compose.yaml` for new projects. The top-level `version` key is obsolete and only retained for backward compatibility. A Compose application normally contains `services`, and may declare `networks`, `volumes`, `configs`, `secrets`, `name`, `include`, fragments, and extensions.

A service is a replaceable application component backed by an image and runtime configuration. Networks provide communication channels; volumes provide persistence; configs and secrets provide explicitly granted read-only files.

## Design checklist

- Name services by role (`api`, `db`, `worker`), not by container hostname.
- Pin image tags or digests for reproducible releases; avoid `latest` for production.
- Keep application configuration in environment variables or mounted files, not image rebuilds.
- Keep state in named volumes or an external storage system, not the writable container layer.
- Make host-published ports intentional. Internal services usually need no `ports` entry.
- Use YAML anchors/extensions only when they reduce repetition without hiding the resolved model.
- Set a top-level `name` or `COMPOSE_PROJECT_NAME` when stable resource names matter.
- Use `include` for independently managed Compose applications whose relative paths should remain local; use `-f` merges for a base plus environment override.

## Minimal application

```yaml
name: example
services:
  web:
    image: nginx:stable
    ports:
      - "8080:80"
```

## Validate the model

```bash
docker compose config --quiet
docker compose config --services
docker compose config --images
docker compose config --environment
docker compose config --format json
```

The resolved model reveals interpolation mistakes, unexpected profile activation, path resolution, duplicate mounts, and accidental port exposure.
