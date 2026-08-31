# Tempest UDP Broadcast Protocol (Port 50222)

The Tempest hub broadcasts JSON messages to the local network on **UDP port
50222**. A listener on the same LAN receives every message the hub publishes:
observations, rapid wind updates, precipitation and lightning events, and
hub/device status. No subscription, pairing, or token is involved — the hub
broadcasts regardless; point a listener at port 50222 and read.

Positioning per WeatherFlow: REST/WebSocket are the primary data interfaces,
and the UDP broadcast is officially recommended for completely off-grid
applications or as a backup. It is nevertheless the lowest-latency feed on
your LAN (rapid wind arrives every ~3 seconds; hub status roughly once a
minute).

## Transport facts

- **Port:** 50222, UDP, local broadcast. Routed/internet reachability is not
  enough — the listener must share the hub's L2 network (same subnet/VLAN, or
  a DHCP/helper forwarding broadcasts).
- **Direction:** the hub sends, listeners receive. The protocol defines no
  acknowledgement or response message; treat it as listen-only. Bind to
  `0.0.0.0:50222` with `SO_REUSEADDR` and read datagrams.
- **Framing:** each UDP datagram carries one complete JSON message (UTF-8).
  Never concatenate datagrams or expect TCP-style stream framing. (UTF-8 and
  one-JSON-per-datagram are the interoperable reading of the protocol's JSON
  examples; the official pages do not spell the encoding out.)
- **No auth:** the broadcast carries no token and cannot be restricted from
  the hub; anyone on the LAN can read your station's data. This is why the
  broadcast is LAN-only.

## THE dispatch rule: message families are structurally different

Every message carries a top-level `"type"`. The payload key and array shape
**change with the type** — a parser that blindly indexes a position will
crash or misread. Dispatch on `type` BEFORE indexing:

| `type` | Payload key | Payload shape |
|---|---|---|
| `obs_st`, `obs_air`, `obs_sky` | `obs` | list containing observation arrays (one per report): `msg["obs"][0][7]` |
| `rapid_wind` | `ob` | ONE 3-element array: `msg["ob"][1]` is wind speed |
| `evt_precip` | `evt` | ONE 1-element array: `msg["evt"][0]` is epoch |
| `evt_strike` | `evt` | ONE 3-element array: epoch, distance km, energy |
| `hub_status` | (named fields) | no payload array: `uptime`, `rssi`, `seq`, `fs`, `radio_stats`, `mqtt_stats` |
| `device_status` | (named fields) | no payload array: `uptime`, `voltage`, `rssi`, `hub_rssi`, `sensor_status` |

The observation families nest arrays inside a list; `rapid_wind` and the
events carry a single array under a *different key* (`ob` / `evt`); the
status families carry named scalar fields and small status arrays. Iterating
`rapid_wind`'s `ob` array element-wise the way you would `obs` rows is a
classic crash (TypeError on the epoch number) — this is exactly the trap the
dispatch rule exists for.

## obs_st — Tempest all-in-one observation (UDP form)

Broadcast roughly once per report interval (default 1 minute). The UDP
datagram carries **18 positions (indices 0–17)**:

```json
{
  "serial_number": "ST-00000512",
  "type": "obs_st",
  "hub_sn": "HB-00013030",
  "obs": [[1588948614, 0.18, 0.22, 0.27, 144, 6, 1017.57, 22.37, 50.26, 328, 0.03, 3, 0.000000, 0, 0, 0, 2.410, 1]],
  "firmware_revision": 129
}
```

| Index | Field | Units |
|---:|---|---|
| 0 | timestamp | epoch seconds, UTC |
| 1 | wind lull (min 3-second sample) | m/s |
| 2 | wind average | m/s |
| 3 | wind gust (max 3-second sample) | m/s |
| 4 | wind direction | degrees (0 = N) |
| 5 | wind sample interval | seconds |
| 6 | station pressure | MB (millibars; numerically identical to hPa) |
| 7 | air temperature | °C |
| 8 | relative humidity | % |
| 9 | illuminance | lux |
| 10 | UV | index |
| 11 | solar radiation | W/m² |
| 12 | rain accumulation over previous minute | mm |
| 13 | precipitation type | 0 none, 1 rain, 2 hail, 3 rain + hail (experimental) |
| 14 | lightning strike average distance | km |
| 15 | lightning strike count | count |
| 16 | battery | volts (≈2.4 nominal; low below ≈2.3) |
| 17 | report interval | minutes |

**UDP vs REST length:** the REST observation record extends the same array
with four Nearcast/analysis fields — index 18 local-day rain accumulation
(mm), 19 Nearcast rain accumulation (mm), 20 local-day Nearcast rain
accumulation (mm), 21 precipitation analysis type (0 none, 1 Nearcast display
on, 2 off) — for 22 positions total. The UDP broadcast stops at 17. A decoder
must tolerate both lengths (the bundled `decode_obs` does) and never assume
the extra fields exist over UDP.

## rapid_wind — 3-second wind snapshot

Broadcast every ~3 seconds between observation reports. Layout differs from
obs_st: payload key is `ob`, a single 3-element array (speed is already
m/s — no conversion on the wire, only when displaying mph):

```json
{
  "serial_number": "SK-00008453",
  "type": "rapid_wind",
  "hub_sn": "HB-00000001",
  "ob": [1493322445, 2.3, 128]
}
```

| Index | Field | Units |
|---:|---|---|
| 0 | timestamp | epoch seconds, UTC |
| 1 | wind speed | m/s |
| 2 | wind direction | degrees |

## evt_precip — rain-start event

Fires when the haptic rain sensor detects the start of rainfall (more than
five seconds of continuous rain). Payload key `evt`, one element:

```json
{
  "serial_number": "SK-00008453",
  "type": "evt_precip",
  "hub_sn": "HB-00000001",
  "evt": [1493322445]
}
```

| Index | Field | Units |
|---:|---|---|
| 0 | timestamp | epoch seconds, UTC |

## evt_strike — lightning strike event

Payload key `evt`, three elements. The energy unit is not specified in the
official reference:

```json
{
  "serial_number": "AR-00004049",
  "type": "evt_strike",
  "hub_sn": "HB-00000001",
  "evt": [1493322445, 27, 3848]
}
```

| Index | Field | Units |
|---:|---|---|
| 0 | timestamp | epoch seconds, UTC |
| 1 | distance | km |
| 2 | energy | undocumented unit |

## hub_status — hub heartbeat (roughly once a minute)

**No payload array at all** — named scalar fields plus small status arrays.
Note `firmware_revision` arrives as a string here (number in observation
messages):

```json
{
  "serial_number": "HB-00000001",
  "type": "hub_status",
  "firmware_revision": "35",
  "uptime": 1670133,
  "rssi": -62,
  "timestamp": 1495724691,
  "reset_flags": "BOR,PIN,POR",
  "seq": 48,
  "fs": [1, 0, 15675411, 524288],
  "radio_stats": [2, 1, 0, 3, 2839],
  "mqtt_stats": [1, 0]
}
```

- `uptime` (s), `rssi` (dBm; closer to 0 is stronger), `timestamp` (epoch
  seconds), `seq` (monotonic message counter — gaps mean lost datagrams).
- `reset_flags`: comma-separated reset causes — BOR, PIN, POR, SFT, WDG,
  WWD, LPW, HRDFLT. Repeated watchdog flags suggest power trouble.
- `radio_stats`: [version, reboot count, I2C bus error count, radio status,
  radio network ID]; radio status 0 = off, 1 = on, 3 = active, 7 = BLE
  connected.
- `fs` and `mqtt_stats` are documented as internal use.
- There is no `freq` or `fs_version` field in the current protocol (both
  appear in old integration notes; do not read them — they are always
  `None`).

## device_status — sensor device health (roughly once a minute)

Also named fields, no payload array:

```json
{
  "serial_number": "AR-00004049",
  "type": "device_status",
  "hub_sn": "HB-00000001",
  "timestamp": 1510855923,
  "uptime": 2189,
  "voltage": 3.50,
  "firmware_revision": 17,
  "rssi": -17,
  "hub_rssi": -87,
  "sensor_status": 0,
  "debug": 0
}
```

`sensor_status` is a decimal **bit flag** field: bits indicate lightning
failed / noise / disturber, pressure failed, temperature failed, humidity
failed, wind failed, precipitation failed, light/UV failed, plus power-booster
flags. `0` means all sensors healthy. Unknown high bits are reserved — ignore
them rather than erroring.

## Legacy sensors: obs_air and obs_sky

Older Air/Sky hardware still broadcasts with the same envelope:

**obs_air** (`obs` list, 8 positions): 0 epoch · 1 pressure MB · 2 air temp °C
· 3 relative humidity % · 4 lightning strike count · 5 lightning average
distance km · 6 battery volts · 7 report interval minutes.

```json
{"serial_number": "AR-00004049", "type": "obs_air", "hub_sn": "HB-00000001",
 "obs": [[1493164835, 835.0, 10.0, 45, 0, 0, 3.46, 1]], "firmware_revision": 17}
```

**obs_sky** (`obs` list, 14 positions): 0 epoch · 1 illuminance lux · 2 UV ·
3 rain mm · 4 wind lull m/s · 5 wind avg m/s · 6 wind gust m/s · 7 wind
direction deg · 8 battery volts · 9 report interval min · 10 solar radiation
W/m² · 11 local-day rain mm (**always null over UDP** — REST provides it) ·
12 precipitation type · 13 wind sample interval s.

```json
{"serial_number": "SK-00008453", "type": "obs_sky", "hub_sn": "HB-00000001",
 "obs": [[1493321340, 9000, 10, 0.0, 2.6, 4.6, 7.4, 187, 3.12, 1, 130, null, 0, 3]],
 "firmware_revision": 29}
```

## Units are metric-native — conversion is the caller's job

Every value on the wire is metric: wind **m/s**, rain **mm**, temperature
**°C**, pressure **MB** (≡ hPa — NOT kPa), distance **km**, illuminance
**lux**, solar radiation **W/m²**, battery **volts**. The UDP protocol ships
no unit-selection and no conversion tables; imperial output is entirely your
code's job. The bundled CLI converts for human display and leaves `--json`
values in the metric-native wire units. Station pressure (raw sensor) is not
sea-level pressure — the Tempest app's "relative pressure" applies an
elevation adjustment you must compute separately if you want it.

## Minimal listener

```bash
# See the raw firehose before writing any code:
tempest udp listen --timeout 30            # decodes families, hides hub_status
tempest udp listen --timeout 30 --show-all # include hub_status and unknown types
```

```python
# Zero-dependency decoder skeleton — dispatch on type, then index.
import json, socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("0.0.0.0", 50222))

while True:
    msg = json.loads(sock.recvfrom(65535)[0].decode("utf-8", errors="replace"))
    t = msg.get("type")
    if t in ("obs_st", "obs_air", "obs_sky"):
        row = msg["obs"][-1]           # list of report rows
    elif t == "rapid_wind":
        row = msg["ob"]                # ONE array: [epoch, m/s, degrees]
    elif t in ("evt_precip", "evt_strike"):
        row = msg["evt"]               # ONE array: [epoch] / [epoch, km, energy]
    elif t in ("hub_status", "device_status"):
        continue                       # named fields, nothing to index
    else:
        continue                       # unknown type: skip, don't crash
    print(t, msg.get("serial_number"), row[0])
```

The bundled CLI implements this dispatch in `udp_listen` (see
`scripts/tempest`) with per-family decoders and `--json` output.

## Sources

- https://weatherflow.github.io/Tempest/api/udp/v171/ (current UDP protocol reference: all message families, layouts, examples)
- https://weatherflow.github.io/Tempest/api/udp/v143/ (prior protocol revision; family set unchanged)
- https://apidocs.tempestwx.com/reference/tempest-udp-broadcast (UDP documented as backup to REST/WebSocket)
- https://apidocs.tempestwx.com/reference/observation-record-format (REST obs_st Nearcast fields 18–21; evt_strike and rapid_wind record tables)
- https://apidocs.tempestwx.com/reference/quick-start (UDP positioned as backup; REST primary guidance)
- https://help.weatherflow.com/hc/en-us/articles/360052101413-Tempest-FAQs (haptic rain-start behavior, RSSI interpretation, station vs sea-level pressure)
