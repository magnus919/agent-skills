# Jellyfin endpoint catalog for browsing and search

Read-only endpoints a browsing CLI needs. Parameter names are verbatim from the canonical
stable OpenAPI spec (api.jellyfin.org). Casing rule resolved there: **query parameters are
camelCase** (`sortBy`, `sortOrder`, `startIndex`, `includeItemTypes`, `parentId`,
`searchTerm`), while **JSON payload properties are PascalCase in the default profile**
(`Items`, `TotalRecordCount`, `Name`, `Id`, `AccessToken`). Some servers emit camelCase
properties depending on the response profile; treat casing as a compatibility minefield and
normalize client-side.

## Auth posture per endpoint

| Endpoint | Method | Auth |
| --- | --- | --- |
| `/System/Info/Public` | GET | none — pre-auth version probe |
| `/Users/Public` | GET | none — login-screen user list |
| `/System/Info` | GET | any valid token (API key or user token) |
| `/Users` | GET | any valid token; params `isHidden`, `isDisabled` |
| `/Users/Me` | GET | user token; 400 "Token is not owned by a user." with an API key |
| `/Users/AuthenticateByName` | POST | none (but see auth reference: MediaBrowser header mandatory) |
| `/UserViews?userId=` | GET | any token — the per-user library list |
| `/Library/MediaFolders` | GET | **admin-only** (RequiresElevation policy) |
| `/Items` | GET | token; `userId` required unless API-key auth |
| `/Items/Latest` | GET | token; `userId` param |
| `/Items/{itemId}` | GET | token; `userId` optional |
| `/Items/Counts` | GET | token; `userId` optional |
| `/Search/Hints` | GET | token; `searchTerm` required |
| `/Shows/{seriesId}/Seasons` | GET | token; `userId` param |
| `/Shows/{seriesId}/Episodes` | GET | token; `userId` param |
| `/Shows/NextUp` | GET | token; `userId` param |

`GET /Users/{userId}/Items` still routes (legacy twin of `/Items?userId=`); controllers mark
the `/Users/{userId}/Views` route `[Obsolete]`. Prefer `/Items` and `/UserViews` on any
recent server.

## /System/Info and /System/Info/Public

`/System/Info/Public` (no auth) returns `PublicSystemInfo`: `ServerName`, `Id`, `Version`,
`ProductName`. Use it as the cheap pre-flight: learn the version before choosing between
behaviors that differ across server releases. `/System/Info` (token) adds `OperatingSystem`,
`HasUpdateAvailable`, and more; the bundled `info` command calls `/System/Info` plus
`/Users` to count users.

## /UserViews — the user's libraries

`GET /UserViews?userId=<id>` returns a `BaseItemDtoQueryResult` of the libraries (views)
that user can see: `Items[]` with `Id`, `Name`, `CollectionType` (`movies`, `tvshows`,
`music`, ...), `TotalRecordCount`. This is the correct "list my libraries" endpoint for any
token; `/Library/MediaFolders` lists raw library folders but requires an administrator
token (403 Forbidden otherwise) and is not user-scoped.

## /Items — the workhorse query

`GET /Items` declares ~88 query parameters in the stable spec. The core browsing set:

| Param | Meaning |
| --- | --- |
| `userId` | **Required unless authenticating with an API key.** Missing on a user-token request → 400 with body `userId is required`. |
| `parentId` | Localize the query to one folder/view; omit for the root |
| `recursive` | Recurse into subfolders (use with `parentId` to enumerate a whole view) |
| `includeItemTypes` | Comma-delimited item types (see enum below) |
| `excludeItemTypes` | Comma-delimited inverse filter |
| `sortBy` | Comma-delimited sort keys: `SortName`, `DateCreated`, `PremiereDate`, `CommunityRating`, `Random`, `ProductionYear`, `ParentIndexNumber`, `IndexNumber`, ... |
| `sortOrder` | `Ascending` or `Descending` (comma-delimited to match multi-key sorts) |
| `startIndex`, `limit` | Paging window |
| `fields` | Comma-delimited extra fields to populate (see below) |
| `filters` | `IsUnplayed`, `IsPlayed`, `IsFavorite`, `IsResumable`, ... |
| `searchTerm` | Term filter inside `/Items` |
| `isPlayed`, `isFavorite` | Boolean filters |
| `genres`, `years`, `studios`, `artists`, `person`, `tags` | Facet filters |
| `enableTotalRecordCount` | Default true; server may skip computing `TotalRecordCount` when false |

Item type enum (`BaseItemKind`, the values you actually use): `Movie`, `Series`, `Season`,
`Episode`, `BoxSet`, `MusicAlbum`, `MusicArtist`, `Audio`, `Photo`, `PhotoAlbum`, `Book`,
`AudioBook`, `Playlist`, `Trailer`, `Channel`, `Folder`, `UserView`, `Genre`, `Studio`,
`Person`, `Year`. `fields` enum members include `Overview`, `Genres`, `People`, `Path`,
`MediaSources`, `MediaStreams`, `ProviderIds`, `Tags`, `DateCreated`, `ChildCount`,
`RecursiveItemCount`, `PrimaryImageAspectRatio`, `SortName`, `OriginalTitle`, `Etag`.

Response 200 is a `BaseItemDtoQueryResult` OBJECT — always this wrapper:

```json
{ "Items": [ { "Name": "Arrival", "Id": "72c5b8e6-...", "Type": "Movie" } ],
  "TotalRecordCount": 137, "StartIndex": 0 }
```

Error contract: `400` (text body `userId is required`) when `userId` is absent on
non-API-key auth; `404` when a supplied-but-nonexistent `userId` fails lookup (the user
lookup happens before the missing-userId guard, so invalid id ≠ absent id); `401`/`403`
per the auth matrix.

## /Items/Latest — recently added (returns a bare ARRAY)

`GET /Items/Latest` params: `userId`, `parentId`, `fields`, `includeItemTypes`, `isPlayed`,
`enableImages`, `imageTypeLimit`, `enableImageTypes`, `enableUserData`, `limit`
(**default 20**), `groupItems` (**default true** — groups episodes by series and movies by
edition).

**Shape trap: the 200 response is a bare JSON ARRAY of `BaseItemDto` — NOT a
`BaseItemDtoQueryResult` wrapper.** There is no `Items` key, no `TotalRecordCount`, no
`StartIndex`. Clients that unwrap `.Items` unconditionally break here (that is exactly the
shape branch the bundled CLI handles in `cmd_recent`).

Because grouping can merge an entire series into one entry, and the item ids in the array
are per-entry, treat `groupItems=true` results as "what's new", not "how many". Filter by
type server-side with `includeItemTypes` (e.g. `Movie,Series,Episode`); the requested
`limit` then applies to the selected types.

## /Search/Hints — fast fuzzy search

`GET /Search/Hints` requires `searchTerm`; optional `startIndex`, `limit`, `userId`
("search within a user's library or omit to search all"), `includeItemTypes`,
`excludeItemTypes`, `mediaTypes` (`Unknown,Video,Audio,Photo,Book`), `parentId`, and
boolean includes (`includePeople`, `includeMedia`, `includeGenres`, `includeStudios`,
`includeArtists`, all default true).

Response 200:

```json
{ "SearchHints": [ { "Id": "e60d4fa5-...", "ItemId": "e60d4fa5-...", "Name": "Breaking Bad",
                     "Type": "Series", "ProductionYear": 2008, "MatchedTerm": "break",
                     "Series": "..." } ],
  "TotalRecordCount": 3 }
```

SearchHint carries BOTH `Id` and `ItemId` with the same value — `ItemId` is marked
deprecated in the spec; read `Id` and fall back to `ItemId` on old servers. Hints also
surface people/genres/studios as pseudo-results when those includes are on, which `/Items`
does not do; hints honor fewer filters and no `sortBy`.

## TV navigation family

| Endpoint | Params | Response |
| --- | --- | --- |
| `/Shows/{seriesId}/Seasons` | `seriesId` (path, required), `userId`, `fields`, `isSpecialSeason`, `isMissing` | `BaseItemDtoQueryResult` of `Season` items (`IndexNumber` 0 = specials convention) |
| `/Shows/{seriesId}/Episodes` | above plus `season` (int) or `seasonId` (Guid), `startItemId`, `startIndex`, `limit`, `sortBy` (SCALAR here, unlike /Items' comma array) | `BaseItemDtoQueryResult` of `Episode` items |
| `/Shows/NextUp` | `userId`, `startIndex`, `limit`, `fields`, `seriesId`, `parentId`, `nextUpDateCutoff` (ISO date-time), `enableTotalRecordCount`, `enableResumable` (default true), `enableRewatching` (default false) | `BaseItemDtoQueryResult` of `Episode` items |

Prefer `seasonId` (GUID) over numeric `season` — season numbers shift when specials are
inserted. Season-less `/Shows/{seriesId}/Episodes` returns every episode across seasons in
order. `enableRewatching` defaults to false: a fully-watched series never reappears in
NextUp unless opted in.

## /Items/{itemId} and /Items/Counts

`GET /Items/{itemId}?userId=<id>` returns one `BaseItemDto` (~155 properties: `Name`, `Id`,
`Type`, `SeriesId`, `SeasonId`, `SeriesName`, `IndexNumber`, `ParentIndexNumber`,
`RunTimeTicks`, `ProductionYear`, `Overview`, `Genres`, `MediaSources`, `ImageTags`,
`BackdropImageTags`, `UserData`, `ProviderIds`, ...). `userId` is optional — supply it to
get that user's `UserData` (playstate, favorites) embedded. Missing item → 404.

`GET /Items/Counts?userId=<id>` returns the `ItemCounts` object: `MovieCount`,
`SeriesCount`, `EpisodeCount`, `SongCount`, `AlbumCount`, `ArtistCount`, `TrailerCount`,
`BoxSetCount`, `BookCount`, `MusicVideoCount`, `ProgramCount`, `ItemCount`.

## Images (read)

`GET /Items/{itemId}/Images/{imageType}` serves image bytes for `Primary`, `Logo`, `Thumb`,
`Backdrop`, `Banner`, and more. Tunables: `maxWidth`/`maxHeight`, `quality`, `fillWidth`/
`fillHeight`, `tag` (supply the `ImageTags` value from the DTO to get long-lived cacheable
URLs), `format`. A 404 is the documented response when the item simply has no such image —
treat it as normal fallback flow, not an error. Backdrops are indexed:
`BackdropImageTags[i]` pairs with `/Items/{itemId}/Images/Backdrop/{i}`.

## Pagination pattern (that actually works)

`/Items`, `/Shows/*`, and `/Search/Hints` page with `startIndex` + `limit` and report
`TotalRecordCount`. Loop with BOTH guards — counts can go stale mid-scan on a live server:

```python
start, page = 0, 100
while True:
    r = get_items(user_id, parent_id, start_index=start, limit=page)
    items = r.get("Items", [])
    if not items:
        break                      # short/empty page = done, even if count disagrees
    yield from items
    start += len(items)
    if r.get("TotalRecordCount") and start >= r["TotalRecordCount"]:
        break
```

`/Items/Latest` has no pagination at all — it is a single array capped by `limit`.

## Sources

- https://api.jellyfin.org/ — official Jellyfin API reference (ReDoc), version 12.0.0 stable
- https://api.jellyfin.org/openapi/jellyfin-openapi-stable.json — canonical OpenAPI spec (all parameter tables, enums, response schemas, 400/401/403/404/503 blocks)
- https://github.com/jellyfin/jellyfin — server source confirming behavior: `ItemsController.cs` (userId 400/404 ordering, legacy /Users/{userId}/Items), `UserViewsController.cs` (obsolete Views route), `LibraryController.cs` (MediaFolders elevation), `TvShowsController.cs` (NextUp/Seasons/Episodes), `UserLibraryController.cs` (GET /Items/{itemId})
- https://mintlify.wiki/jellyfin/jellyfin/api/authentication/overview — official server docs (logout, /Users/Me semantics)
- https://jmshrv.com/posts/jellyfin-api/ — community walkthrough of the items/search/images surface
