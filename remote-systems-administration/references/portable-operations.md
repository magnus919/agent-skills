# Portable Remote Operations

## Start with bounded, read-only discovery

A remote hostname is not a platform classification. Establish identity and available control planes from the live host before selecting an overlay.

```sh
ssh -o BatchMode=yes -o ConnectTimeout=10 admin@example-host '
  printf "host="; hostname
  uname -srm
  command -v systemctl service rcctl launchctl || true
  command -v apt-get dnf yum zypper pacman pkg pkg_add softwareupdate brew || true
  id
'
```

Use a known host alias and a managed `known_hosts` file. Keep `BatchMode=yes` for non-interactive automation so authentication failures stop rather than prompting or hanging. Do not use `StrictHostKeyChecking=no`; an unexpected host key must be investigated through an authorized identity channel.

## SSH access patterns

| Need | Prefer | Guardrail |
|---|---|---|
| One host, one bounded command | `ssh host -- command` | Quote the remote command deliberately; capture exit status and bounded output |
| Bastion/jump host | `ProxyJump` in SSH config or `ssh -J` | Validate the route and host keys for each hop |
| Repeated one-host sessions | SSH connection multiplexing | Use a private control socket path and bounded lifetime; do not share it across principals |
| Transfer a known file | `sftp` or `scp` with explicit source/destination | Verify checksum or content and owner/mode after transfer |
| Privileged command | `sudo -n` after checking authorization | Do not consume prompts or transmit passwords in command text |

`ssh` and `sftp` support `ProxyJump`; OpenSSH configuration also supports connection sharing through `ControlMaster` and `ControlPath`. These improve routing and performance, not authorization.

## POSIX baseline

Portable primitives are useful for discovery, not proof that every utility flag is portable. Prefer a small, bounded set:

| Question | Typical tools | Evidence to capture |
|---|---|---|
| Identity and OS | `hostname`, `uname`, `id` | hostname, kernel/system label, effective identity |
| Process/service clue | `ps`, `pgrep`, `kill -0` | process state only, not application health |
| Filesystem capacity | `df`, `du` | affected mount and available capacity |
| Memory/load | `uptime`, `vmstat` where available | bounded sample and platform caveat |
| Network/listener | `netstat`, `sockstat`, `ss`, `lsof` as discovered | listener and bound address, not merely process PID |
| Logs | `tail`, platform log reader | a bounded time/range and redaction |
| Config/file state | `test`, `stat`, `cmp`, checksums | path, ownership/mode, hash or minimal diff |

Do not write a “portable” command that assumes GNU `sed`, GNU `date`, `grep -P`, `xargs -r`, Bash, or Linux `/proc`. If a task needs those capabilities, classify the platform and use the appropriate overlay.

## Safe remote execution

1. Send one command category per SSH invocation: discovery, validation, or a single scoped mutation. Avoid opaque `&&` chains that blur the failed step.
2. Set client-side timeouts and use non-interactive mode for automation.
3. Do not emit secrets into the process list, shell history, logs, or command output. Use an authorized secret mechanism outside command arguments.
4. For a file edit, capture the original metadata/content hash, validate syntax before reload where the platform supports it, and retain a rollback artifact.
5. Preserve output bounds. Ask for the relevant unit, process, or time range instead of `journalctl`/`log show`/`dmesg` dumps.

## Privilege boundaries

`sudo` is a privilege boundary, not a convenient prefix. Confirm the intended account and command authorization using a read-only check appropriate to local policy. `sudo -n` is safer for automation because it fails instead of waiting for an unseen password prompt. Do not modify sudoers, SSH authorization, users, groups, or host keys without an explicit directive and recovery path.

## Verification boundary

A remote command's exit code is evidence about that command only. For a service change, gather:

1. service-manager or process state;
2. relevant logs/events after the change;
3. listener, local socket, or protocol check where applicable; and
4. the actual dependent or external boundary the change was meant to restore.

For platform-specific commands, load the corresponding overlay and `references/safety-and-verification.md`.
