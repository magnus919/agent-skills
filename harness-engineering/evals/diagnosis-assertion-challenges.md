# Diagnostic assertion challenges

Both cases use synthetic traces. The response fragments exercise the rubric.
They supply no evidence of a completed model run or a production repair.

| Case and assertion | Meets | Contradicts | Omits |
|---|---|---|---|
| revision-batch-reject-ancestor-address · eligibility | Rejects R3 because only R7 and R8 are offered. | Accepts R3 because it is an ancestor of R7. | Calls for checking IDs without deciding R3's status. |
| Same case · before effects | Rejects before applying or caching the edit. | Caches the result, then marks it bad. | Rejects it without saying where validation occurs. |
| Same case · replay | Compares R7's payload across the two checkpoints. | Counts R7 as changed from the R3 parent alone. | Focuses on R3 without checking R7. |
| trace-condition-loss-through-deduplication · first loss | Locates the missing condition where deduplication dropped C8 in favor of C2. | Blames the writer despite its input lacking the condition. | Restates the final defect without naming its first appearance. |
| Same case · evidence window | Checks the actual candidate text and surrounding evidence sent to the duplicate judge. | Treats the full source available elsewhere as proof of what the judge received. | Names the judge without inspecting its input. |
| Same case · retained representation | Requires C2 or an alternative representative to retain the non-write condition before dropping C8. | Treats similarity in subject as proof of equivalence. | Recommends a threshold change without stating what must survive. |
| Same case · replay | Verifies the original condition appears in the final brief on the replay. | Declares repair once C8 receives any verdict. | Makes a proposed change without repeating the affected path. |
