# Security and threat model

Use this reference whenever a task involves credentials, repository access, ransomware resistance, remote backends, or sharing recovery authority.

## Security properties and limits

Restic encrypts repository contents and metadata with keys derived from the repository password. It protects repository confidentiality against a storage provider that lacks the password. It does not solve every backup risk:

- A compromised machine that can read the password and write/delete the repository can often damage backups.
- A lost password, with no remaining valid repository key, makes data unrecoverable.
- A storage account with broad access can expose availability even if it cannot decrypt content.
- A successful backup may contain an already corrupted application state.
- Provider-side retention/immutability is a separate capability with provider-specific semantics.

## Threat-model worksheet

For each deployment, answer:

| Asset or failure | Control to examine |
|---|---|
| Repository password lost | Offline recovery process, multiple authorized key holders, documented access test |
| Endpoint ransomware | Separate credentials, least privilege, repository immutability/append-only options if appropriate, offline or independent copy |
| Storage credential leaked | Scoped identity, rotation, audit logs, secret manager, no credentials in URLs/logs |
| Accidental retention deletion | Dry-run review, grouped policy, maintenance window, documented recovery horizon |
| Backend account deletion/outage | Independent copy, provider recovery options, tested alternate restore path |
| Corrupt repository or silent bit rot | Scheduled `check` with data reads and restore drills |
| Operator error | Confirmation gate, separate restore target, peer review for destructive maintenance |

No single checklist proves security. Match controls to an explicit attacker and recovery scenario.

## Credential handling

Use separate credentials for repository encryption and backend access. Keep them in different systems or access paths where practical. A password file should have restrictive permissions and be readable only by the execution identity. A password command should emit only the password on stdout and must not emit prompts, logs, or shell diagnostics.

Preferred patterns:

```sh
# File permissions must be set by the host administrator.
restic --password-file /secure/restic-password snapshots

# The secret manager command must be non-interactive.
restic --password-command 'secret-tool lookup service restic' snapshots
```

Avoid:

```sh
restic --password 'literal-secret' snapshots       # command history/process exposure
export RESTIC_PASSWORD='literal-secret'            # shell/session/log exposure
set -x                                               # leaks expanded commands
```

Do not put backend keys in a systemd unit file, a launchd plist, a repository URL, an example template, or a ticket. Templates in this skill deliberately use placeholders and protected environment-file paths.

## Access control and key lifecycle

Restic repositories can contain multiple keys. Use separate keys for distinct authorized operators so access can be revoked without changing every workflow. Before removing a key, prove that another valid key is present and that the intended operators can open the repository. Do not remove the only known working key.

Backend permissions should be as narrow as the selected backend supports. For object storage, scope to the dedicated bucket/prefix and required list/read/write/delete actions. Any implementation of immutability, versioning, retention locks, or legal holds must be validated against that provider's current policy and against restic maintenance behavior, particularly deletes/prune.

## Network and host controls

- Use TLS and validate server identities for remote backends.
- Pin/verify SSH host keys for SFTP; do not turn off host verification.
- Run scheduled jobs with a dedicated, minimally privileged account.
- Restrict read access to source data and logs.
- Secure the scheduler, because it can become a route to the password file or secret command.
- Treat backup logs as potentially sensitive: file paths, host names, and error text can reveal system structure.

## Sources

- Restic repository/key model and password mechanisms: https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html (accessed 2026-07-15)
- Restic encryption overview: https://restic.readthedocs.io/en/stable/070_encryption.html (accessed 2026-07-15)
- Official security page: https://restic.net/#security (accessed 2026-07-15)
- AWS IAM and S3 permission example: https://restic.readthedocs.io/en/stable/080_examples.html (accessed 2026-07-15)
