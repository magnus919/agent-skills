# Text, identifiers, and entity resolution

## Preserve before normalizing

Keep the source value beside any normalized value. Record the normalization form, locale, case policy, transliteration, punctuation policy, and software version. NFC is often safer than compatibility normalization; NFKC/NFKD can erase meaningful distinctions. Unicode normalization is not encoding detection. For mojibake, use a focused repair tool such as ftfy, emit an explanation/change report, and review high-impact fields.

Treat IDs as identifiers, not numbers: preserve leading zeroes, width, separators, and check digits unless the contract explicitly says otherwise. Do not infer that numeric-looking strings should become integers. Audit invisible/control characters and replacement characters before repair.

## Entity resolution

Exact duplicate detection, record linkage, and entity resolution are different tasks. Define the entity, stable identifiers, blocking keys, comparison fields, and the costs of false matches versus missed matches. Generate candidates with blocking; score candidates with documented comparators; use accepted/rejected labels or a reviewed sample to select thresholds; and keep a clerical-review band for ambiguity.

Every accepted cluster or match should retain source record IDs, candidate pairs, features/evidence, score, threshold, decision, reviewer, and model/rule version. Never auto-merge solely because a fuzzy score is highest. Preserve unmatched and conflicting records. Evaluate on a labeled holdout where feasible and test stability across reruns.

## Privacy

Profiles, candidate tables, and exception exports can expose names, addresses, identifiers, or sensitive text. Minimize fields, redact or hash display values, restrict access, set retention, and keep the mapping from privacy-safe IDs to source IDs separately.
