---
name: tempest-cli
description: 'Query hyper-local weather from a WeatherFlow Tempest station: current
  conditions, 7-day forecast, historical observations, and real-time UDP broadcasts.
  Use when the user asks about the weather, temperature, rain, wind, humidity, forecast,
  or wants conditions from their own station rather than a generic weather service.'
license: MIT
compatibility: Requires TEMPEST_TOKEN env var (free from weatherflow.com), Python
  3.8+, and the `requests` library.
metadata:
  tags: weather, tempest, forecast, weatherflow, station, hyper-local
  sources: https://weatherflow.com, https://swd.weatherflow.com/swd/rest
---

# tempest-cli — Hyper-Local Weather from Your Tempest Station

Query live weather data from a WeatherFlow Tempest station. Supports REST API access to current conditions, forecasts, and history via the cloud, plus local UDP broadcast reception from your hub on the same LAN.

## Setup

1. Get a personal access token at [weatherflow.com](https://weatherflow.com) (Account → API Tokens)
2. Set it in your environment:

```bash
export TEMPEST_TOKEN="your-token-here"
```

The CLI reads `TEMPEST_TOKEN` from the environment. It also falls back to reading `~/.tempest.env` if the env var is not set (for agent subprocesses that don't inherit env vars). `--help` and `--dry-run` work without a token.

## Essential Commands

### current — Current conditions

```bash
tempest-cli current                                             # human-readable
tempest-cli current --station-id 12345 --device-id 67890        # specific hardware
tempest-cli current --json                                      # machine-readable
```

If you have one station, it auto-selects it and picks the best sensor (ST > SKY > AIR, skips the HB hub). Pass `--station-id` or `--device-id` to override.

### forecast — Multi-day forecast (+ current conditions + hourly)

```bash
tempest-cli forecast                        # current + 5-day daily + 12-hour hourly
tempest-cli forecast --days 3               # fewer days
tempest-cli forecast --station-id 12345     # specific station
tempest-cli forecast --json                 # machine-readable
```

### stations — List your stations and devices

```bash
tempest-cli stations                    # shows station names, IDs, device types, serials
tempest-cli stations --json             # full device inventory
```

Use this first if you don't know your station ID or want to see what sensors are online.

### obs — Historical observations

```bash
tempest-cli obs --device-id 67890 --days 1       # last 24 hours
tempest-cli obs --device-id 67890 --days 7       # last week
tempest-cli obs --device-id 67890 --json         # machine-readable
```

### udp listen — Real-time broadcasts from the hub

```bash
tempest-cli udp listen                          # listen indefinitely (Ctrl-C to stop)
tempest-cli udp listen --timeout 30             # auto-stop after 30s
tempest-cli udp listen --show-all               # include hub_status messages
```

Requires being on the same LAN as the hub (port 50222 UDP broadcast). Receives observations, rapid wind updates, lightning strike events, and precipitation start events in real time.

## Data Reference

### obs_st field layout (Tempest all-in-one)

Observations from the Tempest sensor arrive as positional arrays. The CLI decodes them, but if you're reading raw JSON output, this map tells you what each index means:

| Index | Field | Units | Notes |
|-------|-------|-------|-------|
| 0 | epoch | seconds UTC | |
| 1 | wind_lull | m/s | Minimum 3-second sample |
| 2 | wind_avg | m/s | Average over report interval |
| 3 | wind_gust | m/s | Maximum 3-second sample |
| 4 | wind_direction | degrees | 0=N |
| 5 | wind_sample_interval | seconds | |
| 6 | station_pressure | MB | |
| 7 | air_temperature | C | CLI converts to °F |
| 8 | relative_humidity | % | |
| 9 | illuminance | lux | |
| 10 | uv | index | |
| 11 | solar_radiation | W/m² | |
| 12 | rain_accumulation | mm | Over last interval |
| 13 | precipitation_type | enum | 0=none 1=rain 2=hail |
| 14 | avg_strike_distance | km | Lightning |
| 15 | strike_count | count | Lightning |
| 16 | battery | volts | ~2.6V normal, ~2.5V low |
| 17 | report_interval | minutes | |
| 18 | local_day_rain_accumulation | mm | |

See [references/tempest-api-field-layouts.md](references/tempest-api-field-layouts.md) for the full obs_air and obs_sky field layouts.

### Unit conversions the CLI applies

| Input | Output | Conversion |
|-------|--------|------------|
| °C | °F | `c * 9/5 + 32` |
| m/s | mph | `mps * 2.237` |
| MB | inHg | `mb * 0.02953` |
| mm | in | `mm / 25.4` |
| degrees | cardinal | N, NNE, NE, ..., NNW |

## Known Gotchas

### The API is metric-native

All raw observation data comes in metric (Celsius, m/s, MB, mm). The CLI converts for human display. If you're parsing raw `--json` output, expect metric values. The `better_forecast` endpoint returns unit-converted values based on station preferences — check the `units` key in the response — but **temperatures are always in Celsius** regardless.

### Timestamps are epoch integers, not strings

The API returns Unix epoch timestamps, not ISO 8601 strings. The `daily[].day_start_local` field is an `int`, not `"2026-05-10T00:00:00"`. Hourly objects have `local_hour` (int 0-23) and `local_day` (int) — there is **no** `local_time` or `time_string` field. The CLI handles this, but raw JSON consumers need to convert with `datetime.fromtimestamp(ts)`.

### Nested forecast response

The `better_forecast` endpoint nests daily and hourly arrays under a `forecast` wrapper key, not at the top level:

```python
# Correct path:
fc = data.get("forecast", {})
days = fc.get("daily", [])
hours = fc.get("hourly", [])
```

The top-level keys are: `current_conditions` (dict), `forecast` (dict with `daily` + `hourly`), `station` (metadata), `units`, `status`, `timezone`.

### Device type filtering

A station returns all devices including the hub (device_type `HB`). The hub cannot serve observations. The CLI auto-filters HB devices and prefers ST > SKY > AIR. If you're bypassing the CLI and calling the API directly, always filter out device_type `HB` before querying observation endpoints.

### Global flags in any position

`--json`, `--dry-run`, `--quiet`, and `--verbose` work anywhere in the command:

```bash
tempest-cli --json current --device-id 67890        # flag before subcommand
tempest-cli current --device-id 67890 --json         # flag after subcommand
```

## References

- [references/tempest-api-field-layouts.md](references/tempest-api-field-layouts.md) — Full field index maps for obs_st, obs_air, and obs_sky observation arrays. Read when decoding raw JSON output or building on top of the Tempest API.
- [scripts/tempest-cli](scripts/tempest-cli) — The CLI binary itself. Designed following the cli-builder patterns: non-interactive, `--json`, `--dry-run`, `--quiet`, `--verbose`, idempotent, dual-output via `emit()`, and structured logging.
