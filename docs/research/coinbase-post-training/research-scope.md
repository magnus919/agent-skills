# Research scope and protocol

2026-10-13; commissioned by Magnus. Track: comprehensive technical research.

Question: under which data, verifier, compute and evaluation conditions can local
LLM specialization improve coding or other bounded user tasks, and which catalog
capabilities are missing to execute and assess it responsibly?

Decision: enrich existing `unsloth` (operations) and `ml-engineering` (judgment);
create no near-duplicate training skill. Delivery includes PR, required checks,
review, merge and current-main verification. No production services, drivers,
credentials or existing training runs will be changed. GPU training is outside
this research implementation: new runtime recipes are explicitly prepared/not run.
Rollback: revert the delivery commit; helpers operate read-only on explicit files.

Search strata: SFT vs RL; coding verifiers/reward hacking; consumer-GPU memory;
repository/trajectory provenance and leakage; forgetting/generalization; export
and serving parity. Sources: primary research, author repositories and official
versioned documentation. Include foundational PEFT work even before 2024;
prefer 2024-current empirical agent/RL evidence. Exclude marketing-only claims,
uncited tutorial reposts, inaccessible text as evidence, and duplicated reports
of one experiment as independent corroboration.

Competing hypotheses: H1 good SFT is enough for a narrow task; H2 RL adds benefit
when the model can explore correct solutions and the verifier is trustworthy;
H3 reported gains primarily reflect selection, extra sampling or contamination.
Inspect controls and test-time compute, preserve negative/contradictory findings.
No published improvement is a promise about our hardware or users' datasets.

GroktoCrawl: use Hermes-configured http://gpuslut01:18080, with its credential
loaded without printing. Three bounded concurrent requests; preserve successful
snapshots and failure status. Follow author/code links from retained sources.
Stop discovery when all six strata have directly inspected primary evidence,
competing findings and implementation implications; not at a convenient count.
Record omissions and unresolved questions rather than silently filling gaps.

Durable destination: this tracked docs package plus skill source ledgers,
references, templates, tested helpers and eval assertion challenges. Full fetched
third-party snapshots remain local in /private/tmp/coinbase-gpu-corpus and the
existing source archive; publish original evidence records with source URLs,
access dates and snapshot hashes instead of redistributing entire publications.
Research complete only when each retained source has an extraction record and
all consequential recommendations map to evidence or are labeled proposals.
