# Harness-adapter eval rubric challenges

These contrasts test whether a reviewer can distinguish satisfaction,
contradiction and missing evidence. They describe response content. Execution
receipts would establish which controls actually ran. [Research brief](research-brief.md)

| Case and assertion | Satisfying response | Contradictory near miss | Evidence omitted |
| --- | --- | --- | --- |
| `qualify-executable-grader` 1 | Reference passes at the defined score | Reference receives a below-threshold score and the task is admitted | No reference trial |
| 2 | Equivalent quoting passes for a separately prepared complete export | Exact bytes from the reference are required | No valid alternative |
| 3 | Untouched state fails on missing export | Empty or untouched state is accepted | No starting-state control |
| 4 | Missing row fails on completeness | Correct header earns a pass despite a missing row | No plausible partial export |
| 5 | Fresh reset and replay reproduce the expected score | Read the original cached receipt as the repeat | No replay |
| 6 | Timeout is recorded as unscored | Timeout is treated as a semantic rejection | Timeout left unexplained |
| 7 | Receipt names task, fixture and grader revisions | Receipt keeps only a run timestamp and treats that as sufficient | No identity record |
| `coding-adapter-deployment-comparison` 1 | Same deployment harness, same effort and budget | Compare base in the old harness to adapter in the new one | Deployment baseline unspecified |
| 2 | Add a stronger supported base configuration within the operational ceiling | Report the adapter as better than the available stronger base from the weak comparison alone | Stronger base omitted |
| 3 | Reuse the coding cases across both harnesses | Infer harness transfer after also changing tasks | No harness transfer design |
| 4 | Try the new task family in the original harness | Infer workload transfer after also changing harnesses | No workload transfer design |
| 5 | Freeze final cases and use development cases for checkpoint selection | Choose the checkpoint on the final roster | Selection split unspecified |
| 6 | Retain newly passed and newly failed task identities | Treat an unchanged aggregate as evidence no tasks regressed | No paired outcomes |
| 7 | Divide all serving-attempt costs by accepted tasks | Count only successful attempts in the numerator | No denominator or cost accounting |
| `learned-adapter-harness-qualification` 1 | Route the trained adapter comparison to ML engineering | Assign adapter specialization entirely to harness engineering | No owner named |
| 2 | Run both artifacts inside the actual desktop harness | Use only the two unmatched system configurations | No fixed harness identified |
| 3 | Explicitly identify artifact and runtime as changed | Attribute the unmatched difference to the adapter alone | No interpretation of the proposed comparison |
