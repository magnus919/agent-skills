# Focused behavioral review, 2026-10-23

The 19 cases appended in this change make previously implicit tutoring behavior
reviewable: cue recognition versus combining concepts; correct procedure versus
meaning; prediction before explanation and its later resolution; a compact
continuation record; and optional reasoning-first practice. They include direct
answers, novice examples, valid alternatives, self-correction, terse dictated
work, unfinished work, requested hints, answer-first checks, and stopping.

## Method and result

Baseline: repository commit `06b7916fcb818ea277a6f1250b85ec0bf331ca7c`.
Each of the 19 cases was given to a separate fresh tutor agent with the baseline
skill and its raw offline source excerpt. Tutor agents were not given assertions,
expected answers, or previous outputs. A separate model reviewed the captured
responses. Another independent model challenged each assertion with satisfying,
contradictory, and omitted-evidence examples. These are model reviews of simulated
interactions, not human adjudication or measured learning gains.

Of 71 focused assertions, 68 output assertions were judged met, none contradicted,
and three external-action assertions were not shown. The latter require complete
execution traces to verify absence of profile writes or scheduling; prose alone
does not establish that absence. Do not report all 71 assertions as passed.

No observed baseline output defect warranted more tutor instructions. Consequently
`SKILL.md` and every teaching reference are byte-identical to the baseline. The
candidate changes the regression manifest and human-facing documentation only.
Ten fresh repeat responses were also generated against those same instructional
bytes; they showed no observed output contradiction. These repeats are not
evidence that the candidate improves behavior. A temporary instruction expansion
was discarded; exploratory responses using it are excluded from these results.

The baseline `SKILL.md` SHA-256 is
`8be477617b0738894bf8306e7aa264ca8ef2869b544ba7ad74c11ddeabd03aba`.
Private run records retain prompt, response, source-file and manifest hashes;
generated transcripts and model-review rationales are intentionally not published.

## Limits and future runs

This review covers the 19 appended cases, not all 41 manifest cases or a
cross-domain validation study. Most cases are single-turn snapshots; prediction
invitation and resolution are separate fixtures, not an observed complete lesson.
No learner success, transfer, delayed retention, real-time audio interruption
handling, or reliability across models is established. Transcription examples
contain supplied text, not tested speech recognition. The optional practice
formats are usability choices, not a claim that verbalization always helps.

Use the existing validation protocol for future fresh runs. Preserve complete
tool traces when judging external-action assertions, and keep met, not met and
not shown separate. Recheck the relevant cases if teaching instructions change;
do not infer behavior from the presence of the new manifest.
