# Assumption Map

Map the assumptions driving a proposed product change. Classify each by risk, evidence strength, and testability before designing experiments.

## Instructions

1. List every assumption underlying the proposed change. Be exhaustive — an unstated assumption is the most dangerous kind.
2. For each assumption, score risk, evidence, and testability.
3. Sort by risk (descending). The highest-risk, least-evidenced assumptions are your top experiment candidates.

## Map

| # | Assumption | Risk (1-5) | Evidence (1-5) | Testability (1-5) | Priority | Method hint |
|---|-----------|------------|----------------|-------------------|----------|-------------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |

**Risk (1-5):** 1 = wrong assumption has trivial impact; 5 = wrong assumption wastes months of engineering or causes user harm.
**Evidence (1-5):** 1 = pure guess, no evidence; 5 = confirmed by multiple independent sources.
**Testability (1-5):** 1 = cannot be tested without building the full product; 5 = testable with a 30-minute interview.

## Guidance

- If an assumption scores 4+ on risk and 1-2 on evidence, it must be tested before building.
- If an assumption scores 5 on evidence, document the evidence source and move on — do not test what is already known.
- The "method hint" column is a first guess; the formal method selection happens in the experiment brief.

## Example

| # | Assumption | Risk | Evidence | Testability | Priority | Method hint |
|---|-----------|------|----------|-------------|----------|-------------|
| 1 | Users want to share playlists with friends | 5 | 1 | 4 | 20 | Qualitative interviews |
| 2 | The share-UI can be built in 2 weeks | 2 | 3 | 2 | 4 | Prototype test |
| 3 | Sharing will increase DAU by 5% | 4 | 2 | 1 | 8 | A/B test (after value validated) |
