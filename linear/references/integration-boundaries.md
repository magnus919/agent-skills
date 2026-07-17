# Integration Boundaries

| Need | Use |
|---|---|
| A bounded terminal read or carefully confirmed issue mutation | This CLI |
| An interactive tool connection inside an AI client | Linear's native MCP integration |
| A documented operation absent from the focused command surface | `linear raw` with a narrow GraphQL query |
| A multi-user application acting for each user | OAuth 2.0 with user access tokens |
| A workspace agent or service actor | OAuth actor authorization or client credentials, as documented by Linear |
| An agent that receives delegation, mentions, or user follow-ups in Linear | Agent Session and webhook APIs |

This CLI intentionally does not run an OAuth callback server, manage refresh tokens, receive
webhooks, create Agent Sessions, or emit Agent Activities. Those paths require an application
integration with secure token storage, webhook verification, and lifecycle handling.

Agent Session webhooks notify a configured agent when it is mentioned, delegated an issue, or
receives a follow-up prompt. Their receiver must respond within five seconds, and a new session
should send an activity or external URL within ten seconds. These availability requirements do not
fit a one-shot terminal command.

Agent Activities are semantic progress events such as thoughts, actions, elicitation requests,
responses, and errors. They belong to an Agent Session and are validated by Linear. Do not use
ordinary issue comments as a substitute when building an embedded Linear agent integration.

OAuth application integrations should request the smallest documented scope. The documented
`admin` scope is not a default; use it only when the integration truly needs administrative API
access. This terminal CLI receives an already-issued environment credential and never chooses
scopes itself.

For a standalone agent operating Linear from a terminal, prefer this CLI's read commands and its
`--dry-run` plus `--confirm` mutation gate. For an unsupported but documented GraphQL operation,
use `raw` only after confirming the exact field, permissions, target, scope, and rollback path.

Use the GraphQL schema explorer before promoting a repeated raw operation into this CLI. A command
belongs in the focused surface only when it has a recurring agent workflow, a clear safe default,
and a bounded contract. Promotion is complete only when CLI help and routing, SKILL/README command
maps, official source provenance, offline request/failure tests, schema re-verification, and the
repository regression gates all agree. Until then, keep the verified operation behind narrow `raw`.
