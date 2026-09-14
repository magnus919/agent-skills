# Browser integration scaffold

Application code, not a drop-in service. Supply real authorized storage and key-store hooks.
Start with `code` plus a known UTF-8 text file before testing Office conversions.

```html
<div id="editor" style="height: 80vh"></div>
<script src="https://cryptpad.example.org/cryptpad-api.js"></script>
```

In your application's browser module, after the loader has loaded:

```javascript
import {createEvents} from './integration-adapter.mjs';

// These are your application's functions, not CryptPad API methods:
// loadAuthorizedBlob(), readAuthorizedEditKey(), persistRevision(blob),
// compareAndSwapAuthorizedKeyPair(data), showError(code), showUnsaved(boolean).
const blob = await loadAuthorizedBlob();
const url = URL.createObjectURL(blob);
const events = createEvents({
  persist: persistRevision,
  compareAndSwapKeys: compareAndSwapAuthorizedKeyPair,
  report: showError,
  setUnsaved: showUnsaved
});
const config = {
  document: {url, fileType: 'txt', title: 'Working notes',
             key: await readAuthorizedEditKey()},
  documentType: 'code',
  mode: 'edit',
  editorConfig: {lang: 'en', user: {name: 'Collaborator'}},
  autosave: 10,
  events
};
window.CryptPadAPI('editor', config);
// Retain the Blob URL for the editor's loading/reloading lifecycle.
// Revoke it on final teardown after the editor no longer needs it.
```

Do not put keys in source code, log them, or use the user's display name as authentication.
For view-only use, fetch the authorized **view key**, set `mode: 'view'`, and omit `onNewKey`;
never make an edit-key-returning endpoint available to viewers. Adapt save hooks to preserve
client-side encryption if your storage threat model requires it. Show failed key/save operations
in the containing UI, and test the exact instance's startup/error behavior.
