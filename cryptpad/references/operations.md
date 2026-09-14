# Instance operations and diagnostics

## Read-only first

Record the main/sandbox origins and deployed release (administrator or deployment evidence).
Run `scripts/cryptpad.py probe --origin https://your-instance.example`. A recognized loader
and config prove only resource availability. A 200 HTML login/404 page is not a usable API;
redirects are deliberately refused. Choose the canonical origin explicitly.

Inspect the official `/checkup/` page only after reading its test scope: some diagnostics
create/retrieve/remove test data, so running the suite belongs inside an authorized test scope.
Do not describe the entire checkup suite as read-only.

| Observation | Next evidence |
|---|---|
| HTTP works, editor blank | Browser console, sandbox TLS/DNS, CSP and actual embedding policy |
| Editor loads, edits fail to sync | WebSocket upgrade/proxy path, disconnects and server logs |
| Source file fails to load | Authorized browser fetch, CORS, expired URL, file type and conversion assets |
| Session forks | Atomic old-key comparison and callback's winning stored key |
| Reopened document is stale | Durable save acknowledgement, revision conflict and stale-session writes |
| Viewer can edit | Check key supplied, not only `mode`; inspect app-side authorization |
| Config parser rejects response | Version/proxy mismatch; inspect response privately, never execute downloaded JS |

Redact capability links, tokens, document contents and session keys before collecting evidence.
Do not publish raw browser traces until reviewed for those values.

## Deployment and recovery

Use the release-matched official installation guide and configuration examples. Confirm the
chosen release rather than copying a possibly stale version from a documentation example.
Production needs the intended main/sandbox separation, TLS, correct reverse proxy headers,
WebSocket forwarding and persistent storage. Node's supported version, OnlyOffice assets,
Docker image tags and upgrade steps are version-specific. Do not replace shipped CSP with
wildcards to make an embed work. Discover permitted-embedder behavior for that deployment.

Before deployment changes, record a tested backup/restore path covering configuration,
customizations and all configured data directories, including channel data, blobs, blocks,
pins and archive state as applicable. Backups of encrypted server data do not recover lost
client keys. Test a restore plus client reopening, not only that an archive exists.

Inventory the configured retention and ownership/pinning rules before discussing recovery.
Never run `evict-inactive.js`, `evict-archived.js`, `clear.js`, migrations or restore scripts
as a generic health check. Read the target release's source, establish the exact target and
rollback, and require explicit direction for destructive actions. Office format upgrades
may be non-reversible; read every intervening release note before upgrading.

For existing-document exports: record the app's available export formats, use an authorized
session, verify the downloaded file, and keep export destination access consistent with the
plaintext it now contains. Browser access does not authorize creating new public share links.
