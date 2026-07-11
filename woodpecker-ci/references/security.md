# Security and trust boundaries

## Assume pipeline code is hostile unless proven otherwise

A repository author controls workflow commands. The backend determines what those commands can reach. Treat every agent as a trust domain and isolate agents by repository trust, network access, credentials, and host capability.

## Docker backend

The Docker agent commonly mounts `/var/run/docker.sock`. A pipeline can often use that socket to control the host daemon, so do not place untrusted pull-request workloads on an agent with sensitive host access. Use dedicated agents, labels, network segmentation, and least-privilege credentials.

## Local backend

The local backend runs directly in the agent's filesystem and user context. Official documentation warns that a malicious pipeline can access agent configuration and the `WOODPECKER_AGENT_SECRET`. Use it only when every pipeline author is trusted and the host is disposable or tightly isolated.

## Pull requests and secrets

Secrets are not exposed to pull requests by default. Keep that default. If a workflow truly needs a secret on pull requests:

- enable the event deliberately;
- restrict the secret to the smallest repository/organization scope;
- restrict it to exact plugin images where possible;
- avoid arbitrary shell access to the secret;
- assume a public repository can exfiltrate it;
- use a short-lived, low-privilege credential.

Woodpecker can mask secrets from its own store, but an external secret fetched by a pipeline may appear in logs.

## Plugins

Plugins are executable images, not declarative configuration. Pin image tags or digests, review the source, restrict which secrets can be passed to them, and avoid privileged plugins unless the agent is dedicated and trusted. Keep deployment credentials out of general-purpose build steps.

## Kubernetes

Keep workflow-controlled ServiceAccount selection disabled unless required. If enabled, it can allow a user with push access to run pods under another ServiceAccount in the namespace. Use namespace isolation, RBAC, network policy, resource limits, non-root settings where compatible, and private registry pull secrets.

## Registration and transport

Use a high-entropy agent secret, separate credentials per environment where supported, and encrypted gRPC for remote agents. Do not expose the agent endpoint broadly. `WOODPECKER_OPEN=false` is the safer default for registration.

## Public configuration audit

Before publishing a workflow or skill, scan for:

- real OAuth client secrets, agent tokens, registry passwords, and private keys;
- internal hostnames, domains, usernames, filesystem paths, or repository names;
- unpinned images used for privileged operations;
- examples that accidentally expose secrets to pull requests.

Use placeholders in templates and state where values come from; do not include real values.