# ESP32 hardware-test automation research brief

Date: 2026-10-11. Requested by Magnus. Track: comprehensive technical investigation.

## Question and decision

Which documented testing mechanisms and failure boundaries should enrich the ESP32 skill so an agent can plan and execute a bounded hardware feedback loop with trustworthy evidence?

## Scope fixed before further retrieval

Include primary ESP-IDF, pytest-embedded, hardware-lab orchestration, network fault injection, OTA/recovery, and the video's source repository. Prefer current documentation, recording the observed version; retain older material only when explicitly version-qualified. Exclude model speed/productivity claims, vendor-independent compatibility promises, production certification, new wrapper development, and live hardware operations. Use the video as an attributed example, not proof of our local runtime. English captions cover the spoken presentation; they do not independently establish visual demonstrations or hardware results.

Search angles: native test execution; fixture ownership and commissioning; independent oracles and fault injection; firmware identity/recovery and reproducible evidence. Stop when each angle has actionable source-to-claim closure and remaining uncertainties are explicit, not at an arbitrary source count.

## Durable destination

This tracked report package preserves scope, source-level extraction, exclusions, synthesis, and assertion challenges. The skill's focused reference and worksheet preserve the operational recommendations. No hardware is attached or commissioned by this change; documentation validation cannot establish behavioral uplift.

## Findings

The skill benefits from the video's explicit hardware feedback loop, refined by native testing and lab-control documentation. The result is a bounded, evidence-preserving procedure with distinct test tiers, independent oracles, fixture ownership, partial-setup cleanup, layer-specific faults, and configured recovery tests. Confidence is high in the documented mechanisms, moderate in this unexecuted cross-source design, and unassessed for runtime effectiveness.

## Findings and source closure

| Finding | Evidence | Implementation decision |
|---|---|---|
| A fast host/target/bench/field ladder needs explicit claim boundaries | V1, D1, D3, D4 | Test real production logic, retain physical cases, name simulator limits and reset stages. |
| A native test invocation may mutate hardware during setup | D2 | Confirm target/build/recovery before invoking fixtures; bind running identity to artifacts. |
| Commissioning cannot rule out later fixture failure | V1/R1's stronger claim; L1, L2, P1 show ownership/state/cleanup obligations | Recheck topology, separate infrastructure errors, own shared resources, handle failure before yield. This qualification is engineering synthesis, not a measured contradiction of the video demo. |
| Fault evidence is specific to the injected layer | T1, O1 | Separate TCP impairments from radio/DNS/BLE claims; verify configured OTA state and eligible fallback images. |
| Instrumentation and missing observations constrain acceptance | H1, A1 | Keep release/test configuration differences, incomplete traces, skips and rerun history visible. |

Independent oracles, stale-message correlation, bounded loops and immutable failure history are conservative engineering recommendations synthesized for this skill; no source is presented as proving their causal uplift. Source-level records and limitations are in [sources.md](sources.md).

## Confidence and unresolved questions

Official ESP-IDF/pytest docs support mechanism semantics. labgrid and Toxiproxy provide maintainer examples with different scope; the video and its README share an author and are not independent confirmations. Mutable stable/latest/main documents require installed-version revalidation. No board, controlled AP, broker, meter, or instrument was commissioned. Therefore flashing/reset details for a real target, electrical fixture design, actual restore behavior, timing/current acceptance, Codex compatibility with the external harness, and real-output behavioral improvement remain unresolved.

Stop rationale: each scoped search angle has actionable primary-source closure and explicit limitations. Broader certification, RF qualification or statistical reliability would require a separate hardware/domain investigation rather than more generic guidance.

## Durable artifact inventory

- This brief: scope, decision, synthesis, confidence and open questions.
- [sources.md](sources.md): every retained source, reusable extraction, provenance, exclusions and retrieval failures.
- [assertion-challenges.md](assertion-challenges.md): seven new case rubrics, with satisfying, contradictory and missing-evidence examples; no generated behavioral grades.
- `esp32-development/references/hardware-test-automation.md`: focused operational guidance and primary links.
- `esp32-development/templates/hardware-test-plan.md`: portable plan/run record.
- `esp32-development/references/source-index.md`: topic-specific refresh; older topic dates retained.

All retained sources and material findings are represented in tracked artifacts. Structural checks and schema validation are recorded at delivery; they do not establish hardware success or behavioral uplift.

The separate [trigger-review.md](trigger-review.md) records three positive and two near-miss description probes as an author routing review, not activation-rate evidence.
