# Test Design Techniques Checklist

> Quick-reference for selecting test design techniques. Check the techniques that apply to your scenario, then derive test cases. See [test-design-techniques.md](../references/test-design-techniques.md) for detailed guidance and worked examples.

## Feature Under Test

| Field | Value |
|-------|-------|
| Feature / Component | <name> |
| Tester | <name> |
| Date | <YYYY-MM-DD> |

## Technique Selection

| Technique | Applies? | Rationale |
|-----------|:--------:|-----------|
| Equivalence Partitioning (EP) | [ ] | <Why: input domains exist with distinct behavior classes> |
| Boundary Value Analysis (BVA) | [ ] | <Why: numeric or ordered ranges with edge behavior> |
| Decision Tables | [ ] | <Why: business rules with multiple interacting conditions> |
| State Transition | [ ] | <Why: stateful workflow with valid/invalid transitions> |
| Pairwise / Combinatorial | [ ] | <Why: multi-parameter configuration space> |
| Error Guessing | [ ] | <Why: known defect patterns, historical failure areas> |

## When to Use Which

| Scenario Type | Primary Technique | Supporting Technique |
|---------------|-------------------|---------------------|
| Input validation (ranges, formats) | EP + BVA | Error Guessing |
| Business logic with conditions | Decision Tables | EP |
| Workflow with states and transitions | State Transition | Decision Tables |
| Configuration with many parameters | Pairwise | EP |
| Integration with external systems | Error Guessing | EP (interface partitions) |
| UI with form fields | EP + BVA | Error Guessing |
| Permission / role-based access | Decision Tables | State Transition |

## Technique Application Notes

### Equivalence Partitioning

- [ ] Identified all input domains
- [ ] Defined valid and invalid partitions
- [ ] Selected one representative per partition
- [ ] Included type/format partitions (non-integer, empty, null)

### Boundary Value Analysis

- [ ] Used 2-value (min, max) for quick coverage
- [ ] Used 3-value (min-1, min, max, max+1) where off-by-one is likely
- [ ] Tested empty/null boundaries

### Decision Tables

- [ ] Listed all conditions and actions
- [ ] Generated complete rule combinations
- [ ] Reduced redundant rules where outcomes are identical
- [ ] Covered impossible/contradictory combinations explicitly

### State Transition

- [ ] Drew or referenced the state model
- [ ] Covered all valid transitions (0-switch)
- [ ] Tested at least one invalid transition per state
- [ ] Checked for dead states and unreachable states

### Pairwise / Combinatorial

- [ ] Listed parameters and their values
- [ ] Generated pairwise combinations (tool: PICT / allpairs)
- [ ] Added known-bad combinations from defect history

### Error Guessing

- [ ] Reviewed defect history for this component
- [ ] Checked common failure patterns (null, overflow, concurrency, timeout)
- [ ] Tested integration boundaries with invalid/malformed data

## Coverage Summary

| Dimension | Covered | Notes |
|-----------|:-------:|-------|
| All valid partitions tested | [ ] | |
| All boundaries tested | [ ] | |
| All decision rules covered | [ ] | |
| All state transitions covered | [ ] | |
| Pairwise combinations generated | [ ] | |
| Known error patterns tested | [ ] | |

> The pyramid level for each technique is a starting point, not a rule. Adapt to your system's risk profile. See [test-strategy.md](../references/test-strategy.md).
