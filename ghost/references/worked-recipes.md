# Worked Recipes: CLI and Raw API

Recipes combining the bundled `scripts/ghost` CLI with raw Admin API calls. Every recipe is executable end-to-end with only `GHOST_URL` and `GHOST_ADMIN_KEY` set (and `jq` for JSON plumbing). HTML/Lexical examples use placeholder tokens, never real credentials.

## Recipe 1: Draft a post now, publish after review

Draft-first keeps half-written work off the public site while still letting you preview with admin themes.

```bash
# 1. Create the draft
ghost --json create-post --title "Release notes" \
  --html "<p>What shipped this week…</p>" > /tmp/draft.json

post_id=$(jq -r '.post.id' /tmp/draft.json)

# 2. Later: re-read to fetch the CURRENT updated_at (collision guard)
ghost get-post "$post_id" | grep updated_at

# 3. Publish, passing the fresh timestamp
ghost update-post "$post_id" \
  --status published \
  --updated-at "$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"   # NO — use the value from step 2
```

The last line above is deliberately wrong: never synthesize `updated_at`. Copy the exact string from step 2's output; the server compares timestamps literally, and a mismatch means 409.

Raw-API equivalent of step 3:

```bash
curl -sS -X PUT "$BASE/posts/$POST_ID/" \
  -H "Authorization: Ghost $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept-Version: v6.0" \
  --data "{\"posts\":[{\"updated_at\":\"$UPDATED_AT\",\"status\":\"published\"}]}"
```

## Recipe 2: Review queue — everything unpublished

Drafts, scheduled, and published live on different filters; one call per status:

```bash
ghost posts --status draft     --limit 50 --json | jq -r '.posts[] | "\(.title)\t\(.slug)"'
ghost posts --status scheduled --json | jq -r '.posts[] | "\(.title)\t(.published_at // "-")"'
```

Pair it with an authoring-wide sanity check via jq types before feeding slugs onward:

```bash
ghost posts --status draft --json | jq '{count: (.posts|length), all_slugs_strings: ([.posts[].slug | type] | all(. == "string"))}'
```

## Recipe 3: Full export, page by page

Ghost 6 caps pages at 100 rows; `limit=all` is gone.

```bash
page=1
while :; do
  ghost posts --limit 100 --page "$page" --json > "/tmp/posts-$page.json"
  next=$(jq -r '.page.next // empty' "/tmp/posts-$page.json")
  jq -r '.posts[].id' "/tmp/posts-$page.json"
  [ -z "$next" ] && break
  page=$next
  sleep 0.2
done
```

Note the loop reads `meta.pagination.next` from the CLI's `.page` field rather than computing `(page * limit) < total`; totals shift under concurrent edits.

## Recipe 4: Publish at a future time (scheduling)

```bash
ghost create-post --title "Launch day" \
  --html "<p>We're live.</p>" \
  --status scheduled \
  --published-at "2026-09-01T09:00:00.000Z"
```

Requirements: the timestamp must be in the future and ISO 8601; Ghost processes the queue on its own schedule (typically within five minutes of the mark). The post remains visible as `scheduled` in the Admin plane, invisible publicly until flip time. CLI enforces the pairing (`--status scheduled` without `--published-at` errors before any request is made).

## Recipe 5: Slug-based handoff between systems

External systems key content by slug. Resolve slug → id → full record:

```bash
curl -sS "$BASE/posts/slug/$SLUG/" \
  -H "Authorization: Ghost $TOKEN" \
  -H "Accept-Version: v6.0" | jq -r '.posts[0].id'
```

Then read or edit by that id. The CLI reads by id (`ghost get-post <id>`); for slug lookups use the curl form above.

## Recipe 6: Tag hygiene pass

Find tags nobody uses, then create missing ones for a new series:

```bash
# Usage-counted listing
ghost tags --limit 200 --json | jq -r '.tags[] | select((.count.posts // 0) == 0) | .slug'

# Create two series tags (idempotency: check existence first, creation duplicates error out)
ghost create-tag --name "Engineering" --slug engineering --description "Technical posts"
```

Remember relation semantics when tagging posts programmatically: PUT replaces the tag array wholesale, so send `[...existing_slugs, "engineering"]`, not just the addition.

## Recipe 7: Connectivity triage

When nothing works, descend this ladder:

```bash
# 1. Is Ghost up? (no auth required)
curl -sS "$GHOST_URL/ghost/api/admin/site/" | jq .

# 2. Does our JWT authenticate?
ghost site

# 3. Can we browse? (exercises query params + permissions)
ghost posts --limit 1
```

Step 1 failing = wrong URL/site down. Step 2 failing = auth contract problem (see the auth reference's signature table: expired vs invalid-algorithm vs audience). Step 3 failing while step 2 passes usually means integration permission gaps rather than token problems.

## Sources

- https://docs.ghost.org/admin-api/#token-generation-examples
- https://docs.ghost.org/admin-api/posts/creating-a-post
- https://docs.ghost.org/admin-api/posts/updating-a-post
- https://docs.ghost.org/admin-api/posts/publishing-a-post
- https://docs.ghost.org/admin-api/posts/scheduling-a-post
- https://docs.ghost.org/content-api/pagination
- https://docs.ghost.org/changes
