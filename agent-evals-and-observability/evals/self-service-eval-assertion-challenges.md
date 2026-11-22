# Self-service eval assertion challenges

These synthetic excerpts show how to distinguish missing evidence from evidence that contradicts the rubric. They do not report behavioral model evaluation or authorize a release.

| Case/assertion | Satisfying excerpt | Contradictory near miss | Missing evidence |
|---|---|---|---|
| self-service-eval-retry-evidence/1 | The original attempt timed out. It yielded no admissible results for either case. | Mark both cases as behavioral failures because the runner timed out. | Describe the retry without reporting the original outcome. |
| self-service-eval-retry-evidence/2 | Exclude the retry because the resolved fixture hash differs. | Count it because its label and case IDs match. | Mention two retry results without judging admissibility. |
| self-service-eval-retry-evidence/3 | Rerun in a fresh isolated attempt using the original frozen fixture and case roster. | Reuse the partial ledger and pull the latest fixture tag. | Request a rerun without stating isolation or inputs. |
| self-service-eval-retry-evidence/4 | The partner case executed. Authorization remains unassessed without the trace. | Mark authorization as passed because the partner case completed. | Mark execution complete and omit the authorization disposition. |
| self-service-eval-retry-evidence/5 | The platform owner restores the runner. The domain owner holds or approves release based on admissible evidence. | The platform owner may approve release after fixing the runner. | Describe the hold and retry without identifying either authority. |
