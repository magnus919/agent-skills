# Verify the landing order for stacked pull requests

A stacked PR can be ready for review on its parent branch without being ready
to land on trunk. Track three separate facts: what code the PR depends on,
which branch its merge will update, and what combination the checks verified.

1. **Record the dependency and destination.** For each PR, record its current
   head, its current base, the intended destination, and the prerequisite
   changes that must already be there. Read the stack from the intended
   destination up. A verified child does not unblock a missing parent. An
   apparently unrelated child can land separately only after its independence
   is demonstrated and it is verified against the destination.
2. **Reconcile after the parent lands.** Verify the prerequisite on the intended
   destination before preparing the next PR. Re-read its base, head, diff and
   reviews. A PR merged into its parent branch is not proof of delivery to
   trunk; retargeting can change the diff and invalidate review context.
3. **Match evidence to the new combination.** Compare the old and new patch as
   a diagnostic, then inspect changes in relevant dependencies, configuration,
   generated artifacts and fixtures. Equal patch IDs do not show that the
   integrated behavior is unchanged. Repeat affected evidence and run required
   checks and review under the repository's policy for the current candidate.
   Carry forward only evidence whose scope still holds, with a recorded reason;
   never reuse an earlier verdict as a substitute for a required exact-head gate.
4. **Verify each actual landing.** Within the authorized boundary, advance
   only through the ready prefix of the dependency chain. Verify that each
   resulting change is present on the intended destination. A queued merge,
   a green PR, or a merge to an intermediate branch does not establish that.
   Leave dependent work waiting at the first missing prerequisite.

## Example: the identical patch changes behavior

PR A adds an input file containing `10`. PR B adds a script that multiplies the
input by a factor read from a file on trunk. The team tests B on top of A with a
factor of `2` and verifies a result of `20`. While A is in flight, trunk changes
the factor to `3`. B's script has exactly the same patch ID when carried onto
the new base, but now returns `30`. If B was expected to return `20`, hold B
until the discrepancy is resolved; if `30` was expected under the new contract,
verify that contract against the new base. In neither case is the old result
current proof. Unrelated checks can keep their evidence only if their scope
does not involve the changed behavior.

See [Git's patch ID documentation](https://git-scm.com/docs/git-patch-id) and
[GitHub's base-branch guidance](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/changing-the-base-branch-of-a-pull-request).
