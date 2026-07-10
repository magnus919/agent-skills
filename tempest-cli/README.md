# Tempest — Hyper-Local Weather from Your Station

Query live weather data from a WeatherFlow Tempest station. Current conditions, 7-day forecast, historical observations, and real-time UDP broadcasts.

## Why Install This Skill

When your agent loads this skill, it can **check hyper-local weather from your own station** — more accurate than generic services. That means:

- **Current conditions** — temperature, humidity, wind, rain, UV, solar radiation, barometric pressure
- **7-day forecast** — daily and hourly outlook with precipitation probability
- **Historical data** — past observations for analysis
- **Real-time UDP** — local broadcast reception without cloud dependency
- **Auto-discovery** — finds your station and sensors automatically

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Complete command reference with examples |
| `scripts/tempest-cli` | CLI tool for WeatherFlow Tempest API |
| `references/` | API field layout reference |

## Quick Start

```bash
export TEMPEST_TOKEN="your-token-here"
tempest-cli current
tempest-cli forecast
```

## Triggers

Load this for weather, temperature, rain, wind, humidity, forecast, or conditions from a specific Tempest station.

## Requirements

Python 3.8+ with `requests` library. Free token from weatherflow.com.
