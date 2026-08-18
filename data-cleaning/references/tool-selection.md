# Data-cleaning tool selection

Choose the smallest tool that proves the needed contract.

| Tool/family | Best fit | Boundary |
|---|---|---|
| pandas | moderate in-memory tabular work | memory-bound; declare types |
| Polars | fast local/lazy tabular work | semantics and dtypes differ from pandas |
| pyjanitor | readable pandas cleaning verbs | convenience, not a quality contract |
| Pandera | Python DataFrame schemas/checks | rules must encode domain meaning |
| Great Expectations | named suites, checkpoints, reports | pin current API/version |
| ydata-profiling | exploratory HTML/JSON profiles | discovery, not validation |
| ftfy | Unicode/mojibake repair | inspect potentially changed text |
| Cerberus/Pydantic | nested JSON records | not relational/distribution checks |
| OpenRefine | interactive exports/entity review | human judgment is required |
| Frictionless | tabular/package validation | add custom business checks |
| dbt data tests | SQL models and warehouse boundaries | SQL/warehouse-oriented |
| Deequ/PyDeequ | Spark-scale metrics/constraints | JVM/Spark compatibility cost |

Selection: classify boundary and scale; choose transformation engine separately from validator; use declarative contracts at stable boundaries; keep a dependency-free triage fallback; pin versions; pilot human reconciliation and retain decisions. The orientation article names pyjanitor, Great Expectations, ftfy, ydata-profiling, and Cerberus; primary documentation governs behavior.
