# Acquisition and stopping

Use a declared mixture of representative sampling and targeted acquisition.
Representative items estimate deployment prevalence; uncertainty, novelty,
diversity, and risk strata expose weaknesses. Do not merge their results into a
single unweighted quality claim.

For each active batch, record selector, model/version, score, seed, candidate
pool, slice coverage, and exclusions. Maintain a representative held-out audit
set that the selector cannot see. Compare label quality and downstream utility
between active batches and the audit set; a high-yield active batch does not prove
population coverage.

Stop when additional labels fail a predeclared marginal-value rule: required
slice coverage is met, quality is stable under blind rechecks, and the expected
downstream improvement per item is below its cost or time budget. Reopen when the
data distribution, label guide, model, or production failure profile changes.
