# Tailscale/Headscale Identity Model

## Personal Nodes vs Tagged Nodes

Tailscale distinguishes two types of nodes, which affects how they're managed in policies:

### Personal Nodes
- Owned by a human user (e.g. `alice@`)
- End-user devices: laptops, phones, workstations
- Managed by a single user
- Can Tailscale SSH into devices (if policy allows)
- Examples: laptop, phone, iPad
- Registration: `tailscale up --login-server <URL>` → web auth → admin approves

### Tagged Nodes
- Owned by tags (e.g. `tag:server`), not a user
- Service/infrastructure nodes: servers, CI runners, database hosts
- Managed by team (any tagOwner can administer)
- **Cannot** Tailscale SSH into personal nodes (by design)
- Land under the special user `tagged-devices` in headscale
- Registration: `tailscale up --login-server <URL> --advertise-tags tag:server`
- Must be authorized via `tagOwners` in policy file

## Registration Methods

### 1. Web Authentication (Interactive)
```
# Client side
tailscale up --login-server https://headscale.example.com
# → Opens browser with auth URL
# → Displays Auth ID

# Admin side
headscale auth register --user alice --auth-id <AUTH_ID>
```

Best for: personal end-user devices, interactive setup.

### 2. Pre-Authenticated Key (Non-Interactive)
```
# Admin creates key
headscale preauthkeys create --user alice --expiration 24h

# Client uses key
tailscale up --login-server https://headscale.example.com --authkey <KEY>
```

Best for: automation, CI/CD, headless servers, ephemeral nodes.

### 3. Tagged Node Registration
```
# Admin creates key for tagged node
headscale preauthkeys create --user alice --tags tag:server

# Client registers with tags
tailscale up --login-server https://headscale.example.com --authkey <KEY>
```

Best for: service nodes that shouldn't be tied to a specific user.

## Key Properties

| Property | Pre-Auth Key | Description |
|---|---|---|
| `--reusable` | No (default) | One-time use. Set to allow multiple nodes with same key. |
| `--expiration` | 1h (default) | Time limit. Use `0` for no expiry. |
| `--ephemeral` | No (default) | Ephemeral nodes are removed from tailnet when they disconnect. |

## User Management

```
headscale users create <name>        Create user
headscale users list                 List all users
headscale users destroy <name>       Delete user (removes their nodes)
headscale users rename <old> <new>   Rename user
headscale users suspend <name>       Suspend user
headscale users restore <name>       Restore suspended user
```
