# Production Hardening

## Security Recommendations

### 1. TLS for LAPI Communication

Encrypt all LAPI traffic, especially across networks:

```yaml
api:
  server:
    tls:
      cert_file: "/etc/crowdsec/tls/server.pem"
      key_file: "/etc/crowdsec/tls/server.key"
      client_verification: "RequireAndVerifyClientCert"
      ca_cert_path: "/etc/crowdsec/tls/ca.pem"
      agents_allowed_ou:
        - agents_ou
      bouncers_allowed_ou:
        - bouncers_ou
```

### 2. Bound LAPI to Localhost When Possible

```yaml
api:
  server:
    listen_uri: "127.0.0.1:8080"
```

If LAPI must be accessible on a network, use a firewall to restrict access.

### 3. Trusted IPs

```yaml
api:
  server:
    trusted_ips:
      - 127.0.0.1
      - ::1
      - 10.0.0.0/8
      - 192.168.0.0/16
```

### 4. Disable Unused Features

```yaml
api:
  server:
    disable_remote_lapi_registration: true    # Block unauthorized agent registration
    disable_usage_metrics_export: false       # Set true if you don't want analytics
```

### 5. Use .local Config Overrides

Keep custom config in `config.yaml.local` (or appropriate `.local` file) to avoid conflicts during package upgrades.

### 6. CAPI Whitelist

Protect against false positives from community blocklists:

```yaml
api:
  server:
    capi_whitelists_path: "/etc/crowdsec/capi-whitelists.yaml"
```

```yaml
# /etc/crowdsec/capi-whitelists.yaml
ips:
  - 1.2.3.4
cidrs:
  - 10.0.0.0/8
```

### 7. Database Security

- Use strong passwords stored in environment variables, not in config files
- For MySQL/PostgreSQL, use a dedicated database user with minimal privileges
- Enable WAL for SQLite (except on network shares)
- Set flush parameters to prevent unbounded data growth

### 8. Notification Plugins Security

Notification plugin binaries must be:
- Root-owned
- Non-world-writable
- Named as `<plugin_type>-<plugin_subtype>` (e.g., `notification-slack`)

## Performance Tuning

### Thread/Routine Counts

```yaml
crowdsec_service:
  parser_routines: 4        # Increase for high log throughput
  buckets_routines: 4
  output_routines: 2
```

On multi-core systems (4+ cores), start with `parser_routines: 4` and `buckets_routines: 4`. Monitor with `cscli metrics` and adjust.

### Database

```yaml
db_config:
  use_wal: true             # Critical for SQLite performance
  max_open_conns: 100       # Increase for MySQL/PostgreSQL under load
  decision_bulk_size: 1000  # Max 2000 — increase for slow storage
```

### Prometheus Metrics

```yaml
prometheus:
  level: aggregated          # Lower cardinality for less overhead
```

### Decision Duration

Configure appropriate ban durations in profiles:

```yaml
# /etc/crowdsec/profiles.yaml
name: default_ip_remediation
filters:
  - Alert.Remediation == true && Alert.GetScope() == "Ip"
decisions:
  - type: ban
    duration: 4h
on_success: break
```

For exponential banning, use `duration_expr`:
```yaml
decisions:
  - type: ban
    duration_expr: SceExpiryDuration(Scenario)  # Exponential backoff
```

## High Availability

For multi-instance deployments:
- Use **MySQL or PostgreSQL** backend (shared database)
- Run LAPI on multiple nodes behind a load balancer
- Use multiple log processors pushing to the same LAPI
- Each bouncer connects to the shared LAPI

## Auditing

- Monitor `cscli metrics` regularly
- Set up alerts for high alert volumes
- Whitelist expected traffic patterns before they cause false positives
- Periodically review decisions: `cscli decisions list`
