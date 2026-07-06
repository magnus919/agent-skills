# Database Configuration

CrowdSec supports multiple database backends for the Local API.

## Supported Backends

| Backend | Type value | Best for |
|---------|------------|----------|
| SQLite | `sqlite` | Single-instance, small to medium deployments |
| MySQL | `mysql` | Distributed setups, high-volume environments |
| PostgreSQL | `postgresql` | Distributed setups, enterprise requirements |
| PGX | `pgx` | PostgreSQL with pgx driver (enhanced PostgreSQL support) |

## SQLite (Default)

```yaml
db_config:
  type: sqlite
  db_path: /var/lib/crowdsec/data/crowdsec.db
  use_wal: true            # Write-Ahead Logging for better concurrency
  max_open_conns: 100
```

**WAL mode** improves performance significantly. Enable it unless the database is on a network share. When WAL is unspecified, a startup warning is shown.

## MySQL

```yaml
db_config:
  type: mysql
  user: crowdsec
  password: "${DB_PASSWORD}"
  db_name: crowdsec
  host: 192.168.1.100
  port: 3306
  sslmode: require
  max_open_conns: 100
```

Socket connection:
```yaml
db_config:
  type: mysql
  db_path: /var/run/mysqld/mysqld.sock
  user: crowdsec
  password: "${DB_PASSWORD}"
  db_name: crowdsec
```

## PostgreSQL

```yaml
db_config:
  type: postgresql
  user: crowdsec
  password: "${DB_PASSWORD}"
  db_name: crowdsec
  host: 192.168.1.100
  port: 5432
  sslmode: require
  ssl_ca_cert: "/path/to/ca.crt"
  ssl_client_cert: "/path/to/client.crt"
  ssl_client_key: "/path/to/client.key"
  max_open_conns: 100
```

## PGX (Enhanced PostgreSQL)

Same as PostgreSQL but uses the pgx driver:

```yaml
db_config:
  type: pgx
  user: crowdsec
  password: "${DB_PASSWORD}"
  db_name: crowdsec
  host: 192.168.1.100
  port: 5432
```

## Flush Configuration

Controls alert/metrics retention:

```yaml
db_config:
  flush:
    max_items: 50000        # Max alerts in DB (older ones are purged)
    max_age: "7d"            # Alert retention (s=seconds, m=minutes, h=hours, d=days)
    metrics_max_age: "90d"   # Metrics retention

    # Auto-delete stale bouncers
    bouncers_autodelete:
      cert: "720h"           # Delete TLS-authenticated bouncers after N hours without pull
      api_key: "720h"        # Delete API key bouncers after N hours without pull

    # Auto-delete stale agents
    agents_autodelete:
      cert: "720h"           # Delete TLS-agents after N hours without push
      login_password: "720h" # Delete login/password agents after N hours without push
```

## Performance Notes

- **SQLite with WAL** is suitable for most deployments up to hundreds of decisions/second
- **MySQL/PostgreSQL** are recommended for distributed multi-instance setups
- `max_open_conns` defaults to 100 — increase if you see `too many connections` errors
- `decision_bulk_size` (default: 1000, max: 2000) controls how many decisions are inserted per query
- On low-power devices (Raspberry Pi, SD cards), raise `decision_bulk_size` to 2000 and ensure WAL is enabled
