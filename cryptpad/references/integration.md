# Browser integration contract

Use the official examples README as the public contract; check the exact deployed loader
when relying on newer options. Its minimum-version statement is 2024.6, while the release
history records later API additions. Do not assume every current callback or view mode is
available on that minimum release.

## Preconditions and configuration

Enable remote embedding only on an authorized instance after confirming scope and rollback.
Load its `/cryptpad-api.js` as a browser script, provide a container element, then call
`window.CryptPadAPI(containerId, config)`. The reviewed source also supports an explicit
origin argument; prefer the documented two-argument form for the scaffold.

| Field | Meaning |
|---|---|
| `document.url` | Initial file URL readable by the client, or a client-created object URL |
| `document.fileType` | File extension used for import/export conversion |
| `document.title` | Display title |
| `document.key` | Current collaborative session key, if one exists |
| `documentType` | CryptPad app: `code`, `pad`, `sheet`, `doc`, `presentation`, etc. |
| `mode` | `edit` or `view`; effective rights also depend on the key |
| `editorConfig.lang`, `editorConfig.user.name` | Language and display identity, not authentication |
| `autosave` | Inactivity delay in seconds; not a guarantee of durable writes |
| `events.onSave(blob, callback)` | Persist exported Blob, acknowledge after success |
| `events.onNewKey(data, callback)` | Coordinate generated keys; data contains `old`, `new`, `view` |
| `events.onHasUnsavedChanges(boolean)` | Present unsaved state to the user |
| `events.onUserlistChange(list)` | Presence information in versions supporting this callback |

The server-side fallback and compatibility paths in the current loader are not a reason
to send private authenticated download URLs to arbitrary instances. Prefer fetching through
your authorized application's client and supplying a Blob URL; revoke it only when no
longer needed for loading or reloading. Cross-origin source files require compatible CORS.
Office applications also require the deployed conversion/editor assets. Test each actual
input format; a filename extension does not prove support or lossless conversion.

## Persistence

The integration provides transient collaborative sessions. Persist the returned Blob in
the integrating service. Encryption on the CryptPad side does not imply encryption in that
service: for E2EE storage, encrypt in the trusted client before upload, and keep decryption
keys out of the storage server. The supplied adapter leaves this policy to its `persist` hook.

A save callback is an acknowledgement, not a request to start writing. On storage failure,
show an error and keep unsaved state; do not acknowledge success. Upstream can retry.
Use revision checks or idempotency to avoid duplicate or stale writes. Avoid claiming that
closing a tab will finish an outstanding write. Prove persistence by reopening in a fresh
session after all collaborators have disconnected.

## Generated keys: default

1. Give the editor the current stored edit key (or omit it on first use).
2. On `onNewKey`, perform an atomic compare-and-swap per document: if stored edit key equals
   `data.old`, store `data.new` and its corresponding `data.view` together.
3. Whether the update wins or loses, return the current stored edit key to the callback.
   Enforce editor authorization at this boundary. Serialize across processes, not just tabs.
4. Store and distribute the view key only to viewers. `mode: 'view'` with an edit key grants
   an editable capability despite the locked UI. Viewers do not generate new keypairs.

After all participants leave, generated session keys become deprecated. A new editor can
negotiate a new session using the stored file. Test the deployed version's behavior for a
viewer's first visit when no active session exists; do not mint an edit key for that viewer.

## Application-managed keys and revocation

Omitting `onNewKey` opts into application-managed keys. This requires secure generation,
sharing and rotation; do not use predictable document IDs, titles, or static password-derived
keys as a production shortcut. Secure view/edit pairs require CryptPad's key format.

An ACL change in your application cannot erase keys a participant already holds or content
already read. Persist the latest authorized revision, remove future key access, rotate the
session and move authorized participants to it. An old active session can remain reachable
by its old key. Define how stale-session saves will be rejected. Never promise immediate
termination or retroactive confidentiality merely because a database permission changed.

The adapter is application-owned example code. It does not implement a durable database,
authorization, client encryption or distributed transactions. Its tests establish callback
behavior only; deployment acceptance requires a real browser and storage service.
