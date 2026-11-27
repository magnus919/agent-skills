# Maintaining Magnus Mode

The scope denominator is the same canonical public catalog used by
`scripts/check-catalog-set.py`. Bundled helpers are not separate install
candidates; catalog infrastructure is excluded. Magnus Mode is an entry point,
not one of its own targets.

When adding, removing, renaming, or materially changing a skill:

1. Review its actual role against the scope: does it contribute specific evidence
   or a capability to planning, delivering, or operating a technology project?
   A tool isn't in scope just because it uses software. Mixed-use skills belong
   only for a named technology lifecycle contribution.
2. Update [scope](magnus-mode-scope.json) with `route` or `unrelated`.
   `python3 scripts/check-magnus-mode.py --fingerprint <skill>` prints the
   normalized description digest. Update it after reviewing a changed trigger.
   For removed or renamed skills remove obsolete identities and update any
   route references. Keep the classification independent of the list of targets.
3. For a routed skill, give it an owner or supporting role at one or more named
   steps in [the route source](../magnus-mode/lifecycle.json). Don't edit the
   generated reference directly. Run
   `python3 scripts/check-magnus-mode.py --write` and commit the refreshed map.
   An unrelated addition does not require touching the route source or map.
4. Run `python3 scripts/test-check-magnus-mode.py` and
   `python3 scripts/check-magnus-mode.py`. Describe changes to existing skill
   responsibilities in the PR, even if the description is unchanged. CI checks
   canonical inventory, reviewed descriptions, graph integrity and the generated
   map; it cannot infer whether a human chose the correct scope or whether an
   agent routes well. Keep the behavioral cases separate.

When a routing decision changes, update the behavioral cases as appropriate.
This is not a new workflow engine, blanket execution approval, live model
requirement, or platform-specific command bundle.
