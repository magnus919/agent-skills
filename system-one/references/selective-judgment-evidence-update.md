# Published evidence and its limits

Li, Miao, Krishnan, and Padman, [JEV-as-a-Judge, revision 3](https://arxiv.org/html/2609.26550v3),
29 September 2026, sections 6–9 and appendices M–N, reviewed 26 November 2026.
This revision adds prospective live calls on two correctness workloads. Using
100 selection pairs per workload, a prespecified threshold selection procedure
matched GPT-6 aggregate accuracy on 570 held-out pairs while escalating about
74% and saving about a quarter of its fee. This is an observed match on these
cases, not demonstrated equivalence or a universal fee or latency promise. The
two workloads use verifiable correctness pairs; some JudgeBench questions
overlap an earlier sample. This is not a live production monitoring trial.

The paper distinguishes a verdict that can be read from supplied evidence from
one that must be derived, such as a difficult code, math, or logic judgment.
Use the distinction to choose the evidence and evaluator, not to route on domain
labels by themselves. For example, identify whether a patch claims recovery
from a log, then run an actual recovery test to establish whether it works.
The paper also finds weaker routing on misleading style and reference-free prose.
It uses maximum label probability, which is not automatically calibrated
correctness or interchangeable with a provider's native confidence field.

[Rao and Callison-Burch](https://arxiv.org/html/2609.29769v1) found that other
judges often shared confident Jev mistakes on graded rubrics. A fallback can
match a baseline in one workload and add little in another if it repeats the
first judge's errors. Read the [rubric judge evidence](rubric-judge-research.md)
before transferring either result. Treat repeatability, agreement with a
reference, and the fallback's ability to catch different errors as distinct.

For the operating procedure, see [selective judgment](selective-judgment.md).
