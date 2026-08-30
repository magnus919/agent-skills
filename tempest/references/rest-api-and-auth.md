# Tempest REST API and Authentication

The Tempest REST API is the cloud service at `https://swd.weatherflow.com/swd/rest`.
It is the primary, recommended data source even for programs running on the same
LAN as the hub; the local UDP broadcast (see udp-broadcast-protocol.md) is
officially positioned as an off-grid backup. Base URL used throughout:

```
https://swd.weatherflow.com/swd/rest
```

## Authentication: the personal access token

There are exactly two documented authentication methods, and the bundled CLI
uses the first:

1. **Personal Access Token** — the right choice for scripts and integrations
   without a graphical interface. Sign in to the Tempest Web App
   (tempestwx.com), then go to **Settings → Data Authorizations → Create
   Token**, and copy the generated token. This is what `TEMPEST_TOKEN`
   carries.
2. **OAuth 2.0** (Authorization Code, optionally with PKCE) — the documented
   choice for production apps with a web UI. Apps are registered from the
   account's Developers page; authorization and token endpoints are documented
   separately in the OAuth reference. The CLI does not implement OAuth.

On the wire, the token travels as a **query parameter**:

```
GET https://swd.weatherflow.com/swd/rest/stations?token=<YOUR_TOKEN>
```

The official quick-start examples use `token=[your_access_token]` and show no
`Authorization` header alternative for this API. Do not send the token as a
header or assume bearer syntax is supported. The OpenAPI document describes the
scheme as `apiKey` with `in: query`, which matches.

Policy notes (remote-developer-policy): personal-use access covers station
metadata, observations, and forecasts with "rate/volume limits (enough for
personal use)". No numeric quota is published, and no 429 response behavior is
documented. Higher-volume or network-wide access requires a commercial
agreement (TempestONE). Keep personal integrations to your own stations.

## Endpoint catalog (personal-use surface)

### GET /stations — your stations with devices

Parameters: `limit` (int64, default 10000), `next_cursor` (string; present
when more than 10,000 stations are provisioned), optional geographic filters
(`lat_min`/`lon_min`/`lat_max`/`lon_max` bounding box, or
`center_lat`/`center_lon`/`radius` in meters).

Response is a **StationSet wrapper**, not a bare list:

```json
{
  "status": { "status_code": 0, "status_message": "SUCCESS" },
  "stations": [
    {
      "station_id": 12799,
      "location_id": 12799,
      "name": "Home",
      "public_name": "Home",
      "latitude": 42.37,
      "longitude": -71.06,
      "timezone": "America/New_York",
      "timezone_offset_minutes": -300,
      "station_meta": { "elevation": 1567.65, "share_with_wf": true, "share_with_wu": true },
      "is_local_mode": false,
      "devices": [
        {
          "device_id": 60526,
          "serial_number": "ST-00012345",
          "device_type": "ST",
          "hardware_revision": "3",
          "firmware_revision": "165",
          "device_meta": { "agl": 2.2, "name": "Backyard", "environment": "outdoor" },
          "device_settings": { "show_precip_final": false },
          "notes": ""
        }
      ],
      "station_items": [ { "item": "air_temperature_humidity", "device_id": 60526, "sort": 0 } ]
    }
  ]
}
```

`device_type` values: `HB` (hub — has **no** observation data),
`ST` (Tempest all-in-one), `AR` (Air sensor), `SK` (Sky sensor). The OpenAPI
enum lists exactly these four. Note that `AR`/`SK` are metadata codes for the
Air/Sky hardware; the observation `type` discriminator for the same hardware is
`obs_air`/`obs_sky`. Always filter `HB` out before auto-selecting a device for
observation calls — the hub has no `/observations/device/{id}` data. A null or
missing `serial_number` on a device means inactive hardware per the legacy docs.

### GET /stations/{station_id} — one station

Same Station model; documented responses are 200 and 404 ("Station not found").
Per the legacy Swagger the body still arrives in the `{stations: [...]}`-style
wrapper shape with the selected station inside, so unwrap defensively rather
than assuming a bare station object.

### GET /observations/device/{device_id} — device observations

Query parameters (mutually exclusive modes):

| Parameter | Meaning |
|---|---|
| `day_offset` | Whole UTC day: `0` = current UTC day, `1` = yesterday UTC |
| `time_start` + `time_end` | UTC epoch-seconds range; one-minute resolution guaranteed for ranges ≤ 5 days |
| `latest=true` | Latest single observation (the CLI's `current` default) |
| `format=csv` | CSV instead of JSON |

Response is an observation set: `obs` (array of positional arrays, oldest to
newest), `type` (`obs_st` | `obs_air` | `obs_sky` — the layout discriminator),
plus device identity/status fields. Field layouts are in
observation-layouts.md. Documented errors: 404 "Device not found". Passing a
hub `HB` device id yields no observation data.

### GET /observations/stn/{station_id} — station observations

Note the segment is **`stn`**, not `stations`. Optional parameters:
`time_start`/`time_end`, `bucket` (`1` | `5` | `30` | `180` minutes; mapped to
1 day / 5 days / 30 days / 180 days of history, and the docs mention `1440` ≈ 4
years), `ob_fields` selection, and the standard unit parameters. Station
observations are **federated from the station's designated primary sensors**;
device observations are one physical device's raw data. Use station
observations when you want "the station's" reading, device observations when
you care about a specific unit.

### GET /better_forecast — conditions + daily + hourly

Parameters: `station_id` (or `lat`/`lon` with optional
`snap_to_nearest_owned_station=true` for within-5 km snapping), plus unit
overrides: `units_temp` (`c`|`f`), `units_wind` (`mph`|`kph`|`kts`|`mps`|`bft`|
`lfm`), `units_pressure` (`mb`|`inhg`|`mmhg`|`hpa`), `units_precip`
(`mm`|`cm`|`in`), `units_distance` (`km`|`mi`).

Response top level:

```json
{
  "status": { "status_code": 0, "status_message": "SUCCESS" },
  "current_conditions": { "air_temperature": 18.2, "conditions": "Mostly Clear", "icon": "partly-cloudy-day", "relative_humidity": 61, "station_pressure": 1015.4, "wind_avg": 2.1, "wind_direction": 225, "feels_like": 18.2 },
  "forecast": {
    "daily": [ { "day_start_local": 1778385600, "air_temp_high": 25.4, "air_temp_low": 15.1, "conditions": "Partly cloudy", "precip_probability": 10, "precip_type": "rain", "sunrise": 1778378400, "sunset": 1778425200 } ],
    "hourly": [ { "time": 1778388000, "local_hour": 10, "local_day": 10, "air_temperature": 19.8, "precip_probability": 5, "conditions": "Sunny" } ]
  },
  "units": { "units_temp": "c", "units_wind": "mps", "units_precip": "mm", "units_pressure": "mb", "units_distance": "km" },
  "latitude": 42.37, "longitude": -71.06,
  "timezone": "America/New_York", "timezone_offset_minutes": -300
}
```

The critical structural fact: **daily and hourly live under the `forecast`
wrapper key**, not at top level. Reading `data["daily"]` returns nothing.

Unit behavior: the response honors the requested units and reports what it used
in `units`. Default is Celsius/m/s/mm/mb, but the endpoint is **unit-selectable
— not Celsius-locked**. `units_temp=f` is documented and honored. Any consumer
that hard-codes Celsius conversion must first read `units.units_temp`, or it
will double-convert Fahrenheit responses (see units-and-conversions.md).

Timestamps: `day_start_local`, `sunrise`, `sunset`, and hourly `time` are
integer epoch seconds. Hourly objects carry `local_hour` (int 0–23) and
`local_day` (int day-of-month); there is **no** `local_time` or `time_string`
field — code expecting one silently falls back to its default branch.

### Other documented endpoints

- `GET /diagnostics/{station_id}` — latest station status; 200/401/404.
- `GET /stats/station/{station_id}` — daily/weekly/monthly/annual/all-time
  high-low-average statistics; 200/401.
- `GET /metadata/network/stations` and `GET /observations/network/stations` —
  network-wide access governed by the remote data policy (not part of the
  personal single-station flow).
- Lightning endpoints exist but documented access is for paid subscribers.
- The current docs index does not document `/user/devices` for the consumer
  surface — use `/stations` and its nested `devices` array. There is no
  `/better_forecast/hourly` route; hourly data is `forecast.hourly` inside the
  standard `/better_forecast` response.

## Error signatures

| Status | Documented meaning | Practical symptom |
|---|---|---|
| 401 | Unauthorized (documented on forecast/diagnostics/stats) | Missing, revoked, or mistyped token — regenerate at tempestwx.com Settings → Data Authorizations |
| 403 | Not documented for this API | Treat as access-denied to that station/device; verify the token belongs to the station owner |
| 404 | "Station not found" / "Device not found" (documented) | Wrong station/device id, or an `HB` hub id passed to an observation endpoint |

No JSON error-body schema is published, so parse defensively. No numeric rate
limit or 429 behavior is documented; the policy only promises personal-use
volume is acceptable. The CLI maps 401/403/404 to targeted messages and dumps
the response body for anything else.

## Worked recipes

### Recipe A: stations → pick sensor → latest observation

```bash
# 1. List stations (StationSet wrapper)
curl -s "https://swd.weatherflow.com/swd/rest/stations?token=$TEMPEST_TOKEN"
# 2. Choose a device: devices[].device_type must not be "HB"; prefer ST
# 3. Latest observation for that device
curl -s "https://swd.weatherflow.com/swd/rest/observations/device/$DEVICE_ID?token=$TEMPEST_TOKEN"
```

The observation response's `type` field selects the positional layout
(`obs_st`: temperature is index 7, epoch is index 0). One command does all
three steps: `tempest current --json`.

### Recipe B: station forecast with explicit units

```bash
curl -s "https://swd.weatherflow.com/swd/rest/better_forecast?station_id=$STATION_ID&units_temp=c&units_wind=mps&units_pressure=mb&units_precip=mm&token=$TEMPEST_TOKEN" \
  | jq '{current: .current_conditions.air_temperature,
         days: [.forecast.daily[] | {day_start_local, air_temp_high, air_temp_low}],
         units: .units.units_temp}'
```

Read `units` instead of assuming units. Extract daily/hourly from
`.forecast.daily` / `.forecast.hourly`.

### Recipe C: a UTC day of device history

```bash
# day_offset=1 is yesterday UTC; day_offset=0 is today
curl -s "https://swd.weatherflow.com/swd/rest/observations/device/$DEVICE_ID?day_offset=1&token=$TEMPEST_TOKEN" \
  | jq '{type, count: (.obs | length), first: .obs[0], last: .obs[-1]}'
```

For a custom range, send both `time_start` and `time_end` as epoch seconds and
keep the span ≤ 5 days to guarantee one-minute resolution. Do not mix
`day_offset` with `time_start`/`time_end` in one call.

## Sources

- https://apidocs.tempestwx.com/reference/quick-start (auth flows, REST examples, primary-source guidance)
- https://apidocs.tempestwx.com/reference/oauth (OAuth 2.0 grant types, app registration)
- https://apidocs.tempestwx.com/reference/get_stations (StationSet/Station/Device OpenAPI schemas)
- https://apidocs.tempestwx.com/reference/getstationbyid-1 (single station, 404 semantics)
- https://apidocs.tempestwx.com/reference/getobservationsbydeviceid (device observation parameters, 404)
- https://apidocs.tempestwx.com/reference/get_observations-stn-station-id (station observations, bucket)
- https://apidocs.tempestwx.com/reference/station-vs-device (device vs station observation semantics)
- https://apidocs.tempestwx.com/reference/get_better-forecast-1 (forecast parameters, unit selection)
- https://apidocs.tempestwx.com/reference/get_diagnostics-station-id-1 (diagnostics endpoint)
- https://apidocs.tempestwx.com/reference/get_stats-station-station-id-1 (stats endpoint)
- https://apidocs.tempestwx.com/reference/observation-record-format (type discriminators, record lengths)
- https://apidocs.tempestwx.com/reference/tempest-udp-broadcast (UDP as backup to REST)
- https://weatherflow.github.io/Tempest/api/swagger/ (legacy response models: forecast nesting, obs_sky null day-rain)
- https://weatherflow.github.io/Tempest/api/remote-developer-policy.html (personal-use policy, rate/volume limits)
