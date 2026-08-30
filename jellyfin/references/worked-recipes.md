# Jellyfin worked recipes

Multi-step workflows against a real server. Every stage consumes the previous stage's
output; field names and types match the endpoint catalog. Constants: `BASE` =
`http://<host>:8096` (official default port). Wire examples use PascalCase properties; your
client should normalize casing (see the gotchas guide).

## Recipe 1 — Log in, capture identity, list what's new for that user

The full pre-token → token → user-scoped-read sequence:

```
1. (probe) GET /System/Info/Public                      # no auth → ServerName, Version
2. POST /Users/AuthenticateByName
     Authorization: MediaBrowser Client="my-cli", Device="terminal",
                    DeviceId="dev-1", Version="1.0.0"    # COMPLETE header, no Token yet
     {"Username": "alice", "Pw": "secret"}
   → AuthenticationResult
3. USER_ID = .User.Id        TOKEN = .AccessToken        # hyphenated UUID; both strings
4. Subsequent calls:
     Authorization: MediaBrowser Client="my-cli", Device="terminal",
                    DeviceId="dev-1", Version="1.0.0", Token="{TOKEN}"
5. GET /Items/Latest?userId={USER_ID}&limit=20&includeItemTypes=Movie,Series,Episode
   → 200 BARE ARRAY of BaseItemDto (NOT a wrapper)       # shape branch here
```

One-liner with curl + jq:

```bash
AUTH='Authorization: MediaBrowser Client="my-cli", Device="terminal", DeviceId="dev-1", Version="1.0.0"'
res=$(curl -s -X POST -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"Username":"alice","Pw":"secret"}' "$BASE/Users/AuthenticateByName")
user_id=$(jq -r '.User.Id' <<<"$res")
token=$(jq -r '.AccessToken' <<<"$res")
curl -s -H "Authorization: MediaBrowser Token=\"$token\"" \
  "$BASE/Items/Latest?userId=$user_id&limit=20" | jq -r '.[] | .Name'
```

Failure branches: step 2 without the full MediaBrowser header → 400 `Error processing
request.`; wrong password → 401; server restarting → 503 + `Retry-After` (retry).

With the bundled CLI, steps 2–5 collapse to env vars: export `JELLYFIN_URL`,
`JELLYFIN_API_KEY` (or `JELLYFIN_TOKEN`), `JELLYFIN_USER_ID`; then
`scripts/jellyfin recent --json`. Post-login requests carry the token in exactly one
channel — the `Token=` parameter of the MediaBrowser `Authorization` header (verified by
the suite's request-capture test); the legacy `X-Emby-Token` header is not co-sent. The
login path itself is available as `scripts/jellyfin login --username alice` (reads
`JELLYFIN_PASSWORD` interactively or via `--password`/`--password-stdin`), which prints the
captured `user_id`/`access_token` for exporting.

## Recipe 2 — Libraries → paged browse of one collection

```
1. GET /UserViews?userId={USER_ID}          # token-auth
   → {Items: [{Id, Name, CollectionType: "movies"|"tvshows"|..., ...}], TotalRecordCount}
2. VIEW_ID = .Items[] | select(.Name == "Movies") | .Id
3. Page loop (both guards — counts can go stale mid-scan):
     start = 0; PAGE = 100
     loop:
       GET /Items?userId={USER_ID}&parentId={VIEW_ID}&recursive=true
            &includeItemTypes=Movie&sortBy=SortName&sortOrder=Ascending
            &startIndex={start}&limit={PAGE}
       → {Items: [...], TotalRecordCount: N, StartIndex: start}
       emit .Items; start += len(Items)
       stop when len(Items) == 0 OR start >= TotalRecordCount
```

Why `/UserViews` and not `/Library/MediaFolders`: MediaFolders is admin-elevated
(RequiresElevation) — a non-admin token gets 403. UserViews is the per-user library list
for any token.

```bash
scripts/jellyfin libraries --json | jq -r '.libraries[] | [.name, .id] | @tsv'
scripts/jellyfin browse --library-id "$VIEW_ID" --type Movie --limit 100 --start-index 0 --json \
  | jq -r '.items[] | [.name, .year] | @tsv'
```

## Recipe 3 — Search → seasons → episodes walk

```
1. FIND SERIES:
   GET /Search/Hints?searchTerm=breaking&includeItemTypes=Series&limit=20&userId={USER_ID}
   → {SearchHints: [{Id (read .Id; .ItemId is the deprecated twin), Name, Type, ...}]}
   Fuller DTOs alternative:
   GET /Items?userId=..&recursive=true&includeItemTypes=Series&searchTerm=..&fields=Overview
2. SEASONS:
   GET /Shows/{SERIES_ID}/Seasons?userId={USER_ID}&fields=Overview
   → {Items: [{Id, Name, IndexNumber (0 = specials), Type: "Season"}]}
3. EPISODES per season (prefer seasonId over numeric season — numbers shift):
   GET /Shows/{seriesId}/Episodes?userId={USER_ID}&seasonId={SEASON_ID}&sortBy=AiredEpisodeOrder
   → {Items: [{Name, IndexNumber, ParentIndexNumber, UserData.PlayedPercentage, RunTimeTicks}]}
4. Whole-series flat option (skip seasons):
   GET /Shows/{seriesId}/Episodes?userId={USER_ID}&startIndex=0&limit=100
5. NEXT UP for one series:
   GET /Shows/NextUp?userId={USER_ID}&seriesId={SERIES_ID}&limit=10
```

```bash
scripts/jellyfin search --query "breaking bad" --type Series --json | jq -r '.results[0].id'
scripts/jellyfin item --id "$SERIES_ID" --user-id "$USER_ID" --json
scripts/jellyfin next-up --user-id "$USER_ID" --limit 10 --json | jq -r '.items[] | .series'
```

## Recipe 4 — server health → stats → next-up evening plan

```
1. GET /System/Info/Public                              # no auth: is the server up? which version?
2. GET /System/Info                                     # token: OperatingSystem, Version (full)
3. GET /Items/Counts?userId={USER_ID}                   # MovieCount, SeriesCount, EpisodeCount, SongCount
4. GET /Shows/NextUp?userId={USER_ID}&limit=5           # always pass userId (NextUp ≤10.8 crashes without)
   → {Items: [Episode...], TotalRecordCount}
```

```bash
scripts/jellyfin info --json
scripts/jellyfin stats --json | jq -r '.movies, .episodes'
scripts/jellyfin next-up --limit 5 --json
```

## Recipe 5 — find an item id → full details → image URL

```
1. scripts/jellyfin search --query "dune" --type Movie --json → .results[0].id
2. GET /Items/{ITEM_ID}?userId={USER_ID}
   → BaseItemDto: Overview, Genres, CommunityRating, OfficialRating, RunTimeTicks,
     ProductionYear, ImageTags.Primary, BackdropImageTags[], ProviderIds
3. Image URL:
     {BASE}/Items/{ITEM_ID}/Images/Primary?maxWidth=300&tag={ImageTags.Primary}
   # 404 here means "no such image" — fall back to Thumb/Backdrop, not an error
```

`RunTimeTicks` are 100-nanosecond ticks (divide by 600,000,000 for minutes).

## Bundled CLI `--dry-run` and exit-code contract

The CLI's dry-run plans are pinned by its offline test suite (`scripts/test_jellyfin_cli.py`),
so jq keys match tested reality exactly. Every plan carries:

```json
{ "dry_run": true, "path": "/Items/Latest", "params": { "userId": null, "limit": 10 } }
```

- `dry_run` (bool, always true), `path` (string) and `params` (object) appear on every
  command plan; `login` instead emits `path: "/Users/AuthenticateByName"`, `server`,
  `username`, `authorization_header`, and `pre_token_header: true` (its
  `authorization_header` is the complete pre-token MediaBrowser header, no `Token=`
  segment); `info` composes a `requests` array of `{path, params}` steps instead of a
  single `path`/`params` pair.
- `params` mirrors the exact query the live call would send (`userId` is JSON `null`
  when not supplied).

Exit codes: `0` on success (including dry-run previews), `1` on CLI errors (missing
credentials, unreachable server, API 4xx/5xx, missing required `--user-id`), `2` on
argparse misuse such as `--movies --episodes` together or a missing required flag.

## Bundled CLI `--dry-run` and exit-code contract

The CLI's dry-run plans are pinned by its offline test suite (`scripts/test_jellyfin_cli.py`),
so jq keys match tested reality exactly. Every plan carries:

```json
{ "dry_run": true, "path": "/Items/Latest", "params": { "userId": null, "limit": 10 } }
```

- `dry_run` (bool, always true), `path` (string) and `params` (object) appear on every
  command plan; `login` instead emits `path: "/Users/AuthenticateByName"`,
  `server`, `username`, `authorization_header`, and `pre_token_header: true` (its
  `authorization_header` is the complete pre-token MediaBrowser header, no `Token=`
  segment); `info` composes a `requests` array of `{path, params}` steps instead of a
  single `path`/`params` pair.
- `params` mirrors the exact query the live call would send (`userId` is JSON `null`
  when not supplied).

Exit codes: `0` on success (including dry-run previews), `1` on CLI errors (missing
credentials, unreachable server, API 4xx/5xx, missing required `--user-id`), `2` on
argparse misuse such as `--movies --episodes` together or a missing required flag.

## Cross-version-safe baseline (derive your own recipes from these rules)

1. Speak modern auth (`Authorization: MediaBrowser ...`) and put the token in exactly ONE
   channel per request (its `Token=` parameter). Never co-send the legacy `X-Emby-Token`
   header with it — precedence across channels is unspecified; if a legacy-only server
   needs the old header, substitute it there, do not stack channels.
2. Send a complete pre-token header everywhere — zero cost, avoids the 400-on-login trap.
3. Always send explicit `userId` on `/Items*`, `/UserViews`, `/Shows/*`, `/Items/Latest`.
4. Resolve identity once: `USER_ID = AuthenticationResult.User.Id` (fallback `/Users/Me`
   with a user token; NEVER with an API key).
5. Honor 503 + `Retry-After` on any endpoint; never retry 400-class.
6. Probe `GET /System/Info/Public` first; branch on semver (NextUp userId <10.9; legacy
   header availability ≥10.11 config).
7. Branch on shape: wrapper object vs bare array (`/Items/Latest`) vs `SearchHints` key.
8. DeviceId per profile — one token per `(DeviceId, user)` pair; re-login revokes the pair's
   previous token.

## Sources

Endpoint semantics, pagination, and auth sequencing inherit citations from the auth,
endpoint, and gotchas references (all fetched this session):
https://api.jellyfin.org/ ·
https://api.jellyfin.org/openapi/jellyfin-openapi-stable.json ·
https://gist.github.com/nielsvanvelzen/ea047d9028f676185832e51ffaf12a6f ·
https://mintlify.wiki/jellyfin/jellyfin/api/authentication/overview ·
https://kotlin-sdk.jellyfin.org/guide/authentication.html ·
https://github.com/jellyfin/jellyfin (ItemsController.cs, TvShowsController.cs, UserViewsController.cs, LibraryController.cs, SessionManager.cs)
