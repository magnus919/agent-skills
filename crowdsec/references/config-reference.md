# CrowdSec Configuration Reference

Full reference for `/etc/crowdsec/config.yaml` — the main configuration file for the CrowdSec Security Engine.

## `common`

```yaml
common:
  daemonize: "true|false"
  pid_dir: "/var/run/"
  log_media: "file|stdout|syslog"
  log_level: "error|info|debug|trace"
  log_dir: "/var/log/crowdsec/"
  working_dir: "/"
  log_max_size: 500           # MB before rotation
  log_max_age: 28             # days to retain
  log_max_files: 3            # rotated files to keep
  compress_logs: true|false
  log_format: "text|json"
```

## `config_paths`

```yaml
config_paths:
  config_dir: "/etc/crowdsec"
  data_dir: "/var/lib/crowdsec/data"
  simulation_path: "/etc/crowdsec/simulation.yaml"
  hub_dir: "/etc/crowdsec/hub"
  index_path: "/etc/crowdsec/hub/.index.json"
  notification_dir: "/etc/crowdsec/notifications/"
  plugin_dir: "/usr/lib/crowdsec/plugins/"
```

## `crowdsec_service`

```yaml
crowdsec_service:
  enable: true
  acquisition_path: "/etc/crowdsec/acquis.yaml"
  acquisition_dir: "/etc/crowdsec/acquis.d/"
  parser_routines: 1
  buckets_routines: 1
  output_routines: 1
```

## `db_config`

See the `references/database-config.md` reference for full details. Quick reference:

```yaml
db_config:
  type: "sqlite|mysql|postgresql|pgx"
  db_path: "/var/lib/crowdsec/data/crowdsec.db"
  user: ""
  password: ""
  db_name: "crowdsec"
  host: ""
  port: 0
  sslmode: "require|disable"
  use_wal: true
  max_open_conns: 100
  flush:
    max_items: 50000
    max_age: "7d"
    metrics_max_age: "90d"
```

## `api`

```yaml
api:
  # CTI (IP reputation)
  cti:
    key: ""
    cache_timeout: "60m"
    cache_size: 50
    enabled: true|false
    log_level: "info|debug|trace"

  # Client (used by crowdsec + cscli to talk to LAPI)
  client:
    insecure_skip_verify: true|false
    credentials_path: "/etc/crowdsec/local_api_credentials.yaml"

  # LAPI Server
  server:
    enable: true
    listen_uri: "0.0.0.0:8080"
    profiles_path: "/etc/crowdsec/profiles.yaml"
    use_forwarded_for_headers: true|false
    trusted_ips:
      - 127.0.0.1
      - ::1

    # Console / CAPI
    console_path: "/etc/crowdsec/console.yaml"
    online_client:
      sharing: true|false      # Share signals with community
      pull:
        community: true|false  # Pull community blocklist
        blocklists: true|false  # Pull subscribed 3rd-party blocklists
      credentials_path: "/etc/crowdsec/online_api_credentials.yaml"

    # TLS
    tls:
      cert_file: ""
      key_file: ""
      client_verification: "NoClientCert|VerifyClientCertIfGiven|RequireAndVerifyClientCert"
      ca_cert_path: ""
      agents_allowed_ou:
        - agents_ou
      bouncers_allowed_ou:
        - bouncers_ou

    # Auto-registration
    auto_registration:
      enabled: true|false
      token: ""           # Min 32 chars
      allowed_ranges:
        - 10.0.0.0/24

    # Rate limiting
    disable_remote_lapi_registration: true|false
    disable_usage_metrics_export: true|false
    capi_whitelists_path: ""
```

## `prometheus`

```yaml
prometheus:
  enabled: true|false
  level: "full|aggregated"
  listen_addr: "0.0.0.0"
  listen_port: 6060
```

## `cscli`

```yaml
cscli:
  output: "human|json|raw"
  hub_branch: "master"
  prometheus_uri: "http://127.0.0.1:6060/"
```

## Environment Variable Substitution

Set values from environment variables:

```yaml
db_config:
  password: ${DB_PASSWORD}
```

Export the variable as root (or in `/etc/environment`):
```bash
export DB_PASSWORD="my_secret_password"
```

> **Note:** Since CrowdSec v1.5.0, undefined variables leave the original string intact (allowing literal `$` in passwords). Earlier versions replaced undefined vars with empty strings.

## Configuration Override via `.local` Files

Files that support `config.yaml.local` overrides:
- `config.yaml`
- `local_api_credentials.yaml`
- `simulation.yaml`
- `bouncers/crowdsec-firewall-bouncer.yaml`
- `bouncers/crowdsec-custom-bouncer.yaml`
- `bouncers/crowdsec-blocklist-mirror.yaml`

> **Important:** Mappings are merged, sequences are REPLACED. You cannot remove a mapping key via .local — only change its value.
> For `profiles.yaml`, .local files are read as multi-document YAML (appended, not merged).
