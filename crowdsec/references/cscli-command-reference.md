# cscli Command Reference

Full reference for `cscli` — the CrowdSec command-line tool for managing the entire stack.

## Global Flags

```
-c, --config string   path to crowdsec config file (default "/etc/crowdsec/config.yaml")
-o, --output string   Output format: human, json, raw
    --color string    Output color: yes, no, auto (default "auto")
    --debug           Set logging to debug
    --info            Set logging to info
    --warning         Set logging to warning
    --error           Set logging to error
    --trace           Set logging to trace
-h, --help            help for cscli
```

## Hub Management

| Command | Description |
|---------|-------------|
| `cscli hub update` | Update the local hub index |
| `cscli hub list` | List hub index info |
| `cscli collections install <name>` | Install a collection |
| `cscli collections list` | List installed collections |
| `cscli collections list --all` | List all available collections |
| `cscli collections upgrade <name>` | Upgrade a collection |
| `cscli collections inspect <name>` | Show collection details and metrics |
| `cscli collections delete <name>` | Remove a collection |
| `cscli parsers install <name>` | Install a parser |
| `cscli parsers list` | List installed parsers |
| `cscli parsers list --all` | List all available parsers |
| `cscli parsers upgrade <name>` | Upgrade a parser |
| `cscli parsers inspect <name>` | Show parser details/metrics |
| `cscli parsers delete <name>` | Remove a parser |
| `cscli scenarios install <name>` | Install a scenario |
| `cscli scenarios list` | List installed scenarios |
| `cscli scenarios list --all` | List all available scenarios |
| `cscli scenarios upgrade <name>` | Upgrade a scenario |
| `cscli scenarios inspect <name>` | Show scenario details/metrics |
| `cscli scenarios delete <name>` | Remove a scenario |
| `cscli postoverflows install <name>` | Install a postoverflow |
| `cscli postoverflows list` | List installed postoverflows |
| `cscli appsec-rules list` | List installed AppSec rules |
| `cscli appsec-configs list` | List AppSec configurations |
| `cscli contexts list` | List contexts |
| `cscli hubtest` | Run functional tests on hub configurations |

## Decision & Alert Management

| Command | Description |
|---------|-------------|
| `cscli decisions add --ip <IP> [--duration 4h] [--type ban] [--reason "..."]` | Add a manual decision |
| `cscli decisions list` | List active decisions |
| `cscli decisions list -o json` | List decisions as JSON (includes CTI data) |
| `cscli decisions delete --id <id>` | Delete a specific decision by ID |
| `cscli decisions delete --ip <IP>` | Delete all decisions for an IP |
| `cscli alerts list` | List alerts |
| `cscli alerts list --contain "scenario:ssh-bf"` | Filter alerts by scenario |
| `cscli alerts inspect <id>` | Show alert details |

## Bouncer & Agent Management

| Command | Description |
|---------|-------------|
| `cscli bouncers add <name>` | Add a bouncer and generate API key (shown once only) |
| `cscli bouncers list` | List all bouncers with IP, validity, last pull |
| `cscli bouncers delete <name>` | Remove a bouncer |
| `cscli machines add <name> [--password <pwd>]` | Register an agent machine |
| `cscli machines list` | List registered agents |
| `cscli machines delete <name>` | Remove an agent |

## Metrics & Observability

| Command | Description |
|---------|-------------|
| `cscli metrics` | Full metrics dashboard |
| `cscli metrics -o json` | JSON output for programmatic use |
| `cscli metrics show appsec` | AppSec-specific metrics (processed vs blocked) |
| `cscli metrics show bouncers` | Bouncer-specific metrics |

## Console & LAPI

| Command | Description |
|---------|-------------|
| `cscli console status` | Check console connection status |
| `cscli console enroll <enroll_key>` | Enroll engine in CrowdSec Console |
| `cscli lapi register` | Register remote agent to LAPI |

## Additional Commands

| Command | Description |
|---------|-------------|
| `cscli version` | Display version and build info |
| `cscli config` | View current configuration |
| `cscli explain` | Explain log pipeline — simulate how a log line is processed |
| `cscli simulation` | Manage simulation status of scenarios |
| `cscli allowlists` | Manage centralized allowlists (v1.6+) |
| `cscli capi` | Manage interaction with Central API |
| `cscli papi` | Manage interaction with Polling API |
| `cscli dashboard` | Manage Metabase dashboard container |
| `cscli support` | Generate support bundle for troubleshooting |
| `cscli notifications list` | List notification plugins |
| `cscli notifications test <name>` | Test a notification plugin |
