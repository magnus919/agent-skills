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
| `references/linux.md` | Linux init, packages, logs, and firewall routing |
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
ssh admin@example-host 'uname -srm; command -v systemctl service rcctl launchctl; id'
```

Then load the matching platform reference before choosing a service manager, package tool, or firewall control plane. For fleet work, put targets in an Ansible inventory, run a canary with `--limit`, and use `--check --diff` only with its limitations understood.

## Triggers

Use this skill when you need to:

- diagnose or administer a remote Linux, FreeBSD, OpenBSD, or macOS host;
- manage services, packages, updates, configuration, logs, or firewalls;
- use SSH, a bastion, file transfer, Ansible, or Paramiko;
- make a controlled change across several Unix-like machines;
- plan rollback and verification for a remote operational change.

## Requirements

You need legitimate remote access and the authority to perform the requested operation. Native SSH is the baseline. Ansible is optional for fleet configuration, and Python plus Paramiko is optional for programmatic SSH workflows. The skill does not create credentials, bypass host-key validation, or authorize destructive operations.
