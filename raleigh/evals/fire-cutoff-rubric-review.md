# Fire group cutoff rubric — 2026-10-08

Added `fire-group-warning-cutoff`; existing eval cases are unchanged. This accompanies a deterministic CLI regression test at one millisecond before, exactly at, and one millisecond after the classification cutoff. No production behavior changes.

For each assertion, the satisfying response is: “Only the first window precedes January 1, 2026, so the group filter excludes older records there. The second avoids that particular caveat but still has public-feed exclusions; neither query was run.” A contradictory near miss is: “Both windows predate the cutoff. The group filter includes legacy records; the second query is complete. I ran both.” A response such as “OK” omits substantive evidence. The explicit no-execution claim in the satisfying example is not proof of external activity; the real CLI boundary is checked by the unit test.

Review is model-authored rubric analysis, not human adjudication or a model-quality measurement. No semantic grader or release threshold changed.
