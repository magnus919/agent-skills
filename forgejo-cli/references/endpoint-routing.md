# Endpoint routing guide

Use the first-class command when it exposes every field needed by the task. It gives semantic flags, safe path encoding, mutation confirmation, and predictable JSON output.

| Task | Default command | Use `api` instead when |
| --- | --- | --- |
| Issues and comments | `issue` | attachments, reactions, dependencies, time tracking, or a schema field not exposed by flags |
| Pull requests | `pr` | commits/files/statuses, reviewers beyond the basic review call, or version-specific merge fields |
| Repository and files | `repo`, `content` | collaborators, branch/tag protection, keys, mirrors, transfer, archive, or advanced settings |
| Metadata and delivery | `label`, `milestone`, `release`, `hook` | a payload needs fields not represented by the first-class command |
| Account settings | `user` | tokens, notifications, subscriptions, SSH/GPG keys, organizations, teams, or admin operations |
| Actions, packages, projects | `api` | always: these APIs evolve independently and need the live Swagger schema or native package client |

For a generic call, first read the target server's Swagger operation, copy its method and required fields exactly, then dry-run the request. Add `--force` only after reviewing the plan. If the endpoint returns a list, include `--page`, `--limit`, and `--include-response`.
