# Production Operations Checklist

## Gotchas

- Install `crowdsecurity/whitelist-good-actors` to avoid blocking search engines and CDNs.
- Set `use_time_machine: true` for log sources that buffer before writing.
- Persist `/var/lib/crowdsec/data` in Docker deployments.
- Reload CrowdSec after installing collections or changing configuration.
- Set `labels.type` in acquisition configuration so parsers can handle logs.
- Save bouncer API keys when created; they are shown once.
- Use firewall and reverse-proxy remediation components where their coverage differs.
- Configure profiles deliberately instead of relying on the default four-hour decision duration.
- Treat `cscli <type> list --all` as available items, not only installed items.
- Enroll Docker deployments from inside the CrowdSec container.
- "Bouncer" and "remediation component" refer to the same role in newer documentation.
- Local YAML overrides merge mappings but replace sequences; `profiles.yaml.local` is read as multi-document YAML.

## Verification

After setup, verify the service, collections, remediation components, acquisition metrics, and AppSec when enabled:

```bash
sudo systemctl status crowdsec
sudo cscli collections list
sudo cscli bouncers list
sudo cscli metrics | grep -A5 "Acquisition"
sudo cscli decisions add --ip 198.51.100.1 --duration 5m
sudo cscli decisions list | grep 198.51.100.1
sudo cscli decisions delete --ip 198.51.100.1
sudo cscli metrics show appsec
```
