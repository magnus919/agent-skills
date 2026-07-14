# Remote Systems Administration

Operate remote Linux, FreeBSD, NetBSD, OpenBSD, and macOS hosts safely, without pretending their service managers, packages, firewalls, and configuration systems are interchangeable.

## Why Install This Skill

Remote administration is where a plausible command can turn into an outage. This skill gives an agent a disciplined path from host discovery through scoped change and verification. It starts with native SSH for a single bounded job, moves to Ansible for repeatable fleet work, and reserves Paramiko for Python programs that actually need protocol-level control.

It is deliberately platform-aware. The agent learns to find the active control plane before touching a service, package, firewall, or configuration file, and to preserve a rollback path before changing anything that could strand remote access.

## What You Get

| Resource | What it provides |
|---|---|
| `SKILL.md` | Operating contract, routing, boundaries, and verification checklist |
| `references/portable-operations.md` | POSIX baseline, SSH, discovery, diagnostics, and bounded evidence |
| `references/ansible.md` | Deep Ansible administration: inventory, roles, collections, secrets, testing, execution, troubleshooting, and safe fleet rollout |
| `references/fleet-automation.md` | Paramiko guidance plus fleet-control comparison and per-host result requirements |
| `references/linux.md` | Linux distribution/control-plane classification and cross-family routing |
| `references/linux-debian-ubuntu.md` | APT/dpkg, Ubuntu lifecycle, and network ownership boundaries |
| `references/linux-rhel-fedora.md` | DNF/RPM, supported major upgrades, and firewalld ownership |
| `references/linux-suse.md` | zypper/RPM and transactional-root distinctions |
| `references/linux-arch.md` | pacman full-upgrade and recovery boundaries |
| `references/linux-alpine.md` | apk, OpenRC, and diskless persistence boundaries |
| `references/freebsd.md` | FreeBSD rc, packages, jails, and firewall routing |
| `references/netbsd.md` | NetBSD rc.d, services, pkgsrc, and firewall routing |
| `references/openbsd.md` | OpenBSD rcctl, updates, packages, and PF routing |
| `references/macos.md` | launchd, updates, profiles, and macOS operational limits |
| `references/safety-and-verification.md` | Mutation gates, rollback, and verification evidence |
| `references/source-index.md` | Primary sources and freshness notes |
| `templates/remote-change-plan.md` | A compact plan for a remote change before it starts |

## Quick Start

Start with a read-only preflight. Replace the example target with a host you are authorized to inspect.

```sh
ssh -o BatchMode=yes -o ConnectTimeout=10 admin@example-host '
  printf "host="; hostname; uname -srm; id
  [ -r /etc/os-release ] && while IFS= read -r line; do
    case $line in ID=*|ID_LIKE=*|VERSION_ID=*) printf "%s\n" "$line";; esac
  done < /etc/os-release
  ps -p 1 -o pid= -o comm= 2>/dev/null || true
  for tool in systemctl service rcctl launchctl apt-cache dnf yum zypper pacman apk pkg pkg_add softwareupdate nmcli networkctl firewall-cmd nft pfctl ipfw npfctl; do
    command -v "$tool" 2>/dev/null || true
  done
  command -v sw_vers >/dev/null 2>&1 && sw_vers
'
```

Then load the matching OS/family reference and run its command preflight before choosing a service manager, package tool, or firewall control plane. Only then, and after the safety gate, select a specific mutation command. For fleet work, put targets in an Ansible inventory, run a canary with `--limit`, and use `--check --diff` only with its limitations understood.

## Triggers

Use this skill when you need to:

- diagnose or administer a remote Linux (including Debian/Ubuntu, RHEL/Fedora, SUSE, Arch, or Alpine), FreeBSD, NetBSD, OpenBSD, or macOS host;
- manage services, packages, updates, configuration, logs, or firewalls;
- use SSH, a bastion, file transfer, Ansible, or Paramiko;
- make a controlled change across several Unix-like machines;
- plan rollback and verification for a remote operational change.

## Requirements

You need legitimate remote access and the authority to perform the requested operation. Native SSH is the baseline. Ansible is optional for fleet configuration, and Python plus Paramiko is optional for programmatic SSH workflows. The skill does not create credentials, bypass host-key validation, or authorize destructive operations.
