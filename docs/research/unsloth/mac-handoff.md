# Mac worker handoff: Unsloth GPU validation

Coordinator workspace: `/home/magnus/git/agent-skills` on `wanker01`.
Worker host: `auriga` (Mac). GPU target: `gpuslut01`.

## Authorization and access

Magnus explicitly authorized using gpuslut01 for this workflow and coordinating
through Codex on his Mac, which has the necessary SSH identities. Use those
identities in place; never copy private keys or credentials to the coordinator.
Respect existing SSH host verification and ordinary Codex approval settings.

The user verified the GPU host ED25519 fingerprint:
`SHA256:u6SMarpB+AR9pEVmfVaNpRShz2NYd9pozCRePP0XpTs`.
The GPU is user-reported as an RTX 5070 Ti; discover actual hardware and memory.

## Objective

Turn the initial Unsloth skill's text-SFT guidance into one reproducible,
hardware-validated workflow. Prioritize actual execution over expanding the
catalog of conceptual advice.

The coordinator's changes are uncommitted on `feat/unsloth-skill`, initially based
on origin/main `fb32533`. A remote clone of the branch will not contain them.
Receive an explicit snapshot from the coordinator before modifying the skill.
Read the snapshot's AGENTS.md and relevant skills. Keep worker edits in a separate
checkout/output directory and return a patch; do not overwrite coordinator work.

## Execution scope

1. Discover GPU-host identity, OS, account, driver, free VRAM/RAM/disk, existing
   GPU processes, and available environment tooling. Record observed facts.
2. Use a new user-owned experiment directory and isolated environment. Preserve
   existing installations and jobs. Do not change drivers, system packages,
   access settings, or services. Rollback is abandoning the new environment and
   stopping only this experiment's process; keep evidence instead of deleting it.
3. Select a small public, ungated model with a current official Unsloth recipe
   compatible with the observed GPU/backend. Record immutable model/source
   revisions and the resolved package stack. No paid service or publication.
4. Build a small synthetic text-SFT dataset with separate held-out examples.
   Implement and test template rendering, actual collator-label inspection,
   supervised-token counts, token lengths, and answer truncation checks.
5. Capture base-model outputs. Run an initial bounded smoke test (about 20
   training steps), saving full checkpoints and adapter/tokenizer artifacts.
   Stop on GPU contention, nonfinite loss, repeated OOM, or a failing data audit.
   Do not launch a large training run to manufacture quality improvements.
6. Reload the adapter in a fresh process and demonstrate checkpoint resume.
   Compare held-out task outcomes under recorded decoding settings. A smoke run
   may demonstrate mechanics without improving quality; report that accurately.
7. Where feasible, merge and export, then test reload and target-runtime parity.
   Distinguish tested paths from deferred ones. Bound diagnostic retries to
   three attempts without new evidence; preserve failure logs and hypotheses.

## Return evidence and changes

- Exact scripts/configuration, synthetic fixtures, dependency lock or freeze,
  model revision and commands required to reproduce the successful path.
- Host/backend inventory, logs, exit statuses, timing, measured peak memory,
  and clear pass/fail/not-run status for each stage.
- Label audit, held-out base/candidate comparison, fresh-process reload and
  checkpoint-resume evidence; export/runtime evidence if executed.
- Patch improving the skill's SFT, installation, evaluation and artifact guidance,
  with focused tests and eval cases tied to real failure modes encountered.
- File hashes and locations of retained artifacts. Return small reports and code,
  not model weights, credentials, private data, or whole environment dumps.

Do not claim GPU validation from local helper tests or semantic eval passes from
schema validation. Do not push, publish, or merge changes as part of this handoff.
