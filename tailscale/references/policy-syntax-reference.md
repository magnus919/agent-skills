# Tailscale Policy Syntax Reference (huJSON)

Headscale uses the same policy file format as Tailscale: huJSON (human JSON — allows
comments and trailing commas). The policy file is loaded from `policy.path` in
config.yaml and reloaded via SIGHUP.

## Structure

The policy file is a single JSON object with these sections:

```json
{
  "acls": [...],           // Legacy ACL rules
  "grants": [...],         // Modern access rules (preferred)
  "tagOwners": {...},      // Who can create tagged nodes
  "autoApprovers": {...},  // Auto-approve routes and exit nodes
  "ssh": [...],            // Tailscale SSH rules
  "nodeAttrs": [...],      // Node attributes
  "groups": {...},         // Named groups
  "hosts": {...},          // Hostname aliases
  "tests": [...],          // Policy test definitions
  "sshTests": [...]        // SSH policy tests
}
```

## Grants (Modern — Preferred)

Grants replace ACLs for new deployments:
```json
{
  "grants": [
    {
      "src": ["alice@"],
      "dst": ["tag:server"],
      "ip": ["*"]
    }
  ]
}
```

- `src`: Source users, tags, or autogroups
- `dst`: Destination users, tags, or autogroups
- `ip`: Port/protocol rules: `["*"]` (all), `["80"]`, `["80,443"]`, `["tcp:22"]`
- `app`: App connector rules
- `via`: Route filtering for cross-subnet access

## ACLs (Legacy)

```json
{
  "acls": [
    {"action": "accept", "src": ["alice@"], "dst": ["tag:server:*"]},
    {"action": "accept", "src": ["tag:server"], "dst": ["tag:db:*"]}
  ]
}
```

- `action`: "accept" (allow) or no default deny
- `src`: Source users/tags
- `dst`: `<tag>:<port>` — destination and port

## TagOwners

```json
{
  "tagOwners": {
    "tag:server": ["alice@"],
    "tag:db": ["alice@", "bob@"],
    "tag:ci": ["autogroup:admin"]
  }
}
```

Only users listed as tagOwners can register nodes with those tags.

## Auto Approvers

Automatically approve subnet routes and exit nodes:
```json
{
  "autoApprovers": {
    "routes": {
      "192.168.0.0/16": ["alice@"],
      "10.0.0.0/8":   ["bob@"]
    },
    "exitNode": ["tag:server"]
  }
}
```

## Autogroups

Built-in dynamic groups:
- `autogroup:internet` — Access to internet via exit nodes (dst only)
- `autogroup:member` — All personal (user-owned, untagged) devices
- `autogroup:tagged` — All tagged (service) devices
- `autogroup:admin` — Admin users

## Tailscale SSH

```json
{
  "ssh": [
    {
      "action": "accept",
      "src": ["alice@"],
      "dst": ["tag:server"],
      "users": ["ubuntu", "root"]
    },
    {
      "action": "check",
      "src": ["autogroup:member"],
      "dst": ["autogroup:member"],
      "users": ["*"]
    }
  ]
}
```

- `action`: "accept" (no check) or "check" (requires key verification)
- `users`: Remote usernames allowed

## Node Attributes

```json
{
  "nodeAttrs": [
    {
      "target": ["tag:gateway"],
      "attr": ["allow-exit-node", "allow-subnet-routing"]
    }
  ]
}
```

## Groups

```json
{
  "groups": {
    "group:engineering": ["alice@", "bob@", "carol@"],
    "group:infra": ["alice@", "dave@"]
  }
}
```

## Tests

```json
{
  "tests": [
    {
      "src": "alice@",
      "accept": ["tag:server:80", "tag:server:443"],
      "deny": ["tag:db:22"]
    }
  ]
}
```

Also `sshTests` for SSH rules.

## Gotchas for Headscale

- **Device posture** is NOT supported
- **IP sets** are NOT supported
- **OIDC groups** cannot be used in ACLs (though OIDC auth works for login)
- **Funnel/Serve** not supported
- **Policy reload**: SIGHUP, not automatic
- **Autogroup:admin**: Not available if no OIDC admin group configured
- Default (no policy file) = allow all traffic between nodes
