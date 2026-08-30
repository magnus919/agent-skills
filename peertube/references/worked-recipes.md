# Worked recipes and CLI workflows

Multi-step workflows for the bundled `scripts/peertube` CLI, plus raw curl/jq equivalents.
Every stage's output field names and JSON types are what the next stage consumes — the
pipelines are proven by the CLI's offline test suite. `PEERTUBE_SERVER` must be exported
for all commands (any instance host works; SepiaSearch works too — see below).

```bash
export PEERTUBE_SERVER="https://<INSTANCE_HOST>"   # e.g. https://tilvids.com
```

## CLI command map

| Command | Does | Auth needed |
| --- | --- | --- |
| `server` | instance name + description (`/config/about`) + stats (`/server/stats`) | no |
| `videos` | latest instance videos (`/videos`, offset paging) | no |
| `search --query Q` | **instance-local** search (`/search/videos`, `searchTarget=local`) | no |
| `video --id ID` | full video detail (id, UUID, or shortUUID) | no |
| `comments --id ID` | top-level comment threads (`/comment-threads`) | no |
| `channels` | instance channel list (`/video-channels`) | no |
| `channel --handle H` | one channel's metadata + recent uploads | no |
| `account --name N` | account metadata (`/accounts/{name}`) | no |
| `me` | your profile (`/users/me`) | yes |
| `my-videos` | your uploads (`/users/me/videos`) | yes |
| `login` | OAuth2 password grant → persists token file | yes (credentials) |
| `logout` | revoke token server-side + delete token file | yes (token) |

Global flags: `--json` (machine output), `--dry-run` (print the request plan, zero
network), `--limit N` (page size, max 100), `--offset N` (start offset). All flags work
before or after the subcommand. `--help` and `--dry-run` never require credentials.

## Recipe 1 — browse what's new, then inspect one video

```bash
scripts/peertube videos --limit 5 --json | jq -r '.videos[] | [.name, .uuid, .duration] | @tsv'
UUID=$(scripts/peertube videos --limit 1 --json | jq -r '.videos[0].uuid')
scripts/peertube video --id "$UUID" --json | jq '{name, description, views, likes, url}'
```

`videos` emits `{"total": <number>, "videos": [...each raw video object with uuid/name/
duration/views/publishedAt/channel/account...]}`; `video` emits the raw detail object
(fields include `description`, `files[]`, `commentsEnabled`).

## Recipe 2 — instance-local search, then pull the description

```bash
scripts/peertube search --query "linux" --limit 10 --json | jq -r '.videos[0].uuid'
scripts/peertube search --query "linux" --limit 5 --json \
  | jq -r '.videos[] | select(.language.label == "English") | .name'
# detail for the top hit:
scripts/peertube video --id "$(scripts/peertube search --query linux --limit 1 --json | jq -r '.videos[0].uuid')" --json
```

Search results are the same video-object shape as `videos` (plus nothing missing that the
detail call needs — `uuid` is always present). To search the **whole fediverse** instead of
one instance, point the same CLI at SepiaSearch:

```bash
PEERTUBE_SERVER="https://sepiasearch.org" scripts/peertube search --query "linux" --limit 10
```

## Recipe 3 — channels: find the busy ones, then page their uploads

```bash
scripts/peertube channels --json | jq -r '.channels[] | [.displayName, .name, .host, .videosCount, .followersCount] | @tsv' \
  | sort -t$'\t' -k4,4nr | head
# page through a channel's uploads with offsets (no page param exists):
scripts/peertube channel --handle "framasoft@framatube.org" --limit 100 --offset 0 --json | jq -r '.videos[].name'
scripts/peertube channel --handle "framasoft@framatube.org" --limit 100 --offset 100 --json | jq -c '{returned: (.videos | length), total}'
```

Handles accept `name` (local) or `name@host` (remote). The offset loop is the only
pagination mechanism — stop when `returned` is 0 or `offset >= total`.

## Recipe 4 — log in, check your quota, upload-aware housekeeping, log out

```bash
scripts/peertube login --username "<USERNAME>"          # prompts for password (hidden)
scripts/peertube me --json | jq '{username, role: .role.label, quota_bytes: .videoQuota}'
scripts/peertube my-videos --limit 100 --json | jq -r '.videos[] | [.name, .privacy.label, .duration] | @tsv'
scripts/peertube logout                                  # revokes server-side + deletes local file
```

The token file lands in `~/.config/peertube/token.json` (owner-only permissions;
`PEERTUBE_CONFIG_DIR` overrides the directory for tests). It records the server URL,
access token, refresh token, and absolute `expires_at`; the CLI re-authenticates if the
server changes or the token is expired. `login --dry-run --json` previews the token
request (fields only — no secret values) without network.

## Recipe 5 — instance report card (compose three anonymous endpoints)

```bash
scripts/peertube server --json \
  | jq '{name: .instance.name, description: .instance.shortDescription,
         local_videos: .stats.totalLocalVideos, total_videos: .stats.totalVideos,
         users: .stats.totalUsers, views: .stats.totalLocalVideoViews}'
```

Equivalent raw curl: `/api/v1/config/about` for identity, `/api/v1/server/stats` for the
counters (note: the stats path is `/server/stats`, not `/instance/stats`).

## Recipe 6 — jq processing patterns

```bash
# TSV table of the five most-viewed local videos
scripts/peertube videos --limit 100 --json \
  | jq -r '.videos | sort_by(-.views)[:5][] | [.name, .views, .channel.displayName] | @tsv'

# Count videos per origin host on a search-index-style result set
PEERTUBE_SERVER="https://sepiasearch.org" scripts/peertube search --query "peertube" --limit 100 --json \
  | jq -r '.videos | group_by(.channel.host) | map({host: .[0].channel.host, n: length}) | sort_by(-.n)[] | "\(.n)\t\(.host)"'

# Comments of a video, flattening thread counts
scripts/peertube comments --id "<UUID>" --json | jq '{total, total_not_deleted: .totalNotDeletedComments, threads: (.threads | length)}'

# Verify the request plan before running it live (zero network)
scripts/peertube --dry-run --json search --query "test" | jq '{path, params: (.params | keys)}'
```

`--dry-run` output shape: `{"dry_run": true, "method": "GET", "path": "/api/v1/...",
"params": {...}}` — every plan carries exactly `dry_run`, `method`, `path`, and `params`
(test-pinned in `scripts/test_peertube.py`); composite commands emit a `requests` array of
those same keyed steps, and the `login` plan is a `POST /api/v1/users/token` whose
`form_fields` lists the field NAMES only (never values). One jq pattern audits any
command.

## Raw curl equivalents (auth chain end-to-end)

```bash
BASE="$PEERTUBE_SERVER/api/v1"
CLIENT_ID=$(curl -sS "$BASE/oauth-clients/local" | jq -r .client_id)
# NOTE: production instances mask client_secret ("****...") in this response; if masked,
# obtain the secret as the web client does (served front-end assets) before proceeding.
curl -sS -X POST "$BASE/users/token" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "client_id=$CLIENT_ID" \
  --data-urlencode 'client_secret=<CLIENT_SECRET>' \
  --data-urlencode 'grant_type=password' \
  --data-urlencode 'username=<USERNAME>' \
  --data-urlencode 'password=<PASSWORD>'
ACCESS_TOKEN="<ACCESS_TOKEN>"
curl -sS -H "Authorization: Bearer $ACCESS_TOKEN" "$BASE/users/me"
```

## Sources

- https://docs.joinpeertube.org/api/rest-getting-started (auth chain, pagination basics)
- https://docs.joinpeertube.org/api-rest-reference.html (endpoint parameter tables and
  response shapes referenced per recipe)
- https://sepiasearch.org/api/v1/search/videos (fediverse-wide search base URL)
- Field names/types corroborated by live anonymous probes and the CLI's offline mocked
  tests, 2026-08-29.
