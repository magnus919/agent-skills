# Troubleshooting playbooks

## First classify the boundary

Capture the first error, not the last cascade. Check in order:

1. Forge OAuth/webhook and repository activation
2. Server startup, database, and public URL
3. Agent handshake, labels, backend, and capacity
4. Clone/network/credentials
5. Image pull or backend permissions
6. Workflow syntax/conditions/secrets
7. Application command or test

## Server or login failure

- Inspect server logs from startup through the request.
- Confirm `WOODPECKER_HOST` is the public URL and the OAuth callback matches it exactly.
- Confirm the forge enable flag, forge server URL, client ID, and client secret are for the same provider.
- Check proxy headers, TLS termination, and clock skew.
- Do not edit pipeline YAML until repository activation and login work.

## Agent connected but idle

- Confirm server and agent use the same `WOODPECKER_AGENT_SECRET`.
- Confirm the agent's `WOODPECKER_SERVER` is the gRPC endpoint, not the HTTP UI URL.
- Check agent labels against workflow labels and backend selection.
- Check `WOODPECKER_MAX_WORKFLOWS` and whether all slots are occupied.
- Read agent logs for handshake, registration, image, and backend errors.
- Persist the agent config file so its identity is not regenerated after every restart.

## Clone failure

For errors such as `fatal: could not read Username`:

1. Check repository visibility and forge credentials.
2. Check whether `WOODPECKER_AUTHENTICATE_PUBLIC_REPOS=true` is needed for internal/public repository behavior in the installed release.
3. Prove network reachability from the agent/container. Temporarily use `skip_clone: true` and a diagnostic step with `ping`, `wget`, or equivalent, then pause the container.
4. Enter the exact running container and reproduce the `git init`, `git remote add`, and `git fetch` commands with safe test credentials.
5. Remove the diagnostic pause and restore normal checkout.

Never put credentials in logs or a committed workflow.

## Docker backend failure

- Confirm the agent can access Docker and the socket path is correct.
- On SELinux hosts, use the documented `:z`/`:Z` labeling or an appropriate policy; do not permanently disable SELinux merely to test.
- Check image architecture, registry authentication, disk space, and daemon logs.
- Remember that mounting the Docker socket gives pipeline workloads control over the host Docker daemon.

## Kubernetes backend failure

- Check agent namespace, ServiceAccount, RBAC, PVC/storage class, and pull secrets.
- Verify the temporary workspace PVC can be created and mounted.
- Add per-step CPU/memory requests and limits to distinguish scheduling from application failure.
- If a workflow sets `serviceAccountName`, check whether the agent allows it. Enabling this setting can grant arbitrary namespace permissions to anyone who can push.
- Inspect pod events and the labels Woodpecker adds (`woodpecker-ci.org/repo-id`, `repo-full-name`, `branch`, `task-uuid`, and `step`).

## Workflow and condition surprises

- `when` entries are OR; fields inside one entry are AND.
- A branch filter can match a pull request's target branch. Add `event: push` for push-only behavior.
- A step normally runs only after prior success. Use `status: [failure]` for failure handlers.
- `commands` are shell commands in build steps; plugin/service containers do not use them the same way.
- If a secret appears empty, check its scope, event filter, plugin-image filter, and `$${VAR}` escaping.
- Run `woodpecker-cli lint` before pushing.

## Service readiness

A service hostname resolving only proves DNS/network setup. Add a bounded readiness loop using the service's native probe (`pg_isready`, `mysqladmin ping`, HTTP health endpoint) and fail with a useful message. Avoid unbounded sleeps.

## SELinux symptoms

`permission denied while trying to connect to the Docker daemon socket` on RHEL-like hosts may be an SELinux labeling/policy issue. Check audit logs and use a correctly labeled mount or policy. Permissive mode is a temporary diagnostic only.

## Evidence template

Use `assets/troubleshooting-checklist.md`; preserve the first error, exact image tags, relevant configuration names, and commands run. Redact secret values.