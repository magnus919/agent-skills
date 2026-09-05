The day-5 deadline is not achievable with the stated durations, dependencies, and one exclusive specialist. The earliest completion is day 7: two working days late.

Using elapsed working-day boundaries from time 0:

| Task | Start | Finish | Constraint |
|---|---:|---:|---|
| design | 0 | 2 | None |
| build | 2 | 5 | After design; specialist |
| review-prep | 5 | 6 | After design; same exclusive specialist |
| accept | 6 | 7 | After build and review-prep |

Review-prep could run before build without changing completion. After design, the specialist must perform four days of work serially; acceptance then takes another day. Thus the resource-constrained duration is 2 + 3 + 1 + 1 = 7 days.

Even ignoring the resource conflict, the dependency-only critical path is design → build → accept, totaling six days. A second specialist alone therefore improves completion to day 6, still one day late.

To make day 5 credible, approve and validate changes that remove two elapsed days from the resource-constrained plan. For example, a second qualified specialist plus a one-day reduction in the dependency critical path could suffice. Alternatively, reduce two days from the serial schedule without compromising acceptance. Without such validated scope, duration, or dependency changes, move the deadline to at least day 7. These are deterministic earliest dates; they contain no allowance for uncertainty or resource availability beyond the fixture.
