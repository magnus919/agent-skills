# Ansible: Administration and Safety

> Part of the Ansible fleet-administration reference — sections 1-13: tool choice, installation, inventory, connection, content architecture, collections, secrets, execution, failure and recovery, testing, troubleshooting, platform boundaries, and performance. Index: [ansible.md](ansible.md)

## 1. First decide whether Ansible is the right tool

Use native SSH for a bounded, investigative task on one host. Use Ansible when the intended state is repeatable across hosts and the playbook is worth preserving. Do not write a playbook merely to run a one-off command on a fleet; first determine whether the work has a stable desired state, an explicit target set, an idempotent representation, and a verification boundary.

Before any state-changing run, establish:

- the exact inventory source, host pattern, and an explicit `--limit` for the first run;
- the affected platform, connection method, remote user, escalation method, and secret source;
- a canary, batch size, health check, stop condition, and recovery action;
- the desired-state module or a documented reason to use `command`/`shell`;
- component-level and external/user-visible verification; and
- a per-host accounting for `ok`, `changed`, `failed`, `unreachable`, and `skipped`.

Do not use an ad hoc command as a substitute for a reviewed playbook when a fleet mutation is recurring or safety-sensitive.

## 2. Installation, version, and control-node policy

### Pin the automation environment, not just a package name

`ansible` is a community package that includes `ansible-core` plus curated collections. `ansible-core` is the runtime. Collection and Python dependency versions can change behavior independently of either package. For a team or production repository:

1. Pin the supported `ansible-core` / `ansible` range in the project environment.
2. Pin required collection versions in `collections/requirements.yml`.
3. Record the tested control-node Python and automation versions in CI output or a lockfile.
4. Upgrade intentionally in a branch, read the relevant porting guide, lint, test, preview, and canary before broad rollout.

Use an isolated Python environment (`pipx`, venv, or an execution environment) rather than mutating the control host’s system Python. The official installation guide documents pipx, pip, container, and distribution installation paths. Select the path that permits a reproducible upgrade and rollback, not merely the shortest first install.

```sh
# Inspect the actual runtime before trusting a runbook or CI image.
ansible --version
ansible-playbook --version
ansible-galaxy collection list
```

Treat output from those commands as evidence. Do not infer the runtime from a repository requirement or a workstation’s package manager.

### Configuration ownership

Keep project configuration in the repository when it is part of how the project runs. Know that Ansible configuration can come from configuration files, environment variables, and command-line options. Before debugging surprising behavior, capture effective versions, inventory, configuration file location, collection paths, and relevant environment overrides.

Do not copy a global `ansible.cfg` into a project blindly. A project configuration should express only deliberate project policy, such as inventory location, roles/collections paths, callback behavior, or a known connection setting. Do not disable host-key checking in production configuration.

Sources: [installation](https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_installation.html), [configuration](https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_configuration.html), [configuration settings](https://docs.ansible.com/projects/ansible/latest/reference_appendices/config.html), [porting guides](https://docs.ansible.com/projects/ansible/latest/porting_guides/porting_guides.html).

## 3. Inventory is a safety boundary

Inventory answers two different questions:

- **Who is in scope?** Hosts and groups define the possible blast radius.
- **How should Ansible behave toward them?** Connection variables, interpreter selection, credentials, platform data, and group variables define behavior.

Keep environments separate and legible. A production target should not become selectable just because a permissive host pattern or a merged inventory happened to include it. Prefer YAML inventory for reviewable structure. Use dynamic inventory only where its source of truth is authoritative and its resulting host set is inspectable.

### Required inventory checks

Run these before a mutation, and retain bounded output with the change record:

```sh
ansible-inventory -i inventories/production --graph
ansible-inventory -i inventories/production --list
ansible-inventory -i inventories/production --host canary-01
ansible all -i inventories/production --list-hosts --limit 'web:&production'
```

The last command should show exactly the intended first-wave hosts. If it does not, stop. Do not compensate by changing playbook logic until the inventory and pattern are understood.

### Organization rules

- Group by stable operational properties: environment, platform family, service role, lifecycle, maintenance domain, or connection type.
- Keep host-specific exceptions in `host_vars`; keep shared intentional state in `group_vars`.
- Do not hide a production exception in a generic group that also affects staging.
- Prefer distinct platform groups when module names, package names, service managers, filesystems, or firewall semantics differ.
- Treat dynamic inventory output as generated input: inspect it, cache only with a known freshness policy, and test its selectors in CI when possible.
- Inventory variable precedence is complex and version-sensitive. At the category level, configuration settings are overridden by command-line options, then playbook keywords, then variables, then direct assignment where a plugin/module supports it. Within variables, `-e`/extra vars have the highest precedence. Design so correctness does not depend on a contest between unrelated overrides; do not use `-e` as an implicit production configuration mechanism.

### Patterns and limits

A play’s `hosts:` is not a sufficient rollout guard. Use `--limit` for the canary and each approved batch. Quote patterns in the shell so the shell cannot reinterpret characters. Prefer an explicit named canary group to clever negation or interpolation.

Sources: [inventory](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html), [patterns](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_patterns.html), [dynamic inventory](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_dynamic_inventory.html), [variables and precedence](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html), [general precedence](https://docs.ansible.com/projects/ansible/latest/reference_appendices/general_precedence.html).

## 4. Connection, identity, and privilege

An SSH connection proves connectivity, not host identity, authority, or escalation policy.

- Preserve host-key checking. An unknown or changed key is an identity event; resolve it through the authorized trust path.
- Use an approved SSH key or credential source. Do not put passwords, private keys, proxy secrets, or `--ask-pass` transcripts into source or CI logs.
- Verify the remote user and `become` behavior with a read-only canary before a privileged mutation.
- Use `become` narrowly. Set `become_user` or `become_method` only where the target platform and policy require it. Do not assume Unix escalation applies to Windows or network devices.
- Use a documented bastion/jump-host configuration. Keep the recovery connection distinct from the access path being changed.

For Windows, use the supported Windows connection and setup documentation, not Unix SSH assumptions. For network devices, select the vendor collection and supported network connection plugin; do not model a network device as a generic Linux target.

Sources: [connection details](https://docs.ansible.com/projects/ansible/latest/inventory_guide/connection_details.html), [privilege escalation](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_privilege_escalation.html), [Windows guide](https://docs.ansible.com/projects/ansible/latest/os_guide/intro_windows.html), [network guide](https://docs.ansible.com/projects/ansible/latest/network/getting_started/index.html).

## 5. Content architecture and style

### Default repository shape

Use a structure that makes scope, variables, dependencies, and tests discoverable:

```text
.
├── ansible.cfg
├── inventories/
│   ├── production/
│   │   ├── hosts.yml
│   │   ├── group_vars/
│   │   └── host_vars/
│   └── staging/
├── playbooks/
│   ├── site.yml
│   └── service.yml
├── roles/
│   └── service/
│       ├── defaults/main.yml
│       ├── tasks/main.yml
│       ├── handlers/main.yml
│       ├── templates/
│       ├── files/
│       ├── vars/
│       └── meta/
├── collections/requirements.yml
├── molecule/
└── .ansible-lint
```

This is a starting shape, not a mandate to create every directory. Use roles for reusable units with a stable input contract. Keep a one-off playbook small instead of creating a role that will never be reused.

### Style rules that prevent operational mistakes

- Name every play, block, task, and handler by the intended outcome, not the module name.
- Use fully qualified collection names, such as `ansible.builtin.template` or `community.general.some_module`, so origin is explicit and collection collisions are visible.
- Prefer a purpose-built module over `command`, `shell`, `raw`, or a copied script.
- When `command` or `shell` is genuinely necessary, use `argv` when appropriate, register the result, define `changed_when` and `failed_when`, and make idempotence explicit. Do not claim idempotence merely because a command often succeeds twice.
- Put user-adjustable role inputs in `defaults`; reserve `vars` for values callers should not casually override. Define an argument specification when a reusable role needs a clear contract.
- Separate platform-specific tasks using explicit variables, facts, or include files. Do not hide incompatible package/service/firewall behavior behind a false generic abstraction.
- Use tags for operational slices such as `preflight`, `deploy`, `verify`, and `rollback`, but do not use tags to skip prerequisite safety work.
- Use `assert` early for assumptions that must hold before mutation.
- Use templates for complete configuration ownership; use narrowly scoped editing modules only when preserving unmanaged content is actually required.

### Handlers

Handlers run when notified and normally run after the tasks in the play. A configuration write that notifies a restart can leave a host inconsistent if a later task fails before handlers run. Decide intentionally whether a sensitive change needs a handler flush, a `block`/`rescue` flow, or forced handlers. Do not add `force_handlers` as a reflex: it changes failure behavior and still cannot run on an unreachable host.

Sources: [roles](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html), [handlers](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_handlers.html), [error handling](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html), [playbook keywords](https://docs.ansible.com/projects/ansible/latest/reference_appendices/playbooks_keywords.html).

## 6. Collections and dependency supply chain

Collections are executable automation dependencies, not snippets. Pin them in `requirements.yml`, review their provenance and version changes, and install the declared dependency set in CI and execution environments.

```yaml
---
collections:
  - name: community.general
    version: '>=10.0.0,<11.0.0'
```

The version range is illustrative. Choose and document a project policy; do not paste it as a universal recommendation.

Operational rules:

1. Use namespaces and FQCNs in content.
2. Install declared requirements before linting or testing content that depends on them.
3. Prefer a repository-managed requirements file over manual workstation installation.
4. For offline or controlled environments, download/build an approved artifact set and install from it.
5. Use signature verification where the collection source and policy support it.
6. Re-list installed collections after an upgrade and test a representative run before rollout.

Do not use unpinned `main` branches as production dependencies. A source checkout can be legitimate for development, but it is not a stable operational dependency.

Sources: [installing collections](https://docs.ansible.com/projects/ansible/latest/collections_guide/collections_installing.html), [verifying collections](https://docs.ansible.com/projects/ansible/latest/collections_guide/collections_verifying.html), [using collections](https://docs.ansible.com/projects/ansible/latest/collections_guide/collections_using_playbooks.html).

## 7. Secrets: Vault is necessary but not sufficient

Ansible Vault protects encrypted data at rest. It does not protect a secret after decryption or prevent it from appearing in module output, diffs, task arguments, callback logs, CI artifacts, editor swap files, or a target host.

Rules:

- Store vault passwords outside source control and retrieve them through an approved secret mechanism.
- Use vault IDs when distinct environments or secret domains need separate passwords.
- Keep secret-bearing values out of task names, `debug`, failure messages, generated artifact names, and shell command lines.
- Apply `no_log: true` to a task that handles a secret, but remember that it suppresses useful diagnostics. Validate inputs before the secret-bearing task and record only redacted evidence.
- Never expose secrets through `--diff`; disable diff for secret-bearing template/copy work or use a safer verification mechanism.
- Give CI the least secret access needed. A lint/syntax job should use dummy defaults or isolated controlled configuration when it does not need real vault data.
- Treat an executable vault password helper as code execution. Do not lint or run untrusted repository content with a configuration that can invoke it.

Sources: [Vault guide](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault.html), [managing vault passwords](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_managing_passwords.html), [ansible-lint vault guidance](https://ansible.readthedocs.io/projects/lint/usage/#vaults).

## 8. Execution model: preview, canary, batches, verify

### Syntax and dependency gate

Before an environment-changing run, execute a local gate from the repository root:

```sh
# `-p collections/` matches the repository's `collections_path` configuration.
ansible-galaxy collection install -r collections/requirements.yml -p collections/
ansible-playbook playbooks/site.yml --syntax-check
ansible-lint --profile=safety
```

Adapt paths and profile to the repository. Do not use `--fix` in CI as a hidden formatter. It can modify YAML; run it deliberately in a working tree, inspect the diff, and commit only intended changes.

### Preview has limits

`--check` simulates only modules that support check mode. `--diff` exposes before/after data only for modules with diff support and can disclose sensitive values. A clean check run proves neither that every task would work nor that the service boundary is healthy.

Use preview as a review input:

```sh
ansible-playbook playbooks/site.yml \
  -i inventories/production \
  --limit canary \
  --check --diff
```

Do not pass `--diff` if any affected task can reveal secret or sensitive configuration material.

### Canary and progressive rollout

Use the smallest viable batch first. For a service change, execute preflight, apply, and verify together for each batch rather than applying every batch before observing outcomes.

```yaml
- name: Roll out service configuration
  hosts: service
  serial:
    - 1
    - 10%
    - 25%
    - 100%
  max_fail_percentage: 0
  any_errors_fatal: true
  roles:
    - service
```

The values are a pattern, not a universal policy. Choose batches based on redundancy, capacity, repair time, and a real stop condition. `max_fail_percentage` applies per serial batch; the documented threshold must be exceeded, not merely reached. `run_once` also runs once per serial batch, not once for the entire play. If an action must run once globally, use an explicit condition tied to the complete play host list or delegate to a designated coordinator.

Do not default to `strategy: free` for coordinated changes. The default linear strategy advances task-by-task across the selected hosts; the free strategy lets hosts progress independently and changes ordering and containment assumptions. Raise `forks` only after measuring control-node and target-side capacity. Use `throttle` for tasks that are expensive or hit a rate-limited dependency.

Sources: [check and diff](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html), [strategies](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_strategies.html), [error handling](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html).

## 9. Failure, recovery, and rollback design

A rescue block is not a rollback plan. It handles a task failure in the current execution path; it cannot necessarily recover an unreachable host, reverse an external side effect, restore data, or undo a partial change that an underlying command applied before failing.

For a risky play, design these explicitly:

- **preflight:** prove reachability, identity, prerequisites, capacity, backup/recovery artifacts, and the safe target set;
- **apply:** one idempotent desired-state change at a time where feasible;
- **containment:** stop further batches if a health signal, diff, error, or target count is unexpected;
- **recovery:** named restoration command/playbook and the credentials/access path needed to run it;
- **verification:** a component check and the service/client boundary; and
- **accounting:** no silent success with hosts that are failed, unreachable, skipped, or only partially rolled back.

Use `failed_when` and `changed_when` to model the actual contract of an exceptional command. Lists of conditions are joined as logical AND; use an explicit OR expression when any condition must trigger failure/change. Avoid `ignore_errors` as a generic availability tactic. It does not cover syntax, undefined variables, connection failure, or execution failures, and it makes a real failure easier to miss.

Use `any_errors_fatal` only when a failed task must halt the current rollout. Use `max_fail_percentage` only with a value chosen for the batch size and redundancy model. Use `meta: clear_host_errors` only after an intentional recovery condition, not as a way to hide an access failure.

Sources: [error handling](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html), [blocks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_blocks.html).

## 10. Testing and CI

### Minimum repository gate

Run from the repository root. Current ansible-lint documentation warns that running from a role/task subdirectory is unsupported and can report zero violations even when violations exist.

1. Install pinned dependencies.
2. Run syntax checking.
3. Run ansible-lint with an explicit project/profile policy.
4. Test a representative convergence path.
5. Test idempotence by applying the same intended state again.
6. Verify outcome assertions, not only task exit status.

```sh
ansible-playbook playbooks/site.yml --syntax-check
ansible-lint --profile=safety
molecule test --scenario default
```

`ansible-lint` supports staged quality profiles from `min` through `production`. Adopt it progressively if a legacy repository has many findings: keep known, reviewed debt narrowly ignored with a reason, and make new violations fail CI. Do not generate an ignore file and call the repository compliant.

Ansible-lint can install collection requirements and maintains a `.cache` under the project directory. Keep that cache out of version control. Its `--offline` mode avoids dependency installation and schema refresh, so it can produce a less complete result; use it only when an offline execution is the intended test condition. For machine-readable CI, it supports SARIF output. Use `--fix` only in a human-reviewed formatting job, because it rewrites YAML.

### Molecule

Molecule provides scenario-based testing. The current official playbook-testing guide demonstrates a lifecycle of dependency, create, prepare, converge, idempotence, verify, cleanup, and destroy. A useful scenario proves:

- the test target can be created or reached;
- dependencies and preconditions are satisfied;
- the play converges;
- a second convergence is idempotent where that is a requirement;
- `verify.yml` asserts the desired observable state; and
- cleanup/destroy returns the test environment to a known state.

Container tests are valuable for role logic but do not prove every fact about a VM, init system, kernel, network, cloud API, or managed service. Match the scenario to the risk. Network content needs vendor/platform-realistic testing; Windows content needs a Windows target; cloud content needs an isolated account/project and explicit cleanup.

Sources: [ansible-lint usage](https://ansible.readthedocs.io/projects/lint/usage/), [ansible-lint rules](https://ansible.readthedocs.io/projects/lint/rules/), [Molecule playbook testing](https://ansible.readthedocs.io/projects/molecule/getting-started-playbooks/), [Molecule CI](https://ansible.readthedocs.io/projects/molecule/ci/).

## 11. Troubleshooting protocol

Do not start by changing flags. Capture evidence in this order.

### A. Reproduce scope and environment

```sh
ansible --version
ansible-inventory -i inventories/target --graph
ansible-inventory -i inventories/target --host target-01
ansible-config dump --only-changed
ansible target-01 -i inventories/target -m ansible.builtin.ping -vvv
```

Confirm the expected configuration file, inventory source, collection paths, host target, connection plugin, remote user, interpreter, and extra variables. `ansible-config dump --only-changed` exposes non-default effective settings; `ansible-config view` displays the selected configuration file. A wrong inventory or configuration source is more likely than a novel Ansible bug.

### B. Separate failure classes

| Symptom | First evidence to gather | Do not assume |
|---|---|---|
| `UNREACHABLE` | DNS/IP, SSH/WinRM route, host-key state, authentication, connection variables | A module or playbook bug |
| Python/module failure | Target interpreter, module requirements, module stdout/stderr, platform fact | The control node’s Python applies remotely |
| Undefined/wrong variable | `debug` only non-sensitive values, inventory host view, group membership, precedence source | The closest var file wins |
| Role/module not found | Installed collection list, requirements file, FQCN, collection paths | A package install made it available to this runtime |
| Changed every run | Module state contract, managed file drift, command result, `changed_when` | The playbook is idempotent because it succeeds |
| Handler did not run | Notification, later failures, flush point, reachability | A config update made the service active |
| Check-mode mismatch | Module check-mode support, task-level overrides, `when` behavior | Check is an integration test |

### C. Increase verbosity deliberately

Use `-v`, `-vv`, or `-vvv` only as needed, with a narrow `--limit`. Verbose output can include sensitive paths, arguments, and response content. Save a bounded redacted excerpt, not the complete transcript, in a ticket or report.

For a single failing task, start with the smallest correct reproduction: one target, relevant tags/start point only if prerequisites are still satisfied, no production broadening. A task that passes alone may still fail in the real sequence because facts, variables, handlers, or prior state differ.

### D. Do not use these as fixes

- disabling host-key checking;
- setting `ignore_errors: true` to make CI green;
- skipping lint rules without an explanation and expiry/review point;
- broadening a limit after a canary failure;
- adding `changed_when: false` to hide drift rather than modelling it; or
- running `--diff` on secret-bearing content to obtain diagnostics.

Sources: [connection details](https://docs.ansible.com/projects/ansible/latest/inventory_guide/connection_details.html), [error handling](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html), [FAQ](https://docs.ansible.com/projects/ansible/latest/reference_appendices/faq.html), [ansible-lint usage](https://ansible.readthedocs.io/projects/lint/usage/).

## 12. Platform-specific boundaries

### Linux and Unix-like hosts

Use the platform-specific module and split inventory when package managers, package names, services, firewall stacks, or configuration conventions differ. `ansible.builtin.package` exposes a common package interface but does not make package naming, repositories, transaction behavior, or OS lifecycle portable. `ansible.builtin.systemd_service` is not a generic Unix service abstraction.

### Windows

Windows management has different connection, authentication, privilege, reboot, module, and fact semantics. Bootstrap and connect according to the official Windows setup guide. Do not copy Unix `become`, shell, or Python assumptions into Windows automation. Verify the chosen Windows collection and target support for each module.

### Network devices

Use a vendor collection, explicit `ansible_network_os`, and supported network connection plugin. Back up or capture the current configuration only through an authorized, redacted path. Treat device configuration changes like connectivity changes: canary first, maintain an out-of-band recovery path, and verify the actual forwarding/service behavior after the device reports success.

### Cloud

Use provider collections with pinned versions and isolated test accounts/projects. Dynamic inventory is not proof that a target is authorized. Apply immutable labels/tags that express environment and ownership, preview the resulting host set, limit first, and explicitly clean up test resources. Provider APIs introduce rate limits, eventual consistency, and external state that a generic local Molecule test may not reproduce.

Sources: [Windows management](https://docs.ansible.com/projects/ansible/latest/os_guide/intro_windows.html), [Windows setup](https://docs.ansible.com/projects/ansible/latest/os_guide/windows_setup.html), [network best practices](https://docs.ansible.com/projects/ansible/latest/network/user_guide/network_best_practices_2.5.html), [cloud guides](https://docs.ansible.com/projects/ansible/latest/scenario_guides/cloud_guides.html).

## 13. Performance without unsafe parallelism

Performance tuning starts with measurement and a narrow representative inventory. The default documented execution uses the linear strategy with five forks. More forks can help only if the control node, network, remote endpoints, and external services can tolerate the concurrency.

Safe order:

1. Measure current runtime and identify whether delay is connection setup, fact gathering, module execution, package/API activity, or controller CPU/disk.
2. Reuse SSH connections only with an approved SSH configuration and host-key policy.
3. Disable or filter fact gathering only when a play does not need those facts and the lost discovery is acceptable.
4. Raise `forks` incrementally in a non-production or limited environment.
5. Use `serial` to bound rollout, and `throttle` for a particular expensive/rate-limited task.
6. Use async/poll only when the task’s state, timeout, completion signal, and recovery behavior are explicit. `poll: 0` launches and continues without automatically observing completion: use the returned job ID with `async_status` when a synchronization point is needed, and do not combine it with operations that require an exclusive lock. Async tasks do not support check mode, so make the check-mode path intentional.

Do not trade away target containment for a faster wall-clock time. A large package transaction, database migration, control-plane request, or reboot is usually governed by the target dependency, not the number of Ansible forks.

Sources: [strategies](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_strategies.html), [asynchronous actions and polling](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_async.html), [FAQ performance and SSH](https://docs.ansible.com/projects/ansible/latest/reference_appendices/faq.html).

