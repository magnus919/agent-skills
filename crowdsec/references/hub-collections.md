# Hub Collections Reference

Essential CrowdSec hub collections organized by category.

## Infrastructure Protection

| Collection | Protects | Includes |
|------------|----------|----------|
| `crowdsecurity/linux` | Linux system logs | Syslog parser, geoip, date parsing |
| `crowdsecurity/sshd` | SSH service | SSH parser + SSH brute force scenario |
| `crowdsecurity/mysql` | MySQL database | MySQL parser + brute force scenario |
| `crowdsecurity/postgres` | PostgreSQL | PostgreSQL parser + scenarios |
| `crowdsecurity/whitelist-good-actors` | False positive prevention | SEO bots, CDN whitelists (Cloudflare, Google, etc.), reverse DNS |

## Web Server Protection

| Collection | Protects |
|------------|----------|
| `crowdsecurity/nginx` | Nginx web server |
| `crowdsecurity/apache2` | Apache httpd |
| `crowdsecurity/caddy` | Caddy web server |
| `crowdsecurity/traefik` | Traefik reverse proxy |
| `crowdsecurity/base-http-scenarios` | Generic HTTP attack scenarios |
| `crowdsecurity/http-cve` | CVE-based HTTP attack detection |

## HTTP Attack Scenarios (from base-http-scenarios)

| Scenario | Detects |
|----------|---------|
| `crowdsecurity/http-crawl-non_statics` | Directory enumeration / forced browsing |
| `crowdsecurity/http-probing` | General HTTP probing |
| `crowdsecurity/http-bad-user-agent` | Known malicious user agents (nmap, sqlmap, gobuster, etc.) |
| `crowdsecurity/http-sensitive-files` | Attempts to access sensitive files (.env, .git, wp-admin) |
| `crowdsecurity/http-backdoors-attempts` | Backdoor / webshell access attempts |
| `crowdsecurity/http-sqli-probing` | SQL injection probing |
| `crowdsecurity/http-xss-probing` | Cross-site scripting probing |
| `crowdsecurity/http-path-traversal-probing` | Path traversal attempts |
| `crowdsecurity/http-bf-wordpress_bf` | WordPress brute force |
| `crowdsecurity/http-bf-joomla_bf` | Joomla brute force |

## AppSec / WAF

| Collection | Description |
|------------|-------------|
| `crowdsecurity/appsec-virtual-patching` | Virtual patching rules for known CVEs |
| `crowdsecurity/appsec-crs` | OWASP Core Rule Set (ModSecurity-compatible) |
| `crowdsecurity/appsec-generic-rules` | Generic WAF rules |

## Bouncer Types

| Bouncer | Level | Supports AppSec |
|---------|-------|-----------------|
| Firewall (iptables/nftables) | Network (IP-level) | No |
| Traefik plugin | Reverse proxy | Yes |
| Nginx | Web server | Yes |
| Caddy module | Web server | Yes |
| HAProxy SPOE | Reverse proxy | Yes |
| Cloudflare worker | CDN | No |
| Blocklist mirror | Downloadable list | No |
| Custom bouncer | Programmatic (LAPI API) | Via integration |

## Finding Collections

Browse all available collections:
- Web UI: https://app.crowdsec.net/hub/collections
- CLI: `sudo cscli collections list --all`
- Hub: https://hub.crowdsec.net/browse/#collections

## Collection Management Commands

```bash
# Install
sudo cscli collections install crowdsecurity/nginx

# List installed
sudo cscli collections list

# List all available
sudo cscli collections list --all

# Inspect (shows version + runtime metrics)
sudo cscli collections inspect crowdsecurity/nginx

# Upgrade
sudo cscli hub update
sudo cscli collections upgrade crowdsecurity/nginx

# Remove
sudo cscli collections delete crowdsecurity/nginx
```

> After installing/upgrading collections: `sudo systemctl reload crowdsec`
