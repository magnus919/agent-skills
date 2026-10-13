# Summarization and context compaction as measured tasks

Summaries are information transformations, not merely shorter strings. Define who
consumes the result, what facts/actions/qualifications must survive, which claims
are forbidden to invent and how the reduced context affects the downstream task.
A faithful short summary may still omit the one deadline that matters.

## Choose a model/output route

Extractive systems select source sentences/spans; they can be grounded yet omit
context, qualifications or antecedents. Encoder-decoder models such as BART, T5
and PEGASUS generate abstractive text; their pretraining objectives differ and
suitable task fine-tuning is still necessary. Decoder-only LLMs offer flexible
instructions but generation length, context and tool/permission boundaries must
be controlled. Hosted task-specific summarizers provide their own input/decoding/
validation contracts, not automatic local weights or non-autoregressive execution.

Compare an extractive baseline and untuned/prompted incumbent before adaptation.
“Constrained decoding” can mean token grammar control or a vendor's product name;
neither demonstrates factual correctness. The inspected ScaleDown summarization
contract calls its output an abstractive rewrite with tuned sampling. Treat claimed
speed/calibration/faithfulness separately from documented interface and measured
whole-task behavior.

## Data and implementation design

Bind source document/version and summaries to immutable hashes, task/source-group
IDs, rights and human/teacher label provenance. Split by document/source family
before chunking, teacher generation or paraphrase augmentation. Reference summaries
can themselves hallucinate; review task-critical facts and omission policy.

For encoder-decoder adaptation, pin tokenizer/model/revision and actual source/
target limits. Audit encoder truncation and decoder label padding (-100 where
required); a chat response-only mask is not the same training contract. Preserve
teacher-forcing labels, EOS/stop behavior and the intended generation length.
Use model-specific implementation docs, not an Unsloth decoder-only script as a
universal trainer. For decoder-only SFT route execution to `unsloth` with its
compatibility/label audits. Track source/target length distributions and dropped
or partially retained examples.

Long-document design may use local-window attention, chunk-and-reduce or retrieval.
Each introduces a new information boundary: chunk relevance/overlap, cross-chunk
facts, map-stage omissions and reduce-stage contradictions. Evaluate original
source coverage and end-to-end task accuracy, not only every chunk's fluency.
Keep date/number/negation/entity/causal qualifications and unresolved conflicts.
For document images include OCR/page-source traceability separately.

## Factuality and retention evidence

ROUGE/lexical overlap, fluent output, JSON shape and compression ratio cannot
independently establish factuality. FRANK supplies a typology of summary errors;
QAGS compares source/summary question answers; SummaC shows that NLI input granularity
and sentence aggregation matter. Automated factuality checks have domain, coverage
and model errors; they are screening signals, not independent universal truth.
Human/domain/reference evidence is needed for consequential claims and missing facts.

Freeze required fact/action/qualification roster before inspecting candidate
summaries. Separate supported, contradicted, missing and unresolved facts; also
review invented claims not on the expected roster. Report source support, salient
and critical retention, contradictions, invented numbers/entities, length, failed
sources and downstream task outcomes under matched consumer budgets. A factuality
score can miss essential omissions. Query/decision-conditioned compression must
preserve what the downstream consumer needs, and be evaluated on actual tasks.

## Receipt audit and limits

```bash
python3 scripts/audit_text_outcomes.py summary templates/summary-receipt.json
```

The authored synthetic example binds original source and summary SHA-256, an
explicit expected-fact roster, and each assessment's relation, criticality,
reviewer kind and evidence pointer. `human` or `reference` evidence is distinguished
from model-teacher/unresolved provenance. Missing, contradictory or unresolved
facts, missing assessments and untrusted provenance yield findings. Outputs reveal
counts/indexes only. Exit 0 is receipt consistency, not semantic execution or release
approval; 1 is findings/invalid input, 2 is invalid CLI arguments.

The helper does not read the referenced reviewer evidence, adjudicate truth,
confirm roster completeness or detect extra invented summary claims. Fabricated
receipts can clear it. Validate original source/summary binding and reviewer records
independently; include a separate invention/contradiction review and downstream
test. Do not portray teacher agreement or a score as human labels.

## Delivery and stopping rules

Use `templates/text-model-record.md`. Record complete data/transform/model/decoding/
assessment lineage, privacy scope, CPU/GPU/resource limits and actual artifacts.
Compare whole-task cold/warm cost, source preparation, generation and consumer
success; token savings may increase downstream error or verification expense.
Fresh reload and target-runtime checks must preserve source limits, truncation,
stop/length behavior and task-critical facts. Reject a critical-loss candidate even
if compression improves. Prepared recipes remain not run until observed; stop
at the agreed budget or three nonconverging compatibility passes with evidence.
