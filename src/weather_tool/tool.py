from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight showers",
    81: "Moderate showers",
    82: "Violent showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


class WeatherInput(BaseModel):
    """Input schema for WeatherTool."""

    city: str = Field(..., description="Name of the city to get weather for, e.g. 'London' or 'New York'")


class WeatherTool(BaseTool):
    name: str = "weather_tool"
    description: str = "Gets current weather conditions for a given city."
    args_schema: Type[BaseModel] = WeatherInput

    def _run(self, city: str) -> str:
        try:
            geo_resp = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1},
                timeout=10,
            )
            if not geo_resp.ok:
                return f"Weather API error ({geo_resp.status_code}): unable to retrieve weather for '{city}'."

            results = geo_resp.json().get("results", [])
            if not results:
                return f"Could not find city: '{city}'. Please check the spelling and try again."

            location = results[0]
            parts = [location["name"]]
            if location.get("admin1"):
                parts.append(location["admin1"])
            parts.append(location["country"])
            display_name = ", ".join(parts)

            weather_resp = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
                    "wind_speed_unit": "kmh",
                },
                timeout=10,
            )
            if not weather_resp.ok:
                return f"Weather API error ({weather_resp.status_code}): unable to retrieve weather for '{city}'."

            current = weather_resp.json().get("current")
            if not current:
                return f"Unexpected API response for '{city}'."

            condition = WMO_CODES.get(current["weather_code"], "Unknown")

            return (
                f"Weather in {display_name}:\n"
                f"  Condition:    {condition}\n"
                f"  Temperature:  {current['temperature_2m']}°C (feels like {current['apparent_temperature']}°C)\n"
                f"  Humidity:     {current['relative_humidity_2m']}%\n"
                f"  Wind speed:   {current['wind_speed_10m']} km/h"
            )
        except requests.exceptions.RequestException as e:
            return f"Network error retrieving weather for '{city}': {e}"
