# Input Validation And Data Handling

## Make The Decision Now

For every input source, decide its schema, size, encoding, allowed operations, destination context, retention, and failure behavior. Inputs include HTTP parameters, files, headers, URLs, webhooks, queues, environment-derived configuration, imports, prompts, retrieved content, and tool responses.

## Build A Boundary Pipeline

- Parse with a format-specific parser, validate against an allowlist schema before business logic, and reject ambiguous or oversized input.
- Keep data as structured values. Use parameterized interfaces for queries, safe APIs for process execution, constrained file paths, and URL allowlists with network egress controls where relevant.
- Encode output for its actual consumer context. Validation does not make HTML, SQL, shell, templates, logs, or downstream prompts safe by itself.
- Classify and minimize stored data. Apply access controls, encryption choices, retention, deletion, and export rules to the classification and threat model.
- Treat prompts, retrieval results, model output, and tool output as untrusted data. Constrain tool arguments with schemas and validate model-produced values before execution or display.

## Evidence And Verification

Map every source to its validation and sink. Add negative tests for malformed input, injection-shaped values, traversal, unsafe redirects, SSRF targets, dangerous deserialization, content-type mismatch, and output-context encoding. Test that rejected data does not reach a privileged sink or leak through errors and logs.

## Misuse To Avoid

- Blacklists that miss encodings or syntax variants.
- Sanitizing once and reusing a value in a different output context.
- Treating a model or retrieval system as a trusted parser, policy engine, or authorization boundary.

Use OWASP ASVS stable 5.0.0, OWASP Top 10:2025, and relevant OWASP Cheat Sheets as adopted implementation guidance; verify exact controls before citing them.
