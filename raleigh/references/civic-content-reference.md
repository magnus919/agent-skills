# RaleighNC.gov Civic Content Reference

RaleighNC.gov exposes public content through a Drupal JSON:API and an RSS feed.

## JSON:API

```text
https://raleighnc.gov/jsonapi
```

The CLI uses an explicit allowlist of public content resource types:

- `node--news`
- `node--event` and `node--event_series`
- `node--project`
- `node--place`
- `node--service` and `node--service_core`
- `node--directory_entry`
- `node--organizational_unit`
- `node--alert`, `node--alert_update`, and `node--status_alert`

Administrative resources, users, webform submissions, and configuration entities are denied.

## Example Endpoint

```text
https://raleighnc.gov/jsonapi/node/news?filter[status]=1&page[limit]=10
```

## RSS Feed

```text
https://raleighnc.gov/rss.xml
```

A lightweight stream for news and updates. Repeated entries with the same RSS
GUID or canonical link are returned once. Use `rss --new-only` to persist seen
identifiers in the local Raleigh cache and return only newly observed entries
on later `--new-only` runs.

## Notes

- The CLI preserves canonical page URLs so users can inspect the source presentation.
- Rendered HTML is treated as content, not executable markup.
- Publication status is requested server-side with `filter[status]=1`; the CLI
  also requires every returned node's status to be the JSON boolean `true` and
  drops missing, false, numeric, or malformed values.
- Text, date, and `--relationship FIELD=ID` filters are applied client-side after
  bounded JSON:API pagination because Raleigh does not expose verified
  server-side contracts for those filters.
