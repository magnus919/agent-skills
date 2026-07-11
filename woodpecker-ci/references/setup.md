# Setup and backend selection

## Docker Compose baseline

The official Compose deployment uses a server and one or more agents. The server persists `/var/lib/woodpecker`; a Docker agent needs access to `/var/run/docker.sock` and the agent config directory. Both server and agent must receive the same `WOODPECKER_AGENT_SECRET`. Generate it with `openssl rand -hex 32` and keep it out of Git.

Before starting:

1. Create an OAuth application in the forge.
2. Set the callback URL to the Woodpecker callback documented for the installed major version and public host.
3. Set `WOODPECKER_HOST` to the externally reachable URL, not the container hostname.
4. Set the forge server URL and OAuth client/secret variables.
5. Decide whether registration is open. Prefer `WOODPECKER_OPEN=false` and explicitly grant admin access.
6. Render the Compose model with `docker compose config --quiet`.
7. Start, inspect `docker compose ps`, and read server and agent logs.

Use the included `templates/docker-compose.yml` as a starting point, then pin the exact server and agent image tag together. Do not mix major versions.

## Forgejo and Gitea

Woodpecker has built-in Forgejo and Gitea integrations. Use the provider-specific variables documented for the installed major version:

```text
# Forgejo
WOODPECKER_FORGEJO=true
WOODPECKER_FORGEJO_URL=https://forge.example.com
WOODPECKER_FORGEJO_CLIENT=<oauth-client-id>
WOODPECKER_FORGEJO_SECRET=<oauth-client-secret>

# Gitea
WOODPECKER_GITEA=true
WOODPECKER_GITEA_URL=https://forge.example.com
WOODPECKER_GITEA_CLIENT=<oauth-client-id>
WOODPECKER_GITEA_SECRET=<oauth-client-secret>
```

Do not assume `GITEA` and `FORGEJO` variable names are interchangeable. Confirm the callback URL, OAuth scopes, skip-verification behavior, and provider-specific behavior from the current provider page.

After login, activate the repository in Woodpecker. Activation requires repository administration rights because Woodpecker installs a webhook. Confirm the webhook reaches the server before debugging the workflow file.

## Agent registration

Minimum agent configuration:

```text
WOODPECKER_SERVER=woodpecker-server:9000
WOODPECKER_AGENT_SECRET=<same shared secret as server>
WOODPECKER_MAX_WORKFLOWS=2
```

On first connection, the server registers the agent and returns an identity. Persist the file configured by `WOODPECKER_AGENT_CONFIG_FILE`; otherwise a recreated agent may register again. For manually registered agents, create the agent in the UI under `Settings -> Agents -> Add agent` and provide the generated token as `WOODPECKER_AGENT_SECRET`.

Use labels to route workloads to suitable agents. Check that a workflow's labels match an available agent before diagnosing application failures.

## Backend choice

| Backend | Use when | Main boundary |
|---|---|---|
| Docker | You need isolated container steps on a Docker host | Docker socket and host trust |
| Kubernetes | You need pod scheduling, resource requests, and cluster isolation | RBAC, PVC/storage, namespace and service accounts |
| Local | You control every pipeline author and need host-native execution | No isolation; pipelines can access the agent host/config |

The Docker backend starts each step in a separate container and shares the workspace volume. The Kubernetes backend creates standalone pods and a temporary PVC for pipeline file transfer. The local backend runs commands in the agent's own context and is unsafe for untrusted repositories.

## Remote agents and TLS

Agents connect to the server's gRPC endpoint. For agents outside the private network, use the documented secure gRPC settings for the installed release, validate certificates, and expose only the required port through a firewall. A TCP connection is not proof of a valid agent handshake: check the agent log and UI state.

## Kubernetes essentials

Set the namespace and backend options explicitly. For private images, place pull credentials in Kubernetes Secrets and list them through `WOODPECKER_BACKEND_K8S_PULL_SECRET_NAMES`. Add per-step resource requests and limits. Keep service-account selection from workflow files disabled unless the repository authors are trusted; enabling it can permit privilege escalation within the namespace.

## Source

See `references/source-index.md` for the official installation, forge, agent, Docker, Kubernetes, and server URLs.