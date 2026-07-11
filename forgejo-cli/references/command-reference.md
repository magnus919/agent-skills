# Command reference

Global flags: `--agent`, `--user`, `--server URL`, `--json`, `--quiet/-q`, `--verbose/-v`, `--dry-run/-n`, `--force/--yes/-y`, `--page`, `--limit`, and `--include-response`. POST, PUT, PATCH, and DELETE require `--force` unless dry-running. `--page` and `--limit` are appended as query parameters; `--include-response` wraps live output as `{data, status, headers}` and preserves `link` and `x-total-count`.

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

## First-class command details

- `issue list` and `pr list` default to `--state open`; override it when reviewing closed or all work. `issue close` and `issue reopen` use the same edit endpoint with an explicit state.
- `content --path` preserves directory separators and encodes unsafe characters. Supply base64 data to `--content`, not plain text. Fetch the current file SHA before an update or delete to avoid overwriting a newer version.
- `repo list --owner OWNER` lists that owner's public/visible repositories; without `--owner`, it lists the authenticated user's repositories. `repo create` intentionally requires no owner because it creates under the authenticated user.
- `release upload --file PATH` sends a multipart attachment. `release upload --external-url URL` sends the equivalent form field. They are mutually exclusive.
- `hook` operates on repository hooks when both `--owner` and `--repo` are present, otherwise on the authenticated user's hooks. Hook creation requires `--url`.

## Safe examples

```bash
# See the exact update request before changing a file.
python3 scripts/forgejo-cli --dry-run --json content update \
  --owner acme --repo app --path docs/guide.md --content BASE64 --sha CURRENT_SHA

# Obtain pagination links and a total count from a live list request.
python3 scripts/forgejo-cli --server https://forge.example --page 1 --limit 50 \
  --include-response --json pr list --owner acme --repo app
```

## Generic API

`forgejo-cli api --method GET|POST|PUT|PATCH|DELETE --path /api/v1/... [--query KEY=VALUE] [--data JSON | --data-file FILE] [--raw-file FILE] [--upload-file FILE --form KEY=VALUE] [--header KEY=VALUE] [--content-type TYPE]`

Only `/api/v1/` paths are accepted. JSON, raw binary, multipart file/form payloads, and custom headers are supported. A supplied `Authorization` header is accepted when no token environment variable is set, enabling documented Basic or Bearer authentication; avoid putting credentials in shell history. Use it for Actions, packages, organizations, teams, admin APIs, notifications, repository permissions, and new endpoints; consult the target server's Swagger document for schemas.
