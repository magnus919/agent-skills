# Restic skill

Operate encrypted, deduplicated backups with a recovery-first workflow. This skill helps an agent turn a collection of restic commands into an operational backup practice: safe setup, clear retention, evidence-backed health checks, and restore drills.

## Why Install This Skill

A backup is only useful when it can be found, decrypted, and restored under pressure. Restic is deliberately simple, but its consequences are not: a lost password is unrecoverable, an accidental prune can change the recovery window, and a green backup job does not prove that a restore will work.

This skill gives your agent a portable operating procedure for local and remote restic repositories. It separates general restic behavior from backend-specific configuration, keeps credentials out of artifacts, and makes restore validation part of normal operations instead of a crisis-only task.

## What You Get

| Resource | Purpose |
|---|---|
| `SKILL.md` | Discovery-first operating contract and routing guide |
| `references/` | Deep guidance for setup, backends, automation, security, recovery, tuning, and incident diagnosis |
| `templates/` | Non-secret backup policy, restore drill, and systemd scheduling examples |
| `scripts/restic-preflight.sh` | Read-only local configuration check that redacts secrets |
| `scripts/restic-verify.sh` | Bounded metadata or data-read verification wrapper |
| `scripts/test-restic-preflight.sh` | Deterministic script test without a live repository |
| `scripts/test-restic-verify.sh` | Deterministic verification-wrapper test without a live repository |
| `evals/evals.json` | Three safety-sensitive scenarios for regression evaluation |

## Quick Start

Install `restic` with your platform package manager or an official release, then configure a repository location and a protected password source:

```sh
export RESTIC_REPOSITORY=/path/to/repository
export RESTIC_PASSWORD_FILE=/secure/path/restic-password
# Do not export a literal RESTIC_PASSWORD; use a protected file or secret command.
restic init
restic backup /data --tag files
restic snapshots
```

Before relying on the backup, restore it to a separate empty directory and inspect the result:

```sh
restic restore latest --target /var/tmp/restic-restore-test
```

## Triggers

Use this skill when you need to install restic, initialize or choose a repository backend, automate backups, define snapshot retention, diagnose locks or failed jobs, test recovery, harden repository access, tune performance, or copy/migrate a repository.

## Requirements

A `restic` binary is required. Live repository operations require repository access plus a password mechanism. Remote backends also require their own credentials, network access, and any provider-specific permissions. The skill does not create cloud accounts, bypass access controls, or store secrets for you.
