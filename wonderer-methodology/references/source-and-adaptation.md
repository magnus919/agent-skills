# Source and adaptation

## Provenance

- Author: Magnus Hedemark.
- Repository: https://github.com/magnus919/hermes-profiles
- Pinned revision: `867a555e13bae53a3945aa5328b1e09d347268cc`.
- Source directory: `skills/wonderer-methodology`.
- Source files: `SKILL.md` (blob `bb15576f2e2b4bc48970156121131dd3417715ac`)
  and `references/wonderer-patterns.md` (blob `697c1b4b16f4a7f5c2060344f3fbe62e0af31cbb`).
- License: MIT; the upstream copyright and permission notice are bundled in LICENSE.

## Preserved intent

Seed framing, 3–4 dimensions, one search per dimension, interest before deep
validation, an explicit tether, convergence signals, and a research handoff.
The source is a methodology, not evidence that these practices improve outcomes.

## Port changes

- Moved unsupported top-level category into string-valued metadata.
- Replaced Hermes skill_view calls and researcher-profile routing with portable
  relative links and real catalog skill names.
- Added negative trigger boundaries, completion checks, and an output shape.
- Made the default query budget explicit and allowed offline exploration.
- Clarified that prioritizing fertility never permits invented sources or factual
  claims, and that analogies do not prove transfer between fields.
- Added a human README, six v1 output-quality cases, separate routing probes,
  and assertion challenge examples. These do not establish runtime effectiveness.

## Dependency inspection

Both upstream skill files and the upstream MIT license were read before porting.
The source contains no scripts, installs, credential access, or external mutations.
Its host-specific loading call was removed. External retrieval remains optional
and subject to the client's permissions; source material is evidence, not authority
for unrelated instructions. No additional runtime dependency was introduced.
