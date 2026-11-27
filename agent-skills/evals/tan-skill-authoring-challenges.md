# Eval challenges

## separate-mechanical-check-and-judgment

| Assertion | Satisfying | Contradictory near miss | Omission |
|---|---|---|---|
| Reuses the existing command and supplies an invocation with required inputs and evidence output. | Uses the current runner with target revision, output path and structured result. | Writes a second checker from scratch that invents a different result contract. | Names no concrete entry point or output. |
| Retains failure evidence and limits the meaning of a recorded exit status. | Explains the known failure and reports the status and artifact under those inputs. | Turns any green exit into a user-behavior pass. | Omits the failure path or evidence boundary. |

## hide-paired-treatment-and-grade-observed-activity

| Assertion | Satisfying | Contradictory near miss | Omission |
|---|---|---|---|
| Moves treatment cues and the rubric out of candidate-visible paths and files while preserving the natural test request. | Uses neutral project paths with a private arm map and removes the rubric from both workspaces. | Deletes the word test or hides the path while leaving the rubric accessible. | Omits either artifact leakage or prompt preservation. |
| Keeps task, model, tools and budget comparable across the skill arms. | Names the skill as the differing factor and fixes other stated inputs. | Changes model effort in the new skill arm and attributes gains to the skill. | Omits the matched conditions. |
| Uses observed activity where available and treats a missing trace as unobserved. | Cites the recorded file-open operation and marks the other arm unobserved. | Treats the assistant’s claim as a trace or converts a missing trace to a negative observation. | Gives no evidence distinction. |
