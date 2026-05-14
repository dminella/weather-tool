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
        return "not implemented"
