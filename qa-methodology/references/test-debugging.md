# Test Debugging

Diagnosing broken tests. Load when a test that should pass is failing, a mock
isn't intercepting, a fixture is producing wrong state, or a test behaves
differently in CI than locally. This is distinct from test *design* (that's
`test-strategy.md`) and test *quality* (that's the contribution-test-quality
skill's scorecard).

## Diagnostic Order

1. **Read the actual failure output.** Not the summary line — the full
   traceback, assertion values, and any captured stdout/stderr.
2. **Reproduce locally** with the same command CI runs (including paths,
   markers, and filters).
3. **Check collection.** `pytest --collect-only <path>` — is the test even
   being collected? Zero items means the test is invisible.
4. **Check environment completeness.** Install the project's declared dev/test
   dependencies using its own manifest. A bare editable install plus `pytest`
   can omit plugins the project deliberately keeps out of runtime dependencies.
5. **Isolate the variable.** Run the single failing test, then the file, then
   the directory. Narrow until the failure appears and disappears.

## Mock Path Binding After Package Refactors

When a Python module is refactored into a package (`research.py` →
`research/__init__.py` + submodules), all test mock paths targeting that module
break silently.

### Root Cause

Relative imports bind local references at import time, before `patch()` runs:

```python
# agent/research/loop.py
from ..llm import LLMClient  # binds LLMClient in loop.py's namespace NOW
```

Mocking at the source module (`agent.llm.LLMClient`) replaces the class object,
but `loop.py`'s local reference still points to the original. The mock is
invisible.

### Fix: Mock at the Usage Point

| Wrong (source-level) | Right (usage-level) |
|---|---|
| `patch("agent.llm.LLMClient")` | `patch("agent.research.loop.LLMClient")` |
| `patch("agent.clients.HttpClient")` | `patch("agent.research.loop.HttpClient")` |

Each submodule has its own namespace. Mock at each one exercised by the test.

### Signals This Is the Problem

- `AttributeError: module X does not have the attribute Y` for a class that IS
  imported at the top of the source file
- Real API calls (401 errors, timeouts) leaking through despite a source-level
  `patch()` return_value
- The refactor commit message mentions "split X.py into X/ package"

## FastAPI Startup Race

When a FastAPI app's `@app.on_event("startup")` handler re-assigns module-level
state, any mock state set before `with TestClient(app) as tc:` is silently
overwritten.

```python
# server.py
_active_engines: dict = {}

@app.on_event("startup")
async def startup():
    global _active_engines
    _active_engines = discover_engines()  # overrides anything test set
```

### Fix: Set Mock State After Context Entry

```python
@pytest.fixture
def client():
    with TestClient(app) as tc:  # startup runs here
        server_mod._active_engines = {"mock": MockEngine()}  # set AFTER
        yield tc
```

### Alternative: Guard the Startup Handler

```python
@app.on_event("startup")
async def startup():
    global _active_engines
    if not _active_engines:  # allow test pre-seeding
        _active_engines = discover_engines()
```

## httpx Mock Testing

When testing async httpx-based adapters that create their own
`httpx.AsyncClient` inline, patch the constructor with a mock transport:

```python
class MockHTTP:
    def __init__(self, handler):
        self.transport = httpx.MockTransport(handler)

    async def __aenter__(self):
        self.mock_client = httpx.AsyncClient(transport=self.transport)
        self.patcher = patch("httpx.AsyncClient")
        mock_class = self.patcher.start()
        mock_class.return_value.__aenter__.return_value = self.mock_client
        return self

    async def __aexit__(self, *args):
        self.patcher.stop()

# Usage:
async with MockHTTP(lambda r: httpx.Response(200, json={"results": []})):
    result = await adapter.search("query")
```

## Test Execution Integrity

A passing command is not necessarily an executed test suite.

1. **Read the collection summary.** `0 items`, `N skipped`, or exit code `5`
   means the intended behavior was not exercised.
2. **For a module-level target**, require a nonzero collected count and a
   passing test relevant to the change.
3. **If a test is skipped** because its fixture, path, or module lookup is
   wrong, repair that harness defect before opening the PR. Do not describe
   the run as passed.
4. **Re-run after the repair** and record the actual result (e.g., `62 passed`),
   not only the command exit status.

### CI Collection-Path Gate

A new test can pass locally and provide zero CI protection when it lives outside
the directories selected by the workflow.

1. Read the exact CI test command, including explicit paths, `-k` filters,
   markers, ignore flags, and project addopts.
2. Confirm the new test's path is included by that command. Do not infer
   collection from a `test_*.py` filename alone.
3. Put the test under an already-collected directory when that matches its scope.
4. Inspect CI logs for the test/module after pushing. A green broad suite that
   never collected the new test is not evidence for the new contract.

## Deterministic Integration Seeds

When an integration test proves a narrow behavior (ownership, authorization,
ordering, isolation) but creates its precondition through a live or variable
dependency (web search, third-party content, provider ranking):

1. State the behavior the test is actually proving.
2. Seed the minimal prerequisite through an existing deterministic fixture or
   a stable, already-tested service path.
3. Assert the seed succeeded with a small contract check.
4. Preserve the original behavior assertion unchanged.

An HTTP-successful search with zero results can be valid. If a test fails at
`assert refs`, it has not exercised the ownership/isolation condition it claims
to cover. Retrying or tuning runner resources does not repair that test design.

## API Signature Changes — Fixture Recovery

When a function gains a new parameter, unit tests that mock that function
silently fail. Every fixture that creates a mock of the changed function needs
the new method wired.

### Batch Fix Method

Do NOT use `read_file`/`write_file` for bulk fixture updates — they add
line-number prefixes. Instead:

```python
from pathlib import Path
path = Path("tests/test_file.py")
content = path.read_text()
old = "scraper = MagicMock()\n        scraper.scrape = AsyncMock()"
new = """scraper = MagicMock()
        scraper.scrape = AsyncMock()
        scraper.scrape_with_fallback = AsyncMock()"""
path.write_text(content.replace(old, new))
```

## Lockfile Hygiene During Verification

`uv run` can rewrite a tracked `uv.lock` while resolving a local workspace
package. Before testing, inspect status. If testing alone created unrelated
lockfile drift, restore only that exact generated file after confirming it was
not intentional. Use `uv run --no-sync` when the existing environment is
sufficient. Never restore a lockfile containing intentional dependency changes.

## Pitfalls

- **Do not mask a test design failure with retries or `xfail`.** If a test for
  isolation seeds itself through a live search, the fix is deterministic
  seeding — not retrying until the search returns results.
- **Do not treat a green exit code as evidence.** Read the collection count.
  Zero collected tests with exit 0 is not a passing suite.
- **Mock at usage, not source.** After any module→package refactor, audit every
  `patch()` path in the test suite against the new import structure.
- **Set mocks after startup, not before.** Any framework lifecycle hook that
  re-assigns module state will overwrite pre-context mock setup.
