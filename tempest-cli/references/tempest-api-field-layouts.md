# Tempest API Field Layouts

Quick reference for the obs_st (Tempest all-in-one) observation array layout.
The API returns observations as positional arrays — these index maps are
required for any CLI or script that reads raw observation data.

## obs_st (Tempest Device)

| Index | Field | Units | Notes |
|-------|-------|-------|-------|
| 0 | epoch | seconds UTC | |
| 1 | wind_lull | m/s | Minimum 3-second sample |
| 2 | wind_avg | m/s | Average over report interval |
| 3 | wind_gust | m/s | Maximum 3-second sample |
| 4 | wind_direction | degrees | 0-360 |
| 5 | wind_sample_interval | seconds | |
| 6 | station_pressure | MB | |
| 7 | air_temperature | C | |
| 8 | relative_humidity | % | |
| 9 | illuminance | lux | |
| 10 | uv | index | |
| 11 | solar_radiation | W/m² | |
| 12 | rain_accumulation | mm | Over last report interval |
| 13 | precipitation_type | 0=none 1=rain 2=hail | |
| 14 | avg_strike_distance | km | |
| 15 | strike_count | count | |
| 16 | battery | volts | |
| 17 | report_interval | minutes | |
| 18 | local_day_rain_accumulation | mm | |
| 19 | nc_rain_accumulation | mm | |
| 20 | local_day_nc_rain_accumulation | mm | |
| 21 | precip_analysis_type | enum | 0=none, 1=RainCheck display on, 2=off |

## obs_air (Air Sensor)

| Index | Field | Units |
|-------|-------|-------|
| 0 | epoch | seconds UTC |
| 1 | station_pressure | MB |
| 2 | air_temperature | C |
| 3 | relative_humidity | % |
| 4 | lightning_strike_count | count |
| 5 | lightning_avg_distance | km |
| 6 | battery | volts |
| 7 | report_interval | minutes |

## obs_sky (Sky Sensor)

| Index | Field | Units | Notes |
|-------|-------|-------|-------|
| 0 | epoch | seconds UTC | |
| 1 | illuminance | lux | |
| 2 | uv | index | |
| 3 | rain_accumulation | mm | |
| 4 | wind_lull | m/s | |
| 5 | wind_avg | m/s | |
| 6 | wind_gust | m/s | |
| 7 | wind_direction | degrees | |
| 8 | battery | volts | |
| 9 | report_interval | minutes | |
| 10 | solar_radiation | W/m² | |
| 11 | local_day_rain_accumulation | mm | |
| 12 | precipitation_type | 0=none 1=rain 2=hail | |
| 13 | wind_sample_interval | seconds | |
| 14 | nc_rain | mm | |
| 15 | local_day_nc_rain | mm | |
| 16 | precip_analysis_type | 0=none 1=RainCheck on 2=off | |

## API Response Quirks

### better_forecast nesting
The `daily` and `hourly` arrays live under a `forecast` wrapper key, NOT at the
top level of the response. If reading from the raw API:

```python
# Wrong (assumes top-level):
days = data.get("daily", [])       # returns []

# Right (respects nesting):
fc = data.get("forecast", {})
days = fc.get("daily", [])
hours = fc.get("hourly", [])
```

The top-level keys of `/better_forecast` are:
- `current_conditions` — dict with air_temperature, conditions, icon, etc.
- `forecast` — dict containing `daily` (list) and `hourly` (list)
- `station` — metadata (elevation, agl, station_id)
- `units` — unit system for the response
- `status` — status_code, status_message
- `timezone`, `timezone_offset_minutes`, `latitude`, `longitude`, `location_name`

### Device types in /stations
Devices within a station have a `device_type` field. Known values:
- `HB` — Hub (cannot query observations — no `/observations/device/{id}` endpoint)
- `ST` — Tempest all-in-one (preferred sensor)
- `SKY` — Sky sensor
- `AIR` — Air sensor

Always filter out HB devices before auto-selecting a device for observation queries.

### Auth
Token is passed as query parameter: `?token=XXX`
No header-based auth for the swd.weatherflow.com REST API.
Personal access tokens generated at https://weatherflow.com (account → API Tokens).

### Units
Raw observations use metric (C, m/s, MB, mm).
The `better_forecast` endpoint returns unit-converted values based on station
preferences. The `units` key in the response documents which units are in use.
All temperature values are in **Celsius** regardless of station preference — CLI
must convert to °F if displaying imperial. Unit labels from the API are authority.

### Field type traps in better_forecast

The forecast endpoint uses epoch integers where you'd expect date strings, and
field names that differ from what common sense suggests:

| Field | Actual type | Common mistake | Fix |
|-------|-----------|---------------|-----|
| `daily[].day_start_local` | epoch int (e.g. 1778385600) | Assumed ISO string "2026-05-10T..." | `datetime.fromtimestamp(ts).strftime(...)` |
| `hourly[].local_hour` | int (e.g. 10) | Assumed ISO timestamp string | Use directly as `{h:02d}:00` |
| `hourly[].local_day` | int (e.g. 10 for the 10th) | N/A | Use alongside `local_hour` for time-of-day |
| `hourly[].local_time` | **does not exist** | Commonly assumed field | Use `local_hour` instead |

The hourly objects do NOT have a `local_time` or `time_string` field — just
`time` (epoch int), `local_day` (int), and `local_hour` (int, 0-23). Any code
looking for `local_time` will silently fall back to its default/"?" branch.
