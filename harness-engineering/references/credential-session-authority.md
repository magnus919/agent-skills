# Credential handles, sessions, and action authority

Use this contract when a harness delegates authentication to a broker or browser.
It describes controls to implement at the trusted execution boundary, not a new
credential service. Compose with the security owner and the existing tool/event
contract; do not put passwords, tokens, recovery codes, or session cookies in a
model prompt, trace, screenshot, exported file, or reusable memory.

## Separate grants

| Grant | Scope to bind before use |
|---|---|
| Use an opaque credential handle | Subject/worker, account, exact canonical origin, operation, expiry, broker policy revision |
| Retain an authenticated session | Session owner, storage/isolation boundary, retention deadline, cleanup owner |
| Reuse a session | Same approved principal, account, origin, task and current grant; recheck after restart |
| Share or hand off a session | Explicit recipient and scope; possession or shared browser profile grants nothing |
| Perform a consequential action | Exact final action, resource, current state and any required approval; authentication alone is insufficient |

A handle should be opaque, audience-bound and non-exportable where the broker
supports it. It can itself be a bearer capability: redact handle values and use
non-sensitive event IDs. The broker resolves secrets outside model context and
fills only an authorized canonical HTTPS origin. Validate redirects and the final
frame origin, including cross-origin iframes and ports; never use suffix matching
or the displayed page title. An approved login does not approve payments, account
changes, publication, or access to a different account.

## Lifecycle and revocation

Record grant/session owner, purpose, creation, expiry, policy version, storage
boundary, session identifier reference, dependent sessions and cleanup outcome.
On handoff, require an explicit share grant; on restart, revalidate current grants
and reconcile existing sessions rather than assuming a recovered cookie is safe.
Do not copy a profile/cookie jar to another worker as an implicit handoff.

Revoking a handle prevents future broker use but may leave cookies, refresh
tokens, browser sessions, cached connections and in-flight actions alive. Revoke
or invalidate dependent sessions at their owning services where supported, close
local access paths, reconcile actions already started, and record residual or
unknown revocation. Fail closed for further actions until current authority is
established. Do not claim global logout from local cookie deletion. If revocation
cannot be confirmed, stop affected work and report the residual exposure and owner.

## Synthetic challenge protocol

Exercise secret leakage into each of model output, logs, and files; wrong origin
and cross-origin frame fills; undeclared retain/reuse/share; cross-worker cookie
reuse; expiry; and handle revocation with a residual session still authenticated.
Use invented canaries only. Check observed sink bytes and actual action receipts,
not a model's statement that it kept secrets safe. Test denial before the action
and suppression/redaction at the boundary, with an actionable non-secret reason.

`evals/fixtures/authority-memory.json` and
`scripts/test_authority_memory_examples.py` exercise a small offline teaching
model of these decisions. Run `python3 -m unittest discover -s scripts -p
'test_authority_memory_examples.py'` from this skill root. These fixtures do not
implement a broker, detect arbitrary secrets, inspect real browser origins, or
establish real service revocation. Test the actual adapter separately before
making those claims; avoid live credentials during these challenges.
