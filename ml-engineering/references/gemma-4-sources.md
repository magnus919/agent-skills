# Gemma 4 tuning source record

Captured on 2026-11-25 using GroktoCrawl. The scope is the fine-tuning overview, all 16 guides in its training navigation, the four embedded overview diagrams, the linked model card and the four external framework destinations. The publisher’s plain-text overview was also captured. Global navigation and further links from the individual guides were outside the crawl scope.

Each SHA-256 below identifies the UTF-8 Markdown returned by GroktoCrawl. HTML was also retained for the overview and all 16 guides so embedded cards, tabs and code remain available. The archive manifest records source URLs, byte counts and digests for the captures.

| Source | Markdown SHA-256 |
| --- | --- |
| [Overview](https://gemma.ai/tuning/) | `7dd04ebf64454e006b00d87d70103910241c81343f80098155cfd8065480d75c` |
| [Best practices](https://gemma.ai/tuning/best-practices/) | `db4c3f8c3b90066154b1890cdec05a0bc33ff75314209c6afc2d2af772dd5b74` |
| [Dataset formatting](https://gemma.ai/tuning/datasets-formatting/) | `586d72f73d24f2a9341262f1854106a4899cf2a1474e8c2b2f4bde93b2303a02` |
| [Continued pre-training](https://gemma.ai/tuning/continued-pretraining/) | `ffc45f2f411f8898cf9db34022ce93a11f20c0b5aa9c972eae652e14452e4d9b` |
| [Custom chat templates](https://gemma.ai/tuning/custom-chat-template/) | `912fbe84e875276ae08bc49319e1bea5187085d2ca012c061bcb0ebcc28e6483` |
| [LoRA and QLoRA](https://gemma.ai/tuning/qlora/) | `80c98f9a5a8ce09d9951d0e3906da41550e9b8a449677cd6139a8bbb63795d76` |
| [Full fine-tuning](https://gemma.ai/tuning/full-finetune/) | `381ab3e69fa291892a58e49b1020a42ce45fe9ad8cbfc065a52a698d0070c37c` |
| [MoE fine-tuning](https://gemma.ai/tuning/moe-finetune/) | `bc1f97787bb7ce459b3bd873d0f9c100c59a7415913bd2a7090b5fe8966ae778` |
| [Reserved tokens](https://gemma.ai/tuning/unused-tokens/) | `2d6999e61265cd604204ec1f4dda1ed4578b2006bbd1badd7a4a9f76f42e65b4` |
| [Vision fine-tuning](https://gemma.ai/tuning/vision-qlora/) | `8237610cf98cfd217ef15211d2321367d1276c81f71af983546e16b0e6599cc3` |
| [Audio fine-tuning](https://gemma.ai/tuning/audio-qlora/) | `f881403e0122483e2ec27c44a5c41fe1e429c9064e8aaa44aa099d18374d0228` |
| [Preference optimization](https://gemma.ai/tuning/preference-alignment/) | `e2d3a76ccfd0759a78c07d4cfe7dfef4cfbabe981866c545a6c5c22275021021` |
| [Verifiable rewards](https://gemma.ai/tuning/reinforcement-learning/) | `81000013eb5d01917194e108fe727810d1555323ee70edf7572c9ea4d64b8e9c` |
| [Scaling](https://gemma.ai/tuning/scaling/) | `71fc5cb87d32a9d13ad012491babe7d69913e3667d72ceb3654d52c81d720bb0` |
| [Export](https://gemma.ai/tuning/export/) | `059cf97f39aa633bcf3eb38cf59588a3420fa47b9a0a90d2eb071241ce948b4d` |
| [Unsloth](https://gemma.ai/tuning/unsloth/) | `2bd937df72bfcfcfedb4c022a292dbfd4c356658327268e163bc4b2576793dcc` |
| [Gemma trainer skill](https://gemma.ai/tuning/gemma-trainer/) | `1d78e660aefe6b6fba2dfa2bef87ece22a2852a2eb45568e00484cc21badf2a9` |
| [Publisher’s Markdown overview](https://gemma.ai/tuning.md.txt) | `7c1205167e67041e38853bb73bb2008e3c39cef1546c86001f2b76da6ae33c2f` |
| [Gemma 4 model card](https://gemma.ai/models/gemma-4/model-card/) | `9adbc93a4b8d8fe1c4a3afdd064f31f8bbcab88f7bcbb32b6a3545de7fc738c0` |
| [TRL](https://huggingface.co/docs/trl) | `5f712cad0576ab41bb2aee302ecdc7d7045072ea0cb89017f98451b4e6a68f0f` |
| [Axolotl Gemma 4](https://docs.axolotl.ai/docs/models/gemma4.html) | `9684e195b98a86cc6839ab9f98fa8157a11ae5ba49cfb3a457d9fb41ac98d4dd` |
| [Managed open-model tuning](https://cloud.google.com/vertex-ai/generative-ai/docs/models/open-model-tuning) | `f5d27182c4567035f339980ac472719dd63e2e7f4e3fa795f3d8ad17988479d4` |
| [GKE framework link](https://cloud.google.com/kubernetes-engine/docs/tutorials/finetune-gemma-gpu) | `03cea10686692feb6d1a926aae6ecdbddbf055b324b133a7a2b0833295b51dda` |

## Extraction notes

- The overview Markdown dropped the interactive path map, the framework cards and the next-steps cards. Compare the captured HTML, the publisher’s Markdown and the rendered overview to recover those links.
- The export Markdown omitted the tabbed vLLM commands. The original HTML and rendered page contain both the merged-checkpoint and separate-adapter examples. GroktoCrawl flagged low Markdown volume for this page.
- The GKE training URL redirected to a general inference page. The managed tuning link redirected to open-model tuning documentation. Neither response established managed support for the requested Gemma 4 checkpoint.
- The overview reports example memory use at 2,048 tokens. The MoE guide specifies the quantization backend needed for its smaller memory estimate. The model card supplies the modality and context table. No model training or export was run while preparing this reference.

## Overview diagrams

- [Training stages](https://gemma.ai/assets/tuning/overview_01_post_training_stages.svg)
- [Adaptation methods](https://gemma.ai/assets/tuning/overview_02_adaptation_spectrum.svg)
- [Training memory](https://gemma.ai/assets/tuning/overview_03_vram_anatomy.svg)
- [Checkpoint comparison](https://gemma.ai/assets/tuning/overview_04_pt_vs_it_checkpoints.svg)
