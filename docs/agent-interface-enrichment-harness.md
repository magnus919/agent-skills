# Agent interface enrichment: evidence and validation

Checked 2026-10-04. This report records a methodology update, not a claim of
behavioral uplift.

## Hypothesis

When agents choose among many tools or process result sets too large for useful
model context, a task-oriented interface that exposes prerequisites, dependency
ordering and recovery may prevent avoidable wrong calls. Keeping bulk data behind
an authorized artifact handle with schema, count, sample, provenance, completeness,
identity, and retention terms may preserve inspectability and restartability.
These hypotheses require realistic comparative task runs; first-party API
documentation and structural validation cannot establish their effects.

## Current gap and change

The existing tool contract already asked for typed schemas, permissions, error
categories, output bounds and a truncation/retrieval path. Its gap was that it
could be read as a schema-centric description: it did not require discovery to
show readiness prerequisites and dependency order, or specify semantics for a
bulk result stored outside context. The additions route large/changeable catalogs
to evaluated discovery, keep static indexes valid for small catalogs, and define
an adaptable external-result contract. They explicitly separate discovery from
authorization and empty results from denial, unavailable prerequisites, and
partial/failure states.

The template is illustrative, not a production schema. Replace its handle format,
identity guarantees, access policy, expiry and recovery steps with verified target
system behavior. Record exact versus estimated counts and incomplete outcomes;
do not merge cross-source entities by display name alone.

## First-party evidence reviewed

- Anthropic's [tool search documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool) describes discovering deferred definitions by catalog search, retaining selected common tools in context, and returning an empty match set when no tools match. This supports on-demand loading as an option for large catalogs and the need to handle no-match; it does not establish match accuracy or require it for small catalogs.
- Anthropic's [programmatic tool calling documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling) describes calls from sandboxed code, filtering/aggregating intermediate results before final output reaches the model context, and product-specific caller restrictions. It also reports benchmark performance/token results. Those are vendor-reported for its product and named benchmarks; they are not independent evidence for this harness or portable MCP behavior.
- Anthropic's [code execution with MCP article](https://www.anthropic.com/engineering/code-execution-with-mcp) describes a vendor pattern for code-mediated MCP calls and filtering intermediate results. Product implementation requires sandbox controls, resource bounds and runtime authorization; this article is not a universal recipe or independent effectiveness study.
- Anthropic's [MCP connector documentation](https://platform.claude.com/docs/en/agents-and-tools/mcp-connector) describes its own remote MCP tool configuration and names relevant limitations. This is a product-specific example, not a universal MCP-client capability claim.
- The dated [MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) defines paginated tool listing, input/output schemas, structured results, resource links and annotations. The [MCP resources specification](https://modelcontextprotocol.io/specification/2025-11-25/server/resources) documents resource reads/templates. Protocol affordances do not themselves define artifact authorization, persistence, identity matching, completeness or retention.
- [MCP security best practices](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) inform runtime-boundary cautions; user-facing description is not enforcement.
- Sarah Simionescu / Composio's conference talk, [“Dashboards Are Dead”](https://www.youtube.com/watch?v=YiFqcu9YA38), is orientation only. The mockup bug-fix segment (5:16–5:46) and analytics segment (8:06–8:39) prompted questions about planning/discovery and moving analysis over large results. Product demos and early unreleased vendor comparisons are not efficacy evidence and are not used to assert uplift.

The first-party sources and their claim boundaries are recorded in
[`harness-engineering/references/primary-sources.md`](../harness-engineering/references/primary-sources.md#tool-discovery-and-large-results).

## Frozen eval cases and challenge examples

Two cases were added without renaming existing IDs. The assertions below are the
case rubric; review should distinguish *met*, *not met*, and *not shown*. These
examples challenge the rubric and are not execution or behavioral-efficacy data.

### `tool-discovery-dependency-order`

Rubric assertions:

1. Matches the requested task and outcome to relevant capabilities, rather than relying on input schemas alone.
2. Considers the user's authority when surfacing candidate tools.
3. Surfaces connection prerequisites before the dependent operation is called.
4. Surfaces permission prerequisites before the dependent operation is called.
5. States the dependency order or identifier handoff required before export.
6. Distinguishes no matching capability from denied access.
7. Distinguishes denied access from a missing connection or other unavailable prerequisite.
8. Allows the three-tool stable task to use a simple static index instead of requiring runtime search.
9. Places authorization at execution of the final operation and does not treat discovery as permission.
10. Refreshes stale or empty discovery against the authoritative catalog within a bounded policy.
11. Reports or escalates when the required capability remains unavailable after refresh.

**Satisfying example:** “For the 420-integration request, map the support export task to workspace search and snapshot/export capabilities, filtered by the user's allowed workspace and export scope. Check connection state and export permission before dependent calls. Connect the workspace, search, pass the returned workspace ID to `create_snapshot`, then pass the snapshot ID to `export_snapshot`. Report no capability match separately from denied export and from missing connection; do not retry under another tool after denial. On stale-index/no-match, refresh once against the authoritative catalog; if still absent, report unavailable/escalate. Keep the three fixed tools in a static index.” All eleven claims are visible.

**Contradictory near miss:** “Search the catalog by schema, then call export with the workspace name. Treat no-match, denial and missing connection as the same error; if it fails, try each integration's export endpoint. Never refresh stale catalog state; use live search for all tasks.” This conflicts with assertions 1–11: it ignores task fit/authority and prerequisites, omits dependency identifiers, conflates distinct outcomes, evades execution authorization, does not recover from stale/no-match safely, and mandates dynamic discovery for the small case.

**Omitted-evidence example:** “Improve tool discovery so agents find the right tool and add better error handling.” This says nothing observable about prerequisite checks, operation order, error distinctions, the static option, enforcement location, or authoritative bounded refresh; those claims are **not shown**, not passed by implication.

### `bulk-result-artifact-contract`

Rubric assertions:

1. Returns a stable or explicitly expiring artifact handle instead of placing the full bulk result in model context.
2. Keeps the full bulk result outside model context.
3. Reports the artifact schema and version.
4. Reports the item count and whether it is exact or estimated.
5. Reports how the sample was selected.
6. Records the source identity.
7. Records the source revision or snapshot.
8. Records the operation or query identity that produced the artifact.
9. States whether the result is complete, partial, or unknown.
10. Defines source-qualified identity keys and version semantics.
11. Accounts for unmatched source records without silently merging them.
12. Accounts for duplicate source records without silently merging them.
13. Records snapshot or time-window differences that affect cross-source comparison.
14. Defines who can read or share the artifact.
15. Defines artifact expiry.
16. Defines the retention owner.
17. Provides bounded continuation for partial results.
18. Defines recovery after artifact expiry or unavailability.
19. Identifies when recomputation can create a different cohort.
20. Distinguishes a complete empty result from denied access.
21. Distinguishes a complete empty result from a failed prerequisite.
22. Does not treat the returned sample as validation of every artifact row or identity match.

**Satisfying example:** “Store rows outside context and return handle `artifact://job-42`, schema `product-v2` version 2, exact count 90,000, and a first-page sample marked illustrative. Record each source and snapshot ID, time window, query fingerprint and operation ID. Mark complete/partial/unknown and include a bounded cursor; use keys `(source, record_id, version)`, report unmatched and duplicate IDs, preserve mismatched snapshot windows, and leave name-only matches unresolved. Restrict reads to the requesting authorized runtime; set expiry and a retention owner. For partial data, continue by cursor. If the handle expires, reuse the pinned immutable snapshot if supported; otherwise reauthorize, recompute under a new version, and report that the cohort may differ. Return distinct complete-empty, denied and source-unavailable statuses. The sample does not validate every row or match.” All 22 claims are visible.

**Contradictory near miss:** “Put all 90,000 rows inline in model context and also save a CSV at `/tmp/latest.csv`. Join records on display name across snapshots from different weeks, omit schema/version and query identity, report ‘about 90k’ without saying it is estimated, and leave match completeness unclear. Let any worker read it, delete it after one hour without an owner, and claim a rerun is the same cohort. If missing, report no rows.” The explicit inline full result, name-only join, missing expiry owner, claimed same cohort after recomputation, and empty-on-missing behavior are **not met**. Other contract properties not addressed by the example remain **not shown**, not inferred as false.

**Omitted-evidence example:** “Use an expiring file handle and summarize the results for the model.” This may meet the handle portion of assertion 1; schema/version, count certainty, sample method, provenance, completeness, identity, unmatched/duplicate handling, permissions, retention ownership, recovery, empty/error distinction, and sample-validation boundary remain **not shown**.

## Validation and limits

Validation completed for this scoped change:

- `python3 -m json.tool harness-engineering/evals/evals.json` and `python3 -m json.tool harness-engineering/templates/bulk-result-contract.json` parsed both JSON files.
- `python3 scripts/test-eval-validation.py` passed 27 tests.
- `python3 scripts/validate-evals.py` validated all 183 manifests against v1 schema and repository semantics.
- `python3 harness-engineering/scripts/test_contracts.py` passed 24 tests; `python3 harness-engineering/scripts/test_harness.py` passed 17 tests.
- `ruby scripts/validate-skill-quality.rb harness-engineering` reported 0 errors and 0 warnings.
- `git diff --check` passed.

The harness script tests ran before the final edits, which changed only rubric,
documentation and template content; eval validation was rerun after the final
rubric edit.

These checks establish valid files and rubric shape only. They do not establish
that a model follows the guidance, that a router finds tools reliably, or that an
artifact survives permission changes/restarts in any specific runtime. Needed
behavioral cases include realistic small/static and large/changing catalogs;
task match, wrong match and no match; missing connection, denied capability and
recovery; and large result complete/empty, partial, exact/estimated count,
cross-source duplicate/false match, unauthorized access, expiry, and restart.
Compare old and new guidance on frozen cases with model/runtime/tools fixed,
review outputs against this rubric, include a held-out task, and record errors,
abstentions, latency/context cost, and verified task outcomes before claiming
improvement. Do not interpret a synthetic screen or a vendor benchmark as this
harness's behavioral uplift.
