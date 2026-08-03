# Diagnostics

Diagnose in evidence order: binary/version → config validation → backend + lock status → state serial/lineage → plan diff → apply error → boundary check. Each layer narrows the next; skipping layers produces guesswork.

## First-response diagnostic (tfops)

```bash
scripts/tfops doctor --json                 # binary, version, config files, backend hint, optional state summary
scripts/tfops plan --state state.json --json    # state-level inventory without a binary
scripts/tfops plan --json                   # real plan against the backend (needs binary + backend access)
```

`doctor` tells you whether the failure is environmental (no binary, no config) or state-related before you interpret any deeper error.

## Failure patterns

### Lock errors (`Error acquiring the state lock`)

- Find the holder through backend-specific inspection (the DynamoDB lock item, the cloud workspace run, the Consul session).
- Confirm no operation is genuinely running; only then `force-unlock <LOCK_ID>` with the ID from the error.
- Never delete the lock row blindly; never bypass locking by switching to the local backend to run a command.

### Serial/lineage mismatches (`Error: state file in path does not match the given serial` or lineage errors)

- The local/backup state and the live state diverged. Use `state pull` to see the live state, compare serials, and restore from a known-good backup after review — never overwrite a newer serial.

### `terraform init` backend errors

- Verify backend configuration, credentials/identity, and network path. `-reconfigure` re-reads the backend block; a changed backend without `-migrate-state`/`-reconfigure` is the usual trigger.

### Plan/apply errors mid-run

- Read the resource-level error, not just the summary; providers give actionable messages (API errors, quota, IAM).
- A partial apply leaves state consistent but the resource may not exist: re-plan to see what remains, then apply again.
- Timeout or "context deadline exceeded": check the provider's operation timeout and the backend/network; bounded retries beat immediate blind re-apply.

### Validate errors

- `terraform validate` diagnostics point at file/line; fix config errors before planning. Tainted resources (`tfops` reports them) are not a validate error — they are a plan/apply concern.

## Verification boundary

| Diagnosis | Minimum evidence |
|---|---|
| Binary healthy | `terraform version` / `tofu version` exit 0 |
| Config valid | `validate` exit 0 with no diagnostics |
| Backend reachable | `init` exit 0; lock acquired and released |
| State intact | `tfops state --state FILE --json` parses; serial/lineage match backend |
| Root cause fixed | The originally failing operation succeeds, then a clean re-plan |

## Sources

> **Last Updated:** 2026-08-03
- Terraform troubleshooting guide: https://developer.hashicorp.com/terraform/tutorials/configuration-language/troubleshooting-workflow (accessed 2026-08-03)
- State locking and force-unlock: https://developer.hashicorp.com/terraform/language/state/locking (accessed 2026-08-03)
- Common error messages: https://developer.hashicorp.com/terraform/internals/error-messages (accessed 2026-08-03)
- OpenTofu CLI reference (diagnostics): https://opentofu.org/docs/cli/ (accessed 2026-08-03)
