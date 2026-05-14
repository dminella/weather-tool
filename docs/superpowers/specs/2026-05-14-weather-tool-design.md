# WeatherTool Design

**Date:** 2026-05-14  
**Status:** Approved

## Overview

Update the CrewAI `WeatherTool` scaffold to fetch real current weather conditions for a given city using two free, no-API-key Open-Meteo endpoints.

## Architecture

Two sequential HTTP calls via `requests`:

1. **Geocoding** — `https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1`  
   Resolves a city name to latitude, longitude, and a display name (e.g. "London, England, United Kingdom").

2. **Weather** — `https://api.open-meteo.com/v1/forecast` with `latitude`, `longitude`, and `current` parameter listing the required fields.  
   Returns current meteorological conditions.

The tool returns a formatted plain-text string suitable for consumption by a CrewAI LLM agent.

## Components

### Input Schema

```python
class WeatherInput(BaseModel):
    city: str = Field(..., description="Name of the city to get weather for, e.g. 'London' or 'New York'")
```

### WeatherTool

```python
class WeatherTool(BaseTool):
    name: str = "weather_tool"
    description: str = "Gets current weather conditions for a given city."
    args_schema: Type[BaseModel] = WeatherInput

    def _run(self, city: str) -> str:
        ...
```

### WMO Weather Code Mapping

Open-Meteo returns integer WMO weather codes. A dictionary maps all ~27 categories to plain-English descriptions (e.g. `0 → "Clear sky"`, `61 → "Slight rain"`, `95 → "Thunderstorm"`).

## Data Fields

Fetched via the `current` parameter of the Open-Meteo forecast API:

| Field | Description |
|---|---|
| `temperature_2m` | Current temperature (°C) |
| `apparent_temperature` | Feels-like temperature (°C) |
| `relative_humidity_2m` | Relative humidity (%) |
| `wind_speed_10m` | Wind speed at 10m (km/h) |
| `weather_code` | WMO condition code |

## Output Format

```
Weather in London, England, United Kingdom:
  Condition:    Clear sky
  Temperature:  18.4°C (feels like 17.1°C)
  Humidity:     62%
  Wind speed:   14.2 km/h
```

## Error Handling

Both failure modes return a descriptive string (no exception raised) so the agent can reason about the failure:

- **City not found** — geocoding returns empty results:  
  `"Could not find city: '{city}'. Please check the spelling and try again."`

- **API error** — either call returns a non-2xx HTTP status:  
  `"Weather API error ({status_code}): unable to retrieve weather for '{city}'."`

## Dependencies

`requests` added explicitly to `pyproject.toml` (already transitively available via `crewai[tools]`, but declared for clarity).

## APIs Used

- Open-Meteo Geocoding: https://geocoding-api.open-meteo.com/v1/search
- Open-Meteo Forecast: https://api.open-meteo.com/v1/forecast
- License: Open-Meteo data is free under CC BY 4.0 for non-commercial use; the API itself has no rate limits for reasonable usage.
