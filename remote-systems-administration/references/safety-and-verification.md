# Safety and Verification

## Classify the operation

| Class | Examples | Required posture |
|---|---|---|
| Read-only | inspect units, packages, logs, sockets, config metadata | Proceed with bounded output and redaction |
| Reversible bounded change | one service reload, add one package, edit one owned config | Confirm target/scope/rollback, validate, then verify |
| Connectivity or access change | SSH, firewall, routing, DNS, sudo/PAM, VPN, network interface | Explicit directive, retained session, independent recovery path, validated rollback, staged application |
| Lifecycle change | broad updates, reboot, storage/mount changes, release upgrade | Explicit directive, maintenance/impact plan, recovery and post-change verification |
| Destructive or security-boundary change | delete data/users, reset credentials, disable protections, flush firewall state | Explicit directive after non-destructive alternatives and exact scope are documented |

## Mutation gate

Before a state-changing operation, answer all of these from evidence:

1. **What exact target is affected?** Host aliases, platform, environment, and count.
2. **What owns the setting?** Native service/package/firewall manager, configuration management, profile/MDM, or application.
3. **What is the desired outcome and blast radius?** One component, one host, canary, batch, or fleet.
4. **What could break?** Access, service availability, data, compatibility, dependencies, boot, or policy.
5. **How is rollback performed?** Exact prior state/artifact and authority to use it.
6. **How is recovery reached if the new path fails?** Retained session, console, bastion, or other authorized channel.
7. **What would prove success?** Component condition plus relevant network/application/user boundary.
8. **When do we stop?** Failure threshold, unexpected diff, loss of canary health, or any loss of admin access.

If a question is unknown, treat it as a blocker, not permission to guess.

## Connectivity-preserving changes

For firewall, SSH, routing, DNS, and privilege-path changes:

- retain the current working session until the replacement path has been tested;
- use a time-bounded rollback where the platform and change process safely support it;
- test new configuration/rules before loading when the control plane supports a parse/validation mode;
- apply one host or a canary first;
- confirm both existing administrative access and the new intended flow; and
- leave evidence sufficient for a human to recover the host.

For an initial remote firewall configuration, an authorized local console is safer than SSH when it is available. If it is not available, the independent recovery path is a hard prerequisite, not a nice-to-have.

Never “solve” an access problem by changing a password, disabling a control, accepting an unknown host key, opening a broad firewall rule, or bypassing authorization without explicit authority.

## Verification levels

| Claim | Minimum evidence |
|---|---|
| Command completed | exit status plus bounded stdout/stderr |
| Service started/reloaded | manager/process state plus relevant logs |
| Service is usable | listener/local protocol check plus dependent or external boundary |
| Configuration is active | syntax/manager validation plus observed active state |
| Package change succeeded | package database state plus expected binary/service behavior |
| Firewall change succeeded | retained administration path, intended allow/deny behavior, and application health |
| Fleet rollout succeeded | accounted per-host results, batch/canary health, and stated external boundary |
| Reboot recovered | host reachable, expected boot/runtime services healthy, and application boundary restored |

Do not promote a lower-level result to a higher-level claim. “Unit active,” “SSH connected,” and “playbook exit 0” are not equivalent to service, system, or fleet health.

## Evidence hygiene

Keep results bounded and safe to share. Record command categories and small relevant excerpts rather than entire environment files, configuration files, secret values, private keys, tokens, customer data, or unrestricted logs. If validation needs sensitive information, perform it through the authorized system and report the non-sensitive verdict.
