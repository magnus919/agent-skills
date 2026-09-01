# Vite Dev Server And Diagnostics

## Dev versus preview

`vite` serves the source graph with hot module replacement and development middleware. `vite preview` serves the already-built output and is useful for checking production-like asset paths; it is not a production server. Read scripts and config before invoking either.

Inspect `server.host`, `server.port`, `server.strictPort`, `server.open`, `server.proxy`, and `preview` settings. Binding to localhost limits access to the local machine. Binding to all interfaces can expose source, proxy targets, or development endpoints to the LAN; do so only with an explicit scope and network review. Never treat `--host 0.0.0.0` as a harmless default.

## Diagnostic order

1. Run `scripts/vite-doctor --project PATH --json` and record tool availability without printing variable values.
2. Read `package.json`, lockfile, config, and workspace boundaries.
3. Reproduce with the smallest declared command and a bounded timeout.
4. Classify the failure as config, dependency, plugin transform, server bind/proxy, browser runtime, or deployment routing.
5. Change one layer, rerun, and preserve the first useful error.

For proxy failures, verify the browser request URL, configured rewrite, target reachability, and CORS/auth expectations separately. A dev proxy can hide a production CORS or reverse-proxy issue. For HMR failures, inspect websocket URL, host/port, proxy upgrades, and browser console; do not immediately disable HMR.

## Script boundary

The bundled doctor is read-only and bounded. It reports Node and package-manager version commands, installed Vite package metadata, config filenames, package-manager lockfiles, and environment variable names (not values). It does not install packages, start servers, read `.env` contents, or modify the project. Use it before any potentially mutating command.
