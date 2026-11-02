# Filing reports derived from private work

Read this before preparing a public issue or PR from a private repository, client
system, personal task or restricted dataset. Publish the defect mechanism and a
synthetic reproduction that preserves it; private context is not automatically
necessary or authorized for disclosure.

## Prepare a reviewable public artifact

- Confirm the intended public destination and existing authorization to publish.
  Permission to diagnose or draft does not alone authorize submitting reports,
  attachments, fixes or merge actions. Reuse authorization already granted; do not
  request it again when it covers the action.
- Replace people, employers, clients, projects, hosts and absolute paths with
  neutral synthetic values. Avoid realistic descriptions that still identify the
  subject indirectly. Preserve the causal structure and label synthetic fixtures.
- Check issue titles/bodies, PR text, diffs, filenames, screenshots, attachments,
  logs, commit messages and embedded metadata. Search known private identifiers and
  secrets, then manually inspect the full rendered artifact. Pattern scans cannot
  establish absence of sensitive information.
- Keep original dossiers and raw evidence in their authorized private location.
  Never upload them as supporting evidence merely because the report is sanitized.
- Search existing issues first. Group by defect mechanism and independently
  actionable fix, following the project's conventions; do not create duplicate
  reports for different private instances of the same defect.

Before authorized submission, inspect the exact payload and destination. If scope
is unclear, finish the sanitized draft and ask for the missing publishing authority.
Do not publish first to discover whether the material is safe.

After submission, read back the public artifact and inspect rendered content and
attachments. This verifies delivery and catches transformations; it does not undo
exposure. If private content escaped, stop further disclosure, notify the user and
use the project's applicable incident/removal process within granted authority.
Never claim that editing or deleting a post erases public copies.

## Close the loop within the authorized scope

For a small, self-contained fix, prepare and verify a scoped PR when requested.
Publish or merge only when existing authorization and project policy allow it.
Use `Closes #N` for each issue actually resolved; do not claim to close unrelated
reports. Following an authorized merge, verify the resulting revision and issue
states rather than trusting the PR body's text.

Complete with the requested sanitized draft, submitted report or verified merged
fix, plus the applicable read-back checks. If authority ends at a draft or open PR,
hand off that artifact and name the remaining action. Do not expand a private-run
bugfix into publication of its original context.
