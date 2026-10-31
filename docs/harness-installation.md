# Harness installation and maintenance

Use one installation method per harness. The Agent Skills format defines a skill package; each harness defines where to find it, how to enable it, and when changes become visible. Similar names and support for `SKILL.md` do not establish interchangeable installation procedures.

**Evidence checked: 2026-10-31.** This guide is based on upstream documentation and source inspection, not end-to-end installation tests. Paths below describe the cited upstream versions; custom homes, profiles, workspaces, containers, and remote servers can change the effective location. Install on the machine or container that performs discovery.

## Choose a method

| Method | Initial installation | Existing skill updates | Newly added catalog skills |
|--------|----------------------|------------------------|----------------------------|
| `skills` CLI | `add` with a supported agent identifier | `update` in the original scope | Rerun full-catalog `add`, or select additional skills |
| Configured checkout | Clone once and configure a supported discovery root | Pull the checkout | Available after rescan, subject to filters and enablement |
| Copied skill directories | Copy selected complete directories into a discovery root | Refresh source and replace the selected copies | Copy additional directories explicitly |
| Harness-managed library, bundle, or plugin | Use the harness's import/install flow | Use its documented update flow | Discover and enable separately unless documented otherwise |

## Harness compatibility

| Harness | Documented discovery or installation | Refresh and activation | Evidence / limitation |
|---------|--------------------------------------|------------------------|-----------------------|
| OpenClaw | Workspace `skills/`, workspace `.agents/skills/`, personal `~/.agents/skills` in default state, managed `<state-dir>/skills`, and `skills.load.extraDirs`; CLI target `openclaw` | CLI update/add, or refresh a configured checkout. Automatic rescans are supported by default; verify the effective skill after refresh. | [Discovery and precedence](https://docs.openclaw.ai/tools/skills), [CLI targets](https://github.com/vercel-labs/skills/blob/main/docs/agents.md). Configured state and sandbox copies matter. |
| Moltis | Personal `<data_dir>/skills/<name>/SKILL.md`; imported repositories under `<data_dir>/installed-skills`, filtered by manifest trust and enablement | Refresh through the installed version's repository management flow; review source changes and trust/enable again when required. Personal skill changes are watched. | [Discovery source](https://github.com/moltis-org/moltis/blob/main/crates/skills/src/discover.rs), [watcher](https://docs.moltis.org/skill-tools.html), [trust lifecycle](https://docs.moltis.org/skills-security.html). Import does not imply activation. |
| PicoClaw | Workspace `skills/`, then global `~/.picoclaw/skills`, then embedded skills; native installer accepts GitHub skill paths and ClawHub sources | Refresh copied directories from the source checkout; use `/list skills` and inspect the skill. Reload/restart according to the running version if content remains stale. | [Official guide](https://github.com/sipeed/picoclaw/blob/main/workspace/skills/picoclaw-agent/SKILL.md). A general native repository-update command is not established here. |
| NullClaw | Workspace skills, including `~/.nullclaw/workspace/skills/<name>/` and category layouts; native `skills list/install/remove/info` | Refresh copies explicitly and check `skills list` / `skills info`; confirm reload behavior for the installed version. | [Repository guide](https://github.com/nullclaw/nullclaw). Exact catalog update/reload recipe remains untested. |
| ZeroClaw | Per-agent `<install>/agents/<alias>/workspace/skills`; shared `<install>/shared/skills/<bundle>/<name>` assigned through `agents.<alias>.skill_bundles` | Refresh the assigned directory/bundle, then inspect `zeroclaw skills list --agent <alias>`. Confirm reload behavior for the installed release. | [Current skills guide](https://docs.zeroclaw.com/master/en/tools/skills.html). Global `<install>/data/skills` is not automatically loaded by agents. |
| NanoClaw | Distinguishes customization skills that apply integrations/code from runtime instruction skills | `/update-nanoclaw` owns customization/core upgrades. Runtime catalog refresh depends on the provider and container's actual discovery/mount configuration. | [Skills model](https://github.com/nanocoai/nanoclaw/blob/main/docs/skills-model.md). No universal runtime catalog-install recipe verified here. |
| IronClaw | Has undergone a runtime/storage transition; legacy paths and current profile-scoped skill roots must not be assumed equivalent | Verify the installed release's import, storage, and refresh contract before using this catalog. | [Current project](https://github.com/nearai/ironclaw), [reported path mismatch](https://github.com/nearai/ironclaw/issues/6814). Catalog installation remains unverified. |
| Grok Bot | Managed private skill library, with per-Bot enablement; team publishing provides a separate shared copy | Later published edits use Sync to update the team's copy. No Git-backed catalog refresh contract verified. | [Official skills guide](https://docs.x.ai/grok-bot/skills-routines-and-automations). The CLI's `grok` target is Grok Build, not Grok Bot. |
| Meta Muse | Public personal-agent documentation describes built-in skills and connectors | Third-party `SKILL.md` import and Git repository update behavior are not verified | [Official product documentation](https://ai.meta.com/muse/). Do not infer personal-agent support from the separate Muse Code product. |

## Managed through the skills CLI

The [README](../README.md#skills-cli-cross-harness) lists full-catalog commands. OpenClaw uses the same pattern as the other supported harnesses:

```sh
npx skills add magnus919/agent-skills --skill '*' --agent openclaw --global --yes
```

The installer targets `~/.openclaw/skills/`. With a custom state directory, confirm that this is the directory your OpenClaw instance reads. For project scope, run from the actual agent workspace and omit `--global`; the target is `skills/` there.

```sh
# Inspect availability and installed selections
npx skills list --global
npx skills check

# Refresh globally installed selections
npx skills update --global
```

Rerun the full-catalog `add` command to include newly added skills. Keep the original agent identifier and scope. The installer does not update unrelated manual copies or native plugin installations. See the [CLI command reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md) for scope and removal options.

## Local checkout or skill directory

Use a dedicated source checkout when the harness can scan an external directory, or as the source for selected copies:

```sh
git clone https://github.com/magnus919/agent-skills.git "$HOME/agent-skills"

# Later, with a clean checkout:
git -C "$HOME/agent-skills" pull --ff-only
```

If the pull reports local changes or divergent history, stop and preserve those changes before resolving them. Record the previous commit with `git -C "$HOME/agent-skills" rev-parse HEAD` before updating so you can restore a reviewed revision in a separate checkout if needed.

For OpenClaw, add the checkout root to `skills.load.extraDirs` in the existing configuration. For Hermes, use `skills.external_dirs` as shown in the [README](../README.md#hermes-agent). These settings have different names and semantics; do not copy configuration between harnesses.

For a harness that only scans fixed directories, copy each selected **complete skill directory**, including references, scripts, templates, and assets, into the documented root. Preserve personal edits separately before replacing an installed copy. Pulling the source checkout does not update those copies: repeat the selected-directory synchronization after each refresh.

Check the loader's depth before nesting the whole repository under its skills root. Moltis personal discovery scans one level deep, for example; `<root>/agent-skills/<skill>/SKILL.md` is not equivalent to `<root>/<skill>/SKILL.md`. Use configured roots, individual directories, or the native repository importer as appropriate. Do not assume symlinks or host paths will work through a sandbox; use the harness's supported mount or materialization mechanism.

## Harness-managed installation

Keep native plugins on their native update route. The README covers [Claude Code](../README.md#claude-code), [Codex](../README.md#openai-codex), and [Hermes](../README.md#hermes-agent).

For **Moltis**, use its Skills page repository import flow with `magnus919/agent-skills` or the repository URL. Review the imported selection, trust the reviewed skills, then enable them. The registry discovery code requires both trusted and enabled state. Moltis records a commit SHA; when local repository HEAD drifts from the pinned revision, its documented response is to revoke trust and disable the repository's skills. Refreshing files is therefore only part of maintenance: review the change and restore trust/enablement through Moltis. The exact update controls depend on the installed version; this guide does not prescribe an unverified update command.

For **ZeroClaw**, use the installed version's shared-bundle configuration to point a bundle at the catalog checkout and assign that bundle to the intended agent. Its documented `skill_bundles.<alias>.directory` setting supports an explicit directory; omitting it uses the default shared-bundle path. Verify the assigned inventory with `zeroclaw skills list --agent <alias>`. Updating the checkout must be followed by verifying the agent's loaded selection. Do not rely on a global installation appearing automatically.

For **NanoClaw**, establish whether the requested skill changes NanoClaw itself or supplies instructions to its runtime agent. Follow `/update-nanoclaw` for the former; confirm the provider/container discovery location before installing this catalog for the latter. The customization updater is not a catalog synchronization command.

For **Grok Bot** and **Meta Muse**, retain the unverified status in the matrix until a documented import and update contract or a bounded installation test establishes one. Reading a catalog file during a task is useful, but does not demonstrate persistent skill installation.

## Verify after installation or refresh

1. Confirm the intended agent's effective inventory includes a selected skill. Use the harness's list/info UI or commands, rather than checking only that files exist.
2. Confirm the selected source and revision, especially when workspace skills can override global, bundled, or imported copies.
3. Read the selected skill through the harness and check a distinctive updated instruction or supporting file. Start a new session or reload if required by that harness.
4. Check dependencies and available tools before exercising a representative task. Discovery alone does not prove the skill can run in that environment.
5. Review new catalog entries and upstream removals/renames separately. Do not automatically delete local or agent-authored skills while refreshing this repository.

When extending this guide, record the upstream documentation or source, verification date, applicable release/profile, discovery roots and precedence, install/update method, activation step, and a bounded verification result. Label source-inspected behavior separately from installation-tested behavior.
