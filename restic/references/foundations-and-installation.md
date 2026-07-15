# Foundations and installation

Use this reference when selecting a binary, explaining what restic does, or establishing a safe local baseline.

## What restic is

Restic creates encrypted, content-addressed snapshots in a repository. It is not a persistent service. A scheduler such as systemd, launchd, Task Scheduler, cron, or a CI/job runner invokes the CLI. Each repository has one or more password-derived keys; losing every valid password makes the repository unrecoverable. Restic's repository format version is independent of the command binary version.

Do not confuse a snapshot list with a file copy. Snapshot metadata, deduplication, encryption, source consistency, retention, and restore testing each need separate consideration.

## Select an installation method

Use the platform's package manager when its version satisfies the required feature and repository compatibility. Use an official release when you need a specific current version or a package manager lags. Verify the downloaded artifact using the project's published release checksums/signatures before trusting it.

Examples, subject to the package repository's version:

```sh
# macOS
brew install restic

# Debian/Ubuntu family
sudo apt update && sudo apt install restic

# Fedora/RHEL family
sudo dnf install restic

# Windows, with Winget where available
winget install restic.restic
```

For an official release, obtain the binary and checksum from the restic GitHub release page. Do not use an unverified third-party binary or pipe an installer script from an unrelated site into a shell.

Verify the executable itself:

```sh
restic version
restic help
```

Record the observed version in the backup policy. Version-sensitive behavior belongs in [source index](source-index.md), not in an assumption embedded in automation.

## Minimum local configuration

Restic accepts repository and password settings as flags or environment variables:

```sh
export RESTIC_REPOSITORY=/srv/restic-repository
export RESTIC_PASSWORD_FILE=/etc/restic/password
```

Alternatives include `--repo` / `RESTIC_REPOSITORY_FILE` and `--password-command` / `RESTIC_PASSWORD_COMMAND`. A password file or secret-manager command is usually safer than a literal `RESTIC_PASSWORD` environment value because it is less likely to land in shell history, process inspection, or logs. Permissions on any password file must permit only the execution identity that needs it.

Avoid putting credentials in a systemd unit, shell script, repository URL, backup log, ticket, or source-control file. The unit should reference a root-readable environment file or a secret retrieval command instead.

## Initialize deliberately

`restic init` creates a repository and its initial key. It does not back up data. Confirm that the target is the intended new repository, then initialize:

```sh
restic init --repo /srv/restic-repository --password-file /etc/restic/password
```

For a new repository, restic's current stable documentation describes repository format version 2 as the default, with version 2 requiring restic 0.14.0 or newer and adding compression support. Do not force an older format without a compatibility reason. Before upgrading clients or migrating a repository, consult [troubleshooting and migration](troubleshooting-and-migration.md).

## First backup and first recovery proof

```sh
restic --repo /srv/restic-repository --password-file /etc/restic/password \
  backup /data --tag files
restic --repo /srv/restic-repository --password-file /etc/restic/password snapshots
restic --repo /srv/restic-repository --password-file /etc/restic/password \
  restore latest --target /var/tmp/restic-restore-test
```

The restore target must be separate from the original source. Inspect file presence, a representative content sample, permissions/ownership expectations, and application-level consistency where applicable. A byte-perfect file repository does not by itself prove an application database was captured consistently.

## Sources

- Restic introduction and quickstart: https://restic.readthedocs.io/en/stable/010_introduction.html (accessed 2026-07-15)
- Preparing a new repository: https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html (accessed 2026-07-15)
- Official releases and checksums: https://github.com/restic/restic/releases (accessed 2026-07-15)
