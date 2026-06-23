# Network & Connectivity

## Communication Model

Self-hosted runners connect to GitHub via **outbound HTTPS (port 443) only** — no inbound ports needed.

They poll for jobs via **HTTPS long-poll connections** to `*.actions.githubusercontent.com`.

**Minimum bandwidth:** 70 kbps upload and download.

## Required Domains

### Essential Operations
```
github.com
api.github.com
*.actions.githubusercontent.com
```

### Downloading Actions
```
codeload.github.com
```

### Uploading/Downloading Artifacts, Logs, Caches, Summaries
```
results-receiver.actions.githubusercontent.com
*.blob.core.windows.net
```

### Runner Version Updates
```
objects.githubusercontent.com
objects-origin.githubusercontent.com
github-releases.githubusercontent.com
github-registry-files.githubusercontent.com
```

### OIDC Token Retrieval
```
*.actions.githubusercontent.com
```

### GitHub Packages (Container Registry, etc.)
```
*.pkg.github.com
pkg-containers.githubusercontent.com
ghcr.io
```

### Git LFS
```
github-cloud.githubusercontent.com
github-cloud.s3.amazonaws.com
```

### Dependabot Update Jobs
```
dependabot-actions.githubapp.com
```

**Runner group access for Dependabot:** If Dependabot PRs aren't triggering CI on self-hosted runners, check two settings:
1. **Org/repo setting:** Settings → Actions → General → "Allow Dependabot to use self-hosted runners"
2. **Runner group API:** If using groups, enable via:
   ```bash
   gh api --method PATCH orgs/<org>/actions/runner-groups/<group-id> \
     -f allows_dependabot=true
   ```

### Release Assets
```
release-assets.githubusercontent.com
```

## TLS Verification

- **Enabled by default** — the runner verifies GitHub's TLS certificate
- **Disable for testing only**: Set `GITHUB_ACTIONS_RUNNER_TLS_NO_VERIFY=1`
- **Better approach**: Install GitHub's certificate in the OS trust store

## Firewall Configuration

For strict egress rules:
- Allow outbound HTTPS (443) to all domains listed above
- Some domains use CNAME records — firewalls may need recursive CNAME resolution
- Note: CNAME records may change; the listed domains are stable

## IP Allow Lists

If your GitHub organization or enterprise uses IP allow lists, you must add your self-hosted runner's IP address to the allow list. Without this, the runner cannot communicate with GitHub APIs.

## Proxy Configuration

Self-hosted runners support standard HTTP proxy environment variables:
- `HTTP_PROXY`
- `HTTPS_PROXY`
- `NO_PROXY`

Set these in the service environment or Docker container environment.

## Connectivity Diagram

```
┌──────────────────┐     Outbound HTTPS (443)     ┌──────────────────────┐
│  Self-Hosted     │ ────────────────────────────> │  GitHub Actions      │
│  Runner          │ <──────────────────────────── │  Service             │
│  (Docker/VM)     │   Long-poll for jobs          │  *.actions.github.   │
│                  │   Upload logs & artifacts     │  com / api.github.   │
│                  │   Download action code         │  com / blob.core.    │
└──────────────────┘                               │  windows.net / CDN   │
        │                                          └──────────────────────┘
        │ Mounted Docker socket (if using DinD)
        ▼
┌──────────────────┐
│  Host Docker      │
│  Daemon           │
│  (builds, runs)   │
└──────────────────┘
```
