# Observation Layouts and Units (obs_st, obs_air, obs_sky)

Observations arrive as **positional arrays**: a list of values whose meaning
depends on the array index. The `type` field on the containing object selects
the layout (`obs_st` = Tempest all-in-one, `obs_air` = Air, `obs_sky` = Sky).
There are no field names on the wire — any decoder is a table like the ones
below, and reading the wrong index silently yields a wrong value (e.g.
treating index 6 pressure as index 7 temperature).

Two different record lengths exist for obs_st: REST returns **22 positions**
and the UDP broadcast returns **18** (the four Nearcast/analysis fields are
REST-only). obs_air is 8 positions in both transports; obs_sky is 17 over
REST and 14 over UDP.

## obs_st — Tempest all-in-one (REST record, 22 positions)

| Index | Field | Units | Notes |
|---:|---|---|---|
| 0 | timestamp | epoch seconds, UTC | |
| 1 | wind lull | m/s | minimum 3-second sample |
| 2 | wind average | m/s | average over report interval |
| 3 | wind gust | m/s | maximum 3-second sample |
| 4 | wind direction | degrees | 0 = N |
| 5 | wind sample interval | seconds | |
| 6 | station pressure | MB (millibars) | ≡ hPa; raw sensor pressure, not sea-level |
| 7 | air temperature | °C | |
| 8 | relative humidity | % | |
| 9 | illuminance | lux | |
| 10 | UV | index | |
| 11 | solar radiation | W/m² | |
| 12 | rain accumulation | mm | during the reporting interval |
| 13 | precipitation type | enum | 0 none, 1 rain, 2 hail, 3 rain + hail (experimental) |
| 14 | lightning strike average distance | km | |
| 15 | lightning strike count | count | during the reporting interval |
| 16 | battery | volts | ≈2.4 nominal; below ≈2.3 plan service |
| 17 | report interval | minutes | |
| 18 | local day rain accumulation | mm | midnight-to-midnight, station timezone |
| 19 | Nearcast rain accumulation | mm | REST only |
| 20 | local day Nearcast rain accumulation | mm | REST only |
| 21 | precipitation analysis type | enum | 0 none, 1 Nearcast display on, 2 off — REST only |

UDP `obs_st` datagrams end at index 17 (see udp-broadcast-protocol.md).

## obs_air — Air sensor (8 positions, both transports)

| Index | Field | Units | Notes |
|---:|---|---|---|
| 0 | timestamp | epoch seconds, UTC | |
| 1 | station pressure | MB (millibars) | ≡ hPa |
| 2 | air temperature | °C | |
| 3 | relative humidity | % | |
| 4 | lightning strike count | count | during the reporting interval |
| 5 | lightning strike average distance | km | |
| 6 | battery | volts | |
| 7 | report interval | minutes | |

## obs_sky — Sky sensor (REST record, 17 positions)

| Index | Field | Units | Notes |
|---:|---|---|---|
| 0 | timestamp | epoch seconds, UTC | |
| 1 | illuminance | lux | |
| 2 | UV | index | |
| 3 | rain accumulation | mm | during the reporting interval |
| 4 | wind lull | m/s | |
| 5 | wind average | m/s | |
| 6 | wind gust | m/s | |
| 7 | wind direction | degrees | |
| 8 | battery | volts | |
| 9 | report interval | minutes | |
| 10 | solar radiation | W/m² | |
| 11 | local day rain accumulation | mm | **always null over UDP** — REST supplies it |
| 12 | precipitation type | enum | 0 none, 1 rain, 2 hail, 3 rain + hail |
| 13 | wind sample interval | seconds | |
| 14 | Nearcast rain accumulation | mm | REST only |
| 15 | local day Nearcast rain accumulation | mm | REST only |
| 16 | precipitation analysis type | enum | 0 none, 1 Nearcast display on, 2 off — REST only |

UDP `obs_sky` datagrams end at index 13 and always carry `null` at index 11.

## Daily summary records (obs_*_ext)

The API also emits midnight-to-midnight daily summaries with their own
discriminators: `obs_st_ext` (34 positions — avg/high/low pressure,
temperature, humidity, illuminance, UV, solar, wind stats, strikes, battery,
day rain, precipitation minutes), `obs_air_ext` (14), and `obs_sky_ext` (22).
They appear in stats/history contexts, not in the minute firehose. Decode
them only from their own `type` — never with the minute-record tables.

## The units story: metric-native, caller converts

Every raw value is metric: wind **m/s**, rain **mm**, temperature **°C**,
pressure **MB** (millibars — numerically identical to hPa, *not* kPa),
distance **km**, illuminance **lux**, solar radiation **W/m²**, battery
**volts**. Nothing on the wire is imperial; conversions are the consumer's
job:

| Wire unit | Imperial | Formula |
|---|---|---|
| °C | °F | `c * 9/5 + 32` |
| m/s | mph | `mps * 2.23694` (≈ ×2.237) |
| m/s | km/h | `mps * 3.6` |
| m/s | knots | `mps * 1.94384` |
| MB (hPa) | inHg | `mb * 0.02953` |
| mm | inches | `mm / 25.4` |
| km | miles | `km / 1.60934` |

Two traps:

1. **`/better_forecast` is unit-selectable, not Celsius-locked.** It defaults
   to metric (`units_temp=c`), honors overrides (`units_temp=f`,
   `units_wind=mph`, `units_pressure=inhg`, `units_precip=in`,
   `units_distance=mi`), and reports what it used in `response.units`. Read
   `units` before converting anything, or a Fahrenheit response gets
   double-converted into absurd values.
2. **Station vs sea-level pressure.** Index 6 / index 1 pressure is the raw
   station pressure. The Tempest app's "relative pressure" adds an elevation
   adjustment — don't compare your raw value against the app and conclude the
   sensor is broken.

The bundled CLI keeps `--json` output in metric-native wire units (raw,
lossless — convert with your own jq) and converts only in human display.
Decode positionally with jq like:

```bash
tempest current --json \
  | jq '{temp_c: .observation.air_temperature,
         temp_f: (.observation.air_temperature * 9 / 5 + 32),
         wind_mps: .observation.wind_avg,
         wind_mph: (.observation.wind_avg * 2.237),
         pressure_mb: .observation.station_pressure}'
```

## Field type traps in /better_forecast

The forecast endpoint uses epoch integers where you'd expect date strings,
and field names that differ from what common sense suggests:

| Field | Actual type | Common mistake | Fix |
|---|---|---|---|
| `daily[].day_start_local` | epoch int (e.g. 1778385600) | assumed ISO string | `datetime.fromtimestamp(ts).strftime(...)` |
| `hourly[].local_hour` | int (0–23) | assumed timestamp string | format directly `{h:02d}:00` |
| `hourly[].local_day` | int (day of month) | N/A | use alongside `local_hour` |
| `hourly[].local_time` | **does not exist** | commonly assumed field | use `local_hour` instead |

Code looking for `local_time` silently falls back to its default/"?" branch —
no error is raised.

## Decoding recipe (jq, no script needed)

Latest REST observation, positionally decoded to named fields:

```bash
curl -s "https://swd.weatherflow.com/swd/rest/observations/device/$DEVICE_ID?token=$TEMPEST_TOKEN" \
  | jq --argjson layout '["timestamp","wind_lull","wind_avg","wind_gust","wind_direction",
      "wind_sample_interval","station_pressure","air_temperature","relative_humidity",
      "illuminance","uv","solar_radiation","rain_accumulation","precipitation_type",
      "avg_strike_distance","strike_count","battery","report_interval",
      "local_day_rain","nc_rain","local_day_nc_rain","precip_analysis_type"]' '
      {type: .type,
       obs: (.obs[-1] | [$layout, .] | transpose | map({(.[0]): .[1]}) | add)}'
```

The bundled CLI does the same in Python (`decode_obs` in `scripts/tempest`,
driven by the `OBS_ST_FIELDS`/`OBS_AIR_FIELDS`/`OBS_SKY_FIELDS` tables) and
tolerates both UDP-length and REST-length rows.

## Sources

- https://apidocs.tempestwx.com/reference/observation-record-format (canonical index tables: obs_st 22, obs_air 8, obs_sky 17, daily _ext records, evt_strike, rapid_wind)
- https://weatherflow.github.io/Tempest/api/swagger/ (legacy response models; better_forecast field types; obs_sky UDP day-rain null note)
- https://weatherflow.github.io/Tempest/api/udp/v171/ (UDP obs_st 18-position record; metric-native units)
- https://apidocs.tempestwx.com/reference/get_better-forecast-1 (unit selection parameters and response `units` object)
- https://apidocs.tempestwx.com/reference/getobservationsbydeviceid (observation set envelope: `obs` array + `type` discriminator)
- https://help.weatherflow.com/hc/en-us/articles/360052101413-Tempest-FAQs (station vs sea-level pressure; battery guidance)
