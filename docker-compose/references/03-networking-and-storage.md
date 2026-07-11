# Networking and Storage

## Service DNS and ports

Compose creates a project network and registers each service name in Docker's internal DNS. From one container to another, use `http://SERVICE:CONTAINER_PORT`. A host mapping such as `127.0.0.1:8000:8000` is for host-to-container access; it is not the address another service should use.

Container IPs are ephemeral. Applications must reconnect by service name after a container is recreated.

## Network isolation

```yaml
services:
  proxy:
    image: nginx:stable
    networks: [front]
  api:
    image: example/api:1.2
    networks: [front, back]
  db:
    image: postgres:18
    networks: [back]
networks:
  front: {}
  back:
    internal: true
```

Use an external network only when it is intentionally shared:

```yaml
networks:
  shared:
    name: shared-network
    external: true
```

The network must already exist. `network_mode: host` disables normal service DNS and port publishing; use it only when the requirement genuinely needs the host network.

## Storage choice

- **Named volume**: durable application data managed by Docker.
- **Bind mount**: host-controlled source/configuration; sensitive to host paths and permissions.
- **tmpfs**: ephemeral data where supported.
- **External volume**: data managed outside the Compose lifecycle; verify it exists before startup.

```bash
docker compose exec SERVICE sh -lc 'id; df -h; ls -la /mount'
docker volume ls
docker volume inspect PROJECT_VOLUME
docker compose port SERVICE 8080
docker network inspect PROJECT_default
```

If a service cannot write, inspect the container user, mount mode (`:ro`), host ownership, and the image's expected path before changing permissions broadly.
