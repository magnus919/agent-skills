# Portable qualification probes for decision models

Use these probes before adapting a model to routing, relevance judgments or
candidate acceptance. They test semantic boundaries; they are not a benchmark,
calibration set or evidence that any model meets a production requirement.

## Self-contained synthetic fixtures

`examples/decision-qualification.synthetic.jsonl` contains eight authored cases:
paired inventory, fixed-time freshness and dependency judgments, plus relevance
versus superficial topical overlap. Each line separates `request` from the
expected answer and rationale. Only `request` may reach the model. Keep fixture
IDs, expected labels and rationales outside state and question instructions.
The fixtures illustrate failure classes observed in exploratory testing; they
are newly authored examples, not the packet behind any published accuracy claim.

Run this offline structural check from the skill root:

```python
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from systemone_probe import validate_request

for line in Path("examples/decision-qualification.synthetic.jsonl").read_text().splitlines():
    case = json.loads(line)
    validate_request(case["request"])
    assert case["expected_choice"] in case["request"]["questions"]["decision"]["criteria"]
```

This checks fixture shape only. To measure decisions, pass each request through
an independently qualified native client. Record model/runtime/adapter revisions
and parsed answers, then compare the returned Choice ID with `expected_choice`.
Do not send labels to a provider, reinterpret missing answers as valid defaults,
or describe offline validation as successful model inference.

For every base case, reverse option order and paraphrase the question without
changing its meaning. Add fixed-state question-only counterfactuals where the
expected answer reverses, and decisive-evidence counterfactuals with irrelevant
lexical cues held stable. Have a reviewer confirm the new labels before running.
Count distinct scenarios separately from variants and repetitions; repeated
agreement measures stability, which can include consistently wrong answers.

Exact inventory arithmetic and timestamp eligibility belong in code. Use model
probes to detect inappropriate reliance on judgment, then test the deterministic
policy boundary. A shared-dependency probe checks whether the model follows
relations rather than independent team names. Passing a few polarity or negation
examples does not establish arbitrary-question understanding.

## Relevance and acceptance tradeoffs

Define useful relevance in terms of the user's task, not shared topic words.
For example, a rollback procedure helps a request about recovering a failed
upgrade; a document that merely mentions the same deployment technology may not.
Include useful, superficially overlapping, unrelated and insufficient-evidence
candidates. Define the unknown/review lane before scoring. No model authorizes
publishing, routing or acting on a selected candidate.

Measure false-positive acceptance and useful-candidate coverage together. A
model selecting more useful candidates can also accept more weak candidates;
a selective model can miss useful ones. Higher selection volume, richer context
or repeatability alone does not establish better recommendations. Compare
compact and richer inputs as separate frozen contracts, including decisive
evidence position and overflow behavior; do not pool them into one leaderboard.

Use grouped, independently reviewed target cases with separate development,
calibration and untouched test splits. Label according to the evidence available
to the decision model; if a reviewer sees fuller evidence, disclose that asymmetry
and report missing-evidence effects separately. Topic/domain transfer needs a new
qualification set rather than thresholds copied from another workload.

## Judge and runtime provenance

Model-produced labels are pseudo-labels, even when inputs hide the candidates'
identities and predictions. Keep the rubric, input hashes, requested judge ID,
returned model identity and routing configuration. A gateway alias is not proof
that the intended judge answered. If identity is hidden or unresolved, mark it
unknown rather than attributing the labels to a named model.

Blind labeling reduces bias but does not create human ground truth. Inspect
label disagreements and test how alternative reviewed labels change acceptance
conclusions. Do not select the judge that makes a candidate look best. A few
correlated scenarios cannot qualify probability calibration or a confidence gate.

Report cold and warm latency separately, with input size, request shape,
concurrency, precision and actual delivery boundary. Direct engine timing,
local HTTP and remote HTTPS are different boundaries; observed timings are not
controlled architecture speedups. Allocator memory is not total-device memory.
Treat rejected overflow as an explicit compatibility outcome; silent truncation
must fail a fixed-contract comparison when it removes required evidence.

Use [comparison design](comparison-design.md), [request-shape evaluation](request-shape-evaluation.md)
and [evaluation and calibration](evaluation-and-calibration.md) for qualification
and release evidence beyond these illustrative probes.
