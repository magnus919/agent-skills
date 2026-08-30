# The Episode Publish Lifecycle (draft → audio → publish)

The single most important behavioral fact of the Transistor API:
**creating an episode never publishes it, and updating an episode never
publishes it.** Publishing, scheduling, and unpublishing travel on their
own dedicated endpoint. Everything below is from the official reference
(developers.transistor.fm, fetched live 2026-08-29).

## States

`attributes.status` is exactly one of:

| Status | Meaning |
| --- | --- |
| `draft` | Not in the RSS feed. New episodes start here (`published_at: null`). |
| `scheduled` | Will publish at `episode[published_at]` (show's time zone). |
| `published` | Live in the RSS feed; `published_at` records the publish time. |

Transistor's own tooling describes the same model ("Episodes are always
created as drafts, and publishing is a separate tool call" — the vendor MCP
server), and the REST docs describe the publish endpoint's purpose as
"Publish a single episode now or in the past, schedule for the future, or
revert to a draft." All three states go through the same endpoint: it is a
setter, not a one-way transition — you can pull a published episode back to
draft, or re-publish a draft later.

## The publish request (exact documented shape)

The endpoint is `PATCH /v1/episodes/:id/publish` — a metadata PATCH to
`/v1/episodes/:id` will **not** publish (the docs say so on the update
endpoint's own page). The episode ID is the URL path parameter; the body
carries the status:

```sh
curl https://api.transistor.fm/v1/episodes/<EPISODE_ID>/publish -X PATCH \
  -H "x-api-key: <API_KEY>" \
  -d "episode[status]=published" \
  -d "fields[episode][]=status"
```

- Required: `episode[status]` ∈ {`draft`, `scheduled`, `published`}.
- Optional: `episode[published_at]` — the publish date/time **in the
  show's time zone**. Combine it with `episode[status]=scheduled` to
  schedule for the future, or with `published` to backdate an episode
  (e.g. importing an archive with historical dates).
- The documented request body is form-encoded bracket keys. The API intro
  says JSON bodies are accepted generally, but the reference publishes no
  JSON equivalent for this action — copy the documented shape above.
- Note what the body does **not** contain: no `id`, no `type`, no JSON:API
  `data` wrapper. This is not a JSON:API resource-identifier request body;
  the resource identity lives in the URL. (The *response*, by contrast, is
  a standard JSON:API document — see below.)

Documented scheduling example (same endpoint):

```sh
curl https://api.transistor.fm/v1/episodes/<EPISODE_ID>/publish -X PATCH \
  -H "x-api-key: <API_KEY>" \
  -d "episode[status]=scheduled" \
  -d "episode[published_at]=2026-09-03 09:00:00"
```

## The publish response

With `fields[episode][]=status` the documented response is:

```json
{
  "data": {
    "id": "<EPISODE_ID>",
    "type": "episode",
    "attributes": {"status": "published"},
    "relationships": {}
  }
}
```

Read success off the response: `data.id` matches the episode you patched,
`data.type` is `"episode"`, and `data.attributes.status` carries the new
state. Without the fieldset you also get `published_at`, `media_url`,
`share_url`, `duration`, and the rest of the episode resource.

## Worked recipe: create → attach audio → publish (CLI)

```bash
export TRANSISTOR_API_KEY="<API_KEY>"

# 1. Create the episode (always a draft). Audio can ride along now:
transistor episode-create --show <SHOW_ID> \
  --title "Episode 12: Roasting" \
  --summary "A primer on roasting coffee" \
  --season 2 --number 4 \
  --audio-url "https://uploads.example.com/ep12.mp3"
# -> {"id": "<EPISODE_ID>", "status": "draft", ...}

# (skip to 3 if you attached audio above)
# 2. Attach audio later via the metadata PATCH — this does NOT publish:
transistor episode-update --id <EPISODE_ID> \
  --audio-url "https://uploads.example.com/ep12.mp3"

# 3. Publish on the dedicated endpoint:
transistor episode-publish --id <EPISODE_ID>
# PATCH /v1/episodes/<EPISODE_ID>/publish with episode[status]=published
```

The bundled CLI guards step 3: if `attributes.media_url` is still empty it
refuses to publish (an audio-less item would go out to every feed reader)
and prints the attach-audio recipe; `--force` overrides. The guard is scoped
to `--status published` (the default) — scheduling intentionally precedes
audio attach, so a `scheduled` publish needs no audio yet — and it performs
one pre-publish `GET /episodes/:id`, which consumes one of the
10-requests-per-10-seconds rate-limit slots: worth counting in bulk
re-publish loops.

## Worked recipe: raw curl

```bash
# 1. Create a draft
curl https://api.transistor.fm/v1/episodes -X POST \
  -H "x-api-key: <API_KEY>" \
  -d "episode[show_id]=<SHOW_ID>" \
  -d "episode[title]=Example episode" \
  -d "episode[audio_url]=https://example.com/audio/episode.mp3"
# -> {"data": {"id": "<EPISODE_ID>", "attributes": {"status": "draft", "published_at": null, ...}}}

# 2. (only if audio was omitted) attach through the ordinary metadata PATCH
curl https://api.transistor.fm/v1/episodes/<EPISODE_ID> -X PATCH \
  -H "x-api-key: <API_KEY>" \
  -d "episode[audio_url]=https://example.com/audio/episode.mp3"

# 3. Publish through the dedicated endpoint
curl https://api.transistor.fm/v1/episodes/<EPISODE_ID>/publish -X PATCH \
  -H "x-api-key: <API_KEY>" \
  -d "episode[status]=published"
# -> {"data": {"id": "<EPISODE_ID>", "type": "episode",
#              "attributes": {"status": "published"}, "relationships": {}}}
```

## Local files: the authorize-upload detour

If the audio exists only on disk (no public URL), insert this before step 1
or 2:

```bash
# 1. Authorize: get a signed upload URL (max 5GB)
transistor authorize-upload --filename Episode1.mp3
# -> {"audio_url": "https://uploads.example.com/ep1.mp3",
#     "upload_url": "https://...r2.cloudflarestorage.com/...",
#     "content_type": "audio/mpeg", "expires_in": 600}

# 2. PUT the file bytes to attributes.upload_url with the returned
#    Content-Type (the CLI does this when you pass --file):
curl -X PUT -H "Content-Type: audio/mpeg" -T /path/to/Episode1.mp3 "<UPLOAD_URL>"

# 3. Attach attributes.audio_url via episode-create/episode-update, then publish.
```

The signed URL expires (`expires_in`, example 600 s) — upload promptly and
only then attach. Accepted formats (vendor-documented): .mp3, .m4a, .wav,
.aif, .aiff, .aifc, .mp4, .mov.

## Gotchas in the lifecycle

- **Publishing is never a side effect.** POST /episodes and PATCH
  /episodes/:id both return `status: "draft"` (or leave it untouched) no
  matter what fields you send. If your episode stays stubbornly draft,
  you are missing the `/publish` endpoint call — that is the bug, not a
  permissions problem.
- **`published_at` vs status.** Setting `episode[published_at]` alone on
  the metadata PATCH does nothing to feed visibility; the publish
  endpoint's `episode[status]` field is what changes state, and
  `published_at` only qualifies *when*.
- **Time zone.** `episode[published_at]` is interpreted in the show's
  configured `time_zone` (a show attribute), not in UTC and not in your
  machine's zone. Check `transistor show --id <SHOW_ID> --json`.
- **Watch processing.** After attaching audio, `audio_processing` is true
  until Transistor finishes; `processing_failure` explains failures.
  Publishing with an unprocessed/failed file pushes silence to subscribers.
- **Unpublish = status draft.** Same endpoint, `episode[status]=draft`;
  the episode drops out of the RSS feed but keeps its id, audio, and
  metadata.
- **Rate budget.** The 10 req / 10 s limit applies to the whole lifecycle;
  a create + audio-attach + publish burst is fine, a loop re-publishing
  50 episodes needs sleeps or webhooks.

## Sources

- https://developers.transistor.fm/#patch-v1-episodes-id-publish
  ("Publish, schedule, or unpublish an episode": required `episode[status]`
  ∈ draft/scheduled/published, optional `episode[published_at]`, publish
  request + response examples) — fetched live 2026-08-29
- https://developers.transistor.fm/#post-v1-episodes ("Create a new draft
  episode... publishing an episode involves a separate endpoint"; response
  with `status: "draft"`, `published_at: null`) — fetched live 2026-08-29
- https://developers.transistor.fm/#patch-v1-episodes-id ("publishing or
  unpublishing an episode involves a separate endpoint") — fetched live 2026-08-29
- https://developers.transistor.fm/#get-v1-episodes-authorize_upload
  (authorize_upload flow, upload_url/content_type/expires_in/audio_url,
  5GB max, PUT requirement) — fetched live 2026-08-29
- https://developers.transistor.fm/#Episode (status values, audio/video
  processing attributes) — fetched live 2026-08-29
- https://mcp.transistor.fm/ ("Episodes are always created as drafts, and
  publishing is a separate tool call"; accepted upload formats) — fetched live 2026-08-29
- https://pkg.go.dev/gitlab.com/flimzy/transistor (PublishEpisode against
  PATCH /v1/episodes/:id/publish — independent implementation corroborating
  the dedicated endpoint) — fetched live 2026-08-29
