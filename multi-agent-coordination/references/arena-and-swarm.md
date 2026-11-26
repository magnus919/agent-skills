# Choose a bake-off, coverage fan-out, or race

Choose the work shape before choosing workers. A **council** weighs perspectives
on a decision. An **arena** produces several independent renditions of one
deliverable, then verifies one synthesized solution. A **coverage swarm** divides
an evidence or implementation surface into independently checkable slices, then
accounts for each slice. A **race** searches for a verified result under a declared
selection rule. A hybrid keeps the rules explicit for each arm.

## Arena: same problem, independently built solutions

1. Establish accepted intent, decision owner, scope, artifact and evaluation
   criteria. Route unresolved product questions to discovery or planning.
   Define a budget and why alternative artifacts could change the decision.
2. Freeze shared inputs and acceptable effects before work. Give candidates the
   same brief, acceptance requirements, and pinned grounding, with independent
   workspaces and no peer outputs during generation. Keep private grader evidence
   separate where justified. Capture each candidate's rejected alternatives.
3. Compare finished artifacts criterion by criterion. Prefer executable or
   domain evidence; a read-only independent reviewer can challenge the ranking.
   Different model vendors do not make an assertion true. Record dropouts and
   conflicting evidence. Do not select an incomplete result merely to meet quota.
4. Choose one coherent base. Borrow compatible elements with their provenance;
   reject mutually incompatible choices, even if both scored well alone. Reframe
   only when lack of agreement traces to the brief, not merely because there are
   real tradeoffs. Leave consequential tradeoffs to their authorized owner.
5. Verify the combined artifact against the original criteria and actual target.
   Rerun affected checks after synthesis; green candidates cannot certify
   their combination. Report the base, grafts, rejected alternatives, uncertainty
   and measured result. If only one candidate survives, report that the intended
   comparison did not happen; use it as a single result only if the owner allows.

## Swarm: declare closure before dispatch

- **Coverage:** Enumerate required slices, exact inputs/revisions, acceptance
  evidence and who integrates. Each worker returns an independent status, its
  observed evidence and any remaining gap. Merge duplicate findings; a slice
  that is blocked, missing, stale or mismeasured is not a pass. Retry or reassign
  only within declared bounds; otherwise record honestly incomplete coverage.
- **Race:** Before dispatch choose first *verified* pass, rank all, or select the
  best admissible result under the rubric. First response is not first pass.
  Cancel needless remaining work only when the completion rule allows it.
  A model comparison needs the same candidate revision, workload and comparison
  method, not just takeaways from workers who ran different tasks.
- **Hybrid:** For example, partition a repo audit by package and race alternate
  methods only on one difficult package. All required packages still need the
  declared evidence; a winner in one package does not complete the audit.

Example: three prototypes render a scheduling control from the same brief.
Choose the prototype with the sound keyboard model. Borrow another prototype's
clearer date labels only if the combined version still passes keyboard navigation
and screen-reader checks. In a separate coverage swarm auditing three libraries,
two PASS results and one missing report mean two of three accounted for, not a
green audit.

Lauren Tan's pstack [Arena](https://github.com/cursor/plugins/blob/b7b93c36be9bcc36a74db438e0fd385d660bc559/pstack/skills/arena/SKILL.md)
and [Swarm](https://github.com/cursor/plugins/blob/b7b93c36be9bcc36a74db438e0fd385d660bc559/pstack/skills/swarm/SKILL.md)
were instrumental in this adaptation. They describe practitioner workflows,
not measured proof that more candidates or reviewers improve outcomes. The
catalog retains its discovery, planning and authorization requirements.
