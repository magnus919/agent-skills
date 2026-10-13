# Research log and extraction closure

Date: 2026-10-12. Scope and acceptance were recorded in research-brief.md before
implementation. This is a moderate technical investigation, not a systematic
review of all Unsloth models or an independent performance benchmark.

## Search and citation trail

| Step | Query/retrieval | Result and decision |
|---|---|---|
| 1 | Prior full auto-caption extraction of qxO1l5iY33E; 0–693 seconds | Orientation topics only. No frame/audio fidelity or successful demo execution inferred. |
| 2 | Current local SKILL/references vs transcript topics | Five capability gaps; retained as questions, not facts. |
| 3 | Official llms.txt, links from training/API/Desktop guides | Added MCP, Data Recipes, NVFP4 and decision head export investigation. |
| 4 | GroktoCrawl fast search: site:unsloth.ai decision model FastDecisionModel calibration | Five discovery results; primary URLs followed. No model synthesis call. |
| 5 | GroktoCrawl fast search: site:unsloth.ai Desktop audio music sandbox MCP | Six discovery results; official pages followed. |
| 6 | Web search: original Cloudflare Clef, Desktop music, Blackwell/NVFP4 | Original Clef article and applicable docs; no vendor numeric uplift adopted. |
| 7 | Pinned upstream source b865e895 and notebook87c1e89 | Actual defaults/APIs, exact hash records in source-probes.json. |
| 8 | GroktoCrawl GitHub issue13160 extraction, API pull13176 | Closed report with maintainer explanation; API confirms merged SHA3b0e721. |
| 9 | Original calibration paper1706.04599v2 | Principle of separate calibration assessment; no assumed guarantee for Clef. |

## Source evaluation and preservation

Every retained source R01–R18 appears in source-records.json with URL, date,
extraction, limitations and evidence class. These records support claim-ledger.md
and research-results.md; repository source hashes and pure-data observations are
in source-probes.json. Search/adapter metadata receipts are separately retained
in retrieval-receipts.json. Vendor docs + vendor implementation are correlated;
Cloudflare's architecture account is primary but also vendor-owned. The paper
supports a general measurement distinction, not this application's accuracy.
No numerical credibility score is used to imply independent reproduction.

## Failed/rejected/redundant retrievals

- Default GroktoCrawl endpoint refused connection. Read-only container port
  discovery identified the live service; explicit per-command endpoint used.
  No configuration/service change or credential copying.
- GroktoCrawl scrape of the decision documentation returned BARRIER_DETECTED.
  It was not treated as page content. Web retrieval of the canonical page worked.
- One bounded direct-HTTP batch of 16 official markdown pages returned403 for
  every page. Stopped that path; web canonical URLs supplied the retained sources.
  No challenge bypass or repeated retry loop. Raw docs byte hashes unavailable;
  their provenance is URL + access date, not an immutable release contract.
- Web `.md` retrievals of image/sandbox docs failed; non-.md canonical URLs worked.
- A guessed Cloudflare clef-typed-decisions URL failed; search located the real
  clef-decision-models article. No claim rests on the guessed URL.
- Reddit comments, mirrors, third-party summaries and search snippets were
  discovery-only/redundant. No support or performance conclusion relies on them.
- Entire captions, downloaded source trees and copied third-party articles are
  excluded from the repository. Small paraphrased source records preserve the
  retained findings without weights, private configuration or credentials.

## Decisions and stopping

Enrich the existing named-tool skill with four conditional references, a common
capability record, a conservative offline decision audit, fixtures and evals.
No new sibling skill. Preserve the GPU-tested BF16 text-SFT path. Keep all new
model/API/media/NVFP4 execution stages not run; do not change the known working
host environment merely to reproduce vendor benchmarks.

Stopped discovery once each scoped question had an explicit source/implementation
answer or an unresolved compatibility/runtime boundary. All retained sources are
extracted. Additional model-specific benchmarking is a separate bounded GPU
experiment with a pinned stack and preregistered task metrics.

## Completion gate

- Retained sources: R01–R18 accounted for in source-records.json.
- Material findings/contradictions: claim-ledger.md and research-results.md.
- Reusable procedures: four new Unsloth references and capability template.
- Executable artifact evidence: verification.json after repository checks.
- Unexecuted model/backend paths: explicit stage table in research-results.md.

## Validation execution context

The first artifact sweep in the restricted shell failed local fixture socket binds
and subprocess probes. The permitted rerun passed without code changes. Initial
helper testing caught an overly specific test expectation about finding order;
that expectation was corrected. Focused tests, core regressions, integration,
format/schema/quality, coverage ratchet and catalog/artifact checks passed; see
verification.json. New model-runtime and generated behavioral stages remain not run.
