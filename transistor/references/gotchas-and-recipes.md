# Gotchas Field Guide and Worked Recipes

Symptom-first troubleshooting for the Transistor API, followed by end-to-end
recipes. Everything traces to developers.transistor.fm or Transistor's
support pages (fetched live 2026-08-29); independent-implementation
corroboration (the flimzy/transistor Go SDK) is cited where noted.

## Symptom → cause → fix

### `404` on the "current user" call

- **Symptom:** `GET /v1/user` (or `/v1/authorization`) returns 404.
- **Cause:** those routes do not exist. The authenticated-user probe is
  `GET /v1` — root, no suffix.
- **Fix:** `transistor user` (sends `GET /v1`). Older tutorials showing
  `/v1/user` predate the current API surface.

### Writes "succeed" but the episode never appears in the feed

- **Symptom:** episode exists via `GET /v1/episodes/:id`, `status` stays
  `"draft"` even after updates.
- **Cause:** POST /episodes and PATCH /episodes/:id never publish; only
  `PATCH /v1/episodes/:id/publish` changes status. (The docs state this on
  both the create and update pages.)
- **Fix:** `transistor episode-publish --id <EPISODE_ID>`, or the raw call:
  `curl .../v1/episodes/<EPISODE_ID>/publish -X PATCH -d "episode[status]=published"`
  with `x-api-key`.

### Pagination loop re-reads page 1 forever

- **Symptom:** every page of your loop returns the same items.
- **Cause:** wrong param name. There is no `pagination[limit]`, no
  `page[number]`, no `page` — unknown params are ignored. Per-page is
  `pagination[per]` (default 10) and the page number is `pagination[page]`
  (docs' default 0, examples request 1).
- **Fix:** loop on `meta.currentPage < meta.totalPages`, sending
  `pagination[page]=N`; verify with `meta.totalCount` that you captured
  everything. In the bundled CLI: `--page N --per M`.

### `meta.totalCount` disagrees with the number of items

- **Symptom:** `totalCount: 25` but only 10 objects in `data`.
- **Cause:** nothing is wrong — `per` defaults to 10 and the rest are on
  later pages.
- **Fix:** raise `pagination[per]` or walk pages. Compare your accumulated
  item count to `meta.totalCount`, not to `len(data)` of one page.

### Show "counts" fields are missing

- **Symptom:** your script reads `attributes.episodes_count` /
  `subscribers_count` and gets `null`.
- **Cause:** show resources do not carry those fields (an older wrapper's
  display invented them).
- **Fix:** list episodes with `show_id` and read `meta.totalCount`;
  subscribers likewise (`GET /v1/subscribers?show_id=...`).

### The user object has no email

- **Symptom:** you expected `data.attributes.email` from the user probe.
- **Cause:** the `user` resource has `name`, `time_zone`, `image_url`,
  timestamps — no email.
- **Fix:** use `name`/`time_zone`; identify accounts by the dashboard, not
  the API.

### Analytics numbers look "empty"

- **Symptom:** you expected `attributes.totals.downloads.total`; you got an
  array.
- **Cause:** analytics resources return per-day arrays:
  `attributes.downloads = [{"date": ..., "downloads": N}, ...]`.
- **Fix:** sum the array. The bundled CLI exposes `downloads_total` and
  keeps the raw `downloads` array in `--json`.
- **Related:** don't parse the row `date` format — the docs' examples echo
  dates inconsistently (`15-08-2026` vs `08-15-2026`); your requested
  `start_date`/`end_date` (dd-mm-yyyy) define the window, and both are
  required if either is given.

### `429` mid-loop

- **Symptom:** bulk operations fail after ~10 quick calls.
- **Cause:** rate limit is 10 requests / 10 seconds, and the 429 blocks
  access for 10 seconds. No retry headers are documented.
- **Fix:** sleep ≥10 s on 429 and retry; batch what you can
  (`/v1/subscribers/batch` for imports); prefer webhooks
  (`episode_published`) over polling; cache — Transistor explicitly says
  the API is not a website back end.

### `403` on something you can see in the dashboard

- **Symptom:** the key is valid (other calls pass) but one resource 403s.
- **Cause:** role scoping. Keys inherit the user's per-podcast role
  (owner/admin/team member); some operations require owner/admin.
- **Fix:** have a podcast owner/admin run it, or adjust roles in the
  dashboard.

### Signed upload URL suddenly 403s

- **Symptom:** your PUT to the `upload_url` worked in testing, fails now.
- **Cause:** `expires_in` (example: 600 s) elapsed.
- **Fix:** re-run `authorize-upload`, PUT promptly, then attach. The PUT
  must carry `Content-Type` equal to the returned `content_type`.

### Audio attached but `duration` is null / `media_url` empty in feeds

- **Symptom:** episode created with `episode[audio_url]` but processing
  fields look stuck.
- **Cause:** `audio_processing` is true while Transistor processes;
  `processing_failure` carries an error string on failure.
- **Fix:** poll `transistor episode --id <ID> --json` until
  `audio_processing` is false (respecting the rate limit) before
  publishing.

## Recipe: full publish pipeline (CLI)

```bash
export TRANSISTOR_API_KEY="<API_KEY>"

# 1. Verify the key and find the show
transistor shows --json | jq -r '.shows[] | [.id, .title, .slug] | @tsv'

# 2. Local audio? authorize + upload (skippable if you have a URL)
transistor authorize-upload --filename ep12.mp3 --file ./ep12.mp3 --json | jq -r '.audio_url'

# 3. Create the draft with audio attached
EP=$(transistor episode-create --show <SHOW_ID> --title "Ep 12" \
     --audio-url "$(cat /tmp/audio_url)" --json | jq -r '.id')
echo "$EP"   # draft id, type string

# 4. Publish when ready
transistor episode-publish --id "$EP"

# 5. Confirm state and the trackable media URL
transistor episode --id "$EP" --json | jq '{status, media_url, published_at}'
```

Every stage's JSON output feeds the next: `shows` → string `id`;
`authorize-upload` → string `audio_url`; `episode-create` → string `id`;
`episode-publish` → new `status`. Same pipeline raw:

```bash
AUDIO=$(curl -s https://api.transistor.fm/v1/episodes/authorize_upload?filename=ep12.mp3 \
  -H "x-api-key: <API_KEY>" | jq -r '.data.attributes.audio_url')
EP=$(curl -s https://api.transistor.fm/v1/episodes -X POST \
  -H "x-api-key: <API_KEY>" -d "episode[show_id]=<SHOW_ID>" \
  -d "episode[title]=Ep 12" -d "episode[audio_url]=$AUDIO" | jq -r '.data.id')
curl -s "https://api.transistor.fm/v1/episodes/$EP/publish" -X PATCH \
  -H "x-api-key: <API_KEY>" -d "episode[status]=published" | jq '.data.attributes.status'
```

## Recipe: schedule a season in bulk (respect the rate limit)

```bash
# Renumber + schedule episodes for weekly drops; 1 write call each,
# ≥1 s spacing keeps you far under 10 req / 10 s.
i=0
for AUDIO in /media/season3/*.mp3; do
  i=$((i+1))
  URL=$(transistor authorize-upload --filename "$(basename "$AUDIO")" \
        --file "$AUDIO" --json | jq -r '.audio_url')
  EP=$(transistor episode-create --show <SHOW_ID> \
       --title "S3E$i" --season 3 --number "$i" --audio-url "$URL" \
       --json | jq -r '.id')
  transistor episode-publish --id "$EP" --status scheduled \
    --published-at "2026-09-$((7*i)) 09:00:00"
  sleep 1
done
```

`--published-at` is interpreted in the show's time zone; backdating
(publishing "in the past") uses the same fields with status `published`.

## Recipe: weekly downloads report (analytics)

```bash
# Per-show totals for a window (dd-mm-yyyy, both bounds required)
for S in $(transistor shows --json | jq -r '.shows[].id'); do
  transistor analytics --show "$S" \
    --start-date 01-08-2026 --end-date 28-08-2026 --json \
    | jq -r --arg id "$S" '[$id, (.downloads_total|tostring)] | @tsv'
  sleep 1
done

# Per-episode series for a show's recent drops
transistor episodes --show <SHOW_ID> --status published --per 5 --json \
  | jq -r '.episodes[].id' \
  | while read -r EP; do
      transistor episode-analytics --id "$EP" --json \
        | jq -r '[(.episode_id|tostring), (.downloads_total|tostring)] | @tsv'
      sleep 1
    done
```

## Recipe: private-podcast subscriber import

```bash
# Batch import (single call), then verify with a filtered listing
transistor subscriber-batch --show <SHOW_ID> \
  --email "one@example.com" --email "two@example.com" \
  --skip-welcome-email --json | jq '.subscribers'

transistor subscribers --show <SHOW_ID> --json | jq -r '.meta.totalCount'
# Revoke someone: by email...
transistor subscriber-delete --show <SHOW_ID> --email "two@example.com"
# ...or by id
transistor subscriber-delete --id <SUBSCRIBER_ID>
```

Private subscribers each get personal `feed_url`/`subscribe_url` values —
never share one subscriber's feed URL; it identifies them.

## Recipe: webhook instead of polling

```bash
transistor webhook-create --show <SHOW_ID> \
  --event episode_published --url "https://example.com/hooks/transistor"
transistor webhooks --show <SHOW_ID> --json | jq '.webhooks'
transistor webhook-delete --id <WEBHOOK_ID>
```

Events: `episode_created`, `episode_published`, `subscriber_created`,
`subscriber_deleted`. Account-wide cap: 50 webhooks. This is the sanctioned
way to stay current without spending the 10 req / 10 s budget on polling.

## Automation boundaries

- Show creation is not available via the API (dashboard-only). Everything
  else in this guide is API-land: show updates, episode lifecycle,
  subscribers, webhooks, analytics.
- The API is not meant to power a website's back end: pull once, cache,
  and parse the public RSS feed for display pages.

## Sources

- https://developers.transistor.fm/ (authentication, rate limits, all
  endpoint examples) — fetched live 2026-08-29
- https://developers.transistor.fm/#ratelimits (10 req / 10 s, 429 + 10 s
  block, caching/RSS guidance) — fetched live 2026-08-29
- https://developers.transistor.fm/#patch-v1-episodes-id-publish,
  #post-v1-episodes, #patch-v1-episodes-id (lifecycle facts: draft on
  create, publish via separate endpoint, episode[status] enum,
  episode[published_at]) — fetched live 2026-08-29
- https://developers.transistor.fm/#get-v1-episodes-authorize_upload
  (signed upload flow, expires_in example 600, 5GB max) — fetched live 2026-08-29
- https://developers.transistor.fm/#get-v1-analytics-id,
  #get-v1-analytics-id-episodes, #get-v1-analytics-episodes-id
  (dd-mm-yyyy date pair rule; per-day downloads arrays) — fetched live 2026-08-29
- https://developers.transistor.fm/#Show, #Episode, #Subscriber (attribute
  inventory: no counts on shows, no email on users, per-subscriber feed
  URLs) — fetched live 2026-08-29
- https://developers.transistor.fm/#Webhook (event names, 50-webhook cap) —
  fetched live 2026-08-29
- https://support.transistor.fm/en/article/what-automations-are-possible-with-transistor-bi27am/
  (show creation limitation; automation guidance) — fetched live 2026-08-29
- https://mcp.transistor.fm/ (accepted upload formats) — fetched live 2026-08-29
- https://pkg.go.dev/gitlab.com/flimzy/transistor (route/param
  corroboration) — fetched live 2026-08-29
