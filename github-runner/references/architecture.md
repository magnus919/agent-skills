# Runner Architecture

## Registration Flow

1. **Token generation**: A GitHub PAT (or short-lived registration token) is used to call `POST /actions/runners/registration-token` via the GitHub API. Tokens expire in ~60 minutes.

2. **Configuration**: `config.sh --url <scope> --token <token>` creates `.credentials` and `.runner` files.
   - `--labels`: comma-separated custom labels
   - `--runnergroup`: target group (fails if group doesn't exist)
   - `--ephemeral`: one-job-only mode
   - `--disableupdate`: opt out of auto-updates
   - `--no-default-labels`: strip OS/arch auto-labels

3. **Connection**: `run.sh` establishes an HTTPS long-poll connection to `*.actions.githubusercontent.com`:
   - Sends "listening for jobs" heartbeat
   - Receives job assignments in real-time
   - Output: `√ Connected to GitHub` followed by `Listening for Jobs`

## Job Assignment Lifecycle

1. Workflow triggers → GitHub Actions service dispatches jobs matching `runs-on` labels/groups
2. Runner receives "Job Available" message via long-poll
3. If idle and online, runner acknowledges and accepts the job
4. If the runner doesn't pick up the assigned job within 60 seconds, the job is re-queued
5. Runner downloads job details, executes steps sequentially
6. Streams logs and status back to GitHub via HTTPS
7. For ephemeral runners: runner deregisters automatically after job completion
8. For persistent runners: runner returns to Listening state

## Routing Precedence

- GitHub matches `runs-on: [self-hosted, linux, x64, gpu]` — runner must match ALL labels
- Runner groups can be specified alongside labels:
  ```yaml
  runs-on:
    group: ubuntu-runners
    labels: ubuntu-24.04-16core
  ```
- If no matching runner is online, the job queues for up to 24 hours
- If a runner doesn't pick up an assigned job within 60 seconds, the job is re-queued

## Service Management

| Platform | Command | Notes |
|----------|---------|-------|
| Linux (systemd) | `sudo ./svc.sh install && sudo ./svc.sh start` | Creates unit at `/etc/systemd/system/actions.runner.*` |
| macOS (launchd) | `./svc.sh install && ./svc.sh start` | Creates plist in user's LaunchAgents |
| Windows | Part of config script | Managed via Services app or PowerShell |
| Docker | Container entrypoint handles lifecycle | Named volume persists credentials |

## Service Commands (Linux/macOS)

```bash
./svc.sh install [username]   # Install service (Linux: optional user arg)
sudo ./svc.sh start           # Start service
sudo ./svc.sh status          # Check service status
sudo ./svc.sh stop            # Stop service
sudo ./svc.sh uninstall       # Remove service
```

## Key Files (on-disk runner installation)

| File | Purpose |
|------|---------|
| `.runner` | Configuration — scope, URL, runner name |
| `.credentials` | Encrypted auth credentials (persisted across restarts) |
| `.credentials_rsaparams` | RSA key pair for authentication |
| `.service` | Service name (written by svc.sh install) |
| `_diag/` | Log files — `Runner_<timestamp>.log`, `Worker_<timestamp>.log` |
| `_update/` | Self-update binaries and logs |

## Automatic Cleanup

- **Persistent runner** offline > 14 days: automatically removed by GitHub
- **Ephemeral runner** offline > 1 day: automatically removed by GitHub
- **JIT runners**: removed after single job or automatically if never used
