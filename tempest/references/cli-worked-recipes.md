# CLI Worked Recipes (tempest)

Multi-step, executable recipes for the bundled `tempest` CLI. Global flags
`--json`, `--dry-run`, `--quiet`, `--verbose` work in any position on the
command line. `--json` output is metric-native (raw wire units); human output
is converted. `--dry-run` never touches the network and always exits 0 with a
plan object.

## Recipe 1: Discover the station, then read current conditions

```bash
# Step 1: find station and device ids (works even before you memorize ids)
tempest stations --json | jq '.stations[] | {station_id, name,
  devices: [.devices[] | {device_id, device_type, serial_number}]}'

# Step 2: current conditions, machine-readable
tempest current --json | jq '{station, device_id, type,
  temp_c: .observation.air_temperature,
  wind_mps: .observation.wind_avg,
  rain_mm: .observation.rain_accumulation}'

# Step 3 (pin a specific station/device when several exist)
tempest current --station-id 12799 --device-id 60526 --json
```

Stage compatibility: `stations --json` emits `{"stations": [...]}` with
integer `station_id`/`device_id` fields — feed those ints to
`--station-id`/`--device-id` on `current`. `current --json` emits
`{station, device_id, type, observation}` where `observation` carries the
decoded positional array as named fields (metric-native types: numbers for
measurements, `timestamp` as ISO-8601 string).

Auto-selection rules when you don't pass ids: the first station is used; the
device is the first `ST` (Tempest), then `SKY`/`SK`, then `AIR`/`AR`, always
skipping `HB` hubs (hubs carry no observations). If only a hub exists the CLI
dies with a clear error instead of guessing.

## Recipe 2: 7-day forecast slice for scripts

```bash
tempest forecast --days 7 --json \
  | jq '{units_temp: .forecast.units.units_temp,
         today: (.forecast.forecast.daily[0]
                 | {day_start_local, air_temp_high, air_temp_low, precip_probability}),
         next12: [.forecast.forecast.hourly[:12][]
                  | {local_hour, air_temperature, precip_probability}]}'
```

Converting highs to °F with jq (read `units` from the same document before
converting anything):

```bash
tempest forecast --json \
  | jq '{units_temp: .forecast.units.units_temp,
         highs_f: [.forecast.forecast.daily[] | .air_temp_high * 9 / 5 + 32],
         rain_hours: [.forecast.forecast.hourly[] | select(.precip_probability > 30) | .local_hour]}'
```

**Convert only after reading `units`:** the endpoint honors unit overrides
(`units_temp=f` etc.), so hard-coded Celsius math double-converts Fahrenheit
responses. When the CLI displays forecast values it converts °C→°F only for
stations whose `units_temp` is `c`. Human output prints current conditions,
then the daily table, then the next 12 hours.

## Recipe 3: Rain-watch (yesterday's total + live rain events)

```bash
# What fell yesterday (UTC day): obs from history, day_offset=1
DEVICE_ID=$(tempest stations --json | jq -r '
  .stations[].devices[] | select(.device_type == "ST") | .device_id' | head -1)
tempest obs --device-id "$DEVICE_ID" --days 1 --json \
  | jq '{type, samples: (.observations | length),
         day_rain_mm: .observations[-1].local_day_rain_accumulation}'

# Live: rain-start events and rapid wind from the hub broadcast
tempest udp listen --timeout 600 --json | jq 'select(.type == "evt_precip")'
```

Stage compatibility: `obs --json` emits `{device_id, type, count,
observations}` with each decoded observation carrying
`local_day_rain_accumulation` (mm, number) — the `-1` index grabs the newest
sample of the day. `udp listen --json` emits one JSON object per datagram;
`evt_precip` objects carry `{type, serial_number, timestamp}`.

## Recipe 4: Decode any raw UDP datagram positionally

Feed canned datagram bytes to the same decoder the listener uses — no
sockets, no hub required (this is exactly how `scripts/test_tempest.py`
exercises the parser):

```python
# /tmp/decode_one.py
import importlib.machinery, importlib.util, json
loader = importlib.machinery.SourceFileLoader("t", "tempest/scripts/tempest")
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)

datagram = (b'{"serial_number":"ST-00000512","type":"obs_st","hub_sn":"HB-00013030",'
            b'"obs":[[1588948614,0.18,0.22,0.27,144,6,1017.57,22.37,50.26,328,0.03,3,'
            b'0.0,0,0,0,2.410,1]],"firmware_revision":129}')
msg = json.loads(datagram.decode())
for row in msg["obs"]:                      # obs families: list of rows
    decoded = mod.decode_obs(row, msg["type"])
    print(decoded["air_temperature"], "°C", decoded["air_temperature_unit"])

rapid = json.loads(b'{"type":"rapid_wind","ob":[1493322445,2.3,128],"serial_number":"SK-1"}'.decode())
speed, direction = rapid["ob"][1], rapid["ob"][2]   # rapid_wind: ONE array under "ob"
```

The three structural keys to remember (see udp-broadcast-protocol.md):
observation families nest rows under `obs`; `rapid_wind` carries one array
under `ob`; events (`evt_precip`, `evt_strike`) carry one array under `evt`;
`hub_status`/`device_status` have named fields and no array at all. Dispatch
on `type` before indexing.

## Recipe 5: Dry-run previews and flag behavior

```bash
# Plan, don't execute: valid JSON, exit 0, zero network
tempest forecast --station-id 12799 --days 3 --dry-run --json
# -> {"dry_run": true, "command": "forecast", "station_id": 12799, "days": 3}

# Every documented command has a dry-run plan: current, obs, forecast, stations
tempest obs --device-id 60526 --days 2 --dry-run --json

# Quiet/verbose piping: logs on stderr, data on stdout
tempest current --json --quiet | jq .observation.air_temperature
```

Behavior contract: `--dry-run` works without `TEMPEST_TOKEN` set (no credential
needed to see a plan); `--help` and `--dry-run` are always offline. Without
`--dry-run`, a missing token exits 1 with
`Error: TEMPEST_TOKEN not set...` before any request is attempted.

## Recipe 6: JSON error paths you'll actually see

```bash
tempest current --station-id 99999999
# Error: Station 99999999 not found.            (exit 1)

tempest obs --device-id 123                     # hub or wrong device
# Error: API error (404): ...                   (exit 1)

unset TEMPEST_TOKEN; tempest stations
# Error: TEMPEST_TOKEN not set. Get one at https://weatherflow.com  (exit 1)
```

The client maps 401 → token message, 403 → access-denied message, 404 →
not-found-with-path, and any other ≥400 dumps the response body. In `--json`
mode errors still go to stderr as text; only success payloads print to stdout,
so `jq` pipelines fail loudly instead of parsing prose.

## Sources

- https://apidocs.tempestwx.com/reference/quick-start (token setup, REST examples, primary-source guidance)
- https://apidocs.tempestwx.com/reference/get_stations (StationSet shape feeding the stations command)
- https://apidocs.tempestwx.com/reference/getobservationsbydeviceid (device observation parameters used by current/obs)
- https://apidocs.tempestwx.com/reference/get_better-forecast-1 (forecast unit selection used by recipe 2)
- https://weatherflow.github.io/Tempest/api/udp/v171/ (UDP message families used by recipes 3–4)
