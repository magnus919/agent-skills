# Source Index

This skill is a routing and safety guide, not a frozen command reference. Re-check current primary documentation before asserting version-specific behavior, package availability, service defaults, or upgrade paths.

| Area | Primary source | What it grounds | Checked |
|---|---|---|---|
| OpenSSH client/configuration | [OpenBSD ssh(1)](https://man.openbsd.org/ssh.1), [ssh_config(5)](https://man.openbsd.org/ssh_config.5) | Host-key behavior, `ProxyJump`, connection multiplexing | 2026-07-13 |
| Ansible playbooks | [Check and diff mode](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html), [execution strategies](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_strategies.html) | Simulation limits, diff sensitivity, serial rollout | 2026-07-13 |
| Ansible modules | [package](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/package_module.html), [template](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/template_module.html), [copy](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/copy_module.html), [file](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/file_module.html), [lineinfile](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/lineinfile_module.html), [command](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/command_module.html), [systemd_service](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/systemd_service_module.html), [reboot](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/reboot_module.html) | Generic-module limits, package-name variance, safe config replacement, narrow unmanaged-file editing, command idempotence, systemd scope, and reconnect behavior | 2026-07-13 |
| Ansible administration | [Ansible CLI](https://docs.ansible.com/projects/ansible/latest/command_guide/index.html), [inventory CLI](https://docs.ansible.com/projects/ansible/latest/cli/ansible-inventory.html), [Vault](https://docs.ansible.com/projects/ansible/latest/vault_guide/index.html), [delegation](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_delegation.html), and `references/ansible.md` | Installation, effective configuration, inventory inspection, content patterns, vault lifecycle, delegated rollout, platform boundaries, troubleshooting, and lifecycle routing | 2026-07-13 |
| Ansible quality gates | [ansible-lint configuration](https://ansible.readthedocs.io/projects/lint/configuring/), [Molecule workflow](https://ansible.readthedocs.io/projects/molecule/workflow/), and [Molecule CI](https://ansible.readthedocs.io/projects/molecule/ci/) | Lint policy/exceptions, CI behavior, scenario lifecycle, idempotence, and outcome verification | 2026-07-13 |
| Paramiko | [Paramiko documentation](https://docs.paramiko.org/en/stable/) and [SSHClient API](https://docs.paramiko.org/en/stable/api/client.html) | Client, host-key, channel, and SFTP responsibilities | 2026-07-13 |
| systemd | [systemctl manual](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) | Unit lifecycle and state inspection | 2026-07-13 |
| Linux firewall | [nftables wiki](https://wiki.nftables.org/wiki-nftables/index.php/Main_Page) | nftables architecture and CLI concepts | 2026-07-13 |
| Arch packages | [pacman(8)](https://man.archlinux.org/man/pacman.8) | package database, transaction, cache, and dependency controls | 2026-07-13 |
| Alpine packages | [Alpine Package Keeper](https://wiki.alpinelinux.org/wiki/Alpine_Package_Keeper) | configuration conflict files, persistence modes, and package state | 2026-07-13 |
| FreeBSD configuration | [FreeBSD Handbook: configuration](https://docs.freebsd.org/en/books/handbook/config/) | rc framework and base-system configuration conventions | 2026-07-13 |
| FreeBSD packages and ports | [FreeBSD Handbook: ports and packages](https://docs.freebsd.org/en/books/handbook/ports/) | package/ports lifecycle and package-management boundaries | 2026-07-13 |
| FreeBSD boot environments | [bectl(8)](https://man.freebsd.org/cgi/man.cgi?query=bectl&sektion=8) | ZFS boot-environment discovery, activation, and recovery boundaries | 2026-07-13 |
| FreeBSD firewalls | [FreeBSD Handbook: firewalls](https://docs.freebsd.org/en/books/handbook/firewalls/) | PF/IPFW distinctions and remote-firewall recovery caution | 2026-07-13 |
| NetBSD services | [NetBSD rc.d guide](https://www.netbsd.org/docs/guide/en/chap-rc.html) | rc.d configuration, package-script activation, service lifecycle, and `service` alias | 2026-07-13 |
| NetBSD packages | [pkgsrc guide](https://www.netbsd.org/docs/pkgsrc/using.html), [pkg_add(1)](https://man.netbsd.org/pkg_add.1) | pkgsrc package origins, binary packages, and pkg tools | 2026-07-13 |
| NetBSD firewall | [NetBSD networking guide](https://www.netbsd.org/docs/guide/en/chap-net-practice.html) | NPF ownership and separate firewall control plane | 2026-07-13 |
| OpenBSD services | [rcctl(8)](https://man.openbsd.org/rcctl) | daemon configuration, enablement, and actions | 2026-07-13 |
| OpenBSD packages | [pkg_add(1)](https://man.openbsd.org/pkg_add) | package install/update, signatures, package/base distinction | 2026-07-13 |
| OpenBSD base patches | [syspatch(8)](https://man.openbsd.org/syspatch) | official-release binary patch lifecycle and rollback behavior | 2026-07-13 |
| OpenBSD PF | [pfctl(8)](https://man.openbsd.org/pfctl), [pf.conf(5)](https://man.openbsd.org/pf.conf) | rule validation/loading and PF control scope | 2026-07-13 |
| Apple launchd | [Creating Launch Daemons and Agents](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html) | daemon/agent distinction, labels, and launchd ownership model | 2026-07-13 |
| Apple networking | target-host `networksetup(8)` manual (version-specific) | network-service configuration controls | 2026-07-13 |
| Apple firewall | [Block connections to your Mac with a firewall](https://support.apple.com/guide/mac-help/change-firewall-settings-mh34041/mac) | application/service firewall behavior | 2026-07-13 |
| Apple deployment | [Apple Platform Deployment](https://support.apple.com/guide/deployment/welcome/web) | Apple-supported management and deployment posture | 2026-07-13 |
| Homebrew | [Homebrew manpage](https://docs.brew.sh/Manpage) | package-manager behavior and environment controls | 2026-07-13 |

## Research observations

- Ansible documents `--check` as a simulation with module support gaps and notes that `--diff` can expose sensitive information; the skill therefore treats both as previews, not proof.
- `references/ansible.md` is the deep operational reference for Ansible. It was grounded in current Ansible Community, ansible-lint, and Molecule documentation; re-check it against the project runtime before asserting version-specific behavior.
- Paramiko documents that clients are responsible for authentication and checking server host keys; the skill therefore forbids automatic acceptance of unknown keys.
- OpenBSD documents `rcctl` actions and `pkg_add`'s signed-package behavior; the skill keeps OpenBSD service and package guidance separate from Linux and FreeBSD.
- The FreeBSD Handbook distinguishes prebuilt packages from ports; the skill does not present them as a single update mechanism.

## Refresh rules

Refresh this index before adding exact release support windows, package versions, security advisories, default firewall behavior, command flags that vary by release, or OS upgrade procedures. If a primary site is unavailable to a crawler, use the maintained canonical URL and state the retrieval limitation rather than replacing it with a plausible paraphrase.
