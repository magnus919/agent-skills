# Changelog

## [0.7.0](https://github.com/magnus919/agent-skills/compare/v0.6.0...v0.7.0) (2026-08-08)


### Features

* add personalized travel-guide skill ([c446858](https://github.com/magnus919/agent-skills/commit/c44685800ed4b2d71e7d98eaab555d3e5742d931))
* **linear:** project mutations and richer issue verbs in CLI ([#288](https://github.com/magnus919/agent-skills/issues/288)) ([b8a5092](https://github.com/magnus919/agent-skills/commit/b8a5092c2664ed8d86e2d3babe7b25e63c91b948)), closes [#287](https://github.com/magnus919/agent-skills/issues/287)
* **skill:** add anydoc — office documents to GitHub-Flavored Markdown ([#295](https://github.com/magnus919/agent-skills/issues/295)) ([f37dc73](https://github.com/magnus919/agent-skills/commit/f37dc7382900de896be336f57377ad8546a45aa9))
* **skill:** add collaboration & business-app tool layer (Slack, Notion, email, CRM, payments) ([#269](https://github.com/magnus919/agent-skills/issues/269)) ([3256a87](https://github.com/magnus919/agent-skills/commit/3256a87bcb59c4a8b5ca622d97b192792495dca5))
* **skill:** add documents family skill (PDF / Word / Excel / PowerPoint) ([#262](https://github.com/magnus919/agent-skills/issues/262)) ([c49666e](https://github.com/magnus919/agent-skills/commit/c49666e29a29600d2cacb30de75e96d273d102f1))
* **skill:** add dsm5 — evidence-based companion to the DSM-5-TR ([#276](https://github.com/magnus919/agent-skills/issues/276)) ([d346970](https://github.com/magnus919/agent-skills/commit/d346970bf8e4d0a2a907b65ae02adced5665485b))
* **skill:** add genius-life creativity practice skill ([#299](https://github.com/magnus919/agent-skills/issues/299)) ([9a42be5](https://github.com/magnus919/agent-skills/commit/9a42be585e489d9fb429fcf390f18cf38bf3de32))
* **skill:** add mobile development skill (iOS / Android / Flutter / React Native) ([#248](https://github.com/magnus919/agent-skills/issues/248)) ([#268](https://github.com/magnus919/agent-skills/issues/268)) ([f687218](https://github.com/magnus919/agent-skills/commit/f68721873ef1aca36b139c6a543d2a3a0a9ba813))
* **skill:** add Playwright skill (E2E testing + scraping + headless browsing) ([#264](https://github.com/magnus919/agent-skills/issues/264)) ([ac1beb1](https://github.com/magnus919/agent-skills/commit/ac1beb117d8d8f9b6be38b7e5699485d76121af6))
* **skill:** add PostgreSQL operational skill ([#245](https://github.com/magnus919/agent-skills/issues/245)) ([#265](https://github.com/magnus919/agent-skills/issues/265)) ([cd14da2](https://github.com/magnus919/agent-skills/commit/cd14da26ccb2625efc1f6e069b21dcede192af5d))
* **skill:** add scripts, templates, and evals to backend-engineering and frontend-engineering ([#256](https://github.com/magnus919/agent-skills/issues/256)) ([48c1a1e](https://github.com/magnus919/agent-skills/commit/48c1a1e6f594d8b0ae9c87d08792dffcc2c9db07))
* **skill:** add telemetry skill (Prometheus + OpenTelemetry + Loki) ([#246](https://github.com/magnus919/agent-skills/issues/246)) ([#266](https://github.com/magnus919/agent-skills/issues/266)) ([f83d48b](https://github.com/magnus919/agent-skills/commit/f83d48ba53ca4908cba3a66bfa24af8c53b49d3c))
* **skill:** add Terraform operational skill ([#263](https://github.com/magnus919/agent-skills/issues/263)) ([00abbf9](https://github.com/magnus919/agent-skills/commit/00abbf90a4b370a9557ca2a32fa29bae0d641b1d))
* **skill:** add vLLM inference-serving skill ([#247](https://github.com/magnus919/agent-skills/issues/247)) ([#267](https://github.com/magnus919/agent-skills/issues/267)) ([6181f17](https://github.com/magnus919/agent-skills/commit/6181f1746dc23abceaa713fe9af3bd37e8409436))
* **skill:** add writing skill for the full writing lifecycle ([#301](https://github.com/magnus919/agent-skills/issues/301)) ([ecdfc65](https://github.com/magnus919/agent-skills/commit/ecdfc658c11e8f2181349efe6ae9c9f4c6c718b1))
* **skill:** beef up ml-engineering with scripts/templates/evals ([#257](https://github.com/magnus919/agent-skills/issues/257)) ([92299e1](https://github.com/magnus919/agent-skills/commit/92299e1238b105c92c52b177eaa008b625d324df))
* **skill:** cross-pollinate the new tool wave into catalog routing ([#275](https://github.com/magnus919/agent-skills/issues/275)) ([6f67a34](https://github.com/magnus919/agent-skills/commit/6f67a34ef1fb2ca5334270f74a3e39826cbcfce0))
* **skill:** rename writing skill to writers-helper ([#302](https://github.com/magnus919/agent-skills/issues/302)) ([6fe5aed](https://github.com/magnus919/agent-skills/commit/6fe5aed86eedf88bcdbe2846731ca6def5833c4d))
* **skill:** thicken platform-engineering with evals, templates, and deeper cloud/IaC references ([#255](https://github.com/magnus919/agent-skills/issues/255)) ([abe1ab3](https://github.com/magnus919/agent-skills/commit/abe1ab3a0003a4c4f865387476a36ea8cb21066f)), closes [#238](https://github.com/magnus919/agent-skills/issues/238)
* **validation:** enforce 60K-char cap on skill reference files ([#279](https://github.com/magnus919/agent-skills/issues/279)) ([3eb7bd4](https://github.com/magnus919/agent-skills/commit/3eb7bd4096a8b3d2f7f3a27f52b2b617fd8a6b31))


### Bug Fixes

* **anydoc:** clarify rendered-layout inspection route ([#297](https://github.com/magnus919/agent-skills/issues/297)) ([43fd4b9](https://github.com/magnus919/agent-skills/commit/43fd4b9518e47e6392a8fbbd31d772900a194fe7))
* **calculator:** honest burn-multiple and runway labels, surface model assumptions ([#274](https://github.com/magnus919/agent-skills/issues/274)) ([f9db3db](https://github.com/magnus919/agent-skills/commit/f9db3dbe4b94930175ab4d621e6242078a60e7d4))
* correct vllm models-check test name and stripe cancel boolean ([#270](https://github.com/magnus919/agent-skills/issues/270)) ([0ff3734](https://github.com/magnus919/agent-skills/commit/0ff373467cc2230330dcc2512a6615ad5a395234))
* **evals:** reword expectations prose in agent-skills eval manifest ([#237](https://github.com/magnus919/agent-skills/issues/237)) ([#261](https://github.com/magnus919/agent-skills/issues/261)) ([d68c1b3](https://github.com/magnus919/agent-skills/commit/d68c1b3552360af931311b8aa56674bdb0125263))
* **raleigh:** skip token-gated imagery folders in discovery and canary ([#280](https://github.com/magnus919/agent-skills/issues/280)) ([e99c6d2](https://github.com/magnus919/agent-skills/commit/e99c6d29942a156b7867b9b8ed815095072453ce))
* repair dead cross-skill routing references in methodology skills ([#251](https://github.com/magnus919/agent-skills/issues/251)) ([0223e2b](https://github.com/magnus919/agent-skills/commit/0223e2bc18f345c472cf5f89e3f2533f9f8157fe)), closes [#234](https://github.com/magnus919/agent-skills/issues/234)
* **skill:** guard churn prints in saas-metrics human-readable output ([#259](https://github.com/magnus919/agent-skills/issues/259)) ([a45952d](https://github.com/magnus919/agent-skills/commit/a45952d9c148a2c61ffe2908de9d9f3771230204))
* SkillOpt 3-epoch optimization of forward-deployed-engineering bundle ([#294](https://github.com/magnus919/agent-skills/issues/294)) ([cff17c5](https://github.com/magnus919/agent-skills/commit/cff17c59748a679718d1e42be5a5719190bc3f90))
* SkillOpt optimization of travel-guide skill (3 epochs) ([29a367e](https://github.com/magnus919/agent-skills/commit/29a367e90bc84a53a31fa1722d286ed4c38dad17))
* **skill:** SkillOpt 3-epoch optimization — dsm5 navigation, decisions, and answer patterns ([#281](https://github.com/magnus919/agent-skills/issues/281)) ([5d10100](https://github.com/magnus919/agent-skills/commit/5d101007ef30a48f3a3f05c0a959f2aad1a25608))
* **skill:** split oversized dsm5 references into index + parts ([#278](https://github.com/magnus919/agent-skills/issues/278)) ([c312b36](https://github.com/magnus919/agent-skills/commit/c312b36166325a7afb476a2c109d0885b3b5408b))
* **skills:** reconcile fireflies CLI with live GraphQL schema ([#290](https://github.com/magnus919/agent-skills/issues/290)) ([eadb82e](https://github.com/magnus919/agent-skills/commit/eadb82e069f3e2595683f57be9a5ba4a89ca5ea2))

## [0.6.0](https://github.com/magnus919/agent-skills/compare/v0.5.0...v0.6.0) (2026-08-03)


### Features

* add CNCF Landscape technology selection skill ([622f341](https://github.com/magnus919/agent-skills/commit/622f341ea467616174592e036c5d3fa8f121ae03))
* add comic chat PNG renderer skill ([2494a66](https://github.com/magnus919/agent-skills/commit/2494a663952f32d5807f900804bafc05aa417352))
* add lightweight test-hardening path to neckbeard ([#230](https://github.com/magnus919/agent-skills/issues/230)) ([36d3fa8](https://github.com/magnus919/agent-skills/commit/36d3fa837e928951aa17bfc7ec4dc772f47becc6))
* **agent-production-operations:** add agent production operations bundle ([#229](https://github.com/magnus919/agent-skills/issues/229)) ([ac1ad5d](https://github.com/magnus919/agent-skills/commit/ac1ad5dbd905fe8de6ea3298896b56d845f30fc7)), closes [#201](https://github.com/magnus919/agent-skills/issues/201)
* binary-analysis skill with Ghidra backend ([0d4a365](https://github.com/magnus919/agent-skills/commit/0d4a3652e4ccb3c25869f5baca52a29f08ddbf44))
* **binary-analysis:** implement CLI skeleton with argparse, JSON envelope, and exit codes ([e9397bb](https://github.com/magnus919/agent-skills/commit/e9397bbb542b195e6c9741805bad491a13ff9ef5))
* **bundles:** define bundle manifests and lifecycle capability matrix ([#203](https://github.com/magnus919/agent-skills/issues/203)) ([#231](https://github.com/magnus919/agent-skills/issues/231)) ([aa893e3](https://github.com/magnus919/agent-skills/commit/aa893e3ec20594da4982f645a31b2675f0abdcf8))
* **capacity-and-cost-engineering:** add capacity-and-cost-engineering skill ([#199](https://github.com/magnus919/agent-skills/issues/199)) ([#224](https://github.com/magnus919/agent-skills/issues/224)) ([a471888](https://github.com/magnus919/agent-skills/commit/a4718886761af0f90438cfd7c14f2460f4dfff89))
* **ci:** add linting, formatting, coverage, and security configs ([476d7e1](https://github.com/magnus919/agent-skills/commit/476d7e11b02f2bee65a2368adff02d9366376791))
* **ci:** add mypy, radon, and deptry to CI pipeline ([bfe05ef](https://github.com/magnus919/agent-skills/commit/bfe05ef18aed5f90e17b2da4b725d1a4d565bfe1))
* **conditional-customer-success:** add conditional customer success skill ([#192](https://github.com/magnus919/agent-skills/issues/192)) ([#218](https://github.com/magnus919/agent-skills/issues/218)) ([1dd564e](https://github.com/magnus919/agent-skills/commit/1dd564e3d9eb8d73129332658d8b7504beeb0f89))
* **decompile:** implement decompile command with pseudocode, address map, and diagnostics ([3e4f07a](https://github.com/magnus919/agent-skills/commit/3e4f07a34cf14550802005c111f91eb76aa710b9))
* **doctor-bootstrap:** implement doctor, bootstrap, and version commands ([55c1451](https://github.com/magnus919/agent-skills/commit/55c145185fd88d51267f5fa776d67207546fd874))
* **domain-foundation:** implement canonical domain model with entities, enums, schemas, errors, and selectors ([3481663](https://github.com/magnus919/agent-skills/commit/3481663595a097a8cb5b1d9fa87db74024ff7813))
* **fake-backend:** implement FakeAdapter with controllable backend testing ([6184673](https://github.com/magnus919/agent-skills/commit/6184673f3585da829d5b64feaba1a6154f16ace4))
* fix remaining agent readiness signals for level 5 ([865a1e9](https://github.com/magnus919/agent-skills/commit/865a1e90c6bb6bdb23c2b182be2fddbf26fd0c17))
* **fix-coverage-config:** add .coveragerc with placeholder module omissions and exclude plain-text output helpers ([86b248e](https://github.com/magnus919/agent-skills/commit/86b248e89a2425fdff520be48eb6aa042f4c6579))
* **fix-fake-adapter-env:** add BINARY_FAKE_* env var support to FakeAdapter ([c408259](https://github.com/magnus919/agent-skills/commit/c408259a7269da8528c250961e6f52b0875df66b))
* **fix-missing-tests:** add register_binary(), clamp warnings in JSON envelope, and new tests ([50e48de](https://github.com/magnus919/agent-skills/commit/50e48deeb7b318b630a6fe4f645e9a34de176246))
* **function-queries:** implement functions, disassemble, and bytes CLI commands ([3cf347b](https://github.com/magnus919/agent-skills/commit/3cf347b06035f6651585686966d867e43e19a5d7))
* **ghidra-adapter:** implement GhidraAdapter skeleton with PyGhidra bridge ([9e8234f](https://github.com/magnus919/agent-skills/commit/9e8234f70f8df1d77b6ca6484f6942bc42f4739e))
* **implementation-planning:** add implementation planning skill ([#217](https://github.com/magnus919/agent-skills/issues/217)) ([f82515e](https://github.com/magnus919/agent-skills/commit/f82515e85d6620e962a93d6341be9d0474b83215)), closes [#186](https://github.com/magnus919/agent-skills/issues/186)
* **import-analyze:** implement binary import, analyze, and metadata commands ([f4e254a](https://github.com/magnus919/agent-skills/commit/f4e254ac6703005fcdb702b63aa64dbaaaa0dfa4))
* improve agent readiness with dev tooling, CI checks, and tests ([6b44d6f](https://github.com/magnus919/agent-skills/commit/6b44d6f490481de100667d900066024f88deafe3))
* **incident-learning:** add incident-learning skill ([#226](https://github.com/magnus919/agent-skills/issues/226)) ([4f14ce3](https://github.com/magnus919/agent-skills/commit/4f14ce3df6e447848392dd477de13a9b5531c7d8)), closes [#200](https://github.com/magnus919/agent-skills/issues/200)
* **json-contracts:** implement JSON contract consistency across all commands ([801a5be](https://github.com/magnus919/agent-skills/commit/801a5be65f2478dd8a04677be1c0f7a90093cd75))
* **migration-engineering:** add migration-engineering skill ([#222](https://github.com/magnus919/agent-skills/issues/222)) ([652521a](https://github.com/magnus919/agent-skills/commit/652521a09e16f222ada2a74ce6a7ed760396dc91))
* **neckbeard:** issue-to-PR delivery workflow ([#181](https://github.com/magnus919/agent-skills/issues/181)-[#185](https://github.com/magnus919/agent-skills/issues/185)) ([#208](https://github.com/magnus919/agent-skills/issues/208)) ([4a4958b](https://github.com/magnus919/agent-skills/commit/4a4958b6761bcdb4382770e4096b92f5a644fcf7))
* **privacy-engineering:** add privacy-engineering skill ([#202](https://github.com/magnus919/agent-skills/issues/202)) ([#225](https://github.com/magnus919/agent-skills/issues/225)) ([6f429a9](https://github.com/magnus919/agent-skills/commit/6f429a91b1a41505c512fe529dd10d67f3b141eb))
* **product-adoption:** add product adoption skill ([#214](https://github.com/magnus919/agent-skills/issues/214)) ([11a6595](https://github.com/magnus919/agent-skills/commit/11a6595d1ca9539fb97e118fdd17fb5026788905))
* **product-analytics-and-measurement:** add product analytics and measurement skill ([#213](https://github.com/magnus919/agent-skills/issues/213)) ([6b650b7](https://github.com/magnus919/agent-skills/commit/6b650b722c2657a45c2f97630bca9ca72e687fcf))
* **product-experimentation:** add product experimentation skill ([#212](https://github.com/magnus919/agent-skills/issues/212)) ([0b32a96](https://github.com/magnus919/agent-skills/commit/0b32a96521e72b21fa5a387da271f19365ce8c0f))
* **product-lifecycle-learning:** add product lifecycle learning skill ([#194](https://github.com/magnus919/agent-skills/issues/194)) ([#219](https://github.com/magnus919/agent-skills/issues/219)) ([2c247a1](https://github.com/magnus919/agent-skills/commit/2c247a17473edce9b41ccd90f59f01e42d22a7ca))
* **product-lifecycle:** add thin product-lifecycle bundle ([#227](https://github.com/magnus919/agent-skills/issues/227)) ([46b92aa](https://github.com/magnus919/agent-skills/commit/46b92aa489891e45be0bf3afe3d69021394c1737)), closes [#187](https://github.com/magnus919/agent-skills/issues/187)
* **product-operations-and-governance:** add product operations and governance skill ([#216](https://github.com/magnus919/agent-skills/issues/216)) ([7756266](https://github.com/magnus919/agent-skills/commit/77562664b87cb3d556e154600735b5a1eb863a95)), closes [#193](https://github.com/magnus919/agent-skills/issues/193)
* **product-roadmapping-and-portfolio:** add product roadmapping and portfolio skill ([#215](https://github.com/magnus919/agent-skills/issues/215)) ([5d95dd6](https://github.com/magnus919/agent-skills/commit/5d95dd6a303303244af42ca821e998a4454efbd3)), closes [#189](https://github.com/magnus919/agent-skills/issues/189)
* **production-excellence:** add thin production-excellence bundle ([#228](https://github.com/magnus919/agent-skills/issues/228)) ([8c05a07](https://github.com/magnus919/agent-skills/commit/8c05a076bb1a29700bdadc246f2bf7a93faff34c))
* **production-readiness:** add production-readiness skill ([#221](https://github.com/magnus919/agent-skills/issues/221)) ([2183c22](https://github.com/magnus919/agent-skills/commit/2183c221352a939636c278b54e10087b6fe31aa9))
* **project-lifecycle:** implement all project lifecycle commands and state machine ([756b50e](https://github.com/magnus919/agent-skills/commit/756b50e285cfa038de4731aeb6204b737885804a))
* **project-system:** implement workspace, manifest, locking, and cache ([defe46c](https://github.com/magnus919/agent-skills/commit/defe46c1386d4c518318e95ba557a2ad96f74a33))
* **qa-methodology:** add 2 stdlib-only CLI scripts and colocated pytest suite ([974fde0](https://github.com/magnus919/agent-skills/commit/974fde017cf6760d491caec7f4c0c79bb1b54b04))
* **qa-methodology:** add 3 new traditional QA references ([ff69b09](https://github.com/magnus919/agent-skills/commit/ff69b0982f036543392352c635ecbefff78893da))
* **qa-methodology:** add 5 fillable templates and 3 assets ([3325787](https://github.com/magnus919/agent-skills/commit/332578766db926695a31adc24060aa6d0665abe8))
* **qa-methodology:** add modern agentic references (ai-code-quality-gates, agentic-eval-design) ([aa8c027](https://github.com/magnus919/agent-skills/commit/aa8c027a6e2d0ed8fba3af93f3bd7ce6dfe1e3de))
* **qa-methodology:** add modern QA career levels and SDET engineering references ([9b10ff5](https://github.com/magnus919/agent-skills/commit/9b10ff546ae968b6df9909ae6f7192c148543d33))
* **qa-methodology:** add mutation-guided test hardening evidence workflow ([8bd042e](https://github.com/magnus919/agent-skills/commit/8bd042eae5a851419c3f6324e4709eb894a8e36f)), closes [#209](https://github.com/magnus919/agent-skills/issues/209)
* **qa-methodology:** add schema-v1 evals with 7 output-quality cases ([107d6d1](https://github.com/magnus919/agent-skills/commit/107d6d11631f70e957b16605ca0bdf4a098e833d))
* **qa-methodology:** rebuild as thin-index QA/SDET skill bundle ([726de89](https://github.com/magnus919/agent-skills/commit/726de898e8d8b81b9cfb2a13902f38d0cf8c63a0))
* **qa-methodology:** rebuild SKILL.md as thin index and rewrite README.md ([8b0220b](https://github.com/magnus919/agent-skills/commit/8b0220b75b62907e9c954cc7dc60584ba077b616))
* **qa-methodology:** refresh 5 traditional QA support references ([5bad13a](https://github.com/magnus919/agent-skills/commit/5bad13af568567529071f65d4cd756ac8492a1c8))
* **qa-methodology:** refresh traditional QA core references and split monolithic file ([966edcf](https://github.com/magnus919/agent-skills/commit/966edcf0c75e2eb64f4320e1f455d64776928ba5))
* **reference-queries:** implement xrefs, callers, callees, and callgraph CLI commands ([93b0431](https://github.com/magnus919/agent-skills/commit/93b04315a9cdfe987d7390aff947aae5df59dd4d))
* **release-engineering:** add release engineering skill bundle ([818d8ca](https://github.com/magnus919/agent-skills/commit/818d8cafa2b435b1556fdafa8603aa70f39cf01d))
* **reporting:** implement export-report and audit commands ([010a308](https://github.com/magnus919/agent-skills/commit/010a3086aa373afc82edb4a0947ee8cfee16be4a))
* **resilience-and-recovery:** add resilience-and-recovery skill ([#223](https://github.com/magnus919/agent-skills/issues/223)) ([c032580](https://github.com/magnus919/agent-skills/commit/c032580197f2f370d4f96895fafc09b36c21f4dd))
* **safety-hardening:** implement path security, output limits, memory limits, and report containment ([e62cf47](https://github.com/magnus919/agent-skills/commit/e62cf47a9b2b01905bfbf0864be7fe13365c7908))
* **search-trace:** implement search and trace commands with cross-area integration flows ([1ead735](https://github.com/magnus919/agent-skills/commit/1ead735513a00bfb3b8dc5a93a82cfb074e30072))
* **security-rules:** implement suspicious-apis and capability-map commands ([d005b9a](https://github.com/magnus919/agent-skills/commit/d005b9aadaa2e7404d4718a7a55877a40c000f20))
* **skill-content:** write SKILL.md and README.md for binary-analysis skill ([72d8462](https://github.com/magnus919/agent-skills/commit/72d8462f073cb20cdeb8dc6b48c08c9515bfc431))
* **skill-evals:** write 6 eval cases for binary-analysis skill ([f79124d](https://github.com/magnus919/agent-skills/commit/f79124d360ae4212816bf595a7ccff9425252a90))
* **skill-references:** write 11 reference files for binary-analysis skill ([a799e0f](https://github.com/magnus919/agent-skills/commit/a799e0f7eb46d48867f0ca9cff5b94c0b22d21f7))
* **structural-queries:** implement sections, entrypoints, imports, exports, symbols, and strings CLI commands ([7df699b](https://github.com/magnus919/agent-skills/commit/7df699ba20d94d09479104caafbad403962269db))
* **triage-diagnostics:** implement triage and diagnostics commands ([0e05960](https://github.com/magnus919/agent-skills/commit/0e05960dd6c53ffa2b07b929469ffa5a22c61ec8))
* **worker:** implement optional local worker with start/stop/status commands and one-shot fallback ([5e8f1d3](https://github.com/magnus919/agent-skills/commit/5e8f1d3aafbb5f06a2aa7898cd16a4d390db7012))


### Bug Fixes

* **ci:** add binary-analysis to deptry extend_exclude ([8ea4053](https://github.com/magnus919/agent-skills/commit/8ea4053e01826008582b9e942fdecae7c3932361))
* **ci:** add sys.path setup in test __init__.py for unittest discover ([4c7f5c4](https://github.com/magnus919/agent-skills/commit/4c7f5c42f49cdc9eba4c537a47f6fe2352b20ded))
* **ci:** add sys.path setup to all test sub-package __init__.py files ([f9354df](https://github.com/magnus919/agent-skills/commit/f9354df2870a97fe85d15e66ad1df1de94afc3f7))
* **ci:** add sys.path setup to individual binary-analysis test files ([736859e](https://github.com/magnus919/agent-skills/commit/736859eafa9ab7c40d0291479a6d87f4a6895055))
* **ci:** prevent sys.modules cross-contamination between test directories in check-artifacts ([96f0bd4](https://github.com/magnus919/agent-skills/commit/96f0bd4e46c8023cd5035aba2299df70562c2837))
* **ci:** use full path for deptry binary-analysis exclude ([b56183b](https://github.com/magnus919/agent-skills/commit/b56183bbabed58089bf79e3d571433e8fe6dd217))
* permit removal of eval-covered skills ([687d7d7](https://github.com/magnus919/agent-skills/commit/687d7d7c33510b7496c50052161596f34ad58eae))
* **product-strategy:** correct stale RICE reference ([#211](https://github.com/magnus919/agent-skills/issues/211)) ([8d30f22](https://github.com/magnus919/agent-skills/commit/8d30f22cb89508b2982c36b8a627a79944f5f2b6))
* **release-engineering:** address review findings in DORA asset, cadence, link, metrics script ([2b90656](https://github.com/magnus919/agent-skills/commit/2b906565d443bf7d460cfe1a8f5d5c258844de51))
* **release-engineering:** align 0.x version bumps with Release Please's minor-feature policy
* **release-engineering:** validate Keep a Changelog and Release Please formats
* relocate binary analysis skill ([6387f7f](https://github.com/magnus919/agent-skills/commit/6387f7f4752a2dd8fd7a92a7e640ec6b62c11698))
* require dated commitments for CoS tasks ([857dfc6](https://github.com/magnus919/agent-skills/commit/857dfc6e1cecccf94ec241a89be20bca3a539fb3))
* **security-ship:** ensure diagnostics have both recoverable values and add pagination cursors to security commands ([d04af37](https://github.com/magnus919/agent-skills/commit/d04af37602eae8304e4c089076c047a0eae8fb9c))
* **security-ship:** fix --limit routing, truncation warnings, and clean confirmation order ([7b0109b](https://github.com/magnus919/agent-skills/commit/7b0109b328c097e6c40c1ff07ac3ce4c01e98aa2))
* **security-ship:** fix three scrutiny blocking issues ([a20adde](https://github.com/magnus919/agent-skills/commit/a20adde298209480b49279aca84a5b6e3c54457e))
* state CoS task-capture boundary ([f285316](https://github.com/magnus919/agent-skills/commit/f285316206258471343c66ea9bfaf15f07f3bfbc))


### Reverts

* restore clean base64 import in helpers.py ([746df95](https://github.com/magnus919/agent-skills/commit/746df95150e7ec092c2d37daa8261f4c3d12004a))

## [0.5.0](https://github.com/magnus919/agent-skills/compare/v0.4.0...v0.5.0) (2026-07-27)


### Features

* add evidence-aware life coaching skill ([#146](https://github.com/magnus919/agent-skills/issues/146)) ([795d142](https://github.com/magnus919/agent-skills/commit/795d1423f87b6847e3d6d5e2f3900eb5063f255e))
* add Gibson cyberpunk skill ([#149](https://github.com/magnus919/agent-skills/issues/149)) ([daece12](https://github.com/magnus919/agent-skills/commit/daece120eebf7fbfa3aaef825bc4da606ed1bfd9))
* add harness adapter contract and reproducible eval run artifacts ([#130](https://github.com/magnus919/agent-skills/issues/130)) ([e83558a](https://github.com/magnus919/agent-skills/commit/e83558a6e3888e0df099955436e4f07b2d493485))
* add llama.cpp operations skill ([#145](https://github.com/magnus919/agent-skills/issues/145)) ([58457b4](https://github.com/magnus919/agent-skills/commit/58457b495ceee7b774c29e9a74c31d1b125262c8))
* add release-grade repeated and rubric-based skill evaluation ([#136](https://github.com/magnus919/agent-skills/issues/136)) ([0a80bda](https://github.com/magnus919/agent-skills/commit/0a80bda800159c45be5f43f6c5a33ee739307d1a)), closes [#106](https://github.com/magnus919/agent-skills/issues/106)
* expand Raleigh civic data skill ([eff14ca](https://github.com/magnus919/agent-skills/commit/eff14ca2b7b92fd5df7b55880d1686ca0a93585d))
* **grafana:** add operations skill ([4c824b7](https://github.com/magnus919/agent-skills/commit/4c824b7a09c1171ee921fe528f761596888c481d))
* **grafana:** add operations skill ([e304366](https://github.com/magnus919/agent-skills/commit/e30436691522e90f970818958bae1fd6c55c1945))
* **raleigh:** add fire protection proximity lookup ([#144](https://github.com/magnus919/agent-skills/issues/144)) ([1f5cd6a](https://github.com/magnus919/agent-skills/commit/1f5cd6a91c8568f43ac414f1c19899fbe2913ae9))
* **raleigh:** add first-class RFD incident workflows and normalize the 2026 schema ([#140](https://github.com/magnus919/agent-skills/issues/140)) ([0ca5c24](https://github.com/magnus919/agent-skills/commit/0ca5c242cea06808aa358c785594ea65b5c1dbd9)), closes [#122](https://github.com/magnus919/agent-skills/issues/122)
* **raleigh:** add first-class RPD incident workflows ([#139](https://github.com/magnus919/agent-skills/issues/139)) ([50be18b](https://github.com/magnus919/agent-skills/commit/50be18b8c2d2389b337e2e742c228a0f1217e531)), closes [#121](https://github.com/magnus919/agent-skills/issues/121)
* **raleigh:** add guarded fire report lookups ([12b650e](https://github.com/magnus919/agent-skills/commit/12b650e6dcff2e8799c8dacb5fe7a05f7b18c4fc))
* **raleigh:** add guarded fire report lookups ([4eaf5aa](https://github.com/magnus919/agent-skills/commit/4eaf5aa7ea0de865a757e47b7ecd5b4608402189))
* **raleigh:** add official public safety statistics ([b030f26](https://github.com/magnus919/agent-skills/commit/b030f2607c716b0e95fb0869b50539f2ffeb6ebf))
* **raleigh:** add Raleigh-Wake ECC active incident feed adapter ([#142](https://github.com/magnus919/agent-skills/issues/142)) ([d4ab656](https://github.com/magnus919/agent-skills/commit/d4ab656c50ca004746731faff62d86d0648fcfb0))
* **raleigh:** expand civic data skill ([903ea05](https://github.com/magnus919/agent-skills/commit/903ea0559ec66e1847ec1596314f82bb5bf97784))
* **raleigh:** expose official public safety statistics ([dcd6f59](https://github.com/magnus919/agent-skills/commit/dcd6f59fe3c3df022c25507e9700b739c41b2105))
* run isolated paired candidate and baseline skill evaluations ([#133](https://github.com/magnus919/agent-skills/issues/133)) ([390f3e3](https://github.com/magnus919/agent-skills/commit/390f3e341785166bdf987642499ac5e04a817ffb))
* **skill:** add PACE plan lifecycle ([e62152c](https://github.com/magnus919/agent-skills/commit/e62152cf6b10c447c84aa7fbee62d94816cd8a76))
* **skill:** add PACE plan lifecycle ([64383d9](https://github.com/magnus919/agent-skills/commit/64383d9aa5e5d3de501184d8b8f335c0e8b3773e))
* validate eval manifest coverage states ([#129](https://github.com/magnus919/agent-skills/issues/129)) ([a617cca](https://github.com/magnus919/agent-skills/commit/a617ccaf2d665330ca949f9719f980af46ed1c82))


### Bug Fixes

* align eval artifact schemas with runtime ([f49e670](https://github.com/magnus919/agent-skills/commit/f49e670c9f462eab06c5dc636d0b17452ecd07ea))
* allow incidental text in cyberpunk image briefs ([6b467df](https://github.com/magnus919/agent-skills/commit/6b467dffb2f24a6216c9ea3a08777d327c487e49))
* complete eval ratchet verification ([#109](https://github.com/magnus919/agent-skills/issues/109)) ([1e10a56](https://github.com/magnus919/agent-skills/commit/1e10a5619961a746ebd4117fc6e1364a36a88cf8))
* enforce eval coverage ratchet for complete changed skill directories ([#107](https://github.com/magnus919/agent-skills/issues/107)) ([fc8a895](https://github.com/magnus919/agent-skills/commit/fc8a8952ee65e8ab625c72fbd059e7d79ac19ca1)), closes [#102](https://github.com/magnus919/agent-skills/issues/102)
* harden paired evaluation isolation ([cb1579f](https://github.com/magnus919/agent-skills/commit/cb1579f23d49def4f9d5f8ae87652e8a126de55a))
* **life-coach:** simplify capability onboarding ([#148](https://github.com/magnus919/agent-skills/issues/148)) ([fdb00b4](https://github.com/magnus919/agent-skills/commit/fdb00b4aacd70fc7b99f848a83f41bad6dca5062))
* **llama-cpp:** harden operational diagnostics ([#147](https://github.com/magnus919/agent-skills/issues/147)) ([86ac280](https://github.com/magnus919/agent-skills/commit/86ac2804763c4666ae092e215b34c65c18b4ce8d))
* **raleigh:** bound publication source contracts ([cc26b4c](https://github.com/magnus919/agent-skills/commit/cc26b4cb279c42f28d06595032d30f45779d6d68))
* **raleigh:** enforce publication request contracts ([1bd7b06](https://github.com/magnus919/agent-skills/commit/1bd7b061121ca647c32eb447621209907a5c5029))
* **raleigh:** fail on missing statistics sections ([8becc22](https://github.com/magnus919/agent-skills/commit/8becc22822685286c501fa15cf151d2c3d9f256d))
* **raleigh:** normalize report probe failures ([f3dfb68](https://github.com/magnus919/agent-skills/commit/f3dfb68832a3834719434a99e34ac4d12bc1e936))
* **raleigh:** normalize statistics source failures ([07c2ae2](https://github.com/magnus919/agent-skills/commit/07c2ae2e8f5dbe02c4ca62ad0294c9c614df1241))
* **raleigh:** reject malformed content identifiers ([5f74b4d](https://github.com/magnus919/agent-skills/commit/5f74b4dde5a2319ef8c64269d020447773fb703c))
* **raleigh:** restore live RPD queries ([cfbcfb0](https://github.com/magnus919/agent-skills/commit/cfbcfb09ec1f1e9f70a50ca3c96bf852e959ef90))
* **raleigh:** restore live RPD queries ([4a23562](https://github.com/magnus919/agent-skills/commit/4a23562e5967b7a6cc6b42be8431053ab112d315))
* **raleigh:** validate included resource identifiers ([9f2e4b6](https://github.com/magnus919/agent-skills/commit/9f2e4b681c054eaae68b3edbf05c94ada8a89b09))
* **raleigh:** validate statistics response shapes ([bf69aa1](https://github.com/magnus919/agent-skills/commit/bf69aa1689d647f776054cd341eb6ecaa9dc056c))
* reject duplicate eval fixture paths ([cbe1b69](https://github.com/magnus919/agent-skills/commit/cbe1b6927a31dc6e54c1fa1b942b68b4b6e0dcfb))
* require causal layer maps for cyberpunk image briefs ([34fab96](https://github.com/magnus919/agent-skills/commit/34fab96b8eaed2e5ecb917152454e58fe8980ae7))
* require causal layer maps for cyberpunk image briefs ([34fab96](https://github.com/magnus919/agent-skills/commit/34fab96b8eaed2e5ecb917152454e58fe8980ae7))
* require causal layer maps for cyberpunk image briefs ([c514c85](https://github.com/magnus919/agent-skills/commit/c514c85fc1bd12b69d7a951bbbab9eb94d9c2f03))
* require evidence for Grafana dashboard defaults ([4b60a2e](https://github.com/magnus919/agent-skills/commit/4b60a2efa04b181e5ba4cca722c916b7a30743af))
* require evidence for Grafana dashboard defaults ([4ecc536](https://github.com/magnus919/agent-skills/commit/4ecc536ad18979b34a1032d976eee59f0a2f7453))
* **skill:** finalize PACE delivery evidence ([f62a5de](https://github.com/magnus919/agent-skills/commit/f62a5de4a0fba2cf089eb6182c4925c88b810631))
* **skills:** rename gibson-cyberpunk to cyberpunk ([#150](https://github.com/magnus919/agent-skills/issues/150)) ([1005462](https://github.com/magnus919/agent-skills/commit/10054621ce35c778ffefff2fec5f893da7b539a9))
* **verification:** preserve requested source fidelity ([#127](https://github.com/magnus919/agent-skills/issues/127)) ([547aed2](https://github.com/magnus919/agent-skills/commit/547aed2db9ddecfce56616e173e02b38a447fd27))

## [0.4.0](https://github.com/magnus919/agent-skills/compare/v0.3.0...v0.4.0) (2026-07-22)


### Features

* add Claude Code plugin marketplace (metadata-only catalog) ([#80](https://github.com/magnus919/agent-skills/issues/80)) ([3c8b6cd](https://github.com/magnus919/agent-skills/commit/3c8b6cd71cae6f36c34d9fca4b439b5d02388474)), closes [#76](https://github.com/magnus919/agent-skills/issues/76)
* add Codex plugin packaging (single-plugin, metadata-only) ([#83](https://github.com/magnus919/agent-skills/issues/83)) ([0f2aaf1](https://github.com/magnus919/agent-skills/commit/0f2aaf1583d8e8d0a9a8d9bd7e2e078e2ac16f17))
* add generated llms.txt skill index ([#93](https://github.com/magnus919/agent-skills/issues/93)) ([cde4a67](https://github.com/magnus919/agent-skills/commit/cde4a67ef44c6c9ff2039bb8deee8897406d03f2)), closes [#78](https://github.com/magnus919/agent-skills/issues/78)
* add neckbeard, an evidence-driven SDLC skill bundle ([#81](https://github.com/magnus919/agent-skills/issues/81)) ([e167718](https://github.com/magnus919/agent-skills/commit/e1677183cd91b9ae09ee26ee9f5fa124246fdc5b))
* add programming-principles skill (14 classic software books) ([#92](https://github.com/magnus919/agent-skills/issues/92)) ([1037324](https://github.com/magnus919/agent-skills/commit/1037324c2a94d5d31b886bf4faa2a927f53794df))
* eval coverage ratchet — gate new skills, track coverage, ratchet thresholds ([#99](https://github.com/magnus919/agent-skills/issues/99)) ([be0c8df](https://github.com/magnus919/agent-skills/commit/be0c8df5e20d75761cf540e36a5fded303f86c51)), closes [#90](https://github.com/magnus919/agent-skills/issues/90)
* **qa-methodology:** add ci-failure-triage and test-debugging references ([#94](https://github.com/magnus919/agent-skills/issues/94)) ([08fafac](https://github.com/magnus919/agent-skills/commit/08fafacd6cabf7ffb23745fd371655f2deaef88b))
* validate changed skill descriptions ([#97](https://github.com/magnus919/agent-skills/issues/97)) ([c092a14](https://github.com/magnus919/agent-skills/commit/c092a14c8ecc81927031d491fc277b46757aaf3a))


### Bug Fixes

* close skill quality lint gaps ([#98](https://github.com/magnus919/agent-skills/issues/98)) ([dd457f1](https://github.com/magnus919/agent-skills/commit/dd457f1170065a7e84b78bf560f23732796e5e0f))
* correct bundle skill paths in Codex plugin manifest ([#91](https://github.com/magnus919/agent-skills/issues/91)) ([3d650da](https://github.com/magnus919/agent-skills/commit/3d650dad774c02f5efdde0ffcfcb09bc8d55ec34))
* pin release-please manifest to v0.3.0 ([#72](https://github.com/magnus919/agent-skills/issues/72)) ([0e8bc26](https://github.com/magnus919/agent-skills/commit/0e8bc261839248a8a9c2521d2bafd5eaa686e9c1))
* SkillOpt 3-epoch optimization of neckbeard — description, routing, stage alignment ([#84](https://github.com/magnus919/agent-skills/issues/84)) ([051bf2a](https://github.com/magnus919/agent-skills/commit/051bf2a9c61e14c5e8f1d7b353d84926eea74ddc))
