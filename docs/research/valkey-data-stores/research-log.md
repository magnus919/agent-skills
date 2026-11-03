# Research log: Valkey-oriented in-memory datastore guidance

## Scope and method

Commissioned by the catalog maintainer on 2026-11-03. Moderate-depth industry/technical documentary research. Start from the Redis video, test its consequential claims against official Valkey/Redis material, and enrich seven existing methodology skills. No runtime datastore validation or population-preference survey was commissioned. The author's stated preference for BSD-licensed Valkey among open-source-oriented users is the editorial orientation; it is not a claimed statistical finding or a claim about business-user preferences.

Use the repository's research-methodology lifecycle: scope, gather, evaluate, analyze, synthesize and preserve. The durable destination is this tracked package plus the focused skill references and case-level assertion challenges. Full retrieval responses were retained locally by the working session; public records preserve source URLs, access dates, content hashes and original paraphrased claim extraction rather than republish entire third-party pages.

## Search history

All searches and page extraction used the configured GroktoCrawl service on 2026-11-03. Search results were discovery only; none were taken as technical authority without reading the linked primary source. Search caps are not claims of exhaustive web coverage.

| Query | Returned | Use |
|---|---:|---|
| site:valkey.io Redis migration BSD persistence transactions streams | 5 | Located migration, persistence and introduction pages |
| Valkey Redis AGPL BSD open source community preference Fedora Debian 2025 | 5 | Followed Fedora's actual change record; excluded generic comparison blogs |
| AGPL controversial corporate policy Google open source license policy | 5 | Followed Google's own policy and counterbalanced with GNU's rationale |
| site.valkey.io JSON search vector migration Redis compatibility | 5 | Followed official Valkey-search announcement; excluded third-party parity claims |
| site:valkey.io Redis AGPL 2025 license community trust | 5 | Followed current history and named Harbor adoption account; excluded aggregator sentiment as a prevalence measure |

| site:valkey.io Lua runtime error rollback writes | 5 | Additional source-gap check; existing Lua/transaction evidence retained, no search snippet promoted to authority |

## Evaluation and extraction ledger

The machine-readable [source ledger](sources.json) records every attempted scrape, its disposition, response hash and independently reusable claim IDs. Sources are authoritative for their own documented behavior or stated rationale; vendor/project advocacy is not independent proof of comparative performance, universal preference or future governance outcomes. Source review covered material relevant to the research question; historical trivia, promotional claims, navigation, duplicated extraction spans and unrequested operational recipes were excluded.

| Source | Disposition | Extracted claim IDs |
|---|---|---|
| [valkey-history](https://valkey.io/about/) | excluded | Initial /about/ retrieval failed with an adapter error; replaced by successful /topics/history/ retrieval. |
| [valkey-intro](https://valkey.io/topics/introduction/) | retained | valkey-intro-1, valkey-intro-2, valkey-intro-3 |
| [valkey-migration](https://valkey.io/topics/migration/) | retained | valkey-migration-1, valkey-migration-2, valkey-migration-3, valkey-migration-4, valkey-migration-5 |
| [valkey-persistence](https://valkey.io/topics/persistence/) | retained | valkey-persistence-1, valkey-persistence-2, valkey-persistence-3, valkey-persistence-4 |
| [valkey-replication](https://valkey.io/topics/replication/) | retained | valkey-replication-1, valkey-replication-2, valkey-replication-3, valkey-replication-4 |
| [valkey-cluster](https://valkey.io/topics/cluster-tutorial/) | retained | valkey-cluster-1, valkey-cluster-2, valkey-cluster-3, valkey-cluster-4 |
| [valkey-transactions](https://valkey.io/topics/transactions/) | retained | valkey-transactions-1, valkey-transactions-2, valkey-transactions-3, valkey-transactions-4 |
| [valkey-lua](https://valkey.io/topics/eval-intro/) | retained | valkey-lua-1, valkey-lua-2, valkey-lua-3 |
| [valkey-pubsub](https://valkey.io/topics/pubsub/) | retained | valkey-pubsub-1, valkey-pubsub-2 |
| [valkey-streams](https://valkey.io/topics/streams-intro/) | retained | valkey-streams-1, valkey-streams-2, valkey-streams-3, valkey-streams-4, valkey-streams-5 |
| [valkey-memory](https://valkey.io/topics/lru-cache/) | retained | valkey-memory-1, valkey-memory-2, valkey-memory-3, valkey-memory-4 |
| [valkey-benchmark](https://valkey.io/topics/benchmark/) | retained | valkey-benchmark-1, valkey-benchmark-2, valkey-benchmark-3, valkey-benchmark-4 |
| [redis-licenses](https://redis.io/legal/licenses/) | retained | redis-licenses-1, redis-licenses-2, redis-licenses-3 |
| [redis-agpl](https://redis.io/blog/agplv3/) | retained | redis-agpl-1, redis-agpl-2, redis-agpl-3 |
| [lf-launch](https://www.linuxfoundation.org/press/linux-foundation-launches-open-source-valkey-community) | retained | lf-launch-1, lf-launch-2, lf-launch-3 |
| [google-agpl](https://opensource.google/documentation/reference/using/agpl-policy) | retained | google-agpl-1, google-agpl-2 |
| [gnu-agpl](https://www.gnu.org/licenses/why-affero-gpl.html) | retained | gnu-agpl-1, gnu-agpl-2, gnu-agpl-3 |
| [fedora-replacement](https://fedoraproject.org/wiki/Changes/Replace_Redis_With_Valkey) | retained | fedora-replacement-1, fedora-replacement-2 |
| [valkey-search](https://valkey.io/blog/introducing-valkey-search/) | retained | valkey-search-1, valkey-search-2, valkey-search-3, valkey-search-4 |
| [valkey-zrange](https://valkey.io/commands/zrange/) | retained | valkey-zrange-1, valkey-zrange-2 |
| [valkey-hset](https://valkey.io/commands/hset/) | retained | valkey-hset-1, valkey-hset-2 |
| [valkey-incr](https://raw.githubusercontent.com/valkey-io/valkey-doc/main/commands/incr.md) | retained | valkey-incr-1, valkey-incr-2 |
| [valkey-history-current](https://valkey.io/topics/history/) | retained | valkey-history-current-1, valkey-history-current-2, valkey-history-current-3 |
| [harbor-valkey](https://valkey.io/blog/harbor-chose-valkey/) | retained | harbor-valkey-1, harbor-valkey-2, harbor-valkey-3 |

| [valkey-incr-page](https://valkey.io/commands/incr/) | excluded | Rendered page blocked twice; official documentation source successfully retrieved instead |

## Citation chains and corrections

Video -> Valkey introduction -> persistence/replication/Cluster -> explicit loss and same-slot boundaries. Memory documentation -> buffer accounting and rejection behavior. Introduction/transactions -> native counters, WATCH and runtime-error handling. Streams -> pending/reclaim, retention and duplicate-effect boundaries. Migration -> post-7.2 file and feature qualification. Search results -> Valkey-search -> subset of RediSearch APIs. License search -> Redis's own AGPL announcement, GNU rationale and Fedora change -> later Harbor report. Each resulting skill reference links its own primary sources directly so it works when installed alone.

The video was fully audio-transcribed in the prior assessment; visual demonstrations were not reviewed. The scoped orientation retained here is: 0:00–1:09 primary-store candidate; 1:09–1:42 execution/latency; 1:42–3:03 persistence; 3:03–4:20 HA/sharding; 4:20–5:47 native structures; 5:47–6:53 working-set economics plus excluded sponsor advocacy; 6:53–7:34 eviction; 7:34–8:23 JSON/search/vector; 8:23–9:56 Lua atomicity/blocking/no rollback; 9:56–10:46 Pub/Sub/Streams. Closing promotions were excluded. Video URL: https://www.youtube.com/watch?v=m8_lnw8ORnE . No transcript wording is promoted above primary technical evidence.

## Completion and limitations

- Every retained source has access-dated extraction and a source hash in sources.json; the failed /about/ path and blocked INCR page each have an exclusion and successful replacement.
- Material findings are preserved in the focused skill guides, not only this synthesis. Proposed evals retain assertion-level satisfying, contradictory and omission fragments.
- These fragments are authored rubric challenges, not real-user results, independent human labels or model-run evidence. No actual-user sample was observed.
- No legal opinion, runtime reliability certification, performance win or successful migration is claimed. AGPL's OSI status does not settle the author's BSD/governance preference; the preference does not establish technical equivalence.
- Missing runtime evidence is handed to the intended skill user as explicit acceptance work. New operational skills and live datastore mutations are outside this delivery.

A final extraction audit corrected the INCR record: the rendered page and a canonical-path retry returned barriers, so its failed receipt is excluded and the retained claim IDs now point to the successfully retrieved official valkey-doc source with its own hashes. No documentation claim relies on a blocked page.

## Follow-through verification for the secondary enrichment

Retrieved Harbor's own [issue #22935](https://github.com/goharbor/harbor/issues/22935) and [merged PR #23157](https://github.com/goharbor/harbor/pull/23157) through GroktoCrawl on 2026-11-03, following the community account's citations. The March 2026 issue explicitly identifies repeated Redis licensing changes as risk and asks for Valkey with smooth migration; the April 2026 merged PR implements the cache replacement. These primary project records strengthen the named post-AGPL example without claiming population sentiment or a performance advantage. Their four extracted claims and retrieval hashes are in sources.json under harbor-issue and harbor-pr. The final ledger has 25 retained sources, two failed/replaced sources and 78 extracted claims. Bot coverage comments and promotional content in the PR were excluded from the enrichment.

The capacity/cost and QA guides use the same technical sources for per-node headroom, durability-preserving unit cost, independent loss/effect oracles and bounded failure/migration test design. Their numeric examples and fault scenarios are explicitly synthetic planning material, not executed evidence.
