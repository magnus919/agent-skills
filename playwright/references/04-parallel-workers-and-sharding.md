# Parallel Workers and Sharding

> **Last Updated:** 2026-08-03

Playwright runs each test in its **own browser context** — isolation is the
default. Parallelism is about scaling that safely, and sharding is how large
suites split across CI machines.

## Workers

- `workers` in the config caps how many parallel worker *processes* run at once.
  Each worker hosts one browser instance and runs one test at a time.
- `fullyParallel: true` lets every spec file run across workers; with it off,
  only files in separate *projects* run in parallel.
- **Size workers to the machine**, not to desire: each Chromium worker needs
  roughly 300–500 MB. A 2-core/4 GB runner with 4 Chromium workers will OOM.
  Start at `Math.min(cores, 4)` and measure.
- CI: pin `workers: 4` (or `--workers=4`) for a stable runtime; `undefined`
  locally lets Playwright pick.

```ts
workers: process.env.CI ? 4 : undefined,
fullyParallel: true,
```

## Sharding

Split one suite across multiple CI jobs:

```bash
npx playwright test --shard=1/4   # job 1 of 4
```

Each shard runs a disjoint set of tests; the HTML report aggregates via
`merge-reports`. Shard count should roughly equal runner count; the sharded
runtime is the slowest shard, so balance by spec-file count, not total tests
(Playwright shards by file).

## Isolation traps (things that break parallel runs)

- **Shared global state in the app under test** — a localStorage flag, a
  singleton cache, a shared DB row: workers race and tests interfere. Reset
  per test (fixtures that clean up, `test.beforeEach` seeding).
- **Shared files on disk** — screenshots/traces written to the same path from
  two workers. Give each test its own output dir (`test-results/<project>/` is
  the default; don't override to one shared file).
- **Port collisions** — multiple webServers or `page.goto('http://localhost:3000')`
  hardcoded across workers. Use `webServer` with one process, or unique ports
  per project.
- **Test-order dependence** — `describe.only`/`test.skip` patterns, tests that
  assume a previous test ran. Every test must pass alone (`--grep` it) and in
  any order (`--workers=1 --repeat-each=3` to check determinism).

## Verifying parallelism is working

```bash
scripts/pwrun inventory --json        # suite shape
npx playwright test --list            # what will run
npx playwright test --workers=4       # parallel run
```

Compare `--workers=1` vs `--workers=4` wall time: healthy suites scale ~linearly
until CPU-bound. If the parallel run is *slower* or flakier than serial, you
have an isolation trap — see above.

## Related

- CI job wiring for shards and artifacts: `05-ci-integration.md`.
- Hermetic mocking so workers don't depend on live external APIs:
  `03-network-interception-and-mocking.md`.
