# Merge queue eval challenges

These response fragments challenge the new assertions. Assess each row
independently on the available response. Omitted evidence stays unresolved.
The examples are rubric checks, with no model run or live queue execution.

| Case and assertion | Meets | Contradicts | Omits |
|---|---|---|---|
| reconcile-rebuilt-queue-candidate · identity | Records PR head P41 and live candidate Q2. | Records Q1 as current or overwrites the PR head with Q2. | Says the queue rebuilt without identifying the revisions. |
| Same case · check evidence | Waits for required Q2 checks and treats Q1 as superseded. | Uses Q1 green to declare Q2 ready. | Mentions Q2 with no decision about its checks. |
| Same case · existing entry | Resumes watching #41 in place. | Submits another merge request while #41 is queued. | Describes verdicts without a next queue action. |
| Same case · completion | Keeps delivery pending and checks the forge's merge record and target for landing. | Reports delivery complete from queue admission. | Ends at Q2 green without addressing landing. |
| size-merge-queue-for-runner-capacity · merge limit | Says the setting groups landings and leaves candidate build count alone. | Says increasing the setting shares CI runs. | Discusses concurrency without addressing merge limits. |
| Same case · per-prefix safety | Retains required results for each landed prefix. | Lets only the final green group cover earlier failing prefixes. | Proposes tuning without stating the evidence required to land. |
| Same case · bottleneck | Reduces speculative depth during high invalidation or adds capacity for measured runner contention. | Raises concurrency immediately despite growing runner wait and discarded builds. | Says to keep monitoring without an adjustment to test. |
| Same case · measures | Compares landed PRs per hour, wasted CI minutes, and ready-to-merge latency. | Counts completed CI jobs as landed work. | Reports runtime only. |
| hold-dependent-work-after-queue-ejection · dependency | Holds C until B lands, or proposes a supported jointly tested group. | Lands C alone before the schema exists. | Reports B and D without accounting for C. |
| Same case · independent work | Continues D on a candidate without B after required checks pass. | Uses D's prior green result with B to land D. | Calls D independent without stating which candidate needs checks. |
| Same case · failure ownership | Makes the schema owner responsible for diagnosing B. | Assigns B to the documentation author solely because D followed B. | Says someone should look at the failure. |
| Same case · review backlog | Pauses or caps new assignments until review capacity is available. | Starts all five tasks despite the growing bottleneck. | Explains queue recovery without deciding what to dispatch. |
