# Architecture and automation boundaries

Research snapshot: 2026-09-14. The reviewed source reports package version 2026.5.1;
that is evidence about the checkout, not the version of any deployed instance.

## How it works

CryptPad is a web collaboration suite. The browser holds plaintext and performs
cryptographic work. Encrypted collaboration messages travel through the server;
ChainPad reconciles document changes and Netflux/WebSockets supplies communication.
The History Keeper stores and serves channel history. File/blob storage and account
credential blocks are distinct from the collaborative channel log.

Normal CryptDrive use stores encrypted documents and an encrypted drive index. An
administrator's filesystem access therefore does not constitute plaintext export access.
A trusted browser with the required keys and supported application can produce exports.
Pinned storage and retention policy matter: saving a link is not a backup or a pin.

The deployment separates the main origin, which handles sensitive operations, from a
sandbox origin used by editors. Preserve this separation and the shipped CSP policy.
E2EE protects content under the intended client execution model; it does not remove trust
in delivered JavaScript, the browser, recipients, or the application that handles exports.
Share URLs may carry key material in their fragment. Fragments are not sent as HTTP
request paths, but copying a full link into logs, chat, telemetry or browser automation
traces can disclose capability material. Modern safe-link handling can differ; do not
infer ownership, key validity or access solely by parsing URL syntax.

## Interface map

| Surface | Practical use | Boundary |
|---|---|---|
| `/cryptpad-api.js`, `CryptPadAPI` | Embed editors for externally stored files | Browser callbacks; host application owns persistence and access |
| Normal web UI | Create, import, export and share CryptDrive content | Requires browser state, app support and appropriate keys/rights |
| `/api/config`, `/api/instance` | Public deployment information | JavaScript AMD modules, not generic document CRUD JSON |
| WebSocket RPC and channel protocol | CryptPad's own client/server communication | Internal, version-sensitive; channel IDs are not plaintext documents |
| `www/common/store-interface.js`, `scripts/api/testapi.js` | Source-level experiments with store API | Not evidence of a stable released external SDK; inspect dependencies and version |
| `/api/auth` | Internal challenge authentication and extensions | Not an OAuth token endpoint or universal document API |
| Server maintenance scripts | Authorized self-hosted administration | Operate ciphertext/metadata; some archive or permanently delete data |

No stable, general-purpose REST CRUD contract for accounts, drives and plaintext documents
was identified in the reviewed official sources. That is a bounded research finding, not
a claim that no plugin or future release can supply one. Check deployed extensions before
promising an integration. The OnlyOffice compatibility shim in the loader does not prove
full OnlyOffice Document Server API compatibility.

## Selecting a workflow

- External file storage plus collaborative editing: use the integration API; define its
  save and key-store contracts first.
- Existing CryptDrive document: use a browser and the application's supported export/import
  menus. Verify the format offered by that specific editor, download completion and contents.
  Reopen the export with a suitable tool; spreadsheet formulas and layout need their own checks.
- Headless bulk extraction: first establish a maintained client capable of decrypting the
  target version and app type. Otherwise report the limitation and use browser exports.
- Instance health: distinguish public HTTP reachability from sandbox, WebSocket, storage,
  permission, conversion and persistence failures.

Sources: official developer guide, architecture source, HTTP worker and API loader;
exact revisions are listed in `references/sources.md` (paths here are relative to skill root).
