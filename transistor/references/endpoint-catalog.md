# Transistor API Endpoint Catalog

Method-by-method reference for Transistor API v1. Every row matches the
official reference at developers.transistor.fm (fetched live 2026-08-29).
Envelope conventions (`data`/`attributes`/`relationships`/`included[]`),
pagination (`pagination[page]`, `pagination[per]`, `meta.currentPage`,
`meta.totalPages`, `meta.totalCount`), and sparse-fieldset/include[] params
apply everywhere — see [auth-and-basics.md](auth-and-basics.md).

## Root

| Method | Path | Purpose / params |
| --- | --- | --- |
| GET | `/v1` | Authenticated user probe. No params. Returns one `user` resource (`name`, `time_zone`, `image_url`, timestamps; **no email**). Use as the "does my key work" check. |

## Shows

| Method | Path | Purpose / params |
| --- | --- | --- |
| GET | `/v1/shows` | List shows, descending by updated date. Params: `private` (boolean), `query` (title search), `pagination[page]` (default 0), `pagination[per]` (default 10). |
| GET | `/v1/shows/:id` | One show. `:id` accepts the show ID **or slug**. |
| PATCH | `/v1/shows/:id` | Update any of: `show[author]`, `show[category]`, `show[copyright]`, `show[description]`, `show[explicit]`, `show[image_url]`, `show[keywords]`, `show[language]`, `show[owner_email]`, `show[secondary_category]`, `show[show_type]` (`episodic`/`serial`), `show[title]`, `show[time_zone]`, `show[website]`. Category/language/time-zone values are large closed enums — fetch the dashboard values or reuse what GET returns. |

- Show attributes include `title`, `slug`, `description`, `author`,
  `private`, `show_type`, `feed_url`, `time_zone`, `category`,
  `secondary_category`, `language`, `owner_email`, `website`, `explicit`,
  `keywords`, plus per-directory URLs (`apple_podcasts`, `spotify`,
  `overcast`, ...).
- **There are no `episodes_count` or `subscribers_count` attributes** —
  count episodes by listing them (`show_id` filter + `meta.totalCount`).
- **No POST /v1/shows exists**: show creation is not available via the API
  (Transistor support, updated 2026-08: "Show creation is not currently
  available via our API. New shows need to be created in the web app").

## Episodes

| Method | Path | Purpose / params |
| --- | --- | --- |
| GET | `/v1/episodes` | List episodes, ordered by published date. Params: `show_id` (ID or slug), `query`, `status` (`draft`/`scheduled`/`published`), `order` (`asc`/`desc`, default `desc`), `pagination[page]`, `pagination[per]`. |
| GET | `/v1/episodes/:id` | One episode. `include[]=show` supported. `:id` is the Episode ID (slug support not documented here). |
| POST | `/v1/episodes` | Create an episode. Required: `episode[show_id]`. Optional: `episode[title]`, `episode[summary]`, `episode[description]` (HTML allowed), `episode[audio_url]`, `episode[author]`, `episode[season]`, `episode[number]`, `episode[number]` + `episode[increment_number]` (auto next number in season), `episode[type]` (`full`/`trailer`/`bonus`), `episode[image_url]`, `episode[keywords]`, `episode[explicit]`, `episode[alternate_url]`, `episode[video_url]` (video plan), `episode[youtube_url]`, `episode[transcript_text]`, `episode[email_notifications]`. **Always creates a DRAFT** (`status: "draft"`, `published_at: null`) — publishing is a separate endpoint. |
| PATCH | `/v1/episodes/:id` | Update metadata/audio. Accepts the same `episode[...]` fields as create (except `show_id`). **Never changes publishing state** — the docs say so explicitly ("publishing or unpublishing an episode involves a separate endpoint"). |
| PATCH | `/v1/episodes/:id/publish` | Publish / schedule / unpublish. Required: `episode[status]` ∈ `draft`, `scheduled`, `published`. Optional: `episode[published_at]` (show's time zone) to publish in the past, schedule for the future, or backdate. See the publish-lifecycle file for the full recipe. |
| GET | `/v1/episodes/authorize_upload` | Authorize a local audio/video upload (max **5GB**). Required: `filename`. Returns an `audio_upload` resource: signed `upload_url` (HTTP PUT the bytes, header `Content-Type: <content_type>`), `content_type` (e.g. `audio/mpeg`), `expires_in` (example: 600 s), and the post-upload `audio_url` to attach via create/update. Skip entirely if you already have a public URL. |

- Episode attributes: `title`, `status`, `season`, `number`,
  `published_at`, `duration` (seconds), `duration_in_mmss`, `media_url`
  (trackable MP3), `share_url`, `alternate_url`, `slug`, `summary`,
  `description` (+ `formatted_*` variants), `author`, `explicit`,
  `keywords`, `image_url`, `video_url`, `youtube_url`, `embed_html`(+dark),
  `transcript_url`, `transcripts[]`, `audio_processing`,
  `video_processing`, `processing_failure`, `hls_manifest_url`, `type`.
- `audio_processing: true` means Transistor is still processing an upload;
  `processing_failure` carries the error string when processing failed.
- Vendor-documented upload formats (mcp.transistor.fm): .mp3, .m4a, .wav,
  .aif, .aiff, .aifc, .mp4, .mov.

## Analytics

| Method | Path | Purpose / params |
| --- | --- | --- |
| GET | `/v1/analytics/:id` | Show downloads per day. `:id` = Show ID or slug. Default window: last 14 days. |
| GET | `/v1/analytics/:id/episodes` | Per-episode download series for a whole show. `:id` = Show ID or slug. Default window: last 7 days. |
| GET | `/v1/analytics/episodes/:id` | Single episode downloads per day. `:id` = Episode ID or slug. Default window: last 14 days. |

- Date range params on all three: `start_date` and `end_date`, documented
  as **dd-mm-yyyy**; if you supply one you must supply both.
- Analytics resources return a per-day `downloads` **array**
  (`[{"date": ..., "downloads": N}, ...]`) — not a totals object. Sum the
  array yourself (or let the bundled CLI do it: `downloads_total`).
- Doc-format quirk: example responses echo download-row dates
  inconsistently (`15-08-2026` in show analytics vs `08-15-2026` in
  episodes analytics). Never parse the row date format; aggregate the
  numeric `downloads` values keyed by position in your requested window.
- There is no `/v1/shows/:id/analytics` route — analytics paths live under
  `/v1/analytics/...`. Downloads are the only analytics exposed by the API
  (no countries/apps/video stats).

## Subscribers (private podcasts)

| Method | Path | Purpose / params |
| --- | --- | --- |
| GET | `/v1/subscribers` | List a private show's subscribers. Required: `show_id`. Optional: `query`, `activated` (boolean), pagination. |
| GET | `/v1/subscribers/:id` | One subscriber with `email`, `status` (`default`/`subscribed`/`unsubscribed`), per-subscriber `feed_url` and `subscribe_url`, `has_downloads`, `last_notified_at`. |
| POST | `/v1/subscribers` | Add one subscriber. Required: `show_id`, `email`. Optional: `skip_welcome_email` (default false). |
| POST | `/v1/subscribers/batch` | Add many. Required: `show_id`, `emails[]` (repeat the key). Optional: `skip_welcome_email`. Response: array of subscriber resources. |
| PATCH | `/v1/subscribers/:id` | Update. Required: `subscriber[email]`. |
| DELETE | `/v1/subscribers` | Revoke by address. Required: `show_id`, `email`. |
| DELETE | `/v1/subscribers/:id` | Revoke by subscriber ID. |

Subscriber routes are top-level (`/v1/subscribers...`), not nested under
`/v1/shows/:id/`. Each subscriber gets a unique personal feed URL — that is
how Transistor tracks private-listener downloads.

## Webhooks

| Method | Path | Purpose / params |
| --- | --- | --- |
| GET | `/v1/webhooks` | List a show's webhooks. Required: `show_id`. |
| POST | `/v1/webhooks` | Subscribe. Required: `event_name`, `show_id`, `url`. `event_name` ∈ `episode_created`, `episode_published`, `subscriber_created`, `subscriber_deleted`. |
| DELETE | `/v1/webhooks/:id` | Unsubscribe by webhook ID. |

Maximum **50 webhooks per user account** (Webhook resource doc). Webhooks
are the sanctioned alternative to polling given the 10 req / 10 s rate
limit: register `episode_published` and react, instead of re-reading
episode lists.

## Routes that do NOT exist (common wrong guesses)

- `GET /v1/user`, `GET /v1/authorization` — the user probe is `GET /v1`.
- `POST /v1/shows` — show creation is dashboard-only.
- `/v1/shows/:id/analytics`, `/v1/episodes/:id/analytics` (nested) —
  analytics lives at `/v1/analytics/...` paths.
- `/v1/shows/:id/subscribers` — subscribers is top-level with `show_id`.
- Any `pagination[limit]`-style param — per-page is `pagination[per]`.

## Sources

- https://developers.transistor.fm/ — fetched live 2026-08-29 (HTTP 200);
  all endpoint tables above correspond to the reference sections:
  #get-v1, #get-v1-analytics-id, #get-v1-analytics-id-episodes,
  #get-v1-analytics-episodes-id, #get-v1-shows, #get-v1-shows-id,
  #patch-v1-shows-id, #get-v1-episodes, #get-v1-episodes-id,
  #get-v1-episodes-authorize_upload, #post-v1-episodes,
  #patch-v1-episodes-id, #patch-v1-episodes-id-publish,
  #get-v1-subscribers, #get-v1-subscribers-id, #post-v1-subscribers,
  #post-v1-subscribers-batch, #patch-v1-subscribers-id,
  #delete-v1-subscribers, #delete-v1-subscribers-id, #get-v1-webhooks,
  #post-v1-webhooks, #delete-v1-webhooks-id, #Show, #Episode,
  #Subscriber, #ShowAnalytics, #EpisodesAnalytics, #EpisodeAnalytics,
  #AudioUpload, #Webhook
- https://support.transistor.fm/en/article/what-automations-are-possible-with-transistor-bi27am/
  (show-creation limitation, supported automations) — fetched live 2026-08-29
- https://mcp.transistor.fm/ (accepted upload formats; draft-then-publish
  semantics as implemented by Transistor's own tooling) — fetched live 2026-08-29
- https://pkg.go.dev/gitlab.com/flimzy/transistor (independent SDK route
  inventory corroborating the catalog) — fetched live 2026-08-29
