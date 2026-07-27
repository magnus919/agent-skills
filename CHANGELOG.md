# Changelog

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
