# Stop a bad pattern from becoming the example

When agents repeat a workaround, inspect the examples they can actually see:
nearby code, shared helpers, generated scaffolds, tests and documentation. Find
what made the shortcut attractive. An architectural problem stated as ten prose
warnings still looks like an available choice in code.

1. **Make the good path easy.** If the caller should not choose among several
   lifecycle or permission options, move the invariant behind a narrow API.
   Give modules and directories names that signal ownership. Enforce the
   dependency boundary with the build, types or a graph check; names alone do
   not enforce it.
2. **Stop new copies without hiding old ones.** Use the cheapest faithful check
   with a diagnostic that explains the consequence and shows the supported
   replacement. Test an allowed use, a prohibited use and a near miss. For a
   large migration, track old sites with an owned, shrinking allowlist. An
   exception must not silently become a new example.
3. **Replace the examples.** Start where generators and agents are most likely
   to copy: scaffolds, official examples and neighboring production code.
   Leave a tested reference path. Editing prose, suppressing a checker or
   measuring only warning count does not establish adoption.
4. **Verify behavior and sampling.** Exercise the affected journey and check a
   bounded set of newly generated changes for the old pattern and regressions.
   Record what was reviewed and what remained untested. Keep explanations and
   manual review for decisions that still need judgment.

**Worked example: saved settings.** A desktop app uses delayed callbacks to
bridge its UI and its settings service. The screen looks correct immediately,
but some saves disappear on reopen. Put persistence behind a single save
interface, prohibit new product-level imports into the service internals,
migrate the old timer examples and route agents to the tested save path. Check
the [feature journey](../../spec-driven-development/templates/FEATURE-MAP.md)
against the running app; the import check cannot prove persistence.

Inspired by [Lauren Tan's account of copied workarounds and enforceable
boundaries](https://ai.engineer/talks/O_zcc6Xl12g-all-code-is-slop-except-mine).
The example above is synthetic; it does not describe her team's architecture
or imply its framework restrictions transfer unchanged.
