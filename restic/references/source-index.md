# Source index

Research baseline: 2026-07-15. Restic changes over time, especially command flags, backend integrations, and release behavior. Treat explicit version claims as stale unless refreshed against the linked source and the installed `restic version`.

## Primary sources

| Topic | Source | Scope |
|---|---|---|
| Documentation home | https://restic.readthedocs.io/en/stable/ | Stable user documentation |
| Introduction | https://restic.readthedocs.io/en/stable/010_introduction.html | Quickstart and core model |
| Installation | https://restic.readthedocs.io/en/stable/020_installation.html | Supported installation guidance |
| New repositories/backends | https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html | Password methods, repository format, native backend setup |
| Backups | https://restic.readthedocs.io/en/stable/040_backup.html | Backup behavior, filtering, VSS, options |
| Repository operations | https://restic.readthedocs.io/en/stable/045_working_with_repos.html | Listing, stats, check, copy, locks and related operations |
| Restore | https://restic.readthedocs.io/en/stable/050_restore.html | Snapshot selection and restore safety |
| Retention/prune | https://restic.readthedocs.io/en/stable/060_forget.html | Forget/prune behavior and scheduling implications |
| Encryption | https://restic.readthedocs.io/en/stable/070_encryption.html | Encryption design and key material model |
| Examples | https://restic.readthedocs.io/en/stable/080_examples.html | S3/IAM and operational examples |
| Command manual | https://restic.readthedocs.io/en/stable/manual_rest.html | Installed-command cross-check and option reference |
| Scripting and JSON | https://restic.readthedocs.io/en/stable/075_scripting.html | Exit codes, automation, structured output, parser compatibility |
| Tuning | https://restic.readthedocs.io/en/stable/047_tuning_parameters.html | Connections, verification, pack size, cache, and resource trade-offs |
| Troubleshooting | https://restic.readthedocs.io/en/stable/077_troubleshooting.html | Checks, repair order, locks, and bounded diagnosis |
| Releases | https://github.com/restic/restic/releases | Current release artifacts and user-visible release notes |
| Changelog | https://github.com/restic/restic/blob/master/CHANGELOG.md | Version-specific behavior history |
| Design | https://github.com/restic/restic/blob/master/doc/design.rst | Repository format and cryptographic implementation detail |

All sources above were accessed 2026-07-15.

## Secondary authoritative sources to add per backend

Restic's documentation establishes how restic talks to a backend. It cannot establish your provider's current operational guarantees. Add the exact provider's official documentation for:

- Bucket/container IAM policy and scoped credentials
- Endpoint and region/path-style requirements
- Object versioning, lifecycle, object lock, retention, legal hold, and deletion behavior
- Durability/availability claims and regional failure model
- Authentication rotation, audit logs, and incident recovery
- Billing and egress limits that affect restore

For a scheduled-job host, also retain official documentation for the scheduler and secret store in use. For application data, retain vendor documentation for backup consistency and restoration.

## Claim hygiene

- Cite restic docs for restic commands and repository semantics.
- Cite the provider for cloud-object behavior.
- Cite the application vendor for database/application consistency.
- Cite a tested restore drill for claims that a particular deployment can recover.
- Cite the installed binary's `restic version` and `restic <command> --help` for current local flag behavior.
