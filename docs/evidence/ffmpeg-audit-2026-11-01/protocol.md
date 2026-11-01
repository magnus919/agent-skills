# FFmpeg audit protocol — #764

Pinned source: `83d2784394ede4e4bab85aabc0545331fcb6ee31`.

Before execution: inspect the current entrypoint, README, fixture/integration
references, selected test bodies and execution boundaries. Inventory hashes for all
skill artifacts and inspect completed issue/PR history. Assess existing reproducible
fixtures instead of inventing user reports or reopening completed scope.

Hypothesis: prior FFmpeg work already handles the principal editing evidence and
safe-output boundaries. A change is justified only by a repeated decision-relevant
failure in at least two representative tasks, or one reproduced severe failure.
No-change is acceptable for this inspected scope, with untested boundaries explicit.

Execute these eight existing tests once: real multi-source concat plan/render;
measured synthetic audio and candidate plan; missing measurement filter; incomplete
acceptance evidence; blocked review; real end-to-end editorial example; refusal of
nonempty workspace; unavailable target lane. Real-media and structured fake-probe
cases must remain distinct. Preserve pytest result and exact local tool versions.
Count skips and failures; do not call skipped tasks passed. Stop on unexpected
failure and preserve it; do not modify the skill under this audit.

Limits: non-personal synthetic local media only, new task-local output paths, no
user footage, network media, external editor/player, human visual/listening review,
model inference, publishing, or production operation. Existing helper commands have
bounded subprocesses. Keep generated media and task-local evidence outside Git;
commit only this protocol, sanitized audit receipts and analysis. Compare primary
FFmpeg documentation, not popularity. No new generative media capability is proposed.
