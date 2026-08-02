# Test Debugging

Diagnosing broken tests. Load when a test that should pass is failing, a mock isn't intercepting, a fixture is producing wrong state, or a test behaves differently in CI than locally. Distinct from test *design* (that's [test-strategy.md](./test-strategy.md)) and CI infrastructure triage (that's [ci-failure-triage.md](./ci-failure-triage.md)).

## Diagnostic Order

1. **Read the actual failure output.** Not the summary line — the full traceback, assertion values, and any captured stdout/stderr.
2. **Reproduce locally** with the same command CI runs (including paths, markers, and filters).
3. **Check collection.** `pytest --collect-only <path>` — is the test even being collected? Zero items means the test is invisible.
4. **Check environment completeness.** Install the project's declared dev/test dependencies using its own manifest.
5. **Isolate the variable.** Run the single failing test, then the file, then the directory. Narrow until the failure appears and disappears.

## CI-vs-Local Divergence Checklist

When a test passes locally but fails in CI (or vice versa), work through these causes systematically:

| # | Divergence Cause | Symptom | Diagnosis | Fix |
|---|-----------------|---------|-----------|-----|
| 1 | **Environment variables** | Test reads `os.environ` differently | `diff <(env | sort) <(ci_env | sort)` | Pin required env vars in CI config; use `.env.test` locally |
| 2 | **Timing and concurrency** | Race conditions surface under CI load | Run failing test 50× locally with `pytest-repeat`; add `--count=50` | Fix the race (proper synchronization), not the timing |
| 3 | **Test ordering / shared state** | Passes alone, fails in suite | Run with `pytest-randomly` or reverse order | Eliminate shared mutable state; each test constructs its own fixtures |
| 4 | **Filesystem differences** | Path separators, symlinks, case sensitivity (Linux CI vs macOS local) | Check for hardcoded paths; `find . -name "Test_*" vs "test_*"` | Use `pathlib.Path`; never hardcode separators |
| 5 | **Network access** | CI has no internet or restricted egress | Check for real HTTP calls; CI logs show `ConnectionRefused` | Mock external calls; use recorded fixtures (VCR.py) |
| 6 | **Dependency versions** | CI resolves different versions than local | Compare `pip freeze` / `npm ls` outputs | Commit lockfiles; use exact pins in CI |
| 7 | **Timezone and locale** | Date formatting, string collation differ | `echo $TZ $LANG` locally vs CI | Set `TZ=UTC` and `LC_ALL=C` explicitly in tests |

### Gotcha: "Works on My Machine" Is a Bug Report

A CI-only failure is not "CI being flaky" until you have ruled out all seven causes above. The most common root causes are ordering (3) and environment variables (1).

## Test Ordering and Shared State

Tests that pass individually but fail as a suite have ordering dependencies. This is a test design defect, not an infrastructure problem.

### Detection

```bash
# Install pytest-randomly — it randomizes order on every run
pip install pytest-randomly

# Run with a specific seed to reproduce
pytest --randomly-seed=12345 tests/

# Reverse execution order
pip install pytest-reverse
pytest --reverse tests/
```

### Common Shared-State Patterns

| Pattern | Symptom | Fix |
|---------|---------|-----|
| Module-level mutable global | Test A sets state; Test B reads it | Reset in fixture `setup`/`teardown`; prefer function-scoped fixtures |
| Class-level `setUpClass` mutation | Later tests depend on earlier test's writes | Move to per-test setup; use `setUp` not `setUpClass` |
| Database rows from prior test | Query returns unexpected count | Transaction rollback per test (see [test-data-management.md](./test-data-management.md)) |
| File artifacts on disk | Test reads a file another test created | Use `tmp_path` fixture; never write to shared directories |
| Environment variable mutation | `os.environ["X"] = "y"` leaks across tests | Use `monkeypatch.setenv()` (auto-reverts) |
| Monkeypatched module attribute | `module.GLOBAL = value` without cleanup | Use `monkeypatch.setattr()` (auto-reverts) |

### pytest-randomly as a Design Tool

Run pytest-randomly in CI on every run. Tests that fail under random ordering have latent shared-state bugs. Fix the isolation defect rather than pinning the order — pinning hides the problem until the next refactor breaks the assumed order.

## Mock Path Binding at the Usage Point

When you `patch()` a name in Python, you must patch it **where it is looked up** (the usage point), not where it is defined.

### Root Cause

Python imports bind names into the importing module's namespace at import time:

```python
# myapp/service.py
from myapp.clients import HttpClient  # binds 'HttpClient' in service.py's namespace

def fetch_data():
    client = HttpClient()  # looks up 'HttpClient' in service.py's globals
    return client.get("/api/data")
```

```python
# WRONG: patches the definition point — service.py still has the original reference
@patch("myapp.clients.HttpClient")

# RIGHT: patches where service.py looks it up
@patch("myapp.service.HttpClient")
def test_fetch_data(mock_client):
    mock_client.return_value.get.return_value = {"result": "ok"}
    assert fetch_data() == {"result": "ok"}
```

### Signals This Is the Problem

| Signal | Meaning |
|--------|---------|
| `AttributeError: module X does not have the attribute Y` | Patching at a module that doesn't import Y directly |
| Real HTTP calls despite `patch()` with `return_value` | Patched the wrong namespace; real client still bound |
| Mock works in one test file but not another | Each importing module has its own binding; patch each |
| Refactor moved code to a subpackage | All `patch()` paths targeting the old module are now wrong |

### Rule of Thumb

| Import Style | Patch Target |
|-------------|-------------|
| `from module import Class` | `patch("consumer_module.Class")` |
| `import module; module.Class()` | `patch("module.Class")` |
| `from module import func` used in 3 files | Patch in all 3 consumer modules |

## FastAPI Startup Race

When a FastAPI app's `@app.on_event("startup")` handler re-assigns module-level state, any mock state set before `with TestClient(app) as tc:` is silently overwritten.

```python
# Fix: set mock state AFTER context entry
@pytest.fixture
def client():
    with TestClient(app) as tc:  # startup runs here
        server_mod._active_engines = {"mock": MockEngine()}  # set AFTER
        yield tc
```

## Test Execution Integrity

A passing command is not necessarily an executed test suite.

1. **Read the collection summary.** `0 items`, `N skipped`, or exit code `5` means the intended behavior was not exercised.
2. **For a module-level target**, require a nonzero collected count and a passing test relevant to the change.
3. **If a test is skipped** because its fixture or path is wrong, repair that harness defect before opening the PR.
4. **Re-run after the repair** and record the actual result (e.g., `62 passed`), not only the exit status.

### CI Collection-Path Gate

A new test can pass locally and provide zero CI protection when it lives outside the directories selected by the workflow.

1. Read the exact CI test command, including explicit paths, `-k` filters, markers, and ignore flags.
2. Confirm the new test's path is included by that command.
3. Put the test under an already-collected directory when that matches its scope.
4. Inspect CI logs for the test/module after pushing.

## Gotchas

- **Do not mask a test design failure with retries or `xfail`.** If a test fails under random ordering, fix the isolation — don't pin the order.
- **Do not treat a green exit code as evidence.** Read the collection count. Zero collected tests with exit 0 is not a passing suite.
- **Mock at usage, not source.** After any module→package refactor, audit every `patch()` path against the new import structure.
- **Set mocks after startup, not before.** Any framework lifecycle hook that re-assigns module state will overwrite pre-context mock setup.
- **Patching `time.sleep` instead of freezing time** creates fragile tests. Use freezegun or timecop (see [test-data-management.md](./test-data-management.md)).

## Composition

- Systematic debugging methodology (hypothesis-driven, evidence-first): [systematic-debugging](../../systematic-debugging/SKILL.md)
- CI infrastructure triage (exit codes, bisect, runner issues): [ci-failure-triage.md](./ci-failure-triage.md)
- Test data isolation and time freezing: [test-data-management.md](./test-data-management.md)

*Sources: pytest-randomly (GitHub, adamchainz), pytest docs on monkeypatch (docs.pytest.org), Python unittest.mock docs (docs.python.org), freezegun (GitHub, spulec).*
