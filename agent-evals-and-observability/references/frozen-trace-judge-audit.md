# Worked example: separate replay, labels, and failure detection

[LangChain's weather-agent study](https://www.langchain.com/blog/jev-agent-evals-langsmith)
and its [archived records](https://github.com/danielgshea/jev-as-a-judge#reproducibility)
show how to freeze a completed run (request, answer, tool events and evidence) and
score the same input repeatedly. There were five distinct runs, 100 repetitions
per run per judge, and one human reference reviewer. An always-pass baseline
agrees on four of five cases. A 500/500 match is repeat agreement on those five
cases, not 500 independent observations. The study measured continuous score
variance, not continuous score accuracy; it is not a model ranking for other work.

Audit the sole human-labeled failure before replacing the judge. The agent asked
which Dublin and did not search: the reviewer found the clarification useful
but the benchmark contract required a search. Asking which Springfield was
accepted. Preserve both the observed action and the task-policy disagreement:
whether to clarify a location is a different question from whether a search
occurred. Check the latter in the event log; use independent reviewers to resolve
the former, retaining both labels and rationales if the contract is disputed.
Version the revised rubric and keep disputed cases visible.

Add a different kind of diagnostic case where the expected answer is already
known: take a sound trace and alter just one observable property, such as
removing the supporting source passage while keeping the final prose intact.
Check that the grader detects that defect and does not penalize the intact
reference. Keep these targeted challenge cases separate from prevalence samples.
[REFLECT](https://arxiv.org/abs/2605.19196) demonstrates this method on research
agents for both trace-level and report-level defects. It tests generative judges,
not Jev; use its construction method, not its scores as a typed-judge benchmark.

For the operating procedure, see [judge stability](judge-stability.md).
