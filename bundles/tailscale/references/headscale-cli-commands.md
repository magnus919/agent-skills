# Headscale CLI Commands Reference

## `headscale users` — User management

```
headscale users create <username>         Create a new user
headscale users list                      List all users
headscale users destroy <username>        Delete a user
headscale users rename <old> <new>        Rename a user
headscale users suspend <username>        Suspend a user
headscale users restore <username>        Restore a suspended user
```

## `headscale nodes` — Node management

```
headscale nodes list                      List all nodes
headscale nodes list --user <user>        List nodes for a user
headscale nodes list --tags <tag>         List nodes with a tag
headscale nodes register --user <user>    Register a node (interactive)
headscale nodes delete <id>               Delete a node
headscale nodes tag <id> <tag>            Tag a node (e.g. tag:server)
headscale nodes move <id> <user>          Move node to another user
headscale nodes expire <id>               Expire a node (force logout)
headscale nodes rename <id> <name>        Rename a node
```

Output columns: ID, Name, IP, User, Tags, Online, Last Seen, OS, Version

## `headscale routes` — Route management

```
headscale routes list                     List all routes
headscale routes list --node <id>         List routes for a node
headscale routes enable <id>              Enable/approve a route
headscale routes disable <id>             Disable a route
headscale routes delete <id>              Delete a route
```

Route statuses: pending, enabled, disabled

## `headscale preauthkeys` — Pre-authenticated keys

```
headscale preauthkeys create --user <user>       Create a key for a user
headscale preauthkeys create --user <user> --tags tag:server  Create tagged node key
headscale preauthkeys create --user <user> --reusable --expiration 24h
headscale preauthkeys create --user <user> --ephemeral
headscale preauthkeys list --user <user>         List keys for a user
headscale preauthkeys expire <key-prefix>        Expire a key
```

## `headscale apikeys` — API key management

```
headscale apikeys create                  Create API key (prints once, 90d default)
headscale apikeys create --expiration 365d Create with custom expiration
headscale apikeys list                    List API key prefixes
headscale apikeys expire --prefix <pfx>   Expire an API key
```

## `headscale policy` — Policy management

```
headscale policy list                     List available policies (if configured)
headscale policy test <file>              Test policy file for syntax
```

## `headscale configtest` — Validate configuration

```
headscale configtest                      Validate config.yaml syntax
```

## `headscale version` — Version info

```
headscale version                         Show version
headscale version --json                  Show version as JSON
```

## `headscale debug` — Debug and diagnostics

```
headscale debug create-node <key> <name>  Create a debug node
headscale debug metrics                   Show Prometheus metrics
headscale debug pprof                     Start CPU profiling
```
