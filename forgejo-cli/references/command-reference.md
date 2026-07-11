# Command reference

Global flags: `--agent`, `--user`, `--server URL`, `--json`, `--quiet/-q`, `--verbose/-v`, `--dry-run/-n`, and `--force/--yes/-y`. POST, PUT, PATCH, and DELETE require `--force` unless dry-running.

| Group | Commands | API route |
| --- | --- | --- |
| `issue` | list, show, create, edit, close, reopen, assign, labels, comment | `/repos/{owner}/{repo}/issues` |
| `pr` | list, show, create, edit, diff, comment, reviews, review, merge | `/repos/{owner}/{repo}/pulls` |
| `repo` | list, show, search, create, edit, delete, branches | `/user/repos`, `/repos`, `/repos/search` |
| `content` | get, create, update, delete | `/repos/{owner}/{repo}/contents/{path}` |
| `label`, `milestone`, `release` | list, show, create, edit, delete | matching repository metadata collection |
| `hook` | list, show, create, edit, delete | `/user/hooks` or `/repos/{owner}/{repo}/hooks` |
| `user` | show, settings, update-settings | `/user`, `/user/settings` |

Comma-separated `--labels`, `--assignees`, and `--events` become JSON arrays. PR inline comments accept `--commit-id`, `--path`, and `--line`. `user update-settings --data JSON` sends its JSON payload.

## Generic API

`forgejo-cli api --method GET|POST|PUT|PATCH|DELETE --path /api/v1/... [--query KEY=VALUE] [--data JSON | --data-file FILE]`

Only `/api/v1/` paths are accepted. Use it for Actions, packages, organizations, teams, admin APIs, notifications, repository permissions, and new endpoints; consult the target server's Swagger document for schemas.
