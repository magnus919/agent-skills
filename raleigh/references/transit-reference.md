# GoRaleigh Transit Reference

GoRaleigh publishes static schedules as a GTFS ZIP archive and realtime updates as GTFS-Realtime Protocol Buffers.

## Static Feed

```text
https://goraleigh.org/gr_gtfs
```

The CLI caches the validated raw ZIP for one day as `gtfs-feed.zip`. A
`gtfs-feed-metadata.json` sidecar records the source URL, retrieval timestamp,
archive size, SHA-256 digest, validation state, discovered tables, and available
`feed_info`. Cached archives are size- and digest-checked and parsed again before
use; invalid or incomplete cache pairs are replaced from the public source.

## Realtime Feeds

| Feed | URL |
|------|-----|
| Alerts | `https://www.goraleighlive.org/gtfsrt/alerts` |
| Trip Updates | `https://www.goraleighlive.org/gtfsrt/trips` |
| Vehicle Positions | `https://www.goraleighlive.org/gtfsrt/vehicles` |

Realtime responses are `application/x-google-protobuf`. The CLI decodes them with the vendored `gtfs_realtime_pb2` descriptor.

## Schedule Logic

`get_schedule_for_route` and `get_arrivals_for_stop` use `calendar` and `calendar_dates` to determine active service IDs for the requested date.

## Notes

- Every realtime command returns an envelope with `feed_timestamp`,
  `staleness_seconds`, and `entities`, including when the entity list is empty.
- Vehicle and trip entities are enriched from matching static route, trip, and
  stop records. Alert `informed_entity` relationships retain their IDs and add
  matching route names, trip headsigns, and stop names.
- Absent realtime entities are treated as missing data, not proof of service status.
- GTFS-Realtime decoding requires `google.protobuf>=6.31.1,<7`; the checked-in binding was generated from the vendored protocol with protoc 31.1.
