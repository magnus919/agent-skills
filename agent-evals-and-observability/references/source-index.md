# Source and Status Index

Sources inform decisions; they become binding only when adopted by applicable policy, contract, or regulation. Versions and statuses were checked 2026-07-13 unless otherwise stated. Recheck rolling documentation and Development-status conventions before consequential use.

| Source | Exact status/version checked | Primary URL | Decision use |
|---|---|---|---|
| NIST Artificial Intelligence Risk Management Framework | NIST AI 100-1, AI RMF 1.0, January 2023; NIST reports revision work underway | https://doi.org/10.6028/NIST.AI.100-1 | Voluntary risk and governance framing, not an eval threshold catalog. |
| NIST AI RMF Generative AI Profile | NIST AI 600-1, July 2024 | https://doi.org/10.6028/NIST.AI.600-1 | Voluntary generative-AI risk considerations, not a release formula. |
| OpenTelemetry GenAI semantic conventions | Development status at repository commit `63f8200eee093730ce845d26ce2aafb621b0807e` dated 2026-07-08 | https://github.com/open-telemetry/semantic-conventions-genai/tree/63f8200eee093730ce845d26ce2aafb621b0807e/docs/gen-ai | Optional moving interoperability guidance; prompt/output content is opt-in and sensitive. |
| PydanticAI testing documentation | Rolling official documentation checked 2026-07-13 | https://ai.pydantic.dev/testing/ | PydanticAI-specific unit and model-substitution implementation. |
| Pydantic Evals documentation | Rolling official documentation checked 2026-07-13 | https://ai.pydantic.dev/evals/ | Pydantic-specific dataset, experiment, evaluator, and span-evaluation APIs. |
| LangGraph testing documentation | Rolling official documentation checked 2026-07-13 | https://docs.langchain.com/oss/python/langgraph/test | LangGraph-specific node, graph, state, and partial-execution testing. |
| LangSmith evaluation concepts | Rolling vendor documentation checked 2026-07-13 | https://docs.langchain.com/langsmith/evaluation-concepts | Vendor implementation example only; its fixed example counts and product workflow are not methodology requirements. |
| “Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena” | Zheng et al., arXiv:2306.05685 v4, 2023-12-24 | https://arxiv.org/abs/2306.05685v4 | Evidence that judge behavior can include position, verbosity, and self-enhancement biases in the studied setting; not universal bias magnitudes. |
| “G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment” | Liu et al., arXiv:2303.16634, 2023 | https://arxiv.org/abs/2303.16634 | Example of rubric-guided model judging; use as research context, not a universal judge protocol. |
| “SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models” | Manakul et al., EMNLP 2023 | https://aclanthology.org/2023.emnlp-main.557/ | Consistency-based hallucination signal and its limits; not a factuality oracle. |
| “FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation” | Min et al., EMNLP 2023 | https://aclanthology.org/2023.emnlp-main.741/ | Claim-level factual precision framing; source attribution and domain limits remain decision-specific. |
| Ragas documentation | Rolling documentation; verify API and metric definitions before use | https://docs.ragas.io/ | Named implementation example for RAG evaluation; metric names do not establish a release threshold. |
