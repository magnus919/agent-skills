# Ansible: Safe Fleet Administration

**Applicability:** Load this reference for any Ansible task beyond a one-host ad hoc read. It governs inventory design, content structure, execution, review, testing, troubleshooting, and operational rollout.

This is a control-plane guide, not a bag of YAML. Ansible can apply a bad decision efficiently to every host in scope. Treat inventory, limits, credentials, concurrency, and verification as part of the change, not boilerplate around it.

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

## 14. Operational runbook

Use this sequence for a nontrivial fleet mutation:

1. **Discover:** capture version, config, inventory graph, target count, platform, connection, privilege, current health, and recovery route.
2. **Review content:** inspect the exact play, task paths, roles, tags, variables, collections, and potentially sensitive diff/log behavior.
3. **Local gate:** install pinned dependencies; syntax-check; lint; run unit/scenario tests appropriate to the change.
4. **Preview:** `--check` and, only when safe, `--diff` against the exact canary limit. Read the complete output rather than its exit code alone.
5. **Canary apply:** execute the smallest set. Verify changed component and user-visible boundary. Account for every selected host.
6. **Progressive apply:** use approved serial batches with a health gate and stop condition between them.
7. **Recover or stop:** on unexpected result, stop broadening scope. Preserve evidence, use the named recovery path, and report actual target status.
8. **Close:** record runtime, inventory/limit, play revision, collection set, per-host result, verification evidence, and remaining uncertainty.

## 15. Minimal production-shaped baseline

This is a deliberately small, inspectable starting point for a Unix-like service. It is not a universal repository template. Replace names, package sources, validation commands, service names, inventories, and health checks with ones that match the system being changed.

```text
.
├── ansible.cfg
├── collections/requirements.yml
├── inventories/
│   ├── staging/hosts.yml
│   ├── production/hosts.yml
│   └── production/group_vars/web.yml
├── playbooks/web.yml
└── roles/web_service/
    ├── defaults/main.yml
    ├── tasks/main.yml
    ├── handlers/main.yml
    └── templates/web-service.conf.j2
```

### Project configuration and dependencies

```ini
# ansible.cfg -- retain only policy this repository owns.
[defaults]
inventory = inventories/staging/hosts.yml
roles_path = roles
collections_path = collections
host_key_checking = True
retry_files_enabled = False
```

```yaml
# collections/requirements.yml -- pin a real version for the repository.
---
collections:
  - name: community.general
    version: '>=10.0.0,<11.0.0'
```

The collection range is an example, not a recommendation to copy. Pin a range the repository has actually tested, install it before syntax/lint/test work, and record the resolved set with `ansible-galaxy collection list`.

### Reviewable inventory and variable ownership

```yaml
# inventories/staging/hosts.yml
---
all:
  children:
    web:
      hosts:
        web-staging-01:
          ansible_host: 192.0.2.10
        web-staging-02:
          ansible_host: 192.0.2.11
```

```yaml
# inventories/production/group_vars/web.yml
---
web_service_name: example-web
web_service_package: example-web
web_service_config_path: /etc/example-web/example-web.conf
web_service_listen_port: 8080
```

Keep connection behavior (`ansible_user`, `ansible_port`, `ansible_python_interpreter`, `ansible_connection`) in inventory or its scoped variables. Keep the desired service state in a role default or explicit group variable. Do not place credentials in either plaintext file.

### Playbook with explicit preflight and narrow rollout

```yaml
# playbooks/web.yml
---
- name: Configure the web service
  hosts: web
  become: true
  serial: 1
  max_fail_percentage: 0

  pre_tasks:
    - name: Assert the service inputs are usable
      ansible.builtin.assert:
        that:
          - web_service_name | length > 0
          - web_service_config_path | length > 0
          - web_service_listen_port | int > 0
        quiet: true
      tags: [preflight, always]

  roles:
    - role: web_service
      tags: [deploy]
```

Run the target-resolution command before applying this example:

```sh
ansible-playbook playbooks/web.yml \
  -i inventories/staging/hosts.yml \
  --limit web-staging-01 --list-hosts
```

A pass from `--list-hosts` means only that Ansible selected the expected host. It is not a connection, privilege, configuration, or health proof.

## 16. Common state patterns

Use these as shapes to adapt, not as cargo-cult snippets. First load the exact module documentation and confirm check/diff/platform support for the installed version.

### Module selection and state contracts

| Need | Default approach | Important boundary |
|---|---|---|
| Package state across Unix families | `ansible.builtin.package` | It selects an underlying package manager but does not translate package names or expose every manager-specific option. |
| Complete managed configuration | `ansible.builtin.template` | Validate before replacement when the target format supports it; explicitly set owner, group, and quoted mode. |
| Static file or directory state | `ansible.builtin.copy` or `ansible.builtin.file` | Use `copy` for controller-owned static content and `file` for ownership, mode, directory, link, or absence state. |
| Existing unmanaged file with a narrow invariant | `ansible.builtin.lineinfile`, `ansible.builtin.blockinfile`, or `ansible.builtin.replace` | Use the narrowest declarative edit only when preserving unmanaged content is required; avoid line surgery when the file should instead be owned as a whole. |
| Service or systemd unit | `ansible.builtin.systemd_service` | This is systemd-specific, not a generic Unix service abstraction. |
| Exceptional imperative command | `ansible.builtin.command` with `argv`, `creates`/`removes`, and explicit result semantics | `command` does not interpret shell syntax. Use `shell` only when shell semantics are genuinely required. |
| Python-less bootstrap or network appliance setup | `ansible.builtin.raw`, narrowly and temporarily | Disable fact gathering until bootstrap is complete; `raw` has no check-mode or change-handler support. |

### Bootstrap a target without Python

Use this only for an approved first-contact path. It is intentionally platform-specific and is not an idempotent general-purpose play. Once Python is installed, switch back to normal modules and collect facts.

```yaml
- name: Bootstrap approved Debian-family targets without Python
  hosts: new_debian_targets
  gather_facts: false
  become: true
  tasks:
    - name: Install Python needed by normal Ansible modules
      ansible.builtin.raw: apt-get update && apt-get install -y python3

    - name: Gather facts after Python is available
      ansible.builtin.setup:
```

Do not reuse this `apt-get` command for a non-Debian target. Choose the target's real package manager, bootstrap through an approved image/provisioning path where possible, and keep the bootstrap inventory separate from regular fleet inventory.

### Install, configure, validate, and notify

```yaml
# roles/web_service/tasks/main.yml
---
- name: Install the service package
  ansible.builtin.package:
    name: "{{ web_service_package }}"
    state: present
  tags: [packages, deploy]

- name: Render the validated service configuration
  ansible.builtin.template:
    src: web-service.conf.j2
    dest: "{{ web_service_config_path }}"
    owner: root
    group: root
    mode: '0640'
    backup: true
    # Replace with the program's safe syntax validator. %s is a temporary file.
    validate: '/usr/bin/example-web --check-config %s'
  notify: Restart web service
  tags: [configuration, deploy]

- name: Enable and start the service
  ansible.builtin.systemd_service:
    name: "{{ web_service_name }}"
    enabled: true
    state: started
  tags: [service, deploy]
```

```yaml
# roles/web_service/handlers/main.yml
---
- name: Restart web service
  ansible.builtin.systemd_service:
    name: "{{ web_service_name }}"
    state: restarted
```

`template` uses atomic file operations by default. Do not enable `unsafe_writes` merely to suppress a filesystem problem: it can introduce races and corrupted reads. Resolve the target filesystem/container boundary, or document the exceptional risk. Use a handler for a configuration-triggered restart; do not use `state: restarted` in every normal service task, because that destroys idempotence.

### Imperative escape hatch with an honest contract

```yaml
- name: Initialize an application database exactly once
  ansible.builtin.command:
    argv:
      - /usr/local/libexec/example-web-init
      - --data-dir
      - /var/lib/example-web
    creates: /var/lib/example-web/.initialized
  register: web_init
  changed_when: web_init.rc == 0
  tags: [initialize]
```

Use `argv` where arguments might contain whitespace or templated data. If a templated value must be incorporated into a command string, quote it with the Ansible `quote` filter. Do not represent an unknown command's result as `changed_when: false`; find a real state probe or acknowledge that the operation is not idempotent.

### Recovery-aware block

```yaml
- name: Apply configuration with an explicit recovery path
  block:
    - name: Render validated configuration
      ansible.builtin.template:
        src: web-service.conf.j2
        dest: "{{ web_service_config_path }}"
        mode: '0640'
        validate: '/usr/bin/example-web --check-config %s'
      notify: Restart web service

    - name: Apply the restart before service verification
      ansible.builtin.meta: flush_handlers

    - name: Verify the service is active
      ansible.builtin.command:
        argv: [systemctl, is-active, '--quiet', "{{ web_service_name }}"]
      changed_when: false

  rescue:
    - name: Report the task that failed without exposing secrets
      ansible.builtin.debug:
        msg: "Configuration batch failed at {{ ansible_failed_task.name }}"

    - name: Stop this rollout explicitly
      ansible.builtin.fail:
        msg: "Recovery requires the documented operator path; do not continue to later hosts."

  always:
    - name: Record that this host completed the safety boundary
      ansible.builtin.debug:
        msg: "Completed the apply/recovery boundary for {{ inventory_hostname }}"
```

A `rescue` section runs only after a task returns `failed`; syntax errors and unreachable hosts do not enter it. A successful rescue also changes play failure accounting. Use it for known, reversible local recovery, not as evidence that a fleet rollback exists.

### Reboot and reconnection

```yaml
- name: Reboot a Unix-like host after an approved maintenance change
  ansible.builtin.reboot:
    reboot_timeout: 900
    test_command: /usr/bin/true

- name: Confirm Ansible transport is usable after the reboot
  ansible.builtin.wait_for_connection:
    delay: 10
    timeout: 900
```

`reboot` already waits for the target to return and run its test command. `wait_for_connection` is useful when a later stage needs an independently stated transport boundary, or following an out-of-band reboot. Neither proves the application is healthy; add a service-specific assertion.

### Reuse, tags, delegation, and concurrency

- Use static `import_tasks`/`import_role` when the task graph should be known at parse time and inherited tags should apply to imported tasks.
- Use dynamic `include_tasks`/`include_role` when the file or role must be selected at runtime. Tags on a dynamic include apply to the include itself, not automatically to every included task. Verify tag behavior with `--list-tasks`; dynamic includes are a known preview limitation.
- Tag operational slices consistently (`preflight`, `deploy`, `verify`, `rollback`) and test their selected task set before using them in a change. Do not tag a dangerous task with `never` and assume it is impossible to invoke.
- Use `delegate_to` for a real control-plane action, such as removing one host from a load balancer. Under delegation, connection-related variables are templated using the delegated host. Use `hostvars[inventory_hostname]` when the original host's value is actually needed.
- Delegated tasks still run in parallel by default. If many target hosts write to one delegated control endpoint, use `throttle: 1`, an intentional `run_once` loop, or a serial design. `run_once` runs once per serial batch, not necessarily once for the whole play.
- Use `delegate_facts: true` only when gathered facts should be assigned to the delegated host rather than the current inventory host.

Sources: [package](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/package_module.html), [template](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/template_module.html), [copy](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/copy_module.html), [file](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/file_module.html), [lineinfile](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/lineinfile_module.html), [blockinfile](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/blockinfile_module.html), [replace](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/replace_module.html), [command](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/command_module.html), [raw](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/raw_module.html), [systemd service](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/systemd_service_module.html), [reboot](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/reboot_module.html), [wait for connection](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/wait_for_connection_module.html), [blocks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_blocks.html), [delegation](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_delegation.html), [tags](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_tags.html).

## 17. Vault operations without secret leakage

Section 7 explains the security boundary. This section provides the operating workflow.

### Choose file-level or variable-level encryption deliberately

- Use a fully encrypted variable file when variable names or surrounding structure are sensitive, or when rotation/rekeying the file as a unit is valuable.
- Use `encrypt_string` for an isolated value when readable variable names and reviewable non-secret structure are valuable.
- Do not pass a plaintext secret directly as a shell argument. It can be retained in shell history and process inspection. Prefer a protected prompt or a secured standard-input workflow.

```sh
# Create an encrypted environment file. The password source is intentionally not shown.
ansible-vault create --vault-id production@PROMPT_OR_APPROVED_HELPER \
  inventories/production/group_vars/web/secrets.yml

# Encrypt an individual value without exposing its plaintext in a command line.
ansible-vault encrypt_string \
  --vault-id production@PROMPT_OR_APPROVED_HELPER \
  --stdin-name web_service_api_token

# Inspect or edit encrypted content only through the Vault tool.
ansible-vault view --vault-id production@PROMPT_OR_APPROVED_HELPER path/to/secrets.yml
ansible-vault edit --vault-id production@PROMPT_OR_APPROVED_HELPER path/to/secrets.yml

# Rotate a fully encrypted file and make the new label explicit.
ansible-vault rekey \
  --vault-id old-production@APPROVED_OLD_SOURCE \
  --new-vault-id production@APPROVED_NEW_SOURCE \
  path/to/secrets.yml
```

Vault IDs are labels and hints by default, not proof that the same label always means the same password. Where a project uses multiple vault identities, evaluate `DEFAULT_VAULT_ID_MATCH` as deliberate project policy. Never commit a vault password file. Treat a vault password client script as security-sensitive executable code: it must emit a password only on standard output and must have a reviewed, minimal authorization path.

Before a Vault-bearing production command, use the explicit `--vault-id label@source` form. It makes secret-domain selection visible in the run record. Do not make a lint-only CI job able to retrieve a production vault merely to satisfy syntax checking.

Sources: [encrypting Vault content](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_encrypting_content.html), [managing Vault passwords](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_managing_passwords.html), [using encrypted content](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_using_encrypted_content.html), [ansible-vault CLI](https://docs.ansible.com/projects/ansible/latest/cli/ansible-vault.html).

## 18. Operator command cookbook

Run commands from the automation repository root unless the project documents another working directory. Substitute real paths and limits; do not paste examples that select production into a shell.

### Discover the effective execution context

```sh
ansible --version
ansible-config view
ansible-config dump --only-changed
ansible-galaxy collection list
ansible-inventory -i inventories/staging/hosts.yml --graph
ansible-inventory -i inventories/staging/hosts.yml --host web-staging-01
ansible-inventory -i inventories/staging/hosts.yml --list --yaml
```

`ansible-inventory --list` shows the inventory as Ansible has processed it; `--export` is optimized for export and is not an exact representation of processed inventory. For a standalone inventory query that needs relative `group_vars`/roles behavior, provide `--playbook-dir` deliberately.

### Inspect before applying

```sh
ansible-playbook playbooks/web.yml \
  -i inventories/staging/hosts.yml \
  --limit web-staging-01 \
  --syntax-check

ansible-playbook playbooks/web.yml \
  -i inventories/staging/hosts.yml \
  --limit web-staging-01 \
  --list-hosts

ansible-playbook playbooks/web.yml \
  -i inventories/staging/hosts.yml \
  --limit web-staging-01 \
  --list-tags

ansible-playbook playbooks/web.yml \
  -i inventories/staging/hosts.yml \
  --limit web-staging-01 \
  --tags preflight,deploy --list-tasks
```

### Preview, apply, and account for results

```sh
# Use --diff only when it cannot expose sensitive content.
ansible-playbook playbooks/web.yml \
  -i inventories/staging/hosts.yml \
  --limit web-staging-01 \
  --check --diff

# Apply only after the preview and target set are accepted.
ansible-playbook playbooks/web.yml \
  -i inventories/staging/hosts.yml \
  --limit web-staging-01 \
  --tags preflight,deploy,verify
```

For a failure investigation, start with `-vvv` on one explicitly selected host. The CLI documents `-vvv` as a reasonable initial debug level and `-vvvv` as a likely connection-debug level. Redact before retaining output: verbosity can reveal private addresses, file paths, arguments, and response content.

### Failure-specific probes

| Symptom | Probe in order | Corrective direction |
|---|---|---|
| Wrong hosts | `--graph`, `--host`, then `--list-hosts` with the exact proposed limit | Fix inventory/group/pattern. Never compensate with task conditionals. |
| Wrong config or collection path | `ansible --version`, `ansible-config view`, `ansible-config dump --only-changed`, `ansible-galaxy collection list` | Identify the active configuration/runtime before editing content. |
| SSH, WinRM, or privilege failure | One-host transport probe: `ansible ... -m ansible.builtin.ping -vvv` for POSIX, or `ansible.windows.win_ping` for Windows; then inspect connection variables and approved trust/auth path | Preserve host identity checks; do not disable them to make the run green. |
| Python/module execution failure | Confirm the target interpreter and module requirements; use a narrow `raw` bootstrap only if the target genuinely lacks Python | Return to normal modules/fact gathering after bootstrap. |
| Variable surprise | `--host`, non-secret `debug`, and effective precedence sources | Remove competing overrides instead of adding a higher-precedence override. |
| Changed every run | Inspect module state and managed content; check templates for unstable values such as timestamps; inspect `changed_when` | Model the real state, not the desired summary color. |
| Handler did not produce health | Inspect notification, later task failures, handler order, and reachability | Add an intentional flush/health gate where correctness requires it. |
| Check mode disagrees with apply | Inspect each module's check-mode attribute and task conditions | Treat check mode as a partial preview and use an isolated convergence test. |
| Dynamic inventory stale or wrong | Inspect source output with `--list`, then evaluate cache freshness and source selectors | Fix source/cache policy, not the playbook's host conditions. |

### Async job synchronization

```yaml
- name: Start a bounded asynchronous maintenance action
  ansible.builtin.command:
    argv: [/usr/local/sbin/example-maintenance]
  async: 1800
  poll: 0
  register: maintenance_job

- name: Wait for the asynchronous maintenance action
  ansible.builtin.async_status:
    jid: "{{ maintenance_job.ansible_job_id }}"
  register: maintenance_result
  until: maintenance_result.finished
  retries: 180
  delay: 10
```

Async tasks do not support check mode. A `poll: 0` task continues without automatic observation, so do not start one before a conflicting package/database/control-plane lock operation. Define a timeout, a durable completion signal, and a recovery/cleanup procedure before using it.

Sources: [ansible-playbook CLI](https://docs.ansible.com/projects/ansible/latest/cli/ansible-playbook.html), [ansible-inventory CLI](https://docs.ansible.com/projects/ansible/latest/cli/ansible-inventory.html), [ansible-config CLI](https://docs.ansible.com/projects/ansible/latest/cli/ansible-config.html), [asynchronous actions](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_async.html).

## 19. Quality gates that test behavior

### Lint policy and exceptions

Place `.ansible-lint` in the project root and invoke `ansible-lint` there. Command-line scalar options override config values; list values extend rather than replace them. Do not make a broad `skip_list` the normal policy, because it hides violations entirely. For a narrow, reviewed exception, prefer an adjacent `.ansible-lint-ignore` entry with a reason, then remove it when the exception is resolved.

```yaml
# .ansible-lint -- choose the profile after reviewing the repository's baseline.
---
profile: safety
enable_list:
  - no-log-password
```

The example is intentionally modest. A new repository may choose a stricter reviewed profile; a legacy repository can ratchet up deliberately. `ansible-lint --fix` modifies YAML and may apply rule transforms, so it belongs in a human-reviewed local formatting step, not an opaque CI repair step.

### Minimal Molecule scenario

A Molecule scenario is an isolated test lifecycle, not merely a command name. For a role, provide an apply play and an outcome-verification play. Keep provisioning details appropriate to the actual platform/driver; do not pretend that a generic container proves VM, Windows, appliance, or cloud behavior.

```yaml
# molecule/default/converge.yml
---
- name: Converge
  hosts: all
  become: true
  roles:
    - role: web_service
```

```yaml
# molecule/default/verify.yml
---
- name: Verify web service outcome
  hosts: all
  become: true
  tasks:
    - name: Read service state
      ansible.builtin.command:
        argv: [systemctl, is-active, '--quiet', example-web]
      changed_when: false

    - name: Assert configuration is present
      ansible.builtin.stat:
        path: /etc/example-web/example-web.conf
      register: web_config

    - name: Assert managed configuration exists
      ansible.builtin.assert:
        that:
          - web_config.stat.exists
          - web_config.stat.mode == '0640'
```

```sh
ansible-lint --profile=safety
ansible-playbook playbooks/web.yml --syntax-check
molecule test --scenario default
```

For an integration inventory that is disposable or explicitly approved for repeated convergence, also apply the same play twice and inspect the second recap for `changed=0`:

```sh
# Test inventory only. Do not use this as a blind production rollout command.
ansible-playbook playbooks/web.yml -i inventories/test/hosts.yml --limit web-test-01
ansible-playbook playbooks/web.yml -i inventories/test/hosts.yml --limit web-test-01
```

The standard `molecule test` sequence includes dependency, cleanup/destroy, syntax, create, prepare, converge, idempotence, side effect, verify, cleanup, and destroy. Use individual Molecule actions only when diagnosing a stage, and run the full sequence before declaring a scenario healthy. Molecule's current prerun behavior can install project dependencies into a cache; make dependency source/pinning and network/offline conditions explicit in CI.

CI should report the exact Python, Ansible, collection, ansible-lint, and Molecule versions, run lint/syntax before scenario tests, and store redacted failure output. If CI needs platform resources, select runners that really provide them. Do not treat a container-only pass as proof of Windows, network, or cloud behavior.

Sources: [ansible-lint configuration](https://ansible.readthedocs.io/projects/lint/configuring/), [Molecule configuration](https://ansible.readthedocs.io/projects/molecule/configuration/), [Molecule workflow](https://ansible.readthedocs.io/projects/molecule/workflow/), [Molecule CI](https://ansible.readthedocs.io/projects/molecule/ci/).

## 20. Platform and execution-environment routes

The core reference owns cross-platform safety and Ansible mechanics. These routes prevent false portability.

### Windows

Windows normally uses WinRM through the `psrp` or `winrm` connection plugins, which require separately installed Python dependencies on the control node. WinRM HTTP and HTTPS listeners, certificate validation, authentication, and double-hop behavior are security choices, not a copy/paste preflight. In a domain environment, the official guide recommends Kerberos; Basic and NTLM should not be used over an HTTP listener. Use `ansible.windows` modules (`win_package`, `win_template`, `win_reboot`, and so on) rather than Unix module assumptions.

Windows SSH is a supported alternative in current Ansible, but it needs Windows OpenSSH and correctly matched `ansible_connection: ssh` plus `ansible_shell_type: powershell` or `cmd`. Treat it as a separately validated connection model. Do not mix Unix privilege escalation, `/bin/sh`, or Python bootstrap lore into it.

### Network devices

Select the vendor collection, `ansible_network_os`, and a connection plugin that the vendor supports. Network-device command output and configuration semantics are vendor-specific. Before mutation, capture an authorized, redacted baseline and prove an out-of-band recovery path. Use a real-device or vendor-realistic test environment for risky changes; generic Molecule containers are not a substitute.

### Cloud and dynamic inventory

Provider collections and their dynamic inventory plugins need pinned dependencies, scoped credentials, explicit ownership/environment selectors, and teardown for test resources. An inventory result proves what the provider returned, not that every returned target is authorized for the intended change. Preview selectors, limit the first wave, account for provider rate limits and eventual consistency, and verify the service boundary after API success.

### Execution environments and enterprise tooling

An execution environment is useful when workstation drift, native dependencies, or CI reproducibility make a Python environment insufficient. Before adopting one, inspect its image definition, `ansible-core`, collections, Python dependencies, credentials injection path, and target compatibility. `ansible-navigator`, `ansible-builder`, and Red Hat Ansible Automation Platform are optional enterprise/execution-environment layers, not prerequisites for ordinary community Ansible. Load their current official documentation when they are in scope rather than applying this general reference as if it configured them.

Sources: [Windows WinRM](https://docs.ansible.com/projects/ansible/latest/os_guide/windows_winrm.html), [Windows SSH](https://docs.ansible.com/projects/ansible/latest/os_guide/windows_ssh.html), [network command output](https://docs.ansible.com/projects/ansible/latest/network/user_guide/network_working_with_command_output.html), [execution environments](https://docs.ansible.com/projects/ansible/latest/getting_started_ee/index.html).

## 21. Source-to-task routing

Use this reference for fleet safety, common patterns, and first-line diagnosis. Load the linked primary source before committing to a version-sensitive detail, module parameter, vendor behavior, or platform connection setup.

| Need | Load first | Then verify |
|---|---|---|
| A module parameter, check mode, diff mode, or platform support | The installed collection/module page via `ansible-doc` and the matching official module page | Installed `ansible-core` and collection version. |
| A host-selection question | Inventory, patterns, and `ansible-inventory` CLI docs | `--graph`, `--host`, and exact `--list-hosts` output. |
| A variable surprise | Variables/facts/precedence docs | Effective inventory, non-secret debug output, and all override sources. |
| A connection or escalation failure | Connection details and the target platform's connection guide | One-host `ping`/transport probe using approved authentication. |
| A secret workflow | Vault encrypting, password-management, and encrypted-content guides | Repository secret policy and actual CI secret boundary. |
| A lint finding or suppression | ansible-lint rule and configuring docs | Current linter version and project-root run. |
| A role scenario test | Molecule workflow and configuration docs | Full `molecule test` lifecycle on a representative target. |
| Windows, network, cloud, or execution-environment work | The dedicated official platform/tool guide | Vendor/provider/connection collection and a realistic test path. |

## Source index and freshness

This reference was refreshed from primary documentation on 2026-07-13. It deliberately avoids frozen support windows and release-specific defaults. Before acting on a version-sensitive detail, confirm it against the exact installed `ansible-core`, collection, connection plugin, and target platform documentation.

Primary sources consulted:

- [Ansible installation](https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_installation.html)
- [Ansible configuration](https://docs.ansible.com/projects/ansible/latest/installation_guide/intro_configuration.html)
- [Inventory](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html)
- [Dynamic inventory](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_dynamic_inventory.html)
- [Connection details](https://docs.ansible.com/projects/ansible/latest/inventory_guide/connection_details.html)
- [Variables](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html)
- [Facts and magic variables](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_vars_facts.html)
- [General precedence](https://docs.ansible.com/projects/ansible/latest/reference_appendices/general_precedence.html)
- [Roles](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html)
- [Handlers](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_handlers.html)
- [Strategies](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_strategies.html)
- [Check and diff mode](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html)
- [Error handling](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html)
- [Privilege escalation](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_privilege_escalation.html)
- [Vault](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault.html)
- [Installing collections](https://docs.ansible.com/projects/ansible/latest/collections_guide/collections_installing.html)
- [Verifying collections](https://docs.ansible.com/projects/ansible/latest/collections_guide/collections_verifying.html)
- [Windows management](https://docs.ansible.com/projects/ansible/latest/os_guide/intro_windows.html)
- [Network best practices](https://docs.ansible.com/projects/ansible/latest/network/user_guide/network_best_practices_2.5.html)
- [Ansible configuration settings](https://docs.ansible.com/projects/ansible/latest/reference_appendices/config.html)
- [ansible-config](https://docs.ansible.com/projects/ansible/latest/cli/ansible-config.html)
- [Ansible FAQ](https://docs.ansible.com/projects/ansible/latest/reference_appendices/faq.html)
- [Asynchronous actions and polling](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_async.html)
- [General tips](https://docs.ansible.com/projects/ansible/latest/tips_tricks/ansible_tips_tricks.html)
- [ansible-lint usage](https://ansible.readthedocs.io/projects/lint/usage/)
- [ansible-lint rules](https://ansible.readthedocs.io/projects/lint/rules/)
- [Molecule playbook testing](https://ansible.readthedocs.io/projects/molecule/getting-started-playbooks/)
- [Molecule CI](https://ansible.readthedocs.io/projects/molecule/ci/)
