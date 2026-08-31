# Content API vs Admin API: Which Plane, Which Key

Ghost exposes two REST APIs with different credentials, scopes, and content visibility. Picking the wrong one produces the classic failure: everything looks configured, yet drafts are nowhere to be found and nothing errors.

## The split at a glance

| Aspect | Content API | Admin API |
| --- | --- | --- |
| Base path | `/ghost/api/content/` | `/ghost/api/admin/` |
| Credential | Content key as `?key=<RECORD_KEY>` query param | JWT in `Authorization: Ghost <token>` |
| Verbs | GET only (Browse, Read) | Full REST per resource |
| Scope | Published posts/pages/tags/authors/tiers/settings | Everything public **plus drafts, scheduled posts, members, webhooks, images, themes** |
| Key safety | Safe for browsers and clients (public data only) | Server-side only; signs mutations |
| Cacheability | Designed to be cached/CDN-fronted | Mutating; publish busts front-end caches |
| Typical consumers | Site themes, headless frontends, mobile apps | Editorial automation, migrations, scheduling bots |

Both key types come from the same Custom Integration screen; an integration has a Content API key and an Admin API key side by side. They are not interchangeable.

## Draft-visibility asymmetry (the trap)

The Content API **delivers published content only**. Its docs state the key "only ever provide[s] access to public data," and Ghost enforces this at the model layer: public-context post queries carry a non-overridable `status:published` filter.

Consequences worth internalizing:

1. **Drafts are unreachable via Content API regardless of key validity.** A valid key does not make drafts visible; the request simply never matches them.
2. **It fails silent, not loud.** Browsing with a valid Content key returns HTTP 200 with only published posts — an empty or partial list, no error, no hint. There is no 403 saying "you can't see drafts."
3. **Filtering does not bypass it.** `filter=status:draft` against the Content API returns the same published collection; the disallowed filter is ignored rather than rejected.
4. **Direct reads of non-public posts 404.** Reading `/content/posts/<draft-id>/` behaves as if the post does not exist — consistent with the documented 404 category "data which is not public."

The bundled CLI is Admin-API-first precisely because of this asymmetry: `ghost posts --status draft` works only because it authenticates with the Admin JWT, which sees drafts, scheduled, and published posts alike.

### Diagnostic checklist when "posts are missing"

- Authenticated with the **Content** key? Switch to the Admin key workflow (`GHOST_ADMIN_KEY`); drafts will appear.
- Using Admin and still missing them? Check `filter=status:` values (`draft`, `scheduled`, `published`) and page through with `--page`.
- Post visible in Admin UI but 404s from your site code? That is the same asymmetry in reverse: unpublished content never appears on the public plane.

## When to use which

Use the **Content API** for anything that renders your site to the world: headless frontend builds, static-site generators, search indexes, feeds, mobile apps. It is read-only, key-as-query-param, and cache-friendly.

Use the **Admin API** for anything that changes content or needs non-public data: creating and editing posts, publishing/scheduling, managing tags and pages, uploading images, working with drafts before they go live. Keep Admin keys out of browsers, client bundles, and CI logs.

A frequent pattern pairs both: editorial automation writes through Admin; the public site reads through Content plus CDN. If a workflow only ever reads published content, prefer Content — smaller blast radius, browser-safe key.

## Sources

- https://docs.ghost.org/content-api
- https://docs.ghost.org/content-api/#key
- https://docs.ghost.org/admin-api
- https://docs.ghost.org/admin-api/#choosing-an-authentication-method
- https://docs.ghost.org/content-api/errors
- https://github.com/TryGhost/Ghost/blob/main/ghost/core/core/server/models/post.js
