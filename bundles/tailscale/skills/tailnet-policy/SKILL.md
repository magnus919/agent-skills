---
name: tailnet-policy
description: Author, test, and deploy Tailscale-compatible huJSON policy files for Headscale tailnets — ACLs, Grants, Tags, Auto Approvers, Tailscale SSH rules. Use when configuring access control, writing policy files, or troubleshooting connectivity issues caused by ACLs.
category: devops
---

# tailnet-policy

## Overview

Headscale uses Tailscale-compatible policy files written in **huJSON** (Human JSON — standard JSON with trailing commas and `//` comments). Policy files control:

- **ACLs** (deprecated legacy syntax) — `{action, users, ports}` rules
- **Grants** (modern syntax) — `{src, dst, ip, proto, via}` rules
- **Tags** — Node identity tags (`tag:dev`, `tag:prod`)
- **TagOwners** — Which users/groups can apply which tags
- **AutoApprovers** — Auto-approval for subnet routers and exit nodes
- **Tailscale SSH** — SSH access rules via `ssh.users` and `ssh.action`

### ACLs vs Grants

| Feature | ACLs (legacy) | Grants (modern) |
|---------|--------------|-----------------|
| Format | `{action: "accept", users: [...], ports: [...]}` | `{src: [...], dst: [...], ip: [...], proto: "tcp"}` |
| Port filtering | Embedded in `ports: ["*:*"]` | Separate `ip` field for ports |
| Protocol filtering | Not supported | `proto` field (`tcp`, `udp`, `icmp`) |
| Destination routing | Not supported | `via` field for relay/exit nodes |
| Status | Deprecated by Tailscale | Current recommended syntax |

Use Grants wherever possible. The `migrate-acls-to-grants.py` script can convert legacy ACL files automatically.

## Policy Location

The policy file path is configured in Headscale's `config.yaml`:

```yaml
policy:
  path: /etc/headscale/policy.hujson
```

After modifying the policy file, reload it on the Headscale server:

```bash
# Reload via SIGHUP
kill -HUP $(pgrep headscale)

# Or use the convenience script
./skills/tailnet-policy/reload-headscale-policy.sh
```

## Writing Policy

### Allow-All (default-open)

```hujson
{
  // Grants that allow all traffic
  "grants": [
    {
      "src": ["autogroup:member"],
      "dst": ["autogroup:member"],
      "ip": ["*:*"]
    }
  ],
  // Tag ownership
  "tagOwners": {
    "tag:dev": ["autogroup:admin"],
    "tag:prod": ["autogroup:admin"]
  }
}
```

### Deny-All (default-closed)

```hujson
{
  "grants": [
    // Only allow ICMP (ping) between all members
    {
      "src": ["autogroup:member"],
      "dst": ["autogroup:member"],
      "ip": ["*"],
      "proto": "icmp"
    }
  ],
  // Specific grants added per-service
  "tagOwners": {
    "tag:monitor": ["autogroup:admin"]
  }
}
```

### Segmented (environments)

```hujson
{
  "grants": [
    // Dev can reach dev
    {
      "src": ["tag:dev"],
      "dst": ["tag:dev"],
      "ip": ["*:*"]
    },
    // Prod can reach prod
    {
      "src": ["tag:prod"],
      "dst": ["tag:prod"],
      "ip": ["*:*"]
    },
    // Admin access to all
    {
      "src": ["autogroup:admin"],
      "dst": ["tag:dev", "tag:prod"],
      "ip": ["*:*"]
    }
  ],
  "tagOwners": {
    "tag:dev": ["autogroup:admin"],
    "tag:prod": ["autogroup:admin"]
  }
}
```

### Tag-Based Patterns

Tags are node-level identifiers set via `tailscale up --advertise-tags=tag:dev`. They decouple policy from user identity.

```hujson
{
  "tagOwners": {
    "tag:ci-runner":  ["autogroup:admin"],
    "tag:database":   ["autogroup:admin"],
    "tag:webserver":  ["autogroup:admin"],
    "tag:monitoring": ["autogroup:admin"]
  },
  "grants": [
    {
      "src": ["tag:monitoring"],
      "dst": ["tag:webserver", "tag:database"],
      "ip": ["*:*"]
    },
    {
      "src": ["tag:webserver"],
      "dst": ["tag:database"],
      "ip": ["tcp:5432"]
    }
  ]
}
```

## Grants Syntax

Grants are the modern policy primitive:

```hujson
{
  "grants": [
    {
      "src": ["tag:source", "user@example.com"],
      "dst": ["tag:destination", "100.64.0.1"],
      "ip": ["*:*"],                    // proto:port — "*:*" means all
      "proto": "tcp",                   // optional protocol filter
      "via": ["tag:exit-node"]          // optional via/routing
    }
  ]
}
```

Fields:
- **`src`** — Source entities (tags, users, autogroups, IPs)
- **`dst`** — Destination entities
- **`ip`** — Protocol and port filter (e.g. `tcp:80`, `udp:53`, `*:*`, `*`)
- **`proto`** — Protocol constraint (`tcp`, `udp`, `icmp`)
- **`via`** — Route through a specific exit node or relay

## Auto Approvers

Auto-approvers let specific users approve subnet routes and exit nodes without manual intervention:

```hujson
{
  "autoApprovers": {
    "routes": {
      "10.0.0.0/8": ["autogroup:admin"],
      "172.16.0.0/12": ["alice@example.com"]
    },
    "exitNode": ["autogroup:admin"]
  }
}
```

- `routes`: Maps CIDR ranges to lists of users who can auto-approve those routes
- `exitNode`: Lists users who can advertise exit nodes

## Autogroups

Autogroups are dynamic groups resolved by Headscale/Tailscale at runtime:

| Autogroup | Description |
|-----------|-------------|
| `autogroup:member` | All tailnet members |
| `autogroup:admin` | Tailnet admins |
| `autogroup:tagged` | All tagged nodes (any node with at least one tag) |
| `autogroup:internet` | The public internet (used for exit node routing) |

## Tailscale SSH Configuration

Tailscale SSH rules are configured via the `ssh` section:

```hujson
{
  "ssh": [
    {
      "action": "accept",         // "accept" or "check"
      "src": ["autogroup:admin"],
      "dst": ["tag:webserver"],
      "users": ["root", "ubuntu"]
    },
    {
      "action": "check",          // "check" requires node-level SSH authorization
      "src": ["autogroup:member"],
      "dst": ["tag:dev"],
      "users": ["*"]
    }
  ]
}
```

- `action`: `"accept"` (allow directly) or `"check"` (require node-level auth)
- `src`: Source users/groups
- `dst`: Destination tags/users
- `users`: Which OS users can be SSH'd into

## Testing Policies

Policy files include test definitions that are validated when loaded:

```hujson
{
  "grants": [...],
  "tests": [
    {
      "src": "alice@example.com",
      "dst": "tag:webserver",
      "ip": ["tcp:443"],
      "action": "accept"  // expected result
    },
    {
      "src": "bob@example.com",
      "dst": "tag:database",
      "ip": ["tcp:22"],
      "action": "drop"    // expected result
    }
  ]
}
```

Validate tests with:

```bash
./skills/tailnet-policy/validate-policy.py --policy policy.hujson
```

## Gotchas

- **Headscale does NOT support device posture** — rules like `devicePosture` or `device:managed` are Tailscale-only
- **Headscale does NOT support IP sets** — `ipSets` and `ipprotocol` are not supported
- **Headscale does NOT support OIDC groups in ACLs** — groups from OIDC claims cannot be used in policy; use `autogroup:admin` and `autogroup:member` instead
- **Tag names must start with `tag:`** and contain only lowercase letters, numbers, and hyphens
- **Policy reload via SIGHUP does not return errors on failure** — always validate before reloading
- **ACL `users` field and Grant `src` field are NOT interchangeable** — grants use `src`/`dst`, legacy ACLs use `users`/`ports`
- **Tests are not enforced at runtime** — they only validate during parsing; a passing test does not guarantee runtime behavior

## Trigger Conditions

This skill is automatically loaded when the user's message contains any of these keywords:

- tailnet policy
- headscale acl
- hujson policy
- tailscale grant
- tagowners
- autoapprovers
- tailscale ssh policy
- policy validation
- migrate acls
- /etc/headscale/policy
- policy.hujson
