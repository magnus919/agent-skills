# Performance and observability

Use this reference when a backup is slow, expensive, noisy, or insufficiently observable.

## Measure before tuning

Collect a bounded baseline:

```sh
restic version
restic snapshots --json
restic stats --mode raw-data
restic stats --mode restore-size
```

Record source data size/file count, elapsed duration, added/stored bytes, backend latency/error rate, CPU/memory pressure, cache location/size, bandwidth constraints, and whether the job overlaps with another backup or maintenance task. The backup progress display reports processed source files, not necessarily transferred bytes; deduplication and compression make those quantities differ.

## Highest-value tuning order

1. Fix the source boundary. Avoid backing up rebuildable caches, temporary files, duplicate mounts, or inconsistent live application data.
2. Eliminate backend and network mistakes. Confirm endpoint, region/path style, DNS/TLS, bandwidth caps, and credentials before changing restic knobs.
3. Manage schedule contention. Keep backups, prune, full checks, and heavy restores from competing for the same repository or disk/network window.
4. Use restic options only against observed bottlenecks and the current command reference.
5. Re-measure with the same source scope and report the tradeoff.

Do not blindly disable scanning, caching, compression, or verification because a job is slow. Each change shifts correctness, CPU, bandwidth, or restore behavior.

## Useful controls

- `--limit-upload` and `--limit-download`: bound network use when shared capacity matters.
- `--cache-dir` and `RESTIC_CACHE_DIR`: choose a persistent local cache location with adequate capacity and appropriate permissions.
- `cache --cleanup`: remove unused cache data after confirming it is safe for the local host; cache removal affects performance, not repository contents.
- `--exclude-file`: reduce source scanning and repository growth by defining intentional exclusions.
- `--no-scan`: changes progress estimation behavior; it is not a general performance cure.
- `--read-concurrency` / `--pack-size`: version- and workload-sensitive controls. Consult `restic backup --help` for the installed binary and test in a bounded window before standardizing.

For a slow remote backend, first compare a small test backup and restore against the same backend from the same execution environment. A CLI option cannot correct packet loss, provider throttling, an overloaded gateway, or an incorrect endpoint.

## Observability design

A job should yield evidence usable by both a human and an alert rule:

| Signal | Why it matters |
|---|---|
| Process exit status | Immediate failure signal, but insufficient alone |
| Newest snapshot age by host/path/tag | Detects a schedule that ran but captured the wrong source or no source |
| Duration and bytes added/stored | Detects unusual growth, stalled jobs, deduplication changes |
| Restic error count and stderr | Identifies partial backups or unreadable source files |
| `check` and data-read date/result | Tracks repository readability |
| Restore-drill date/result | Tracks actual recovery capability |
| Backend capacity/billing/availability | Prevents a repository becoming unavailable outside restic |

Use structured output for machines and keep human logs bounded. Never send raw secret-bearing environment dumps to a monitoring system. If a monitoring agent parses a snapshot list, filter it to the expected group rather than assuming `latest` across all hosts is the correct recovery point.

## Data-read cadence

A practical default is metadata checks more frequently than full data reads, with sampled reads between them. The right interval depends on repository size, risk tolerance, backend error history, and recovery objective. Document the chosen cadence in `templates/backup-policy.env.example` and test a full data read after material changes.

## Sources

- Backup progress, deduplication, compression, and options: https://restic.readthedocs.io/en/stable/040_backup.html (accessed 2026-07-15)
- Cache command reference: https://restic.readthedocs.io/en/stable/manual_rest.html#restic-cache (accessed 2026-07-15)
- Global options and command help: https://restic.readthedocs.io/en/stable/manual_rest.html (accessed 2026-07-15)
