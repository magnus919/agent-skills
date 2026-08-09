# Fireflies API Reference

## Model and Auth

Fireflies exposes GraphQL at `https://api.fireflies.ai/graphql`. Send JSON with `query`, optional
`variables`, and optional `operationName`; authenticate with `Authorization: Bearer <API key>`.
Queries are read-only. Mutations create, update, or delete server-side state.

Use `scripts/fireflies query` and `scripts/fireflies mutation` as the compatibility escape hatch
for every documented current or future operation. The CLI rejects mutations on `query`, queries on
`mutation`, and requires `--confirm` for a non-dry-run generic mutation.

## Documented Families

| Family | Documented operation |
|---|---|
| Meetings | `transcripts`, `transcript`, `deleteTranscript`, `updateMeetingTitle`, `updateMeetingPrivacy`, `updateMeetingState`, `updateMeetingChannel`, `shareMeeting`, `revokeSharedMeetingAccess` |
| Workspace | `user`, `users`, `contacts`, `channels`, `channel`, `user_groups`, `setUserRole` |
| Content | `bites`, `bite`, `createBite`, `apps`, `analytics` |
| Live | `active_meetings`, `live_action_items`, `createLiveActionItem`, `addToLiveMeeting`, `createLiveSoundbite` |
| Automation | `auditEvents`, `rule_executions_by_meeting`, `uploadAudio`, `createUploadUrl`, `confirmUpload` |
| AskFred | `askfred_threads`, `askfred_thread`, `createAskFredThread`, `continueAskFredThread`, `deleteAskFredThread` |

The ergonomic CLI documents use conservative selections. `live add` calls
`createLiveActionItem(input: CreateLiveActionItemInput!)` with `meeting_id` and `prompt` only;
`live add-to` calls `addToLiveMeeting` with the documented flat arguments; `live soundbite` calls
`createLiveSoundbite`. Use the generic `mutation` escape hatch for any operation not represented
by an ergonomic command. Use introspection only through `schema introspect`; availability
depends on the deployment.

## Live-Schema Audit (2026-08-05)

CLI documents were re-validated against live GraphQL introspection on 2026-08-05. The published
docs at docs.fireflies.ai drifted from the live schema in the following ways, which the CLI now
follows (live schema wins):

- `TranscriptsQueryScope` is documented for the `transcripts` query but absent from the live
  schema; `scope` is a plain `String` there.
- `transcripts` organizers/participants require non-null elements (`[String!]`), and the query
  accepts `title`, `organizer_email`, and `participant_email` filters.
- `createBite` names its argument `transcript_Id` (capital I) and `privacies` takes
  `[BitePrivacy!]` (enum: `public`, `team`, `participants`).
- `shareMeeting` input gained `expiry_days` (7, 14, or 30).
- `updateMeetingChannel` (changelog 2.15.0), `addToLiveMeeting`, `createLiveSoundbite`,
  `createUploadUrl`/`confirmUpload`, `setUserRole`, and `askfred_thread` were added as ergonomic
  commands after the audit found them documented but uncovered.

## Pagination and Limits

`transcripts` uses `limit` plus `skip`, with a documented maximum limit of 50. The CLI rejects a
higher value. Bites also support `limit` and `skip`; their list query requires one of `mine`,
`transcript_id`, or `my_team`. Respect plan limits: Free is 50 requests/day, Pro 500/day, and
Business/Enterprise 60/minute. Add to Live is 3 per 20 minutes, meeting sharing is 10/hour, and
`deleteTranscript` is 10/minute.

## Errors and Access

GraphQL errors are returned in `errors` and can include `message`, `code`, `friendly`, and
`extensions.helpUrls`. The CLI preserves that response on stdout in JSON mode and exits 5.
`too_many_requests` can include `retryAfter`; delay before retrying. Audit events and rule execution
logs have Enterprise/admin restrictions. Do not infer the caller's plan or authorization locally.
AskFred mutations require AI credits.

## Primary Sources

See [source-index.md](source-index.md) for dated primary documentation URLs and claim scope.
