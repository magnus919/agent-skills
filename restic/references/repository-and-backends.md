# Repository and backend setup

Use this reference when selecting storage, initializing a remote repository, or diagnosing a backend-specific failure.

## Separate restic behavior from backend behavior

Restic encrypts repository data before it is stored. The backend still determines availability, billing, identity, network exposure, durability, object versioning/immutability, lifecycle policies, and incident recovery. A URL beginning with `s3:` does not make every S3-compatible service behave like AWS S3.

Record for every repository:

- Backend type and exact endpoint/provider
- Repository location, without credentials embedded in the URL
- Execution identity and credential source
- Storage-region/availability assumptions
- Encryption/key custody model
- Provider retention, versioning, lifecycle, and object-lock posture
- Recovery objective and a tested alternate access path

## Common backend choices

| Backend | Useful when | Main operational concern |
|---|---|---|
| Local directory | Direct-attached storage or a controlled mounted volume | Filesystem reliability, mount availability, physical access |
| SFTP | A controlled SSH host | Key-only access, remote disk capacity, SSH host-key verification |
| S3-compatible object storage | Durable object storage or cloud/off-site repository | Least-privilege bucket policy, endpoint correctness, lifecycle/object-lock semantics |
| REST server | A rest-server deployment | Server authentication/TLS, append-only mode behavior, server lifecycle |
| rclone | A provider is supported by rclone but not a native restic backend | Two tools and two configurations to maintain; test error behavior and throughput |

The official documentation enumerates native backend syntax and backend-specific environment variables. Load the exact backend section before composing a production URL; do not invent flags from a nearby backend.

## Local repository

```sh
restic init --repo /srv/restic-repository --password-file /etc/restic/password
```

Use a filesystem with predictable persistence and access permissions. Do not assume that an SMB/CIFS mount behaves like a local POSIX filesystem: the restic manual specifically warns about CIFS compatibility issues on Linux and advises using another backend or the documented workaround. A mounted remote filesystem is not automatically a supported restic backend.

## SFTP repository

```sh
restic -r 'sftp:user@example.net:/srv/restic-repository' init \
  --password-file /etc/restic/password
```

Automation needs non-interactive SSH authentication and host-key verification. Do not disable host-key checking to make a job pass. Restic documents that SFTP servers do not normally expand `~`; use a path relative to the remote account's home directory or an explicit absolute path. A domain-qualified user can require `user@domain@host` syntax.

## S3-compatible repository

```sh
export AWS_ACCESS_KEY_ID=REDACTED
export AWS_SECRET_ACCESS_KEY=REDACTED
restic -r 's3:s3.example.invalid/restic-repository' init \
  --password-file /etc/restic/password
```

The credentials shown are placeholders. Use a dedicated identity restricted to the intended bucket/prefix and the operations restic needs. The official AWS example documents object `GetObject`, `PutObject`, and `DeleteObject` plus bucket-listing permissions; adapt this against the provider's current IAM documentation and your retention design. If provider-side immutability is required, verify the provider's object-lock and retention rules independently and rehearse a restore through that policy.

Do not run a generic S3 configuration against MinIO, Backblaze B2 S3, Wasabi, or another compatible service without reading that provider's endpoint, region, path-style, TLS, credential, and lifecycle documentation.

## REST and rclone

For REST repositories, deploy and secure the REST server as a separate service. Enforce TLS when traffic crosses an untrusted network, authenticate clients, limit exposure, and understand whether append-only mode changes deletion/prune behavior. For rclone, configure and test rclone independently first, then use restic's rclone backend syntax. Both add a layer whose logs must be redacted and whose version compatibility must be tracked.

## Repository access patterns

Use one of these, in descending order of clarity for automation:

```sh
# Explicit flags: useful in an audited script.
restic --repo /path --password-file /secure/password snapshots

# Environment: useful for a constrained job environment.
RESTIC_REPOSITORY=/path RESTIC_PASSWORD_FILE=/secure/password restic snapshots

# Secret manager: command output must contain only the password.
restic --repo /path --password-command 'secret-tool lookup service restic' snapshots
```

Do not print the environment or run a shell with tracing enabled around secret commands.

## Sources

- Repository setup and backend-specific sections: https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html (accessed 2026-07-15)
- Restic AWS S3 example and minimal policy discussion: https://restic.readthedocs.io/en/stable/080_examples.html (accessed 2026-07-15)
- Backend reference: https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html#backends (accessed 2026-07-15)
