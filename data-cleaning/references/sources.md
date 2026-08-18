# Source notes and evidence map

Accessed 2026-08-17. The KDnuggets article is orientation; primary docs govern current behavior.

- [KDnuggets: 5 Python Libraries](https://www.kdnuggets.com/5-python-libraries-that-make-data-cleaning-more-enjoyable): tool map and broad use cases; secondary source, so verify APIs.
- [Wes McKinney, Data Cleaning](https://wesmckinney.com/book/data-cleaning): pandas mapping, replacement, missing data, strings, categoricals, and reshaping.
- [pyjanitor docs](https://pyjanitor-devs.github.io/pyjanitor/): chainable pandas-style cleaning.
- [Pandera schemas](https://pandera.readthedocs.io/en/stable/dataframe_schemas.html): schema, nullability, coercion, strictness, uniqueness, and backends.
- [Great Expectations validation](https://docs.greatexpectations.io/docs/reference/learn/validation/validate_data_overview/): expectations, batches, checkpoints, and evidence.
- [ftfy docs](https://ftfy.readthedocs.io/en/latest/): focused Unicode/mojibake repair.
- [ydata-profiling](https://docs.profiling.ydata.ai/latest/): profiles and comparisons.
- [Cerberus](https://docs.python-cerberus.org/): nested dictionary validation and coercion.
- [OpenRefine reconciliation](https://openrefine.org/docs/manual/reconciling): semi-automated matching with required human review.
- [Frictionless validation](https://framework.frictionlessdata.io/docs/guides/validating-data.html): structured tabular errors and custom checks.
- [dbt data tests](https://docs.getdbt.com/docs/build/data-tests): reusable failing-row assertions and generic tests.
- [Deequ](https://github.com/awslabs/deequ): Spark-scale metrics and constraints.
- [Wickham, Tidy Data](https://vita.had.co.nz/papers/tidy-data.pdf): variables in columns, observations in rows, values in cells.
- [pandas missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html) and [pandas merging](https://pandas.pydata.org/docs/user_guide/merging.html): nullable dtypes, sentinel behavior, `skipna`, merge cardinality, and row multiplication.
- [Unicode UAX #15](https://www.unicode.org/reports/tr15/): normative normalization forms and the risk of erasing distinctions with compatibility normalization.
- [dedupe documentation](https://docs.dedupe.io/en/latest/): labeled, blocked, reviewable probabilistic record linkage.
- [csvkit](https://csvkit.readthedocs.io/en/latest/) and [Miller](https://miller.readthedocs.io/en/latest/): scriptable inspection and streaming tabular transformation.

Conclusion: profile to discover, transform explicitly, validate named contracts, and preserve evidence. The reusable artifact is a plan + decision log + contract + before/after report, not a magic cleaner.
