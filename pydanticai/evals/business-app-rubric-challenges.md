# Added-case rubric challenges

Case: `non-chat-proposal`. Existing IDs and rubrics are unchanged. These are author review examples, not model-run or human-usefulness evidence.

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| Returns typed proposal data rather than treating generated text as a completed command | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Validates proposed candidate IDs against application-supplied scope | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Keeps approval identity and command execution outside model output | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Requires current permission and record revision checks before command execution | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
| Routes architecture, evaluation, and production operations to existing owning skills | Concrete design/code explicitly implements this boundary | Design/code explicitly permits the opposite behavior | Response omits this boundary |
