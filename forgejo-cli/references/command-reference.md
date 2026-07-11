# Command reference

Global flags: `--agent`, `--user`, `--server URL`, `--json`, `--quiet/-q`, `--verbose/-v`, `--dry-run/-n`, and `--force/--yes/-y`. POST, PUT, PATCH, and DELETE require `--force` unless dry-running.

| Group | Commands | API route |
| --- | --- | --- |
| `issue` | list, show, create, edit, close, reopen, assign, labels, set-labels, add-labels, clear-labels, comments, comment, delete-comment | `/repos/{owner}/{repo}/issues` |
| `pr` | list, show, create, edit, diff, comment, reviews, review, merge | `/repos/{owner}/{repo}/pulls` |
| `repo` | list, show, search, create, edit, delete, branches | `/user/repos`, `/repos`, `/repos/search` |
| `content` | get, create, update, delete | `/repos/{owner}/{repo}/contents/{path}` |
| `label`, `milestone` | list, show, create, edit, delete | matching repository metadata collection |
| `release` | list, show, create, edit, delete, assets, upload | `/repos/{owner}/{repo}/releases` |
| `hook` | list, show, create, edit, delete | `/user/hooks` or `/repos/{owner}/{repo}/hooks` |
| `user` | show, settings, update-settings | `/user`, `/user/settings` |

Comma-separated `--labels`, `--assignees`, and `--events` become JSON arrays. PR merge maps `--style` to Forgejo's `Do` field. Hook create accepts `--url`, `--secret`, `--events`, and `--type`; it builds Forgejo's required nested `config` payload. Release create requires `--tag-name`; its display name is `--name`. Content is base64 in `--content`; update and delete require `--sha`.

## Generic API

`forgejo-cli api --method GET|POST|PUT|PATCH|DELETE --path /api/v1/... [--query KEY=VALUE] [--data JSON | --data-file FILE] [--raw-file FILE] [--upload-file FILE --form KEY=VALUE] [--header KEY=VALUE] [--content-type TYPE]`

Only `/api/v1/` paths are accepted. JSON, raw binary, multipart file/form payloads, and custom headers are supported. Use it for Actions, packages, organizations, teams, admin APIs, notifications, repository permissions, and new endpoints; consult the target server's Swagger document for schemas.
