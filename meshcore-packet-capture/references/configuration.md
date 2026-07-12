# Configuration reference

Source basis: `agessaman/meshcore-packet-capture` commit `1d69230fbd2959412f77788a430c91e1b11cd765`, release `v2.0.0`, inspected 2026-07-11. Re-check upstream before relying on version-sensitive details.

## TOML layout

The primary file is `/etc/meshcore-packet-capture/config.toml`. Sorted `config.d/*.toml` files are applied afterward. The installer puts presets in `config.d/10-*.toml`; put local changes in `config.d/99-user.toml`.

```toml
[general]
iata = "SEA"
log_level = "INFO"

[topics]
status = "meshcore/{IATA}/{PUBLIC_KEY}/status"
packets = "meshcore/{IATA}/{PUBLIC_KEY}/packets"
# raw = "meshcore/{IATA}/{PUBLIC_KEY}/raw"

[capture]
connection_type = "ble"       # ble, serial, tcp
timeout = 30
data_dir = "/var/lib/meshcore-packet-capture/data"
max_connection_retries = 5    # 0 means infinite
connection_retry_delay = 5
health_check_interval = 30
advert_interval_hours = 47     # 0 disables periodic adverts

[serial]
ports = ["/dev/ttyUSB0"]
baud_rate = 115200
timeout = 2

[[broker]]
name = "home"
enabled = true
server = "mqtt.example.com"
port = 1883
transport = "tcp"
keepalive = 60
qos = 0
retain = false

[broker.auth]
method = "password"            # password, token, or none
username = "user"
password = "secret"

[broker.tls]
enabled = false
verify = true

[broker.topics]
packets = "custom/{IATA}/{PUBLIC_KEY}/packets"
```

`[capture]` also accepts `tcp_host`, `tcp_port`, `ble_address`, `ble_device_name`, `origin`, `private_key`, `private_key_file`, retry/backoff controls, stats controls, `drain_messages`, TCP keepalive controls, `upload_packet_types`, `exit_on_reconnect_fail`, and binary-interface controls. `config.toml.example` in the upstream repository is the authoritative complete list.

## Precedence and merging

Runtime precedence is:

1. Variables already present in the process environment.
2. Explicit `--config PATH` files, in argument order, or the default `/etc/.../config.toml` plus sorted `config.d/*.toml`.
3. `.env.local`, then `.env`.

There is an important implementation detail: the application snapshots the real process environment before reading dotenv files. TOML may replace a value sourced only from `.env`, but never replaces a real process variable.

TOML dictionaries deep-merge. Broker arrays merge by non-empty `name`; a same-named broker is deep-merged, and a new broker is appended. Disabled brokers are omitted when flattening to MQTT slots. Because the runtime discovers slots sequentially, keep enabled broker entries contiguous as `MQTT1`, `MQTT2`, and so on.

## Environment names

Every flat runtime setting uses the `PACKETCAPTURE_` prefix:

- Connection: `PACKETCAPTURE_CONNECTION_TYPE`, `PACKETCAPTURE_BLE_ADDRESS`, `PACKETCAPTURE_BLE_DEVICE_NAME`, `PACKETCAPTURE_SERIAL_PORTS`, `PACKETCAPTURE_TCP_HOST`, `PACKETCAPTURE_TCP_PORT`.
- Runtime: `PACKETCAPTURE_TIMEOUT`, `PACKETCAPTURE_MAX_CONNECTION_RETRIES`, `PACKETCAPTURE_CONNECTION_RETRY_DELAY`, `PACKETCAPTURE_HEALTH_CHECK_INTERVAL`, `PACKETCAPTURE_DRAIN_MESSAGES`, `PACKETCAPTURE_STATS_IN_STATUS_ENABLED`, `PACKETCAPTURE_STATS_REFRESH_INTERVAL`.
- Identity/topics: `PACKETCAPTURE_IATA`, `PACKETCAPTURE_ORIGIN`, `PACKETCAPTURE_TOPIC_STATUS`, `PACKETCAPTURE_TOPIC_PACKETS`, `PACKETCAPTURE_TOPIC_DECODED`, `PACKETCAPTURE_TOPIC_DEBUG`, `PACKETCAPTURE_TOPIC_RAW`.
- Keys: `PACKETCAPTURE_PRIVATE_KEY` or `PACKETCAPTURE_PRIVATE_KEY_FILE`.

Use the TOML names when writing configuration. Use the environment names when injecting Docker or service settings.

## MQTT broker slots

For broker `n`, the environment form is `PACKETCAPTURE_MQTT<n>_*`. Common fields are `ENABLED`, `NAME`, `SERVER`, `PORT`, `TRANSPORT`, `USE_TLS`, `TLS_VERIFY`, `USERNAME`, `PASSWORD`, `USE_AUTH_TOKEN`, `TOKEN_AUDIENCE`, `TOKEN_TTL`, `TOKEN_OWNER`, `TOKEN_EMAIL`, `TOPIC_TOKEN`, `CLIENT_ID_PREFIX`, `QOS`, `RETAIN`, and `KEEPALIVE`.

Supported topic placeholders:

- `{IATA}`: uppercase IATA code
- `{IATA_lower}`: lowercase IATA code
- `{PUBLIC_KEY}`: connected radio public key
- `{TOKEN}`: broker-specific or global topic token

A broker-specific topic wins over the global topic. `RAW` has no implicit default and is skipped unless configured. If no topic is configured, an IATA-aware default is used when a non-`LOC` IATA exists; custom brokers without IATA use classic topics; LetsMesh brokers without IATA do not receive default topics.

## Authentication

Password auth:

```toml
[broker.auth]
method = "password"
username = "mqtt-user"
password = "mqtt-password"
```

Token auth:

```toml
[broker.auth]
method = "token"
audience = "mqtt.example.com"
token_ttl = 3600
# owner = "64_HEX_CHAR_PUBLIC_KEY"
# email = "owner@example.com"
```

Token generation prefers on-device signing through the connected MeshCore instance. If that fails, it can use a 64-byte MeshCore private key (128 hex characters) from configuration/environment/file, subject to device and firmware support. `AUTH_TOKEN_METHOD=python` forces Python signing; `AUTH_TOKEN_METHOD=meshcore-decoder` selects the external decoder path. Never log or paste the key.

## Packet filtering and output

`PACKETCAPTURE_UPLOAD_PACKET_TYPES` accepts comma-separated numeric packet types. Known values are `0` REQ, `1` RESPONSE, `2` TXT_MSG, `3` ACK, `4` ADVERT, `5` GRP_TXT, `6` GRP_DATA, `7` ANON_REQ, `8` PATH, `9` TRACE, `10` MULTIPART, `11` CONTROL, `15` RAW_CUSTOM. Empty/unset means all packet types are uploaded; filtering affects MQTT upload, not local capture.

`--output PATH` writes packet output. `--verbose` adds JSON to normal output. `--debug` enables detailed diagnostics. `--no-mqtt` disables publishing while leaving capture active.
