# GraphQL Contract

Endpoint: `https://api.linear.app/graphql`. Send JSON GraphQL requests with `Content-Type:
application/json`. A personal API key is the value of the `Authorization` header. An OAuth access
token is sent in the `Authorization` header with the `Bearer ` prefix.

This CLI supports bounded reads for teams, issues, documents, projects, and cycles, plus
issue-scoped create, update, move, and comment mutations. Use `raw` for a documented operation
outside that surface. Issue reads accept a UUID or shorthand identifier. Document reads accept a
UUID, slug ID, or Linear document URL; slug lookup uses the `documents` filter.

For personal scripts, a personal API key is the simplest authentication method. OAuth is intended
for applications acting on behalf of users; access tokens are sent with the Bearer prefix. This CLI
does not initiate OAuth, store credentials, refresh tokens, or print either supported credential.

Filter input supports equality, inequality, collection membership, comparisons for number/date
fields, and string operators such as `contains` and `startsWith`. Relationship filters can narrow
results by related team, state, assignee, project, or labels. Prefer these filters to client-side
filtering and ask for only fields needed for the task.

All connections use Relay cursor pagination: request `first` and then pass `pageInfo.endCursor` as
`after` while `hasNextPage` is true. The CLI intentionally does not automatically paginate; keep
reads bounded with `--limit`. Use server filters rather than downloading a workspace and filtering
locally.

Check GraphQL's `errors` array even on HTTP 200 because data can be partial. Rate limits and query
complexity are reported in response headers. As accessed on 2026-07-17, the official rate-limit
page contains a conflicting API-key request limit (5,000 in prose and 2,500 in its table); inspect
current headers and documentation rather than hard-coding either value. It also documents API-key
complexity at 3,000,000 points per hour and a 10,000-point maximum for one query.

Linear does not version this GraphQL API. Inspect schema deprecations and the `[API]` changelog
before relying on a field. When a query fails after a schema change, re-run public introspection in
Apollo Studio, update the narrow field selection, and add an offline contract test before release.

Archived records are excluded from paginated responses by default and can be included with
`includeArchived: true` when the connection supports it. Do not add polling loops for updates:
Linear recommends webhooks for applications that need near-real-time changes.
