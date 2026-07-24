# Raleigh Open Data Dataset Catalog

The dataset catalog is now discovered live from the ArcGIS Hub Search API rather than maintained as a hardcoded list. Use the CLI to browse the current catalog:

```bash
raleigh catalog
raleigh search "parks"
raleigh categories
```

For the underlying API contract, see `api-reference.md`.

## Why Live Discovery

Hub collections such as `dataset`, `document`, and `appAndMap` expose the curated public catalog. Live discovery avoids stale endpoints and ensures the CLI reflects the current service inventory.

## Offline Resilience

The CLI caches the normalized catalog locally. Use `--refresh` to bypass the cache, or run `raleigh catalog-check` to validate a sample of canonical endpoints.
