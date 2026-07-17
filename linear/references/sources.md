# Sources

Accessed 2026-07-17. These official Linear pages are the only external sources used by this skill.

| Source | Establishes |
|---|---|
| https://linear.app/developers/graphql | Endpoint, authentication headers, GraphQL errors, issue identifiers, issue mutations, documents |
| https://linear.app/developers/pagination | Relay cursor pagination and bounded `first` requests |
| https://linear.app/developers/filtering | Server-side filters and relationship filters |
| https://linear.app/developers/rate-limiting | Request and complexity limits, headers, rate-limit errors |
| https://linear.app/developers/deprecations | No API versions, schema deprecation policy, changelog notices |
| https://linear.app/developers/oauth-2-0-authentication | OAuth tokens, scopes, refresh flow, and app actors |
| https://linear.app/developers/agent-interaction | Agent Sessions, activities, and session webhooks |
| https://linear.app/developers/agent-best-practices | Markdown and interaction guidance for agent workflows |

## Schema Re-verification

Linear exposes its public GraphQL schema through Apollo Studio without login. Open the API schema
from the GraphQL documentation, inspect the relevant query, mutation, input, and object fields,
then test the narrow query in the Explorer. Record the exact selection and add or update an offline
CLI contract test. Do not infer field shapes from names or from an older SDK.

For authentication behavior, verify the request header against the GraphQL and OAuth pages. For
pagination or filters, verify both the connection arguments and the relevant filter input type.
For mutation behavior, verify the mutation input and returned payload fields before implementation.

When official documentation and a live schema differ, treat the live public schema as the contract
for field availability and retain the documentation URL plus access date as provenance. If an
official page contains internally conflicting limit values, avoid encoding either value in CLI
behavior and inspect response headers during credentialed operation.

The CLI's offline tests verify parser, safety-gate, and error-handling contracts only. They do not
replace a credentialed workspace smoke test for permissions, workspace-specific names, or returned
resource data.

## Document URLs

The CLI extracts a trailing 12-character slug ID from Linear document URLs as an observed current
Linear URL convention, not an officially documented contract. If URL extraction fails, supply the
document UUID or slug ID instead.
