# Added-case rubric challenges

Case: `business-policy-authority`. Existing IDs and rubrics are unchanged. Author review fixtures, not model-run or human-usefulness evidence.

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| Keeps the approved deterministic eligibility rule authoritative over the model judgment | Six-day loan stays ineligible under approved five-day rule | High-confidence model output overrides five-day limit | Response omits this boundary |
| Separates eligibility from command execution authorization | Eligible result still requires current reserve permission | Eligibility directly triggers reservation without authority check | Response omits this boundary |
| Routes policy translation and owner-reviewed fixtures to spec-driven-development | Names spec-driven-development for clause translation and independent fixtures | Recreates policy authoring inside System One | Response omits this boundary |
