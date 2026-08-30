# Tempest — Hyper-Local Weather from Your Own Station

Query live weather from a WeatherFlow Tempest station: current conditions, 7-day forecast, historical observations, and real-time broadcasts from your hub's local network — with every positional sensor array and UDP message family decoded for you.

## Why Install This Skill

Generic weather services tell you what the model thinks the sky is doing kilometers away. This skill reads **your actual station**: the Tempest sitting in your yard, via WeatherFlow's documented REST API and the hub's local UDP broadcast. Once installed, your agent can:

- **Current conditions** — temperature, humidity, wind (lull/avg/gust + direction), rain, UV, solar radiation, barometric pressure
- **7-day forecast** — daily and hourly outlook with precipitation probabilities, unit-aware
- **Historical observations** — past UTC days of minute-level data for analysis
- **Real-time UDP stream** — decoded `obs_st`, `rapid_wind`, `evt_precip`, `evt_strike`, and `hub_status` messages straight from the hub on port 50222, no cloud round-trip
- **Station discovery** — finds your stations and sensors automatically, never mistaking the hub for a sensor

The tricky parts of the Tempest API are handled for you: observations arrive as *positional arrays* whose meaning depends on the index, UDP message families have three different payload shapes, and forecast responses are unit-selectable (a naive script double-converts Fahrenheit data into 172-degree nonsense). The CLI decodes all of it, keeps JSON output in metric-native wire units, and converts only for human display.

## What You Get

| Path | What it provides |
|------|------------------|
| `SKILL.md` | Command reference, pipeline recipes, and the gotchas that actually bite |
| `scripts/tempest` | CLI: `stations`, `current`, `obs`, `forecast`, `udp listen` with `--json`/`--dry-run` |
| `scripts/test_tempest.py` | Offline test suite (canned datagram bytes + mocked REST, no network) |
| `references/rest-api-and-auth.md` | Token auth, endpoint catalog, response shapes, error signatures |
| `references/udp-broadcast-protocol.md` | Port 50222 transport, every message family's exact layout |
| `references/observation-layouts-and-units.md` | Index-by-index field maps for obs_st/obs_air/obs_sky + conversion tables |
| `references/cli-worked-recipes.md` | Copy-paste multi-step recipes with jq stages |

## Quick Start

```bash
# Create a token in the Tempest web app: Settings -> Data Authorizations -> Create Token
export TEMPEST_TOKEN="your-token-here"

tempest stations        # discover your station and device IDs
tempest current         # conditions right now
tempest forecast        # current + daily + hourly outlook
tempest udp listen --timeout 30   # real-time broadcast from the hub (no token needed)
```

Every command accepts `--json` for machine-readable output and `--dry-run` to preview the plan offline.

## Triggers

Load this skill when the user mentions Tempest, WeatherFlow, their weather station, hyper-local conditions, station observations, or parsing the hub's UDP port 50222 broadcast — temperature, rain, wind, humidity, lightning, or forecast questions tied to a personal station.

## Requirements

- Python 3.8+ with the `requests` library (the only dependency)
- A `TEMPEST_TOKEN` (free, personal use) for REST commands — created in the Tempest web app under Settings → Data Authorizations
- **For UDP listening: a Tempest hub on the same LAN** — the hub broadcasts on UDP port 50222 to the local network only; broadcasts do not cross routers, and no token or cloud account is involved. REST commands work from anywhere with internet access.
