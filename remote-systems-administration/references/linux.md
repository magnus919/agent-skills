# Linux Classification and Routing

“Linux” is a kernel family, not an operating model. Before a mutation, discover the distribution/release, init system, package manager, configuration owner, firewall implementation, and management layer. `/etc/os-release`, `ps -p 1`, and executable presence are observations, not authority to overwrite managed state.

## Classify before selecting a control plane

| Observed evidence | Route | Do not infer |
|---|---|---|
| `ID=debian` or `ubuntu`, or a Debian-derived system with `ID_LIKE=debian`; APT/dpkg | `linux-debian-ubuntu.md` | Ubuntu network ownership or release-upgrade procedure from APT/dpkg alone |
| `ID=rhel`, `fedora`, or compatible `ID_LIKE`; Yum/DNF/RPM | `linux-rhel-fedora.md` | Vendor support, DNF module semantics on a yum-only target, or a RHEL major-upgrade path for every derivative |
| `ID=sles`, `opensuse*`, or `ID_LIKE=suse`; zypper/RPM | `linux-suse.md` | That the root is transactional or read-only |
| `ID=arch` or Arch-derived; pacman | `linux-arch.md` | Repository/support policy or a safe partial upgrade |
| `ID=alpine`; apk/OpenRC | `linux-alpine.md` | That package/configuration changes persist across boot |
| Missing, contradictory, minimal, or unsupported derivative | retain this reference and vendor docs | Family, lifecycle, firewall owner, or mutation path |

Record `ID`, `ID_LIKE`, `VERSION_ID`, init PID, package manager, enabled repositories, firewall process/configuration, and file owner or configuration manager. Package transaction semantics, firewall ownership, release lifecycle, and reboot/rollback procedure follow that classification.

**Unsupported-derivative stop rule:** If `ID`/`ID_LIKE` does not identify a documented family, or the vendor changes its package, init, transactional-root, or network model, stop after read-only discovery. Obtain the vendor procedure and explicit authorization before a mutation.

**Derivative lifecycle stop rule:** `ID_LIKE` is a routing clue, not proof that every derivative follows Debian or Ubuntu release or lifecycle procedures. For a Debian-derived target, use the documented vendor procedure only after confirming it applies to the observed distribution and releases.

## Read-only family command routing

`ID` and `ID_LIKE` route this inspection only; they do not authorize a derivative's release procedure. Run the matching overlay preflight next.

| Observed family | Next overlay | Family-native read-only evidence |
|---|---|---|
| Debian/Ubuntu | `linux-debian-ubuntu.md` | `apt-cache policy <package>`; `apt-mark showhold`; `dpkg-query -W -f='${Status} ${Version}\n' <package>` |
| RHEL/Fedora | `linux-rhel-fedora.md` | DNF target: `dnf repolist`; `dnf history list`; `dnf module list --enabled`. Yum-only target: `yum repolist`; `yum history`; `yum info <package>` |
| SUSE/openSUSE | `linux-suse.md` | `zypper repos`; `zypper locks`; `zypper --no-refresh patches` |
| Arch | `linux-arch.md` | `pacman -Q <package>`; `pacman -Qu`; `pacman -Qdt` |
| Alpine | `linux-alpine.md` | `apk policy <package>`; `apk info -vv`; `cat /etc/apk/world` |

## Services and logs

Most contemporary distributions use systemd, but do not assume it. When systemd is active, use `systemctl` for unit state and `journalctl` for bounded journal evidence. A unit becoming `active` is only component-level evidence; verify the listener, dependent service, and external boundary separately.

Other Linux systems may use OpenRC, SysV-style scripts, runit, s6, or a distribution-specific control interface. Discover the active manager and load its authoritative documentation before lifecycle or boot-persistence changes.

| Question | systemd-oriented evidence |
|---|---|
| What is running? | `systemctl status <unit>` and a bounded `journalctl -u <unit>` range |
| Will it start at boot? | `systemctl is-enabled <unit>` |
| Did configuration parse? | service-specific validation before `reload` or `restart` |
| Did it serve traffic? | endpoint/socket check plus relevant client/dependent check |

Do not blindly restart a service because configuration changed. Validate the configuration first where the service provides a check, then use reload only when documented as safe; otherwise plan the restart, effect, and rollback. If a systemd unit file or drop-in changed, run `systemctl daemon-reload` before the lifecycle action so the manager rereads unit metadata.

## Packages and updates

Discover the native package manager. Common families include APT/dpkg, DNF/RPM, zypper/RPM, pacman, and apk. Package-manager commands, repository configuration, update semantics, and reboot requirements are distribution-specific.

Before upgrades:

1. classify the change: one package, security updates, all packages, kernel, distribution release, or third-party repository change;
2. inspect candidates/transaction plan and held/excluded packages;
3. identify service restart and reboot implications;
4. preserve rollback or recovery strategy appropriate to the package system, filesystem, and workload; and
5. stage or canary before a fleet rollout.

Do not claim that a package update is rollback-safe merely because the manager supports downgrade. Availability, dependency graphs, database migrations, and configuration changes determine actual reversibility.

## Cross-family failure signatures

| Signature | Likely boundary | Safe response |
|---|---|---|
| Package database lock or concurrent transaction | timer/automation or another operator | identify holder; do not delete a lock or start a competing transaction |
| Package manager succeeds but config does not take effect | conffile, generated configuration, or manager ownership | inspect conflict/generated files and active configuration |
| Firewall command exists but policy reverts | firewalld, nftables, cloud-init, or configuration management owns it | discover owner; do not layer a second control plane |
| Host returns after reboot but service is unavailable | kernel/base update, unit enablement, or dependency | verify boot, logs, listener, and external boundary |
| Update appears successful but reverts after boot | transactional or diskless root | classify persistence/snapshot mode before retrying |

Package manager discovery is not enough to choose a safe transaction. It must be paired with the distribution release, enabled repositories, package origin, held/excluded policy, and configuration-file behavior. A package transaction can leave a generated or conflict copy of an edited configuration rather than silently replacing it. Inspect and resolve that state deliberately before declaring a configuration change active.

- APT/dpkg, DNF/RPM, zypper/RPM, pacman, and apk have separate repository, solver, cache, and configuration semantics.
- Pacman tracks local package metadata and uses a separate sync operation for repository packages. Its removal and database bypass controls can have broad effects; do not turn off dependency/conflict checks to make a transaction proceed.
- Alpine `apk` can preserve proposed configuration as `.apk-new`; diskless/data-disk installations also require an explicit persistence step. Detect that deployment mode before treating a successful package command as durable across boot.
- A package manager's package name is not portable. `ansible.builtin.package` does not translate it between distributions.

## System configuration

Configuration files may be vendor-managed, package-conffiles, generated by cloud-init, NetworkManager, systemd-networkd, a configuration-management tool, or an application. Discover ownership before editing. Back up or version the existing state, make a minimal change, validate syntax, reload/restart only as required, and verify the active configuration rather than the file alone.

Changes to network configuration, DNS, SSH, sudo, PAM, routing, firewall state, mounts, kernel parameters, users, or storage are high-risk. Load `safety-and-verification.md` first and preserve access.

## Firewall routing

Linux firewall control planes include nftables and systems layered above it, such as firewalld or distribution tooling. Discover which system owns rules before changing anything. Do not mix direct nftables edits with a higher-level manager unless its documentation permits it, and never mechanically translate PF, iptables, or cloud firewall rules.

| Evidence | Decision |
|---|---|
| A firewall binary exists or `firewalld` is active | Ownership is still unknown. Inspect the managed configuration and sanctioned control path; do not select a tool from presence or service state alone, and do not use a trial rule or any other mutation to decide ownership. |
| firewalld is the confirmed policy owner | Use its documented interface; do not add direct nftables rules beside it. |
| Native nftables configuration is the confirmed policy owner | Use nftables only through that configuration's documented management path. |

For nftables, inspect the existing ruleset and ownership before edits. Policy changes can sever the live SSH session. Validate rule syntax where available, retain a recovery path, apply a bounded change, and verify both expected traffic and retained administrative access.

## Reboot and lifecycle

A reboot is a state transition with dependencies. Identify the reason, pending work, required services, users, maintenance window, recovery access, and post-boot validation before issuing it. Verify boot completion, expected units, networking, time synchronization where relevant, and the affected application boundary. A reachable SSH daemon alone is not complete recovery.
