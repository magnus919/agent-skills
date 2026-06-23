# Security Hardening

Self-hosted runners are fundamentally less secure than GitHub-hosted runners because they lack ephemeral, clean-slate VM isolation.

**Core rule:** Self-hosted runners should almost never be used on public repositories. Forks can execute arbitrary code on your runner infrastructure.

## Mitigation Strategies

### 1. Runner Groups (Access Boundaries)

Group runners at the org level and restrict which repos can access them. This limits blast radius if a runner is compromised.

```bash
# Check existing groups
gh api orgs/<org>/actions/runner-groups --jq '.runner_groups[].name'

# Register runner into a specific group
./config.sh --url <url> --token <token> --runnergroup <group-name>
```

**Key points:**
- Default group allows all repos in the org — highest risk configuration
- Create custom groups with restricted repository access
- Public repository access is blocked by default per group (can be overridden)
- Move runners between groups in the GitHub UI

### 2. Ephemeral Runners

Ephemeral runners execute at most one job, then deregister automatically.

```bash
./config.sh --url <url> --token <token> --ephemeral
```

- Each job gets a clean environment (if provisioning creates one)
- Logs must be forwarded externally — they're lost when the runner disappears
- GitHub guarantees only one job per ephemeral runner (cannot guarantee for persistent runners)
- Requires automation to provision clean environments

### 3. Just-in-Time (JIT) Runners

Create ephemeral runner configurations via the REST API — no long-lived registration tokens needed.

```bash
# Generate JIT config
curl -X POST https://api.github.com/orgs/<org>/actions/runners/generate-jitconfig \
  -H "Authorization: Bearer <token>" \
  -d '{"name":"jit-runner","runner_group_id":1,"labels":["self-hosted","linux","x64"]}'

# Use the config at startup
./run.sh --jitconfig <encoded_jit_config>
```

- Runner runs one job, then is automatically removed by GitHub
- Use automation to ensure a clean environment per JIT run

### 4. Secrets Management

- Use `GITHUB_TOKEN` with minimum required permissions
- Never store structured data (JSON, XML, YAML) as a single secret
- Register generated secrets with `::add-mask::VALUE` so they're redacted from logs
- Rotate secrets periodically
- Use environment-level required reviewers for sensitive secrets
- Consider OpenID Connect (OIDC) for cloud resource auth instead of long-lived secrets

### 5. Script Injection Mitigation

- Prefer actions over inline scripts when handling user-supplied values
- Use intermediate environment variables for safe untrusted input:

```yaml
- name: Check PR title
  env:
    TITLE: ${{ github.event.pull_request.title }}
  run: |
    if [[ "$TITLE" =~ ^octocat ]]; then
      echo "PR title starts with 'octocat'"
    fi
```

- Avoid `pull_request_target` trigger unless absolutely necessary

### 6. Third-Party Action Security

- Pin actions to a full-length commit SHA (immutable)
- Audit action source code before using it
- Pin to tags only when you trust the verified creator
- Use Dependabot to keep actions updated and receive vulnerability alerts
- Use OpenSSF Scorecards to flag risky practices
- Use dependency review to screen new/changed workflow dependencies

### 7. Workflow-Level Hardening

- Prevent Actions from creating or approving PRs (org/repo setting)
- Use CODEOWNERS to require review on `.github/workflows/` changes
- Enable code scanning (CodeQL) with GitHub Actions scanning
- Audit Actions events via security log and audit log

### 8. Runner Machine Hardening

- Keep sensitive data off the runner machine (SSH keys, API tokens, internal network access)
- Use OIDC instead of long-lived cloud credentials
- Consider clean VM/container per job execution for sensitive workflows
- Review the GitHub Advisory Database (`ecosystem:actions`) for vulnerabilities

## Summary

1. **Never** use self-hosted runners for public repositories
2. **Isolate** runners by group — restrict repo access
3. **Prefer ephemeral/JIT** runners for workloads needing isolation
4. **Pin actions** to commit SHAs, not tags
5. **Use ACCESS_TOKEN** with minimum scopes, not RUNNER_TOKEN with admin scopes
