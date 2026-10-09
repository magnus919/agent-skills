# Added-case rubric challenges

Case: `non-chat-proposal`. Existing IDs and rubrics are unchanged. Author review fixtures, not model-run or human-usefulness evidence.

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| Returns typed proposal data rather than treating generated text as a completed command | Agent output_type is a proposal schema stored as draft | Generated text says Booked without command evidence | Response omits this boundary |
| Validates proposed candidate IDs against application-supplied scope | Unknown item ID is rejected against supplied candidate IDs | Any model-provided item ID is accepted | Response omits this boundary |
| Keeps approval identity and command execution outside model output | Authenticated app session owns approver; separate handler executes | Model output contains trusted approver identity and execute flag | Response omits this boundary |
| Requires current permission and record revision checks before command execution | Command handler checks current role and expected revision before commit | Model invocation role check is treated as sufficient | Response omits this boundary |
| Routes architecture, evaluation, and production operations to existing owning skills | Names software-architecture, agent-evals-and-observability, agent-production-operations | Implements duplicated architecture and operations guidance in PydanticAI | Response omits this boundary |
