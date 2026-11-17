# Middleware boundary rubric challenges

Added 2026-11-17: `inflight-per-client-limit`, `client-ip-behind-load-balancer`,
and `buffering-streaming-route`. Existing IDs and assertions are unchanged.
These author-written challenge examples clarify the new semantic assertions;
they are not generated runs, independent adjudication, or release evidence.
Each row maps to the corresponding case's 1-based assertion index. A missing
piece of evidence is not shown, not a negative result. Equivalent wording and
equivalent valid configurations are acceptable.

## inflight-per-client-limit

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | `inFlightReq` with `amount: 20` | `rateLimit` with `average: 20`, presented as a concurrency cap | No middleware definition |
| 2 | `sourceCriterion.ipStrategy.depth: 0`, or `ipStrategy: {}` | `ipStrategy.depth: 1`, or `requestHost: true` | No `sourceCriterion` and no statement of the grouping key |
| 3 | The default is per request host; every client of `api.example.com` shares the 20 | The default is per client IP, so `sourceCriterion` is optional | Default grouping not mentioned |
| 4 | A `sourceCriterion` that contains only `ipStrategy` | `requestRemoteAddr: true`, or `requestHost: true` next to `ipStrategy` | No `sourceCriterion` block shown |
| 5 | 25 parallel slow requests from one address: 5 get 429; a second address still gets 200 | A load test of total requests per second | No verification |

## client-ip-behind-load-balancer

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | The load balancer is untrusted, so Traefik drops X-Forwarded-For before ipAllowList and depth 1 yields no address | The 403 comes from a wrong CIDR in `sourceRange` | No cause given, or only "check the logs" |
| 2 | `forwardedHeaders.trustedIPs: ["10.0.0.0/16"]` on the entryPoint | `trustedIPs` placed on the middleware, or set to `0.0.0.0/0` | No entryPoint change |
| 3 | `ipStrategy.depth: 1`, or `excludedIPs: ["10.0.0.0/16"]` | `ipStrategy` removed, so the match uses the load balancer's address | ipAllowList configuration not shown |
| 4 | Rejects `insecure: true`: a client that reaches the entryPoint directly sends `X-Forwarded-For: 203.0.113.7` and passes | Recommends `insecure: true` as the simplest fix | `insecure` not discussed |
| 5 | Office address through the load balancer gets 200; an outside address gets 403 | Tests only from the office and calls the fix verified | No verification |
| 6 | An outside client sends `X-Forwarded-For: 203.0.113.7`; the load balancer appends its real address and the request gets 403 | Expects 200 for a request whose leftmost X-Forwarded-For entry is in the office range | No spoofing check |

## buffering-streaming-route

| Assertion | Satisfying evidence | Contradictory near miss | Missing evidence |
|---|---|---|---|
| 1 | Buffering holds the response body until the backend completes it, so events arrive together at the end | Blames the backend's flush interval or `Cache-Control` headers | No cause given |
| 2 | Router for ``PathPrefix(`/events`)`` without `buf`; upload routers keep `buf` | Removes the buffering middleware from all routers, dropping the upload limit | No v3.7 configuration |
| 3 | v3.7 cannot set `disableResponseBuffer` from files or labels; it needs v3.8 | Sets `disableResponseBuffer: true` in the v3.7 file configuration | v3.7 limitation not mentioned |
| 4 | A second middleware with `disableResponseBuffer: true` and no `retryExpression` | Adds `disableResponseBuffer: true` to the existing middleware that keeps `retryExpression` | No v3.8 middleware |
| 5 | The combination fails with "retryExpression cannot be used when disableRequestBuffer or disableResponseBuffer is enabled" and the routers are disabled | The combination works and retries apply only to request bodies | Combination not discussed |
| 6 | `curl -N` shows each event when the backend sends it | Checks only for HTTP 200 on `/events` | No streaming check |
| 7 | An 11 MB POST through the streaming middleware gets 413 | States that streaming disables every size limit | No upload-limit check |

## Source of the expected behavior

The expected outputs were checked on 2026-11-17 against the Traefik source at
the pinned tags and in `traefik:v3.7.19` and `traefik:v3.8.0-rc.3` containers
with the file provider:

- InFlightReq with `amount: 1` and no `sourceCriterion`: two client addresses
  sending to one host got 200 and 429. With `ipStrategy.depth: 0`, both got 200.
- ipAllowList with `depth: 1` or `excludedIPs`, behind a simulated load
  balancer: 403 without `trustedIPs`; 200 with `trustedIPs`; 403 for a forged
  leftmost entry followed by an outside address; 403 for a direct untrusted
  client with a forged header. With `insecure: true`, the direct client with a
  forged header got 200.
- Buffering, v3.8.0-rc.3: the catalog example delivered three SSE events
  together after 3 s; the streaming example delivered them 1 s apart, and an
  11 MiB POST got 413. Adding `disableResponseBuffer` to the example with
  `retryExpression` disabled both routers that used it. v3.7.19 loaded
  `disableResponseBuffer` without an error and kept buffering.

These checks cover the configuration behavior the assertions describe. They do
not grade any model response.
