# Specialization assertion challenges

2026-10-13; appended rubric v1 for new stable case IDs. Existing cases unchanged.
Author-written satisfying/contradictory/omitted examples, not executed model grading.
Artifact checks require a complete inventory; semantic claims require readable artifacts.
Presence of a filename or policy phrase does not prove correct design or execution.

## coding-provenance-contract

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Inventory includes dataset-contract.md. | Complete inventory lacks the file. | Inventory absent. |
| 2 | Split repository families before mutation. | Shuffle variants from one family into all splits. | No derivation/split ordering. |
| 3 | Identical prompts leak despite distinct targets. | Different answers make the prompt independent. | No prompt-overlap decision. |
| 4 | Pin source and review rights with evidence. | Nonempty rights field certifies legal use. | No rights decision or revision. |
| 5 | Use processor-aware structured tool traces. | Flatten tool calls as text for the helper. | No tool-format handling. |

## verifier-challenge-receipts

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Inventory includes reward-contract.md. | Complete inventory lacks it. | Inventory absent. |
| 2 | Inventory includes challenge-receipts.json. | Complete inventory lacks it. | Inventory absent. |
| 3 | Gold patch passes; wrong edge cases fail. | Generated tests reject gold and are accepted anyway. | No oracle challenges. |
| 4 | Task-correct solution outranks empty lint-clean output. | Empty code wins style reward. | No component ordering. |
| 5 | Timeout/infra retain unknown task truth. | Timeout is labeled a correct or known wrong answer. | No failure taxonomy. |
| 6 | Execution stages remain not run. | Authored receipts are called executed verification. | No runtime status. |

## local-grpo-budget-signal

| Assertion | Satisfying | Contradiction | Omission |
|---|---|---|---|
| 1 | Inventory includes local-grpo.md. | Complete inventory lacks it. | Inventory absent. |
| 2 | Measure rollout KV/state plus optimizer/activations. | SFT peak alone proves RL fits. | No complete memory budget. |
| 3 | Inspect zero-variance groups and exploration/verifier. | More epochs guarantee learning from all-zero rewards. | No signal diagnosis. |
| 4 | Disallow paging unless all-VRAM behavior is proved. | Paged optimizer automatically satisfies all-VRAM. | No residency policy. |
| 5 | Representative model/group/length pilot precedes fit claim. | Coinbase 96GB run proves our 16GB fit. | No pilot criterion. |
