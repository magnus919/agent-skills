# Temporal RAG and time-series evidence

Separate three questions. Timeline retrieval reconstructs sequence and context.
Bitemporal retrieval reconstructs which facts were valid and which were known
at a cutoff. Time-series retrieval supplies measurements for trends, comparisons
and, when justified, forecasting. One agent can use all three.

## Compose the evidence paths

1. Resolve the entity, metric definition, unit, time zone, time window, grain,
   comparison period, and analysis cutoff. For an incident timeline, keep
   event time and ingestion time. For corrections and retroactive updates,
   keep valid time and recorded time. For a forecast, record its origin and
   horizon. Use current access policy on every historical query.
2. Query a typed, bounded analytics tool for authorized numerical evidence.
   A relational measurements table can serve a small corpus. A time-series
   database or metrics backend can support larger append-heavy histories,
   range queries, rollups, retention, and downsampling. Prometheus range
   queries and Timescale time buckets illustrate distinct interfaces. Scope
   the metric, labels, entity IDs, periods, and maximum result size on
   the server. Return units, bucket boundaries, sample counts, gaps,
   coverage or watermark, and a reproducible query or snapshot reference.
3. Retrieve timestamped documents, events, graph assertions, or image evidence
   under the same identity. Join by entity, version, and compatible time
   intervals. Preserve source-specific citations for every join. Send the
   caller structured values and selected records, plus a chart only if helpful.
   A chart is a projection of the data with its own lineage and policy.
4. Interpret deterministic calculations in the generator. Handle resets,
   incomplete buckets, late arrival, time-zone/DST changes, and changes in
   metric definition. Compare compatible baselines and seasonal periods.
   Annotations can explain hypotheses. Temporal proximity alone supplies no
   causal estimate.

## Trends, anomalies, and likelihood

- **Observed trend** uses an explicit statistic and comparison window.
  Compute it from the authorized observations. Report coverage and describe
  gaps, uncertainty, or insufficient data.
- **Anomaly** depends on a defined baseline, seasonality, and threshold.
  Validate on historical incidents and quiet periods, including missing data.
- **Forecast or event probability** must come from a supported statistical
  model or a governed forecasting service. Specify the event, horizon, cutoff,
  model version, assumptions, and eligible data used. Compare to persistence
  or seasonal-naive baselines with rolling-origin evaluation. Check interval
  coverage or event calibration and a proper score such as Brier score for
  binary events, sliced by horizon and regime. Calibrate on past data and
  evaluate on a later held-out period. Keep future data and later corrections
  out of training and evidence at each backtest cutoff. Decline a numeric
  probability when the data or calibration is insufficient. A point forecast
  and an empirical frequency require their own labels and interpretation.

## Worked design

A reliability agent asks whether tomorrow's peak backlog may exceed a
threshold. It resolves the service and eligible queue labels, queries aligned
hourly observations, and retrieves deployment events and runbook revisions
for the same period. It cites the metric definition, window, coverage, and
event records. A separately validated forecast estimates the probability of
the daily maximum crossing the threshold. Pointwise quantiles alone cannot
establish that probability. If the model lacks calibration for a new traffic
regime, the agent reports the observed trend and states that the probability
is unavailable. If some queues are restricted, it identifies the conclusion
as scoped to permitted queues without disclosing which queues were excluded.

Check rollups, anomaly alerts, nearest historical windows, forecast features,
and charts for the same access policy as their inputs. A mixed-scope forecast
or aggregation requires a separately approved release policy, scoped model or
query-time recomputation. Test late event corrections, revoked series, sparse
history, timestamp misalignment, and recovery of the exact evidence visible
at a historical decision cutoff. See the [research log](research-log.md) for
temporal QA, metrics, and forecasting evidence.
