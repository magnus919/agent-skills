# Deliver a change through a merge queue

Use when the forge's protected merge path queues an authorized PR. For queue
design and CI capacity, use `release-engineering`.

1. **Verify admission.** Confirm repository, PR, target, current PR head,
   prerequisite changes, required PR checks, and review under the live
   policy. Use an expected-head guard when available. Reconcile existing
   queue membership before submitting or retrying a merge request.
2. **Follow the live candidate.** Record the queue entry and the candidate
   SHA or forge-provided identity when available. Keep its checks distinct
   from the PR's admission checks. The candidate is the combination the
   queue proposes to land, which can include queued predecessors. Let the
   protected path handle routine base advancement.
3. **Reconcile changes in order.** If a predecessor is removed, the PR head
   changes, or the queue rebuilds the candidate, fetch live membership and
   check evidence again. A late green on the old candidate covers only that
   old combination. Wait for the replacement's required checks if the PR
   remains queued. If the PR was ejected, read the recorded reason. Return
   a conflict or failing check to its owner, hold work that needs an absent
   prerequisite, and only requeue after the reason is resolved and current
   admission gates are met. Reconcile before retrying an uncertain request.
4. **Observe the landing.** Verify the forge reports the PR merged into the
   intended target and that target history and the landed change agree with
   the merge record. Capture the landed revision and mandated post-merge
   evidence. Squash and rebase can produce a different commit SHA. A queue
   entry or a passing candidate alone leaves delivery pending.

On interruption, keep the PR head in `head_sha`. In the existing evidence,
pending steps, and watcher fields record live membership, the candidate
identity if visible, and what remains to verify. On resume fetch live
membership or the merge record first. Keep watching a live entry without
submitting a duplicate. If the forge does not expose candidate identity,
report that evidence limit and use the protected merge record and target
verification for the landing verdict.

[GitHub merge queue mechanics](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue) · [GitLab merge train cancellation](https://docs.gitlab.com/ci/pipelines/merge_trains/)
