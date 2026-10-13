# Task-specific extraction/summarization evidence

Accessed 2026-10-13 through GPU-host GroktoCrawl. Original source-level records,
URLs, limits and hashes are tracked in repository
`docs/model-families/family-3-extraction-summarization.md`. No model runtime,
provider inference, trained extractor or summarizer quality was validated here.

- [GLiNER](https://arxiv.org/abs/2311.08526), [author code](https://github.com/urchade/GLiNER):
  label-conditioned span encoding. [GLiNER2 SDK](https://github.com/fastino-ai/GLiNER2)
  has operation-specific structured schemas, confidence and offset controls;
  its methods/checkpoints must not be conflated with Decide-only classification.
- [BART](https://arxiv.org/abs/1910.13461), [T5](https://arxiv.org/abs/1910.10683),
  [PEGASUS](https://arxiv.org/abs/1912.08777): differing encoder-decoder pretraining
  routes to generation, not proof of factual summaries.
- [QAGS](https://arxiv.org/abs/2004.04228): QA-based factuality screen;
  question/answer pipeline errors and coverage remain limitations.
- [FRANK](https://arxiv.org/abs/2104.13346): human-annotated error typology and
  metric comparisons, not one universal quality score.
- [SummaC](https://arxiv.org/abs/2111.09525),
  [author implementation](https://github.com/tingofurro/summac): sentence granularity
  and aggregation matter for NLI-based factuality predictions.
- [Transformers summarization](https://huggingface.co/docs/transformers/tasks/summarization):
  source/target training contract; match the installed version/model.
- ScaleDown [extraction](https://docs.scaledown.ai/api-reference/extract-overview)
  and [summarization](https://docs.scaledown.ai/api-reference/summarize-overview):
  documented hosted interfaces only; architecture/speed/quality claims unverified.

Dataset/teacher/LLM-judge provenance and source/summary binding are independent
of syntactic output validity. Gold/reference and human assessment records require
real independent review; authored receipts do not manufacture that evidence.
