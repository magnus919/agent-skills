# Skill Wrapper Example — `weather-cli`

A complete worked example of an agent-skills-compliant wrapper around a hypothetical weather API CLI. This follows the Phase 4 pattern: the SKILL.md triggers discovery, the CLI binary provides execution.

## Directory Structure

```
weather-cli/
├── weather-cli              # CLI binary (built with Phases 1-3)
└── SKILL.md                 # Skill wrapper (Phase 4)
```

## `SKILL.md`

```yaml
---
name: weather-cli
description: >-
  Query current weather, forecasts, and historical data from the OpenWeather
  API. Use when the user asks about the weather, forecasts, temperature,
  precipitation, wind, or climate conditions for a location.
license: MIT
compatibility: Requires weather-cli binary on PATH, OPENWEATHER_API_KEY
  set in environment or ~/.openweather.env
metadata:
  tags: [weather, climate, api-client, openweather]
---
```

```markdown
# Weather CLI

Query weather data from the OpenWeather API — current conditions, 7-day
forecasts, and historical records for any location.

## When to Use

- User asks "what's the weather in [city]" or "is it going to rain today"
- User asks about forecasts, temperature trends, wind, humidity, or pressure
- User asks "how hot/cold/windy was it on [date]"
- User wants to check weather across multiple locations

Do NOT use for: severe weather alerts (use a dedicated alert skill),
long-term climate projections, or weather data not available via
OpenWeather API.

## Setup

Credentials are read from the `OPENWEATHER_API_KEY` environment variable
or `~/.openweather.env`. If the agent gets a 401, guide the user to
set up an API key at https://openweathermap.org/api and set the env var.

Default units are metric. Pass `--units imperial` for Fahrenheit/mph.

## Essential Commands

### current — Current conditions for a location

```bash
weather-cli current "Raleigh, NC"                     # metric, human-readable
weather-cli current "London, UK" --json               # metric, machine-readable
weather-cli current "New York, NY" --units imperial    # Fahrenheit/mph
```

Output fields: `temperature`, `feels_like`, `humidity`, `wind_speed`,
`conditions` (text description), `pressure`, `visibility`.

### forecast — 7-day forecast

```bash
weather-cli forecast "Raleigh, NC"                     # human table
weather-cli forecast "Raleigh, NC" --json --days 3     # 3-day forecast as JSON
```

JSON shape: `[{"date", "high", "low", "conditions", "precip_chance"}, ...]`.
The `precip_chance` field is 0-100 (percentage). `conditions` uses
OpenWeather's label strings (`Clear`, `Clouds`, `Rain`, etc.).

### history — Historical data for a date

```bash
weather-cli history "Raleigh, NC" --date 2026-05-15
weather-cli history "London, UK" --date 2025-12-25 --json
```

Historical data is available for dates up to 5 days before the current date
(free tier) or full history (paid plans). The CLI will warn if data is
unavailable for the requested range.

## Location Format

Accepts city names (`"Raleigh, NC"`), ZIP codes (`"27601"`), or
latitude,longitude pairs (`"35.78,-78.64"`). City names with commas
should be quoted. For disambiguation, prefer `"City, State/Country"`
format over bare city names.

## Known Gotchas

- **City name ambiguity:** `"London"` resolves to London, UK. Use `"London, OH"`
  or `"London, Ontario"` for other cities.
- **Units apply per-command:** `--units` is not sticky. Set it on every command
  or override with `WEATHER_CLI_UNITS=imperial` env var.
- **Rate limit:** 60 requests/minute on free tier. Cache repeated location
  queries rather than fetching the same city twice.
- **The `conditions` field uses OpenWeather's English labels** regardless of
  locale. Always compare against `"Clear"`, `"Clouds"`, `"Rain"`, `"Snow"`,
  `"Drizzle"`, `"Thunderstorm"`, or `"Atmosphere"` (fog, haze, etc.).
```
