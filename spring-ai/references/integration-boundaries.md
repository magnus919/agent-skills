# Integration boundaries

## ChatClient and advisors

Record default and per-call advisors and their order. Parameters that select a conversation or retrieval scope must be supplied from the request’s authenticated boundary. Test that two conversation IDs cannot read one another’s memory, including after restart or persistence migration.

## Retrieval

Authorize the document set before retrieval and again at any tool or action boundary. Record source owner, freshness, empty-result behavior, filtering, and prompt-context limits. Test empty, stale, contradictory, unauthorized, and slow retrieval separately from answer quality.

## Tools and MCP

The model proposes a tool call; application code resolves and executes it. Validate tool identity, argument schema, user authority, side-effect scope, timeout, cancellation, retry/deduplication, and audit fields. For MCP, verify transport, server identity, capabilities, and schema against the installed client and current protocol documentation. Keep secrets and unneeded arguments out of logs.

## Memory

Use an explicit conversation identifier derived from the application boundary. Never use a process-global fallback for multi-user traffic. Include tests for missing IDs, cross-user access, concurrent requests, retention/eviction, and tool-call messages where the selected Spring AI line has known limitations.

## Streaming and partial results

Model a stream as provisional until the terminal completion is observed. Preserve partial text for recovery, but do not persist it as a final answer or execute a consequential action from it without the required validation. Exercise disconnect, cancellation, timeout, provider error, and client backpressure.

## Observability

Spring AI observations cover ChatClient, advisors, models, embeddings, and vector stores. Prompt/completion data is not exported by default; enabling it can expose sensitive data. Keep logging disabled by default, and define redaction, access, retention, and rollback before temporary debugging. Treat conversation IDs and tool names as sensitive high-cardinality context where applicable.
