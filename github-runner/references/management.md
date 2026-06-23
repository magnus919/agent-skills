# Management & Operations

## Runner Groups

Groups control which repos can access which runners at the org level.

**Key operations:**
- Create via UI: Settings → Actions → Runner groups → New runner group
- Create via gh CLI:
  ```bash
  gh api --method POST orgs/<org>/actions/runner-groups \
    -f name="<group-name>" -f visibility="selected"
  gh api --method POST orgs/<org>/actions/runner-groups \
    -f name="<group-name>" -f visibility="all"
  ```
- Register into group: `./config.sh --runnergroup <name>`
- Move runner between groups: GitHub UI → Settings → Actions → Runners → click runner → Runner group dropdown
- List groups: `gh api orgs/<org>/actions/runner-groups --jq '.runner_groups[].name'`
- Default group exists in every org; unnamed runners land there
- Restrict repo access: Selected repositories vs All repositories
- Delete group: all runners must be moved or removed first

**Security:** Groups prevent repos in group A from using runners in group B.

## Labels

Labels control job routing at the runner level.

**Default labels:** `self-hosted`, OS (`linux`/`windows`/`macOS`), arch (`x64`/`ARM`/`ARM32`/`ARM64`)

**Custom labels:**
- Add at registration: `./config.sh --labels gpu,fast-ssd`
- Add/remove after registration: via GitHub UI
- Use in workflows: `runs-on: [self-hosted, linux, x64, gpu]`
- All labels must match (AND logic)
- `--no-default-labels`: strip OS/arch auto-labels
- Combine with groups: `runs-on: { group: ubuntu-runners, labels: ubuntu-24.04-16core }`

## Monitoring

### Status in GitHub UI
- **Idle**: Connected, ready for jobs
- **Active**: Currently executing a job
- **Offline**: Not connected

### Log Files
Located in `_diag/` directory:
- `Runner_<timestamp>.log`: App lifecycle, connection status, updates
- `Worker_<timestamp>.log`: Per-job execution details

### Journalctl (Linux systemd runners)
```bash
# Find service name
cat ~/actions-runner/.service

# Follow logs
sudo journalctl -u actions.runner.<scope>.<name>.service -f
```

### Docker Runners
```bash
docker logs <container-name> --tail 20
```

### gh CLI for Runner Status
```bash
# List runners for a repo
gh api repos/<owner>/<repo>/actions/runners --jq '.runners[] | "\(.name) (\(.status))"'

# List runners for an org
gh api orgs/<org>/actions/runners --jq '.runners[] | "\(.name) (\(.status))"'

# Check runner groups
gh api orgs/<org>/actions/runner-groups --jq '.runner_groups[].name'
```

### Network Connectivity Check
```bash
./config.sh --check --url <url> --pat <pat_with_workflow_scope>
```
Tests each required endpoint (github.com, api.github.com, *.actions.githubusercontent.com, etc.) and outputs PASS/FAIL per endpoint. Logs in `_diag/`.

## Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| 404 on registration | Using `RUNNER_TOKEN` instead of `ACCESS_TOKEN` | Switch to `ACCESS_TOKEN` PAT |
| "Not configured" crash | No valid credentials; registration failed | Check logs; verify ACCESS_TOKEN or generate fresh token |
| "Could not find any self-hosted runner group named 'Default'" | Org uses differently-named group | Set `RUNNER_GROUP` to the actual group name |
| Ephemeral mode when not wanted | `EPHEMERAL=0` (truthy in bash) | Use `EPHEMERAL=false` |
| `docker: not found` | Docker not installed | Install Docker or the job doesn't need it |
| `Permission denied` on Docker socket | Runner user not in docker group | Add user to docker group or use root |
| `cd /home/user/path` fails inside Docker container | Runner can't see host paths | Write deploy configs inline; use Docker socket only |
| Runner offline >14 days | Auto-removed by GitHub | Register a new runner |
| GHCR pull "unauthorized" | No Docker registry auth in deploy job | Add `docker/login-action@v4` with `secrets.GITHUB_TOKEN` |

## Removing a Runner

**If you have access to the runner machine:**
```bash
# Run the removal command shown in GitHub UI
./config.sh remove --token <token>
```

**If you don't have access:** Use Force remove in the GitHub UI.

**To re-register without re-downloading:** Delete the `.runner` file in the runner directory. Runner can then be re-configured.

## Runner Software Updates

- **Default**: Self-update enabled — runner auto-updates when a job is assigned or within 1 week
- **Disabled**: `--disableupdate` flag — you manage updates via container image
- **30-day window**: If disabled, runner must be updated within 30 days or GitHub stops assigning jobs
- **Critical security updates**: Immediately block jobs until updated
- **Recommendation for Docker runners**: Set `DISABLE_AUTO_UPDATE=1` and update the container image tag instead

Check latest release: https://github.com/actions/runner/releases

## Common Pitfalls

1. **ACCESS_TOKEN vs RUNNER_TOKEN** — most common failure mode
2. **EPHEMERAL=false** as string, not `0` — bash truthiness trap
3. **Missing RUNNER_GROUP** — fails to register if group doesn't exist
4. **Volume cleanup wipes credentials** — `docker compose down -v` removes named volumes; ACCESS_TOKEN auto-recovers
5. **Docker container filesystem** — runner cannot see host paths
6. **Ubuntu 20.04 Python 3.8** — `dict | None` syntax fails; use `from __future__ import annotations`
7. **Hugo modules need Go** — vendor modules or add `actions/setup-go@v5`
