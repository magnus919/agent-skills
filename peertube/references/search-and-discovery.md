# PeerTube search: instance-local vs the fediverse-wide index

PeerTube search has two distinct scopes, and confusing them is the single most common
mistake clients make. This file pins down exactly what each scope does, what SepiaSearch
is, and which one the bundled CLI performs.

## The two scopes

`GET /api/v1/search/videos` accepts `searchTarget` with exactly two documented values:

| `searchTarget` | Scope | What you get |
| --- | --- | --- |
| `local` | platform/instance search | Results known to the platform you are querying: its own videos plus objects it has discovered/federated from instances it follows. Same behavior as the instance's web UI search box. |
| `search-index` | global/fediverse search | Results served through an **external search index** configured by the instance administrator. The result set is not scoped to objects your instance knows. The reference warns these results come from a third-party service, and the instance may not yet know (have copies of) the returned objects. |

Facts that matter operationally:

- `remote` is **not** a current `searchTarget` value (it appears in old blog posts and
  older wrappers); the current enum is `local` | `search-index`.
- The current reference does not state what happens when `searchTarget` is omitted.
  Observed behavior on a public instance (2026-08-29): omitting it returned local results
  identical to `searchTarget=local`, i.e. **the default scope is the instance's own
  index**, not the fediverse. Do not assume otherwise; if you need the instance's results,
  pass `searchTarget=local` explicitly, and if you want the fediverse, use a search-index
  host (below) rather than an undocumented default.
- `searchTarget=search-index` only works when the administrator has enabled and configured
  an external search index (admin config section "Global search"); instances without one
  cannot serve index results. Errors when the index is unavailable surface as HTTP 500 on
  search endpoints.
- Index results may reference videos your instance has never federated. The official
  recommendation for consuming them: if URI search is enabled, fetch the result's URL into
  your instance first, then use the classic REST endpoint; otherwise fetch from or redirect
  to the **origin instance** (every result carries its origin in `account`/`channel.host`
  and the video `url`).

## SepiaSearch: the fediverse-wide index

[SepiaSearch](https://sepiasearch.org) is Framasoft's public search index for PeerTube: a
separately hosted service that crawls and indexes public PeerTube instances (its front
page advertises ~1,700 sites indexed) and exposes **the same REST API shape** under its own
base URL:

```
GET https://sepiasearch.org/api/v1/search/videos?search=<query>&start=0&count=15
```

Verified live (2026-08-29): the response is the standard `{total, data: [...]}` collection
of PeerTube-shaped video objects (`uuid`, `shortUUID`, `name`, `category`, `language`,
`privacy`, `publishedAt`, `account`, `channel`, `views`, `duration`, plus a `score` field
the instance endpoints do not return). Consequences:

- A client only needs to swap the base host from an instance to `https://sepiasearch.org`
  to get fediverse-wide search — same parameters, same pagination, same parsing.
- There is no documented indexing-latency guarantee; freshly published videos may take an
  unspecified time to appear. Treat indexing lag as variable.
- SepiaSearch is a search service, not a video host: play/upload URLs in results point at
  the origin instances.
- PeerTube administrators may instead configure their own index URL (Framasoft also
  publishes one at `https://search.joinpeertube.org/` built on the same idea); that is what
  `searchTarget=search-index` talks to on such instances. SepiaSearch is simply the
  well-known public instance of this concept.
- SepiaSearch results are not moderated by anyone you are talking to; the official
  documentation explicitly warns the index content is not moderated.

## Search endpoint catalog

| Endpoint | Notes |
| --- | --- |
| `GET /api/v1/search/videos` | required `search`; `searchTarget`, `start`, `count` (1–100, default 15), `sort`, plus video filters below |
| `GET /api/v1/search/video-channels` | required `search`; optional `handles`, `host`, `searchTarget`, `start`, `count`, `sort`; returns 500 if the search index is unavailable |

### Sort values (search + video listing)

`name`, `-duration`, `-createdAt`, `-publishedAt`, `-views`, `-likes`, `-comments`,
`-trending`, `-hot`, `-best`. The last three are relevance/popularity orders computed by
the instance (hot/trending window definitions are instance-side).

### Filter parameters (exact names)

`categoryOneOf`, `licenceOneOf`, `languageOneOf`, `tagsOneOf`, `tagsAllOf`, `nsfw`
(`"true"`/`"false"` string), `nsfwFlagsIncluded`/`nsfwFlagsExcluded`, `isLive`,
`durationMin`/`durationMax` (seconds), `startDate`/`endDate` and
`originallyPublishedStartDate`/`originallyPublishedEndDate` (ISO dates), `host`,
`uuids`, `skipCount` (`true` avoids computing `total`), plus admin-only
`autoTagOneOf` (>=6.2), `include` (bitmask), `privacyOneOf`, `stateOneOf` (>=8.2).
`category` (without `OneOf`) is not the current parameter name — older wrappers using it
silently drop the filter.

## Which scope does the bundled CLI use?

The bundled `scripts/peertube` performs **instance-local search only**: it issues
`GET /search/videos` with `searchTarget=local` against `PEERTUBE_SERVER` and never claims
fediverse-wide coverage. For fediverse-wide search, point the same commands at SepiaSearch
(`PEERTUBE_SERVER=https://sepiasearch.org scripts/peertube search --query ...`) — the CLI
is instance-agnostic by design, and SepiaSearch speaks the same API. The CLI's `search
--help` text states its scope so nobody mistakes local results for the whole fediverse.

## Worked recipes

### Instance-local search, then full video detail

```bash
BASE="https://<INSTANCE_HOST>"
curl -G "$BASE/api/v1/search/videos" \
  --data-urlencode 'search=<QUERY>' \
  --data-urlencode 'searchTarget=local' \
  --data-urlencode 'start=0' --data-urlencode 'count=10'
# data[].uuid / shortUUID / id all work as the {id} path parameter below
curl "$BASE/api/v1/videos/<UUID_OR_SHORTUUID>"
```

### Fediverse-wide search via SepiaSearch

```bash
curl -G 'https://sepiasearch.org/api/v1/search/videos' \
  --data-urlencode 'search=<QUERY>' \
  --data-urlencode 'start=0' --data-urlencode 'count=10'
# follow a result to its origin instance:
#   data[0].url / data[0].channel.host tell you where the video lives
```

### Local search with filters and relevance sort

```bash
curl -G "$BASE/api/v1/search/videos" \
  --data-urlencode 'search=<QUERY>' \
  --data-urlencode 'searchTarget=local' \
  --data-urlencode 'sort=-views' \
  --data-urlencode 'durationMin=300' \
  --data-urlencode 'languageOneOf=en' \
  --data-urlencode 'count=20'
```

## Sources

- https://docs.joinpeertube.org/api-rest-reference.html (searchVideos, searchChannels
  operations: searchTarget enum, parameter tables, third-party-index warning)
- https://docs.joinpeertube.org/use/search (platform search vs global search semantics)
- https://docs.joinpeertube.org/admin/configuration (Global search: external index
  configuration, search.joinpeertube.org, non-moderation warning)
- https://sepiasearch.org/ (what SepiaSearch is; indexed-site count)
- https://sepiasearch.org/api/v1/search/videos?search=peertube&start=0&count=1
  (live response shape, 2026-08-29)
- https://docs.joinpeertube.org/CHANGELOG (version-drift notes)
- Live anonymous probe of a public instance's `/search/videos` with and without
  `searchTarget` (default-scope observation), 2026-08-29.
