# Ansible: Runbooks and Advanced Operations

> Part of the Ansible fleet-administration reference — sections 14-21: operational runbook, minimal production-shaped baseline, common state patterns, vault operations, operator command cookbook, quality gates, platform and execution-environment routes, and source-to-task routing. Index: [ansible.md](ansible.md)

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

