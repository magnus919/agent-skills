# Evaluation design

`evals.json` contains ten stable output-quality cases and 35 semantic assertions. The prompts supply the critical scenario facts so that a grader can judge the response without inventing current hardware results. The offline-parser case requires an implementation, guarding against stopping at references when development was requested.

`rubric-challenges.json` contains a satisfying example, a contradictory near miss and an omitted-evidence example for every assertion. These are authored rubric-design examples, not observed agent responses, independently labeled calibration data or a behavioral pass. Allow equivalent valid responses; assess evidence available in the actual response/artifacts.

`trigger-probes.json` is a separate host-specific routing set: three positive and three negative prompts. Reviewing description boundaries is not a live activation run.

Repository validators assess manifest structure/semantics. Prose assertions need response evidence and review; live model/Jev execution, independent behavior grading and camera hardware qualification are not established by these files.
