# PeerTube endpoint catalog for CLI clients

The read surface of the PeerTube REST API with exact parameter names, response shapes, and
pagination semantics — everything a CLI needs to list, filter, and page through videos,
channels, accounts, and instance metadata. Base path: `/api/v1` on any instance
(`https://<INSTANCE_HOST>/api/v1`). Sources footer cites the official reference; a few
shapes were additionally confirmed by live anonymous probes (noted inline).

## The one pagination model: start/count offsets

Every collection endpoint uses **offset pagination**: query params `start` (integer >= 0)
and `count` (1–100, **default 15**). There is no `page` parameter anywhere in the current
API — a client sending `page=` silently gets default paging while believing it paginated
(this bit the original bundled CLI). Responses wrap as:

```json
{ "total": 23792, "data": [ /* resource objects */ ] }
```

Loop by advancing `start` by the number of rows received until `start >= total` (or an
empty page). `skipCount=true` on video collections/search omits the `total` computation —
faster, but then you must stop on the first short/empty page. Max `count` per request is
100; a `count` above the allowed range is rejected.

## Videos

| Endpoint | Auth | Notes |
| --- | --- | --- |
| `GET /videos` | anonymous | instance-wide video list; filters below |
| `GET /videos/{id}` | anonymous | full detail; `{id}` accepts **numeric id, UUIDv4, or shortUUID** |
| `GET /videos/{id}/comment-threads` | anonymous | top-level comment threads; `start`, `count`, `sort` in {-createdAt, -totalReplies}; response `{total, totalNotDeletedComments, data}` |

- The comments route is **`/comment-threads`** (hyphenated). `/comments` and
  `/commentthreads` are not the route (probes: `/comments` 400s on current servers; the
  OpenAPI shows `/comment-threads`). A newer `/videos/{id}/comments/{commentId}/replies`
  route (v8.3 changelog) fetches replies, not top-level threads.
- Listing filters (current exact names): `start`, `count`, `sort`, `categoryOneOf`,
  `tagsOneOf`, `tagsAllOf`, `languageOneOf`, `licenceOneOf`, `nsfw`, `nsfwFlagsIncluded`,
  `nsfwFlagsExcluded`, `isLive`, `isLocal`, `host`, `skipCount`, `search`, plus
  admin-only `include`/`privacyOneOf`/`stateOneOf` (>=8.2)/`autoTagOneOf` (>=6.2) and
  file-format filters `hasHLSFiles`/`hasWebVideoFiles`.
- Sort values: `name`, `-duration`, `-createdAt`, `-publishedAt`, `-views`, `-likes`,
  `-comments`, `-trending`, `-hot`, `-best`.
- List-item shape (probe-confirmed field names): `id`, `uuid`, `shortUUID`, `url`, `name`,
  `category{id,label}`, `licence{id,label}`, `language{id,label}`, `privacy{id,label}`,
  `nsfw`, `truncatedDescription`, `duration` (**seconds** — sample `1419` is ~23.6 min),
  `views`, `likes`, `dislikes`, `comments`, `publishedAt`/`originallyPublishedAt`/`createdAt`
  (ISO-8601), `isLocal`, `isLive`, thumbnail/preview `path`s, and actor summaries:
  `account{id,name,displayName,host,url,avatars[]}`,
  `channel{id,name,displayName,host,url,avatars[]}`.
- `account`/`channel` `host` tells you the **origin instance** of a federated video — on a
  search-index result this is how you find where the video actually lives.
- Detail adds full `description`, `files[]`/`streamingPlaylists[]` (resolutions,
  `fileUrl`/`fileDownloadUrl`, `metadataUrl`s), `commentsEnabled`, `downloadEnabled`,
  `trackerUrls`, `support`, `tags`, `scheduledUpdate` for scheduled/live videos.

## Channels and accounts

| Endpoint | Auth | Notes |
| --- | --- | --- |
| `GET /video-channels` | anonymous | **does exist** (current reference): lists the instance's channels, `start`/`count`/`sort`, `{total,data}` |
| `GET /video-channels/{channelHandle}` | anonymous | handle format `my_username` or `my_username@example.com` (`name@host` for remote channels) |
| `GET /video-channels/{channelHandle}/videos` | anonymous | channel's videos, standard video filters + offset pagination |
| `GET /accounts/{name}` | anonymous | account actor; 404 for unknown; `name` accepts `chocobozzz` or `chocobozzz@example.org` |
| `GET /accounts/{name}/videos` | anonymous | account's videos, offset pagination |
| `GET /accounts/{name}/video-channels` | anonymous | an account's channels |
| `GET /search/video-channels` | anonymous | see search-and-discovery.md |

Channel object fields include `name`, `displayName`, `host`, `url`, `avatars`,
`followersCount` (subscribers), `videosCount` — but note the **global** `/video-channels`
list rows additionally observed carrying `videosCount`/`followersCount` per channel in
list responses (probe 2026-08-29). Historical route drift: pre-1.0 `/videos/channels/*`
routes became `/video-channels/*` and `/videos/accounts/{id}/channels` became
`/accounts/{id}/video-channels` (changelog, v1.0.0-beta.4) — ancient wrappers still using
the old shapes will 404.

## Instance metadata (all anonymous, all public)

| Endpoint | Returns |
| --- | --- |
| `GET /config` | public runtime configuration: `client{}`, `defaults{}`, `webadmin{}`, and an `instance{}` block with `name`, `shortDescription`, classifications, customization, avatars/banners |
| `GET /config/about` | `{instance:{name, shortDescription, description, terms, codeOfConduct, hardwareInformation, administrationInformation, maintenanceInformation, businessInformation, languages, categories, banners}}` |
| `GET /server/stats` | instance counters: `totalUsers`, `totalLocalVideos`, `totalLocalVideoViews`, `totalLocalVideoDownloads`, `totalLocalVideoComments`, `totalVideos`, `totalVideoComments`, `totalLocalVideoChannels`, `totalLocalDailyActiveVideoChannels`, `totalLocalVideoChannels`, `totalLocalVideoPlaylists`, moderation/registration counters, activity-processing stats. Public and cached by the server. |
| `GET /nodeinfo/2.0.json` | standard NodeInfo document (software name/version, usage counts) — handy for instance detection |

**Naming trap:** the stats operation is titled "Get instance stats" but the canonical
current path is **`/server/stats`** (there is no `/instance/stats`), while the config
endpoints are **`/config`** and **`/config/about`** (there is no `/instance/config` or
`/instance/about`). Mixed naming is current reality, not a docs bug. A CLI's `server` /
`info` command should compose `/config/about` + `/server/stats` to give name, description,
and user/video/view counts in one screenful.

## My user (OAuth2 required)

| Endpoint | Notes |
| --- | --- |
| `GET /users/me` | identity + preferences: `id`, `username`, `email`, `role{id,label}`, `videoQuota`, `videoQuotaDaily`, `account{}`, `videoChannels[]`, `twoFactorEnabled`, theme/NSFW/p2p preferences, `createdAt`. The current reference sample is rendered as an array; every live server returns a **single user object** — clients should tolerate both. |
| `GET /users/me/videos` | `{total, data}` of your uploads with the standard video-list fields and filters (`start`, `count`, `sort`, privacy/scope filters) |

The `role` block is `{id, label}` (e.g. `{id: 1, label: "User"}`); `videoQuota` is bytes.
Channel rows inside `videoChannels` carry the same `name`/`displayName`/`host` actor shape
used everywhere else.

## Rate limits (all endpoints)

Default server-side limiter: **50 calls per 10 seconds** per IP across `/*` (the token
endpoint is documented at a tighter 15 per 5 minutes in its operation docs; administrators
can customize all values). On exhaustion you get **HTTP 429** with
`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` (Unix timestamp) and
`Retry-After` (seconds). A CLI should read `Retry-After` and back off; aggressive parallel
listing (count=100 × many pages) on a small instance will trip the limiter.

## Error bodies

Errors use RFC7807-style `application/problem+json` documents with `type`, `title`,
`status`, `detail`, and sometimes a `code`. Unknown routes on current servers typically
answer 400 (not the classic 404) with an `error` body — check the body, not just the
status, when a route mysteriously "doesn't exist".

## Sources

- https://docs.joinpeertube.org/api-rest-reference.html (getVideos, getVideo,
  getVideoChannels, getVideoChannel, getVideoChannelVideos, getAccount, getAccountVideos,
  searchChannels, getConfig, getAbout, getInstanceStats, getUserInfo, comment-threads
  operations; Errors and Rate-limits sections)
- https://docs.joinpeertube.org/api/rest-getting-started (pagination/filter basics,
  instance detection via NodeInfo / x-powered-by / og:platform)
- https://docs.joinpeertube.org/CHANGELOG (route renames v1.0.0-beta.4; v8.2 stateOneOf;
  v8.3 comment routes)
- Live anonymous probes on a public instance (list shapes, channel list fields,
  `/config/about`, `/server/stats`, `/comment-threads` vs `/comments` status), 2026-08-29.
