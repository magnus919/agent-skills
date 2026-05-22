# Advanced Patterns

Edge case patterns that don't apply to every CLI but are essential when they do.

## Morphological Matching for Text-Based Filters

When a CLI provides `--category`, `--type`, or similar text matching against section headers, **exact substring matching fails on morphological variants**:

| User passes | Header reads | Substring match? |
|---|---|---|
| `warehouse` | DATA WAREHOUSING | ❌ "warehouse" ≠ substring of "warehousing" |
| `model` | DATA MODELING | ❌ "model" ≠ substring of "modeling" |
| `format` | STORAGE FORMATS | ❌ "format" ≠ substring of "formats" |

**Fix: Match on a shared word stem.** Take the first N characters of the user's filter term and check if that stem appears in the lowercased header:

```python
def _header_matches(header: str, category: str, stem_len: int = 5) -> bool:
    """Check if a category filter matches a section header on shared stem."""
    cat_lower = category.lower()
    header_lower = header.lower()
    # Exact match first (fast path)
    if cat_lower in header_lower:
        return True
    # Stem match (handles morphological variants)
    stem = cat_lower[:min(len(cat_lower), stem_len)]
    return len(stem) >= 3 and stem in header_lower
```

**When to use:** Any CLI with `--category`, `--type`, or free-text filtering against known labels where the headers may use different morphological forms.

## Version-Dependent Imports After Dry-Run

When a CLI handler wraps an optional library module, imports must respect the dry-run first check:

```python
async def cmd_foo(**kw):
    url = kw["url"]
    # ... parse ALL params BEFORE any imports ...

    if DRY_RUN:
        emit("[dry-run] Would foo", {"dry_run": True, "url": url})
        return

    # Lazy imports — after dry-run, so --dry-run works without the module
    from some_library.optional import CoolFeature
    try:
        from some_library.newer_module import NewThing
    except ImportError:
        NewThing = None  # graceful fallback for older versions

    # ... rest of handler using CoolFeature / NewThing ...
```

**The failure mode:** If the import is at the top of the handler, `--dry-run` crashes with `ModuleNotFoundError` even though it should be safe.

**Detection:** Syntax checks don't catch this. Run `--dry-run` against the actual target environment.

## Robust JSON Consumption from Subprocesses

When consuming JSON from a CLI tool you don't control, filter stdout lines before parsing:

```python
def _parse_json_output(result: subprocess.CompletedProcess) -> list | dict:
    """Parse subprocess stdout as JSON, filtering out non-JSON noise."""
    json_lines = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith(("[", "{")):
            json_lines.append(stripped)
    if not json_lines:
        return []
    return json.loads("\n".join(json_lines))
```

This acts as a "JSON line filter" — anything that doesn't start with `[` or `{` is discarded. Safe because:
- JSON arrays always start with `[`
- JSON objects always start with `{`
- Warning/status messages rarely start with either character

**When to use:** Consuming JSON from tools you didn't build, or tools with environment-specific logging you can't suppress.

## Dry-Run Short-Circuit for Chained-API Commands

The basic dry-run pattern breaks down when a command handler chains multiple API calls where the first call provides context for subsequent calls. Example:

```python
def cmd_current(client, args):
    # First call: fetch station list to get device IDs
    stations = client.get_stations()  # Fails in dry-run — returns []
    # Second call: fetch observations for that device
    obs = client.get_observations(stations[0]["id"])
```

In dry-run mode, the first call returns an empty list. The handler errors: "No stations found." The dry-run never reaches the preview logic.

**Fix: Add a command-level dry-run short-circuit BEFORE any data-fetching calls.**

```python
def cmd_current(client, args):
    # Short-circuit at command level, above all data-fetching
    if client.dry_run:
        emit("[dry-run] Would query latest station observations.",
             {"dry_run": True, "command": "current"})
        return

    # All real logic follows — stations lookup, observations fetch
    stations = client.get_stations()
    obs = client.get_observations(stations[0]["id"])
    # ... format and emit output ...
```

**Pattern rules:**
1. The short-circuit must emit a meaningful preview of what the command would do
2. It must include all parameters the command received (IDs, flags, etc.)
3. It must return — not fall through — so the chained API calls never execute
4. Every command that chains API calls needs its own short-circuit

**Detection:** If a command emits a fatal error (not a dry-run preview) when run with `--dry-run`, it has this problem.

## Container-Key Wrapper Ambiguity

When a CLI wraps an API that expects the POST body wrapped in a container key (e.g., `{"dashboard": {...}, "overwrite": true}`), there's ambiguity about what `--file` should contain: the inner resource only, or the full POST body.

**Rule:** Accept the inner resource body only. Add the wrapper yourself in the handler.

```python
def cmd_create(json_file):
    with open(json_file) as f:
        data = json.load(f)  # expected: {...}, not {"resource": {...}}
    body = {"resource": data, "overwrite": True}
    client._request("POST", "/api/resources", json_data=body)
```

Document this explicitly in `--file` help text: "Path to a JSON file containing just the resource body — the CLI adds the API envelope."

## Library Init Banners in Stdout

Some libraries (Crawl4AI, Playwright) print init banners to stdout via bare `print()`, not logging. These appear before any of your code runs and contaminate `--json` output.

**Preferred fix: route ALL human output to stderr, redirect stdout globally in `main()`.**

```python
import sys
_REAL_STDOUT = None

def emit(human: str, machine: dict) -> None:
    if JSON_OUTPUT:
        print(json.dumps(machine), file=_REAL_STDOUT)
    else:
        print(human, file=sys.stderr)

def main():
    global _REAL_STDOUT
    # ... parse args, detect JSON mode ...

    if JSON_OUTPUT:
        _REAL_STDOUT = sys.stdout
        sys.stdout = sys.stderr  # Library noise → stderr
    # ... dispatch handlers ...
```

No `with` blocks needed in any handler. Only `emit()` writes to the real stdout.

## Input Sanitization for Embedded Queries

When user input gets interpolated into SQL, Cypher, or shell commands, sanitize first:

```bash
sanitize() {
  printf '%s' "$1" | sed -e "s/'//g" -e 's/;/./g'
}
name=$(sanitize "$RAW_NAME")
```

In Python:

```python
def sanitize(value: str) -> str:
    """Strip characters that break string interpolation."""
    for char in ["'", ";", "\\"]:
        value = value.replace(char, "")
    return value
```
