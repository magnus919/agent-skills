# Ansible: Safe Fleet Administration

**Applicability:** Load this reference for any Ansible task beyond a one-host ad hoc read. It governs inventory design, content structure, execution, review, testing, troubleshooting, and operational rollout.

This is a control-plane guide, not a bag of YAML. Ansible can apply a bad decision efficiently to every host in scope. Treat inventory, limits, credentials, concurrency, and verification as part of the change, not boilerplate around it.

The full reference is split into two parts so each file stays within the reference size cap. The table below routes you to the part that covers the section you need.

## Parts of this reference

| Part | Scope |
|---|---|
| [ansible-administration-and-safety.md](ansible-administration-and-safety.md) | Sections 1-13: tool choice, installation, inventory, connection and privilege, content architecture, collections, secrets, execution model, failure and rollback, testing and CI, troubleshooting, platform boundaries, and performance |
| [ansible-runbooks-and-advanced-operations.md](ansible-runbooks-and-advanced-operations.md) | Sections 14-21: operational runbook, minimal production-shaped baseline, common state patterns, vault operations, operator command cookbook, quality gates, platform and execution-environment routes, and source-to-task routing |

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
