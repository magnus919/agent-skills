# Self-service eval assertion challenges

These synthetic excerpts show how to distinguish missing evidence from evidence that contradicts the rubric. They do not report behavioral model evaluation or authorize a release.

| Case/assertion | Satisfying excerpt | Contradictory near miss | Missing evidence |
|---|---|---|---|
| self-service-eval-retry-evidence/1 | The original attempt timed out, which reports execution status. The corrected partner case lacks the required approval trace. | Mark both cases as behavioral failures because the runner timed out. | Describe the retry without reporting the original outcome. |
| self-service-eval-retry-evidence/2 | Exclude the retry because the resolved fixture hash differs. | Count it because its label and case IDs match. | Mention two retry results without judging admissibility. |
| self-service-eval-retry-evidence/3 | Rerun in a fresh isolated attempt with the original frozen dataset, fixture digest, and required case roster. | Start a fresh isolated attempt with the same fixture and case IDs but revised dataset bytes. | Request a rerun without stating isolation or inputs. |
| self-service-eval-retry-evidence/4 | The partner case executed. Authorization remains unassessed without the trace. | Mark authorization as passed because the partner case completed. | Mark execution complete and omit the authorization disposition. |
| self-service-eval-retry-evidence/5 | The platform owner restores the runner. The domain owner holds or approves release based on admissible evidence. | The platform owner may approve release after fixing the runner. | Describe the hold and retry without identifying either authority. |
| self-service-eval-retry-evidence/6 | The domain owner holds release until the required authorization trace or approved equivalent evidence is available. | The domain owner approves despite the missing partner trace. | Identify the domain owner without recording a disposition. |
