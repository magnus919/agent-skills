# Fleet Automation: Ansible and Paramiko

## Choose the fleet control plane

| Work shape | Default | Why |
|---|---|---|
| Diagnose a few distinct hosts | Native SSH | The work is investigative, not desired-state management |
| Apply repeatable state to multiple hosts | Ansible | Inventory, idempotence, check/diff support, bounded rollout, and per-host results already exist |
| Python must manage SSH channels, SFTP, or a custom event loop | Paramiko | It supplies SSH protocol primitives, not fleet safety or desired-state semantics |

Do not build an SSH loop when an Ansible playbook expresses the desired state. Do not introduce Paramiko merely to avoid learning SSH configuration or Ansible inventory.

## Inventory and scope

Inventory is an authorization and blast-radius boundary, not a list of convenient addresses. Before a fleet mutation, identify groups, environment, maintenance constraints, platform differences, escalation method, and exclusion rules. Separate Linux, FreeBSD, NetBSD, OpenBSD, and macOS groups unless you have proved an action is portable.

Start with a canary host and a narrow limit. A fleet run must have:

- an explicit inventory or bounded host expression;
- a target count and maximum parallelism;
- a canary or serial batch strategy for nontrivial changes;
- a stop condition, such as failed health checks or unexpected diffs;
- a rollback or containment action per batch; and
- a per-host result record, including unreachable hosts.

## Ansible execution

Use Ansible for declared state, platform-specific modules, and structured results. Prefer modules over `shell`/`command`; use the latter only when no module accurately represents the job and then make `changed_when`, `failed_when`, and idempotence explicit.

The generic `ansible.builtin.package` module delegates to the package manager detected from target facts. It exposes only the common denominator, does not translate package names between distributions, and inherits check/diff support from the underlying manager. Use it only where that limited contract is enough. Split platform groups or use a specific module when package naming, repository policy, transaction preview, or service implications differ.

`ansible.builtin.systemd_service` applies only to hosts managed by systemd. Its `started` and `stopped` states are idempotent; `restarted` and `reloaded` are active lifecycle requests. Do not use a systemd-specific task against a generic POSIX group.

```sh
# Read-only reachability and facts for a limited group.
ansible unix_canary -m ansible.builtin.ping
ansible unix_canary -m ansible.builtin.setup -a 'filter=ansible_distribution*'

# Preview a single canary. --check is a simulation, not proof.
ansible-playbook site.yml --limit unix_canary --check --diff

# Apply in a deliberately bounded batch after review.
ansible-playbook site.yml --limit unix_canary
```

Ansible check mode runs without making remote changes only for modules that support it; unsupported modules can report nothing and do nothing. Diff output can reveal sensitive values. Treat both as previews with known gaps, not as completed validation. Redact or disable diffs for secrets.

Use `serial` for progressive batches and `max_fail_percentage` or explicit failure handling to stop a rollout. Avoid `strategy: free` for changes whose ordering, capacity, or error containment matters. `run_once` runs once per serial batch, not necessarily once for the entire play; use an explicit condition against the complete play host list when a task must execute globally exactly once.

## Paramiko

Paramiko's `SSHClient` and `Transport` provide SSH protocol access. The caller owns policy: host-key verification, timeouts, authentication source, concurrency limit, command allowlist, stdout/stderr limits, exit-status handling, cleanup, and result aggregation.

Minimum behavioral requirements for a Paramiko-based operation:

1. Load an approved host-key source and reject unknown or changed keys. Never use `AutoAddPolicy` for a managed fleet.
2. Set connection, banner, authentication, channel, and command timeouts.
3. Bound concurrent connections and collect a result for every target.
4. Read stderr and exit status; a channel that opened is not a successful command.
5. Close channels and clients deterministically, including failure paths.
6. Keep credentials out of source, command strings, and logs. Use an authorized credential provider.
7. Establish the procedure on a canary before concurrent execution.

A hand-written Paramiko tool must not silently erase Ansible's safety features. If it needs inventory parsing, host grouping, canary policy, retries, structured result files, privilege management, configuration idempotence, or secrets integration, the job likely belongs in Ansible or a deliberately designed automation system.

## Result and recovery contract

For each target, record only bounded operational metadata:

```text
target: host alias or approved inventory name
platform: detected family/release
operation: discovery | preview | apply | rollback
status: passed | failed | unreachable | skipped | rolled_back
evidence: command category plus bounded result reference
```

Do not mark a fleet run complete while “unreachable” or “skipped” targets are unaccounted for. A partial rollout is an outcome that needs an explicit decision, not an implicit success.
