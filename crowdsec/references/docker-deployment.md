# Docker Deployment Guide

## Quick Start

```bash
docker run -d \
  --name crowdsec \
  --volume /etc/crowdsec:/etc/crowdsec \
  --volume /var/lib/crowdsec/data/:/var/lib/crowdsec/data/ \
  --volume /var/log:/var/log:ro \
  --env COLLECTIONS="crowdsecurity/linux" \
  -p 127.0.0.1:8080:8080 \
  crowdsecurity/crowdsec:latest
```

## Docker Compose (Recommended)

```yaml
services:
  crowdsec:
    image: crowdsecurity/crowdsec:latest
    restart: always
    ports:
      - 127.0.0.1:8080:8080   # LAPI for bouncers on host or Docker
      - 127.0.0.1:6060:6060   # Prometheus metrics
      - 127.0.0.1:7422:7422   # AppSec WAF
    environment:
      COLLECTIONS: "crowdsecurity/traefik crowdsecurity/http-cve crowdsecurity/base-http-scenarios crowdsecurity/sshd crowdsecurity/linux"
      GID: "${GID-1000}"
      TZ: "UTC"
    volumes:
      - ./crowdsec/config:/etc/crowdsec
      - ./crowdsec/data:/var/lib/crowdsec/data
      # Log sources — mount from host or shared volume
      - /var/log/auth.log:/var/log/auth.log:ro
      - /var/log/syslog:/var/log/syslog:ro
      - ./traefik/logs:/var/log/traefik:ro
    networks:
      - proxy

networks:
  proxy:
    external: true
```

## Key Aspects

### 1. Log Access
Mount log files from the host or shared volumes:
```yaml
volumes:
  - /var/log/auth.log:/var/log/auth.log:ro
  - /var/log/syslog:/var/log/syslog:ro
  - logs-volume:/var/log/nginx:ro   # Shared volume with nginx container
```

### 2. Persist Data
Persisting these volumes is **mandatory** since CrowdSec v1.7.0:
```yaml
volumes:
  - crowdsec-db:/var/lib/crowdsec/data/
  - crowdsec-config:/etc/crowdsec/
```

### 3. Use `depends_on`
If reading logs from a container that writes logs to a shared volume:
```yaml
depends_on:
  - "reverse-proxy"
```

### 4. Network
CrowdSec must be on the same Docker network as bouncers (e.g., Traefik).

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COLLECTIONS` | *(none)* | Space-separated list of collections to install |
| `TZ` | `UTC` | Timezone |
| `CONFIG_FILE` | `/etc/crowdsec/config.yaml` | Main config path |
| `LOCAL_API_URL` | `http://0.0.0.0:8080` | LAPI listen address |
| `DISABLE_LOCAL_API` | `false` | Agent-only mode (no LAPI) |
| `DISABLE_AGENT` | `false` | LAPI-only mode (no agent) |
| `AGENT_USERNAME` | *(none)* | For connecting to remote LAPI |
| `AGENT_PASSWORD` | *(none)* | For connecting to remote LAPI |
| `BOUNCER_KEY_<name>` | *(none)* | Seed API key for a bouncer |

## Enrolling in Console (Docker)

```bash
docker exec crowdsec cscli console enroll -e context <YOUR_ENROLL_KEY>
```

## Execing Commands in Docker

All `cscli` commands work via `docker exec`:

```bash
docker exec crowdsec cscli collections list
docker exec crowdsec cscli bouncers add traefik-bouncer
docker exec crowdsec cscli metrics
docker exec crowdsec cscli decisions list
```

## Volumes vs Bind Mounts

| Approach | Pros | Cons |
|----------|------|------|
| Named volumes | Managed by Docker, portable | Harder to inspect/modify |
| Bind mounts | Easy to edit config directly | Permissions issues on some hosts |

For production, use bind mounts for config (so you can edit) and named volumes for data.

## Logrotate for Docker

Log files can grow quickly. Configure logrotate on the host:

```bash
# /etc/logrotate.d/traefik
compress
/mnt/docker-volumes/traefik/logs/*.log {
  size 20M
  daily
  rotate 14
  missingok
  notifempty
  postrotate
    docker kill --signal="USR1" traefik
  endscript
}
```
