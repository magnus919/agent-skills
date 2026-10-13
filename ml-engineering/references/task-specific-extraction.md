# Task-specific extraction and structured decisions

Choose the output contract before selecting a model. Source-span extraction,
normalized fields, relations, nested structures and categorical decisions are
separate tasks. An extractor can return correct JSON while inventing values or
missing the most consequential entities. A decision score is not a source citation.

## Model family and baseline map

- Deterministic parsers/regex/schema rules: strong baselines for stable formats;
  encode known structural guarantees and document failure coverage.
- Fixed-label encoder NER/token classifiers: sequence labeling over a trained
  vocabulary with token/word alignment and entity boundary decoding.
- Open-label span encoders such as GLiNER: jointly represent text and requested
  labels and score matching spans, without requiring free-form entity generation.
  Label wording, taxonomy overlap, tokenization and threshold matter.
- Multi-task/schema-driven GLiNER2: author SDK supports entities and other structured
  extraction/classification operations. Outputs and score fields differ by method
  and checkpoint; do not assume Decide classification weights support every task.
- Generative schema-constrained extraction: can normalize/combine text, but output
  constraints certify shape rather than source grounding. Inspect invented fields,
  unknown/null handling and prompt-injection response.
- Hosted task-specific APIs: may route categorical keys to a classifier and spans
  to an extraction model. Vendor “CDM” terminology is not an independently verified
  architecture or a guarantee of open/local weights.

For bounded categorical decisions, route typed question/calibration contracts to
`system-one`. For document conversion/OCR mechanics use `anydoc` or the appropriate
document skill; for pipeline/source lineage use `data-engineering`. This methodology
reference does not turn the GLiNER2 repository into a validated operational skill.

## Preserve the source coordinate system

Pin original bytes/hash, decoding, Unicode handling, whitespace/newline processing,
OCR version, page/chunk identity and the text that actually reaches the model.
Know whether offsets count UTF-8 bytes, Unicode code points or tokenizer tokens,
and whether end offsets are inclusive. If normalizing text, retain a verified
mapping back to the original. Python string slicing uses code points and exclusive
ends; it cannot validate byte offsets merely because they are integers.

Chunk before a model's context truncation removes entities. Preserve source IDs,
chunk ranges/overlap and merge/deduplicate predictions deterministically. Overlap
can improve boundary recall but duplicate entities need reconciliation. Tokens,
characters and pages are not interchangeable size units. Model context and OCR
pipeline can lose content before any schema validator sees it.

## Labels and training data

Define label granularity, mutually exclusive/overlapping categories, spans,
normalization, relations, missing/unknown cases and consequential false negatives.
Split documents/source families before chunking or generating variants; use
independent entity/span review. Weak/synthetic labels and teacher confidence need
provenance and disagreement analysis; do not declare them ground truth automatically.

For a pretrained open-label encoder first benchmark call-time labels/thresholds
on development data. If adaptation is warranted, use that encoder's matched
span/token loss, tokenizer alignment and structured collator. Generic chat SFT
is not interchangeable. A generative extractor's training targets require source
support and null/abstention examples; schema conformity alone is inadequate.

## Evaluation and deterministic audit

Freeze source/schema/model/tokenizer/label descriptions, threshold, chunk policy
and normalization. Report exact and protocol-defined partial span precision/recall,
per-type/critical-entity misses, extra/invented values, relations/normalization
accuracy, unknown handling and field-dependent task consequences. For redaction,
evaluate missed sensitive spans and the actual redacted artifact, not just JSON.
Score calibration requires independent labels and representative distributions;
API confidence fields are not automatically calibrated probabilities.

From the skill root:

```bash
python3 scripts/audit_text_outcomes.py spans templates/extraction-receipt.json
```

The synthetic contract binds source text to its UTF-8 SHA-256, declares label set,
flat predicted/gold entities, and human/reference gold provenance. Each span has
label, code-point start/exclusive end and exact text; predicted scores must be
finite in [0,1]. The helper checks source equality, invalid/duplicate spans and
exact gold missing/extra counts. It emits counts/codes/indexes without source text.
Exit 0 clears these checks only; 1 is findings/invalid input; 2 is CLI misuse.

The 16MiB limit bounds input allocation. It does not verify gold quality, label
meaning, calibrated scores, nested/relationship contracts, OCR truth or complete
sensitive-entity coverage. Fake or incomplete gold can pass. Use a genuine complete
source-level reference set and independent review; never replace semantic evidence
with a literal match or put test gold into the model's input.

## Runtime delivery

Record cold/warm end-to-end source preparation, batching/chunking, model and merge
latencies, peak device/RAM, truncation and failed sources. Verify actual device
placement and version/weight permissions before local operation. Hosted integration
adds authorized data-transfer/retention and rollback requirements; local SDK files
alone do not establish offline behavior. Fresh reload preserves tokenizer/schema/
threshold/chunk maps and reproduces actual extraction artifacts. Keep model/task
quality distinct from the offline receipt audit.
