# Documented command contracts

Read this when wrapper instructions or runbooks drift from the CLI they describe,
especially when that tool is unavailable in CI. Documentation repeats part of a
command surface; a renamed verb or changed option can leave agents improvising.

## Use the smallest reliable check

If existing tests execute the documented commands with safe fixtures, reuse them.
Otherwise capture a versioned command manifest and validate documented examples
against it offline. This checks the recorded surface, not live compatibility or
successful behavior. These are design recommendations, not a bundled validator.

Keep three operations separate: check docs against the committed manifest; verify
the manifest against the installed version; explicitly refresh the manifest after
review. A refresh can conceal a defect, so first decide whether the docs are wrong,
the CLI changed, or the capture is incomplete. Prefer the parser's exported schema
where available. Help scraping is a tool/version-specific fallback with explicit
unknowns; never silently fill gaps from assumptions.

## Capture grammar, not just verb names

Record executable identity, version, capture provenance and the supported syntax:

| Element | Required detail |
|---|---|
| Command node | Known subcommands; whether a subcommand is required; declared positional slots |
| Option | Exact spellings, value arity, repeatability and permitted positions |
| Scope | Which options propagate to children, and which belong only to one node |
| Token rules | `--` terminator, inline values, short clusters and supported shell dialect |
| Help | Actual help forms at each relevant node; do not assume universal `--help` |
| Coverage | Cited command paths and any unsupported syntax or unknown grammar |

Capture enough of the parent grammar to distinguish an invalid verb from a valid
positional value. A manifest containing only cited paths must not certify unrecorded
paths. Version changes require a fresh live comparison; an offline pass is bounded
to the captured revision.

## Resolve examples without hiding errors

- Parse tokens in the actual parser's order. Options before/after subcommands are
  valid only where that CLI allows them.
- Consume option values by declared arity. A value matching a subcommand name is
  still a value when the option requires it. Model optional and repeated values
  explicitly; do not guess from a token's spelling.
- At a required-subcommand position, reject unknown verbs. Consume a positional
  only where the grammar declares one. Do not stop checking at the first unknown
  word: that would accept the retired verb the check exists to detect.
- Validate all remaining tokens against declared positional/option rules, including
  excess arguments and the `--` boundary. Do not accept every ancestor option at
  every descendant without evidence of propagation.
- Normalize shell line continuations according to the selected dialect before
  tokenization, preserving quoting and literal backslashes. Support multiline
  examples or report them as unsupported; do not silently skip them.
- Mark intentionally invalid examples and placeholders explicitly. Report both
  checked and excluded spans with reasons so extraction omissions remain visible.
- Fail a required check on unknown syntax or report it as unresolved, never as a
  successful validation. Syntax checking does not validate shell expansions,
  credentials, remote effects, business meaning or output compatibility.

## Challenge the checker

Use safe fixtures; do not execute mutation examples merely to lint documentation.
Include a valid subcommand, retired verb, unknown flag, required option value equal
to a verb, missing value, declared positional, excess argument, non-inherited
parent option, multiline quoting and an explicitly invalid example. A retired verb
at a required-subcommand position must fail while a legal positional still passes.
Restore the fixture after mutation testing and record the actual results.

Complete when the cited surface has accounted-for extraction coverage, applicable
checks pass, and unsupported grammar or missing live verification is explicit.
This reference alone supplies no executable checker or behavioral run evidence.
