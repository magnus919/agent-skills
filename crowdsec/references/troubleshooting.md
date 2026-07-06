# Troubleshooting Guide

## "CrowdSec is installed but not blocking anything"

**Cause:** No remediation component (bouncer) is installed.

**Fix:** Install at least one bouncer:
```bash
sudo apt install crowdsec-firewall-bouncer-iptables
# OR for Docker environments with Traefik, configure the Traefik plugin middleware
```

## "Bouncer shows invalid or 403 Forbidden"

**Cause:** Wrong or missing API key in the bouncer config.

**Fix:** 
```bash
# Generate new key
sudo cscli bouncers add my-bouncer-name
# Or list existing
sudo cscli bouncers list
```

Update the bouncer config with the correct key.

## "crowdsec: command not found" or "cscli: command not found"

**Fix:** Install CrowdSec packages:
```bash
curl -s https://install.crowdsec.net | sudo sh
sudo apt update && sudo apt install crowdsec
```

## "No acquisition file found"

**Cause:** CrowdSec has no log sources configured.

**Fix:** Add acquisition config:
```bash
# Create acquisition file
echo 'filenames:
  - /var/log/auth.log
labels:
  type: syslog' | sudo tee /etc/crowdsec/acquis.d/sshd.yaml

sudo systemctl restart crowdsec
```

## "Labels type is mandatory" warning

**Cause:** An acquisition entry is missing `labels.type`.

**Fix:** Every acquisition entry must have a `type` label. The type determines which parser handles the logs.

## "IPs not being banned in Traefik"

**Cause:** The real client IP is not reaching CrowdSec (due to Cloudflare, load balancer, or proxy).

**Fix:**
1. Ensure Traefik logs show the real client IP (not Cloudflare/proxy IP)
2. Configure `forwardedHeadersTrustedIPs` in the Traefik middleware
3. For Cloudflare: add Cloudflare IP ranges to `forwardedHeaders.trustedIPs`
4. Check `crowdsecLapiKey` is correct

## "Container refuses to start" (Docker)

**Cause:** Missing volume mounts for data persistence.

**Fix:** Since CrowdSec v1.7.0, these volumes are mandatory:
```yaml
volumes:
  - crowdsec-db:/var/lib/crowdsec/data/
  - crowdsec-config:/etc/crowdsec/
```

## "Plugin not found" (Traefik)

**Cause:** Traefik plugin is not enabled in static config.

**Fix:** In `traefik.yaml`:
```yaml
experimental:
  plugins:
    bouncer:
      moduleName: github.com/maxlerebourg/crowdsec-bouncer-traefik-plugin
      version: v1.6.0
```

## "All requests returning 403"

**Cause:** Bouncer can't reach LAPI or API key is wrong.

**Fix:**
1. Verify LAPI is running: `sudo systemctl status crowdsec`
2. Check LAPI URL in bouncer config
3. Verify API key: `sudo cscli bouncers list`
4. Check Docker networking (are containers on the same network?)

## High memory / CPU usage

**Potential causes:**
- Too many parser/bucket routines for the available cores
- Large log files without `use_time_machine: true`
- SQLite without WAL mode under load

**Fixes:**
- Reduce `parser_routines` and `buckets_routines` in config.yaml
- Set `use_time_machine: true` for buffered log sources
- Enable WAL: `db_config.use_wal: true`
- Switch to MySQL/PostgreSQL for high-volume deployments

## "Cannot enroll in Console"

**Fix:**
```bash
# Bare metal
sudo cscli console enroll -e context <ENROLL_KEY>

# Docker
docker exec crowdsec cscli console enroll -e context <ENROLL_KEY>
```

Then approve the engine in the web console at https://app.crowdsec.net

## "Alerts showing but no decisions"

**Cause:** Scenario triggered but no profile matches.

**Fix:** Check `/etc/crowdsec/profiles.yaml`:
```yaml
name: default_ip_remediation
filters:
  - Alert.Remediation == true && Alert.GetScope() == "Ip"
decisions:
  - type: ban
    duration: 4h
on_success: break
```

## Logs not being parsed

1. Check acquisition config: `cat /etc/crowdsec/acquis.yaml` (is the log path correct?)
2. Verify log files exist and are readable: `sudo ls -la /var/log/auth.log`
3. Check metrics: `sudo cscli metrics` (look for Acquisition section)
4. Restart CrowdSec: `sudo systemctl restart crowdsec`

## General Diagnostics

```bash
# Service status
sudo systemctl status crowdsec

# Full metrics
sudo cscli metrics

# Check logs
sudo journalctl -u crowdsec --no-pager -n 50

# List installed collections
sudo cscli collections list

# List active decisions
sudo cscli decisions list

# List bouncers
sudo cscli bouncers list

# List machines (agents)
sudo cscli machines list

# Check CAPI connection
sudo cscli console status
```
