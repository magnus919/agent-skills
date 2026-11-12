# Engineering workflow research: design review and code context

## Research question

Which patterns from a public engineering workflow are concrete enough to improve this catalog's design review and codebase analysis skills, while avoiding product-specific process or unsupported claims about quality?

## Source snapshot and method

The review used the public repository at commit 0997679a1cc3cfe09206160a85f9379f47101053 (2026-11-12). It examined onboarding and FAQ material, review and resolution skills, reviewer personas, design/readiness standards, context-map examples, drift-report guidance, host-specific notes, packaging code, and unit and integration tests. The source contains workflow instructions, prompt and persona documents, reusable standards, and distribution helpers; it does not provide evidence that following the workflow causes a measured improvement in engineering outcomes.

Primary source links: [workflow overview](https://github.com/google/elephant-goldfish-model/blob/0997679a1cc3cfe09206160a85f9379f47101053/docs/getting_started.md), [workflow FAQ](https://github.com/google/elephant-goldfish-model/blob/0997679a1cc3cfe09206160a85f9379f47101053/docs/faq.md), [review boundary](https://github.com/google/elephant-goldfish-model/blob/0997679a1cc3cfe09206160a85f9379f47101053/docs/site/workflow.md), [review loop](https://github.com/google/elephant-goldfish-model/blob/0997679a1cc3cfe09206160a85f9379f47101053/skills/egm-review-loop/SKILL.md), [finding resolution](https://github.com/google/elephant-goldfish-model/blob/0997679a1cc3cfe09206160a85f9379f47101053/skills/egm-resolve/SKILL.md), [package builder](https://github.com/google/elephant-goldfish-model/blob/0997679a1cc3cfe09206160a85f9379f47101053/scripts/pack_plugin.py), [scenario-structure test](https://github.com/google/elephant-goldfish-model/blob/0997679a1cc3cfe09206160a85f9379f47101053/tests/unit/test_scenario_coverage.py), [native host-isolation probe](https://github.com/google/elephant-goldfish-model/blob/0997679a1cc3cfe09206160a85f9379f47101053/tests/integration/test_codex.py), and [trace-evidence limits](https://github.com/google/elephant-goldfish-model/blob/0997679a1cc3cfe09206160a85f9379f47101053/tests/integration/opencode_trace_verifier.py).

## Code and test evidence

The production script surface is distribution-oriented: the package builder creates runtime folders and reproducible ZIPs, validates their contents, and rejects unsupported hooks or dependencies. The review workflow itself is expressed mainly in skill and standards documents rather than a single runtime orchestrator. The scenario-coverage unit test checks that every skill has a nonempty scenario set with required fields; that is structural coverage, not a semantic quality verdict.

The host-specific evidence is stronger but narrower. An opt-in native integration test uses the host's actual subagent parameter, checks a parent-only marker, and verifies the child does not see it. This is the kind of direct probe needed to support an isolation claim for that host/version. Separately, the exported-trace verifier explicitly says its read evidence does not establish full file coverage, context isolation, or transcript authenticity. These boundaries support conditional wording in the catalog: verify the real host schema and runtime when available, and keep an untested boundary marked unknown.

## Findings and catalog opportunities

| Source observation | Transferable lesson | Catalog change |
|---|---|---|
| The getting-started guide permits a lighter path for simple, understood changes, while the FAQ calls out the time and attention cost of reviews and documentation. | Match process depth to consequence, uncertainty, reversibility, and blast radius. The existence of an engineering task alone does not justify a multi-review process. | Extend the spec-driven-development review guidance with a risk-scaled independent review lane and explicit stop conditions. |
| Reviewers receive a selected artifact and supporting materials, while the drafting conversation is withheld. The host-specific documentation cautions that a fresh session may still share project instructions, memory, and filesystem state. | Review the written decision record first, but describe the review boundary only as strongly as the host can enforce. A new agent identity is not proof of isolation. | Add a reader reconstruction step and require recording reviewer inputs and host limitations. |
| The review workflow separates comprehension, critique, and readiness, with selectable lenses and a bounded review loop. | Use a small set of relevant lenses and separate a failed or unavailable reviewer from a completed review with no findings. | Record reviewer status, findings, dispositions, candidate identity, and re-review scope in the existing review template. |
| Finding resolution asks for visible evidence when contesting a claim and routes absent authority to an owner. | A disagreement is not a rebuttal. Consequential missing facts need a named decision path; automated suggestions should not silently make the decision. | Preserve evidence-backed fix, contest, escalate, and accept/defer dispositions. Keep the human or accountable owner as decision maker. |
| Context templates capture component contracts, while drift analysis compares recorded intent with implementation. | A bounded, source-linked context map is often more useful than a repository-wide dump. Code/document differences need triage, not automatic edits. | Add a subsystem context-map reference and template to software-architecture-analysis, with explicit revision, evidence, interface, invariant, side-effect, verification, and unknown fields. |
| The testing guide distinguishes static packaging/frontmatter checks from host integration probes; scenario tests include textual checks. | Structural validation, response-quality grading, and runtime isolation are different evidence classes. A keyword match cannot establish correctness or actual tool isolation. | Add challenge examples for new output-quality cases and state that evals are rubric probes, not measured efficacy. Keep host capability claims conditional. |

## Implementation decisions

1. Reuse the existing spec pipeline's review records and risk modes rather than creating another general-purpose review skill.
2. Add a focused independent design review reference, update the existing review template, and add an optional standard-library helper that hashes only the explicitly selected target and context files. The helper emits paths, sizes, file hashes, and a deterministic bundle hash; it does not copy file contents or prove reviewer access, isolation, or correctness.
3. Add output-quality cases for intent reconstruction, risk scaling, reviewer failure status, unsupported verbal context, and changed-candidate invalidation. Include satisfying, near-miss, and omitted-evidence challenges; these are authored cases, not evaluation runs.
4. Add a subsystem context-map reference and contract template to architecture analysis. Keep existing architecture health, coupling, and clean-room design workflows as the path for broader analysis.
5. Route from design review to source-grounded architecture analysis, approved delivery planning, agent-evaluation methodology, and verified PR delivery where appropriate.

## Limits and cautions

The examined material is primarily workflow text and prompt/persona assets; ancillary scripts emphasize packaging and validation rather than measuring downstream engineering performance. The reviewed sources provide examples and process recommendations, not causal or comparative efficacy evidence. Independent context is host-dependent, review findings can be noisy, and more lenses add cost. The additions therefore avoid quality-improvement claims, make risk and boundaries explicit, preserve human authority over consequential decisions, and keep each map/review scoped to a decision.
