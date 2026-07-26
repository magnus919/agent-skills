# Evidence Ledger

## Intent

Implement the complete Grafana subject-matter-expert Agent Skill requested by issue #152, including discovery, dashboard engineering, alerting/routing, provisioning/GitOps, troubleshooting, and security/change control without collapsing Grafana into broader SRE or infrastructure guidance.

## Authority

The user granted modify, publish, and merge authority for this repository, including commit, push, PR creation, CI/review follow-through, and merge. Changes to the live Grafana instance were not requested.

## Inspected artifacts

- Issue `magnus919/agent-skills#152`, repository `AGENTS.md`, `CONTRIBUTING.md`, Agent Skills specification/guidance, eval schema, validators, catalogs, and CI integration.
- Comparable `llama-cpp`, `supabase`, `restic`, and `kubernetes` skill structures.
- Official Grafana provisioning, dashboard, alerting, API, as-code, service-account, permissions, security, troubleshooting, source, and release material listed in `references/source-index.md`.
- Read-only runtime evidence from Grafana `11.6.14+security-04` on `saru`, including Compose topology, health, provisioning metadata, protected API statuses, and bounded logs.

## Assumptions

- The repository's schema-version-1 eval contract remains authoritative.
- A reference-only first version is preferable to a wrapper CLI because API and authentication behavior is target/version-specific.
- Runtime evidence from `saru` is reusable as a failure pattern but does not establish universal Grafana behavior.

## Alternatives rejected

- Reducing the six required capabilities to a narrower first version: rejected because it violates issue acceptance criteria.
- Expanding SRE/platform skills instead: rejected because Grafana has coherent product-specific APIs, ownership, and failure modes.
- Bundling Prometheus/Loki/Tempo operation or generic Compose/Kubernetes/Terraform guidance: rejected as overlap with specialist skills.
- Directly fixing the duplicate providers on `saru`: outside granted authority and not required to implement the repository skill.

## Files changed

- Added `grafana/SKILL.md`, `README.md`, this ledger, seven focused references, and an eight-case eval manifest.
- Updated root `README.md` and `references/skill-triggers.md`.
- Regenerated `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, and `llms.txt`; `.agents/plugins/marketplace.json` remained unchanged.

## Commands / checks run

- `ruby scripts/validate-skills.rb`
- `ruby scripts/test-validate-skill-quality.rb`
- `ruby scripts/validate-skill-quality.rb --base origin/main`
- `python3 scripts/test-eval-validation.py`
- `python3 scripts/validate-evals.py`
- `python3 scripts/test-eval-coverage.py`
- `python3 scripts/eval-coverage.py --modified-from origin/main`
- `python3 scripts/check-artifacts.py`
- Claude, Codex, and `llms.txt` generator write/check modes plus `ruby scripts/test-gen-llms-txt.rb`
- `python3 -m eval_runner.paired grafana/evals/evals.json --adapter fake --output-dir /var/folders/gn/gpr8z9bn72z5kqm_fmjndj180000gn/T/opencode/grafana-eval-fake`
- `git diff --check`
- `skills-ref validate ./grafana` was attempted but `skills-ref` is not installed.
- A broad `python3 -m unittest discover -s tests -p 'test*.py'` was attempted but imported unrelated `/Volumes/tank01/magnus/git/hermes-cashew` tests and failed on missing external `agent`/cron modules; the repository's canonical `check-artifacts.py` test discovery passed.

## Observed outputs

- Live Grafana health and duplicate-provider evidence are recorded in `references/source-index.md` and `references/troubleshooting.md`.
- Structural validation accepted 111 canonical skills.
- Changed-skill quality checked `grafana` with 0 errors and 0 warnings; its 19-test validator suite passed with 159 assertions.
- All 12 present eval manifests passed schema-v1 and semantic validation; 27 eval-validation tests and 25 coverage tests passed.
- Artifact checks ran 368 repository tests successfully; generated catalogs are current at 101 public skills/plugins.
- The fake paired runner exercised all eight Grafana cases with 40 manual assertions per arm. This proves runner plumbing only; it reported no measurable candidate/baseline delta because the fake adapter cannot grade the manual assertions.
- Independent scope review confirmed all six issue capability areas. Independent factual review findings about multiple policy trees, direct-contact-point routes, deepest-match semantics, OSS RBAC, bounded live claims, and matching eval assertions were corrected.

## Verification boundary

- Research: official primary sources plus one read-only live Grafana target.
- Component/integration: Agent Skills structure, links, README, eval schema, quality rules, artifact checks, and generated catalogs passed repository validation.
- Behavioral: portable eval cases and fake-adapter runner plumbing passed; real-model grading is not established.
- Live: read-only host/container discovery was exercised; authenticated API and notification paths were not.

## Unverified boundaries

- Authenticated dashboard/data-source/alert/RBAC inventory and representative queries on `saru`.
- Alert firing, policy selection, receiver delivery, and resolved notification behavior.
- Real-model paired eval improvement and release-gated evidence.
- Publication, CI, and merge.

## Rollback / follow-up triggers

- Revert if repository validation cannot pass without weakening issue scope or safety gates.
- Refresh on Grafana API/schema, provisioning ownership, alerting, RBAC, or as-code lifecycle changes.
- Add executable discovery tooling only if repeated eval traces demonstrate a stable, error-prone procedure worth maintaining.

## Status

Local implementation and repository integration verification passed. Real-model eval evidence and authenticated live Grafana checks remain unverified. Publication, CI, and merge are the active delivery stage. No live Grafana state was changed.
