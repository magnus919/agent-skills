---
name: crowdsec
description: Deploy, configure, and manage CrowdSec — the open-source, collaborative
  IPS/IDPS/WAF. Covers Security Engine setup (Linux, Docker), cscli hub management,
  remediation components, AppSec WAF, profiles, notifications, blocklists, CTI, and
  metrics. Use when setting up or troubleshooting CrowdSec.
license: MIT
compatibility: Any agent supporting Agent Skills format — commands use standard shell
  and CLI tools
metadata:
  source: https://docs.crowdsec.net
  version: 0.0.2
---
# CrowdSec Skill
CrowdSec is an open-source, collaborative security engine that detects and blocks malicious actors. It analyzes logs and HTTP requests using behavior-based patterns (scenarios) and enforces blocks through remediation components (bouncers).
## Architecture Overview
CrowdSec has a modular, API-centric architecture. The main components:
| Component | Role |
|-----------|------|
| **Security Engine** (crowdsec) | Reads logs, parses them, evaluates scenarios, and produces alerts/decisions. Runs the Log Processor and Local API (LAPI). |
| **Local API (LAPI)** | HTTP API that stores decisions, serves remediation components, and communicates with the Central API. Runs inside the Security Engine. |
| **Central API (CAPI)** | CrowdSec's cloud service — receives signals from all instances and distributes community blocklists. |
| **Remediation Components** (formerly "bouncers") | Connect to LAPI to fetch decisions and enforce blocks at various levels (firewall, reverse proxy, web server). |
| **AppSec Component** | WAF subsystem that inspects HTTP requests in real-time. Lives in the Security Engine. |
| **cscli** | Command-line tool to manage the entire CrowdSec stack. |
**Data flow:** Logs → Parsers (s00-raw, s01-parse, s02-enrich) → Scenarios → Alerts → LAPI → Decisions → Remediation Components → Block
> **Important:** The Security Engine alone only *detects* — it does NOT block. You must add at least one remediation component to enforce decisions.

## Quick Reference

| Task | Command |
|------|---------|
| Install engine | `curl -s https://install.crowdsec.net \| sudo sh` then `sudo apt install crowdsec` |
| Install firewall bouncer | `sudo apt install crowdsec-firewall-bouncer-iptables` (or `-nftables`) |
| Add bouncer API key | `sudo cscli bouncers add <name>` |
| List bouncers | `sudo cscli bouncers list` |
| Install collection | `sudo cscli collections install crowdsecurity/nginx` |
| List collections | `sudo cscli collections list` |
| View metrics | `sudo cscli metrics` |
| List alerts | `sudo cscli alerts list` |
| List decisions | `sudo cscli decisions list` |
| Manually ban IP | `sudo cscli decisions add --ip <IP>` |
| Manually unban IP | `sudo cscli decisions delete --ip <IP>` (or `remove --ip`, which is an alias) |
| View status | `sudo systemctl status crowdsec` |
| Reload config | `sudo systemctl reload crowdsec` |

## Installation

### Linux (Debian/Ubuntu)

```bash
# Add repository
curl -s https://install.crowdsec.net | sudo sh
sudo apt update
sudo apt install crowdsec

# Optionally install firewall bouncer
sudo apt install crowdsec-firewall-bouncer-iptables
```

During installation, CrowdSec auto-detects running services (SSH, nginx, etc.) and installs appropriate collections + acquisition config.

### Docker / Docker Compose

```yaml
services:
  crowdsec:
    image: crowdsecurity/crowdsec:latest
    restart: always
    ports:
      - 127.0.0.1:8080:8080   # LAPI
      - 127.0.0.1:6060:6060   # Prometheus metrics
      - 127.0.0.1:7422:7422   # AppSec WAF
    environment:
      COLLECTIONS: "crowdsecurity/linux crowdsecurity/nginx"
      GID: "${GID-1000}"
      TZ: "UTC"
    volumes:
      - ./crowdsec/config:/etc/crowdsec
      - ./crowdsec/data:/var/lib/crowdsec/data
      - /var/log:/var/log:ro
```

> **Version note:** Persisting `/var/lib/crowdsec/data` is **mandatory since v1.7.0**. On older versions (v1.6.x and earlier), the container uses this directory for the SQLite database but does not require it. However, persisting it is always recommended to avoid data loss on container restart. Use a named volume or bind mount; tmpfs is only suitable for throwaway/non-production deployments.

**Key environment variables:**

| Variable | Default | Description |
|----------|---------|-------------|
| `COLLECTIONS` | *(none)* | Space-separated list of collections to install |
| `DISABLE_LOCAL_API` | `false` | Set `true` to run as log processor only |
| `DISABLE_AGENT` | `false` | Set `true` to run as LAPI only |
| `BOUNCER_KEY_<name>` | *(none)* | Seed API key for a bouncer |
| `TZ` | `UTC` | Timezone |
| `CONFIG_FILE` | `/etc/crowdsec/config.yaml` | Path to main config |

## Configuration

### Main config file (`/etc/crowdsec/config.yaml`)

Key sections: `common`, `config_paths`, `crowdsec_service`, `db_config`, `api`, `prometheus`.

Use `config.yaml.local` for local overrides — values here take precedence over `config.yaml` and survive package upgrades. Supports environment variable substitution (`${VAR}`).

### Acquisition (`/etc/crowdsec/acquis.yaml` or `/etc/crowdsec/acquis.d/*.yaml`)

Tells CrowdSec which log files to read:

```yaml
filenames:
  - /var/log/nginx/*.log
labels:
  type: nginx
---
filenames:
  - /var/log/auth.log
  - /var/log/syslog
labels:
  type: syslog
---
source: docker
container_name_regexp:
  - .*caddy*
labels:
  type: caddy
```

The `labels.type` field is **mandatory** — it determines which parsers handle the logs.

> **Note:** For log files on network shares (NFS, SMB) or Docker bind mounts where inotify doesn't work reliably, add `poll_without_inotify: true` to the acquisition entry. This polls the file at intervals instead of relying on filesystem events.

### Profiles (`/etc/crowdsec/profiles.yaml`)

Controls what remediation action is taken when a scenario triggers:

```yaml
name: default_ip_remediation
filters:
  - Alert.Remediation == true && Alert.GetScope() == "Ip"
decisions:
  - type: ban
    duration: 4h
on_success: break
```

Override values via `profiles.yaml.local`. Files are read sequentially (not merged).

### Simulation mode (`/etc/crowdsec/simulation.yaml`)

When enabled, CrowdSec still detects but does not enforce:

```yaml
simulation: true
exclusions:
  - crowdsecurity/ssh-bf
```

## cscli Command Reference

`cscli` [global flags] `<command>` [subcommand] [options]

**Global flags:** `-c <config>` (config path), `-o json|human|raw` (output format), `--debug`, `--color`

| Category | Key Commands | Load detail |
|----------|-------------|-------------|
| Hub Management | `cscli hub update`, `cscli collections install/list/upgrade/inspect`, `cscli parsers install/list/upgrade`, `cscli scenarios install/list/upgrade` | `references/cscli-command-reference.md` |
| Decisions & Alerts | `cscli decisions add/list/delete`, `cscli alerts list/inspect` | `references/cscli-command-reference.md` |
| Bouncers & Agents | `cscli bouncers add/list/delete`, `cscli machines add/list/delete` | `references/cscli-command-reference.md` |
| Metrics | `cscli metrics`, `cscli metrics show appsec\|bouncers` | `references/cscli-command-reference.md` |
| Console & LAPI | `cscli console status/enroll`, `cscli lapi register` | `references/cscli-command-reference.md` |
| Additional | `cscli version`, `cscli config`, `cscli explain`, `cscli simulation`, `cscli allowlists` | `references/cscli-command-reference.md` |

See the full command reference at `references/cscli-command-reference.md`.

## Hub Collections

Collections bundle parsers + scenarios for a service. **This is the primary way to add protection:**

| Collection | Protects |
|------------|----------|
| `crowdsecurity/linux` | Linux syslog, SSH, sudo |
| `crowdsecurity/sshd` | SSH brute force detection |
| `crowdsecurity/nginx` | Nginx web server |
| `crowdsecurity/traefik` | Traefik reverse proxy |
| `crowdsecurity/caddy` | Caddy web server |
| `crowdsecurity/apache2` | Apache httpd |
| `crowdsecurity/base-http-scenarios` | Generic HTTP attacks |
| `crowdsecurity/http-cve` | CVE-based HTTP attack detection |
| `crowdsecurity/whitelist-good-actors` | Whitelist known good actors (search engines, CDNs) |
| `crowdsecurity/appsec-virtual-patching` | AppSec virtual patching rules |
| `crowdsecurity/appsec-crs` | OWASP CRS rules for AppSec |
| `crowdsecurity/appsec-generic-rules` | Generic AppSec WAF rules |
| `crowdsecurity/mysql` | MySQL database |
| `crowdsecurity/postgres` | PostgreSQL |
| `crowdsecurity/cloudflare` | Cloudflare-protected sites |

Browse all collections at: https://app.crowdsec.net/hub/collections

## Remediation Components (Bouncers)

After installing a bouncer, add it to LAPI:

```bash
sudo cscli bouncers add my-bouncer-name
# Save the API key returned — it won't be shown again
```

### Firewall Bouncer (iptables/nftables)

Blocks IPs at the network level. Best for SSH, databases, SMTP.

```bash
sudo apt install crowdsec-firewall-bouncer-iptables
# or
sudo apt install crowdsec-firewall-bouncer-nftables
```

Config at: `/etc/crowdsec/bouncers/crowdsec-firewall-bouncer.yaml`

### Traefik Bouncer (Plugin)

Block at the reverse proxy level. Supports AppSec WAF forwarding.

**Static config (`traefik.yaml`):**
```yaml
experimental:
  plugins:
    bouncer:
      moduleName: github.com/maxlerebourg/crowdsec-bouncer-traefik-plugin
      version: v1.6.0
```

**Dynamic config (middleware):**
```yaml
middlewares:
  crowdsec:
    plugin:
      bouncer:
        enabled: true
        crowdsecMode: live
        crowdsecLapiScheme: http
        crowdsecLapiHost: crowdsec:8080
        crowdsecLapiKey: "<your-api-key>"
        forwardedHeadersTrustedIPs:
          - 10.0.0.0/8
          - 172.16.0.0/12
          - 192.168.0.0/16
```

### Nginx Bouncer

The Nginx bouncer uses Lua directives to check requests against CrowdSec decisions.

```bash
sudo apt install crowdsec-firewall-bouncer-nginx
```

**Bouncer config** (`/etc/crowdsec/bouncers/crowdsec-nginx-bouncer.yaml`):
```yaml
api_url: http://127.0.0.1:8080
api_key: "<your-bouncer-api-key>"
mode: stream            # stream (push) or live (pull on each request)
update_frequency: 10s   # How often to refresh decisions in stream mode
```

**Nginx config** (add to `server {}` block or `nginx.conf`):
```nginx
lua_package_path "/usr/lib/crowdsec/lua/?.lua;;";
lua_shared_dict crowdsec_cache 10m;

init_by_lua_block {
    local bouncer = require "crowdsec"
    bouncer.init()
}

access_by_lua_block {
    local bouncer = require "crowdsec"
    if bouncer.check() then
        return ngx.exit(ngx.FORBIDDEN)
    end
}
```

After setup: `sudo systemctl reload nginx && sudo systemctl restart crowdsec`.

Config at `/etc/crowdsec/bouncers/crowdsec-nginx-bouncer.yaml`. See the full configuration guide with `nginx.conf` directives and Cloudflare CDN support in `references/nginx-bouncer.md`.

### Other Bouncers

- **Caddy:** Uses the crowdsec module for Caddy
- **HAProxy:** SPOE-based integration
- **Blocklist Mirror:** Provides a downloadable blocklist for firewalls/routers
- **Custom Bouncer:** Build your own via the LAPI HTTP API

Full list: https://hub.crowdsec.net/browse/#remediation-components

## AppSec (WAF)

The AppSec Component turns CrowdSec into a full WAF with virtual patching.

### Enable AppSec

In `acquis.yaml` (or `acquis.yaml.local`):
```yaml
source: appsec
listen_addr: 0.0.0.0:7422
appsec_config: crowdsecurity/appsec-default
labels:
  type: appsec
```

Install AppSec collections:
```bash
sudo cscli collections install crowdsecurity/appsec-virtual-patching
sudo cscli collections install crowdsecurity/appsec-crs
sudo cscli collections install crowdsecurity/appsec-generic-rules
```

### How AppSec Works

1. Web server forwards HTTP request to the CrowdSec engine (port 7422)
2. In-band rules are evaluated first — if triggered, request is blocked (403) or captcha'd
3. Out-of-band rules evaluate asynchronously — non-blocking, used for behavioral detection
4. When rules trigger, events feed into scenarios for longer-term decisions

### AppSec Rule Types

- **In-band rules:** Blocking — return `ban` or `captcha` immediately. Used for SQLi, XSS, path traversal, CVE exploitation.
- **Out-of-band rules:** Non-blocking — emit events for scenario processing. Used for enumeration, scraping, spam.

## Notifications

### Configure Notifications

1. **Enable in profiles:** Add `notification` to profile in `/etc/crowdsec/profiles.yaml`
2. **Create notification config:** File in `/etc/crowdsec/notifications/<plugin>.yaml`

Supported plugins: Slack, HTTP/Webhook, Email (SMTP), Splunk, Telegram, Sentry

### Test Notifications

```bash
sudo cscli notifications test <plugin_name>
sudo cscli notifications list
```

### Example: HTTP Webhook

```yaml
# /etc/crowdsec/notifications/http.yaml
type: http
name: http_default
log_level: info
format: json
url: https://hooks.example.com/crowdsec
method: POST
headers:
  Content-Type: application/json
```

## Blocklists

Blocklists are curated threat feeds you subscribe to via the CrowdSec Console. They augment community blocklists with third-party intelligence.

Two tiers in `config.yaml` under `api.server.online_client.pull`:
- `community: true/false` — Pull from the CrowdSec community network
- `blocklists: true/false` — Pull from subscribed third-party blocklists

## CTI (Cyber Threat Intelligence)

CrowdSec provides an IP reputation API. Configure in `config.yaml`:
```yaml
api:
  cti:
    key: "<your-cti-api-key>"
    cache_timeout: "60m"
    cache_size: 50
    enabled: true
```

Use `cscli decisions list -o json` to see CTI-enriched output.

## Data Sources / Acquisition

CrowdSec supports many log sources:

| Source | Config Type | Stream | One-shot |
|--------|-------------|--------|----------|
| File | `filenames:` | Yes | Yes |
| Docker | `source: docker` | Yes | Yes |
| Journald | `source: journald` | Yes | Yes |
| Syslog | `source: syslog` | Yes | No |
| HTTP | `source: http` | Yes | No |
| Kafka | `source: kafka` | Yes | No |
| AWS CloudWatch | `source: cloudwatch` | Yes | Yes |
| AWS S3 | `source: s3` | Yes | Yes |
| Loki | `source: loki` | Yes | Yes |
| Windows Event | `source: windows_evt_log` | Yes | Yes |

Common acquisition parameters:
- `log_level`: Per-source log level
- `transform`: Expression to modify events pre-parsing
- `use_time_machine: true` — Use log timestamps instead of read time (important for buffered logs like IIS, S3)
- `labels.type`: **Required** — determines which parser handles the logs

## Database Backends

CrowdSec supports multiple database backends in `/etc/crowdsec/config.yaml`:

```yaml
db_config:
  type: sqlite       # or mysql, postgresql, pgx
  db_path: /var/lib/crowdsec/data/crowdsec.db
  use_wal: true      # SQLite WAL mode for better concurrency
  max_open_conns: 100
  flush:
    max_items: 50000    # Max alerts before purge; lower if disk-constrained
    max_age: 7d         # Alert retention — both max_items and max_age act independently
    metrics_max_age: 90d
```

**Flush tuning guidance:**
- Both `max_items` and `max_age` act as independent thresholds — whichever triggers first causes a flush. Set both for belt-and-suspenders control.
- On low-power devices (Raspberry Pi, SD cards), set `max_items: 10000` and `decision_bulk_size: 2000` to reduce write frequency.
- For high-traffic deployments, increase `max_items` to 100000+ but monitor disk usage.
- SQLite flush does NOT reclaim disk space — run `VACUUM` periodically on the SQLite database file to shrink it after large flushes.

## Metrics & Observability

### Built-in metrics

```bash
sudo cscli metrics       # Full metrics dashboard
sudo cscli metrics -o json  # JSON for programmatic use
```

Metrics include: Acquisition stats, parser hits/unparsed, scenario counts, alert counts, decisions (local vs CAPI), bouncer activity.

### Prometheus

Enable in `config.yaml`:
```yaml
prometheus:
  enabled: true
  level: full             # or "aggregated" for low cardinality
  listen_addr: 0.0.0.0
  listen_port: 6060
```

CrowdSec provides Grafana dashboards: https://github.com/crowdsecurity/grafana-dashboards

### CrowdSec Console (Web UI)

Free web console at https://app.crowdsec.net — provides:
- Alert dashboard with IP reputation, MITRE ATT&CK TTPs
- Decision management
- Blocklist subscriptions
- Security Engine enrollment
- Stack health monitoring
- Remediation metrics

Enroll: `sudo cscli console enroll <enrollment_key>`

## TLS / mTLS

CrowdSec supports TLS for LAPI communication:

```yaml
api:
  server:
    tls:
      cert_file: "/path/to/cert.pem"
      key_file: "/path/to/key.pem"
      client_verification: "RequireAndVerifyClientCert"
      ca_cert_path: "/path/to/ca.pem"
      agents_allowed_ou:
        - agents_ou
      bouncers_allowed_ou:
        - bouncers_ou
```

## References

Load the following reference files for deeper coverage of specific topics:
| Reference | Load when | File |
|-----------|-----------|------|
| Full config.yaml reference | You need every configuration directive explained | `references/config-reference.md` |
| cscli command reference | You need every cscli subcommand and flag | `references/cscli-command-reference.md` |
| AppSec WAF deep dive | Setting up or troubleshooting AppSec | `references/appsec-deep-dive.md` |
| Docker deployment guide | Running CrowdSec in Docker Compose | `references/docker-deployment.md` |
| Traefik bouncer setup | Integrating with Traefik reverse proxy | `references/traefik-bouncer.md` |
| Nginx bouncer setup | Configuring the Nginx bouncer with nginx.conf directives | `references/nginx-bouncer.md` |
| Database configuration | Choosing between SQLite, MySQL, PostgreSQL | `references/database-config.md` |
| Production hardening | Security, TLS, performance tuning | `references/production-hardening.md` |
| Hub collections list | You need to know which collection protects what | `references/hub-collections.md` |
| Troubleshooting guide | Something isn't working | `references/troubleshooting.md` |
| Production operations checklist | Verifying or operating a deployment | `references/operations-checklist.md` |
