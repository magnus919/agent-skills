# Research log

Date: 2026-11-06. Tool: installed GroktoCrawl CLI. Track: bounded industry/methodology analysis. Question and acceptance boundary: describe the public method, distinguish prescriptions from evidence, compare catalog owners, and preserve a concrete integration proposal. No paid material or private sources sought.

## Search history

| Query | Returned | Disposition |
|---|---|---|
| `StoryBrand official seven part framework website` | 5 | Located S1, S3, S5, S7; ignored third-party summary |
| `site:storybrand.com website header plan call action failure success` | 6 | Located S2, S4; private-workshop training pages excluded from scope |
| `StoryBrand framework effectiveness controlled study evidence criticism` | 6 | Practitioner commentary; no controlled study retrieved; no snippet promoted to evidence |
| `site.nngroup.com concise scannable objective writing web usability study 124` | 3 | Selected original empirical report S6 rather than its summaries |
| `site:storybrand.com "character" "problem" "guide" "plan"` | 3 | Located official PDF alternatives and RSS feed |

Search results were capped; returned results are not the complete web or a systematic literature corpus. GroktoCrawl reported incomplete coverage. These queries support discovery only, not claims of exhaustive absence.

## Retrieval and recovery

1. Initial sandbox request could not resolve the configured GroktoCrawl host. The same CLI worked with network escalation; no server reconfiguration or credential disclosure was needed.
2. S3, S4, S5, S6, S7 were successfully scraped. Read the source content, not only search snippets.
3. Scraping S1 and S2 returned HTTP 502. Downloading both through `groktocrawl download URL -o /tmp/FILE.pdf --extract-text` succeeded. Read extracted text and use printed page/section locators. Visual inspection of the PDFs was not performed; no claim depends on diagrams or page appearance.
4. Scraping `https://storybrand.com/downloads/your-brand-is-not-the-hero.pdf` also failed HTTP 502. Excluded that retrieval; the successfully downloaded S1 carries the same displayed title, without assuming byte identity.
5. Official feed extraction succeeded but was redundant. No claims depend on it.
6. Full extracted copyrighted content was moved to temporary working storage. Durable paraphrased evidence records and text hashes are retained in the repository. This is not an archival reproduction of the sources.

## Source evaluation and extraction ledger

| Source | Decision | Extracted contribution | Durable destination |
|---|---|---|---|
| S1 | Retain | Model components, problem levels, customer/business roles, proof, action/stakes, unsupported efficacy claims | `sources.md` C1–C5; proposed method |
| S2 | Retain | Website recommendations, consistency, rigid-rule limitations | `sources.md` C6–C10; method/template |
| S3 | Retain | Current training framing and unsupported revenue promise | `sources.md` C11; brief |
| S4 | Retain | Cross-channel scope | `sources.md` C12; owner recommendation |
| S5 | Retain | New-edition coverage boundary | `sources.md` C13; brief limitations |
| S6 | Retain | Original usability experiment and transfer limits | `sources.md` C14–C16; validation proposal |
| S7 | Retain | Customer-centered continuity check | `sources.md` C17 |
| Official RSS feed | Exclude | Redundant with S1 and current pages | Exclusion recorded here and in sources |
| Alternate hero PDF | Exclude | Retrieval failed | Failure retained here; no snippet-only claims |
| Practitioner reviews in search | Discovery only | Suggested questions about generic language and scope | Not factual support; draft treats these as failure hypotheses |
| Paid book/course and linked video | Not accessed | Outside public-document scope | Explicit coverage limit |

Citation chain: initial search → official introduction/learning/book/home pages; website query → website PDF and funnel page; adjacent-evidence query → original NN/G report. The official introduction led conceptually to the customer/business role distinction; repository routing inspection determined ownership independently.

## Decisions and stopping boundary

- Preserve attribution while removing vendor vocabulary from the operational draft.
- Prefer extending an existing messaging owner over creating a duplicate skill.
- Do not treat brand identity, market positioning, persuasive narrative and usable page behavior as interchangeable deliverables.
- Stop this pass once the public components and website prescriptions are extracted, current continuity checked, adjacent empirical evidence bounded, and an actionable ownership proposal preserved. Remaining effectiveness questions need real outputs/users or a broader literature review, not more repetition of promotional descriptions.
- Initial research stopped at a placement proposal. The user then authorized an isolated worktree, both skill enrichments, validation, PR, merge and local synchronization. Integration review is recorded separately.

## Verification

- Upstream fetch succeeded; HEAD and origin/main had zero divergence during research.
- Initial research began with a clean working tree. The integration worktree starts from freshly fetched upstream main and copies this research package; original untracked research is preserved until local sync.
- Initial research checks covered links, JSON and whitespace. Integration adds full skill/eval/catalog checks and the existing brand CLI smoke test because templates changed.
- Behavioral quality, conversion impact and release acceptance remain unassessed.

Completion gate: all seven retained sources have dated evidence records; material claims and limitations map to those records; exclusions are explicit; the index links evidence, synthesis and drafts. Research proposal completed within its boundary; the authorized integration is tracked in `integration-review.md`.
