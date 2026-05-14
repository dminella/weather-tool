# WeatherTool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the WeatherTool scaffold with a real implementation that fetches current weather for any city using two free Open-Meteo APIs (no API key required).

**Architecture:** Geocode the city name to lat/lon via `https://geocoding-api.open-meteo.com/v1/search`, then fetch current conditions via `https://api.open-meteo.com/v1/forecast`. Return a formatted plain-text string. All HTTP calls use `requests`. Errors return descriptive strings rather than raising exceptions.

**Tech Stack:** Python 3.11, CrewAI 1.14.4, `requests`, `pytest`, `unittest.mock` (stdlib)

---

### Task 1: Add dependencies and test scaffold

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/__init__.py`

- [ ] **Step 1: Add `requests` as a runtime dependency**

```bash
uv add requests
```

Expected: `pyproject.toml` now lists `requests` under `[project] dependencies`.

- [ ] **Step 2: Add `pytest` as a dev dependency**

```bash
uv add --dev pytest
```

Expected: `pyproject.toml` now has a `[dependency-groups]` section with `dev = ["pytest>=..."]`.

- [ ] **Step 3: Create `tests/__init__.py`**

Create an empty file at `tests/__init__.py`.

- [ ] **Step 4: Verify the test runner works**

```bash
uv run pytest tests/ -v
```

Expected output: `no tests ran` (or similar — zero failures, zero errors).

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock tests/__init__.py
git commit -m "chore: add requests and pytest dependencies"
```

---

### Task 2: WeatherInput schema and WMO code mapping

**Files:**
- Modify: `src/weather_tool/tool.py`
- Modify: `tests/test_tool.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_tool.py` with the following content:

```python
from weather_tool.tool import WeatherInput, WMO_CODES


def test_weather_input_accepts_city():
    inp = WeatherInput(city="Paris")
    assert inp.city == "Paris"


def test_wmo_codes_clear_sky():
    assert WMO_CODES[0] == "Clear sky"


def test_wmo_codes_slight_rain():
    assert WMO_CODES[61] == "Slight rain"


def test_wmo_codes_thunderstorm():
    assert WMO_CODES[95] == "Thunderstorm"


def test_wmo_codes_covers_all_standard_codes():
    expected = {
        0, 1, 2, 3, 45, 48,
        51, 53, 55, 56, 57,
        61, 63, 65, 66, 67,
        71, 73, 75, 77,
        80, 81, 82, 85, 86,
        95, 96, 99,
    }
    assert expected.issubset(set(WMO_CODES.keys()))
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_tool.py -v
```

Expected: `ImportError` — `WeatherInput` and `WMO_CODES` do not exist yet.

- [ ] **Step 3: Implement `WeatherInput` and `WMO_CODES` in `tool.py`**

Replace the entire contents of `src/weather_tool/tool.py` with:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_tool.py -v
```

Expected: all 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/weather_tool/tool.py tests/test_tool.py
git commit -m "feat: add WeatherInput schema and WMO code mapping"
```

---

### Task 3: Implement `_run` happy path

**Files:**
- Modify: `src/weather_tool/tool.py`
- Modify: `tests/test_tool.py`

- [ ] **Step 1: Append failing happy-path test to `tests/test_tool.py`**

Add the following to the bottom of `tests/test_tool.py`:

```python
from unittest.mock import MagicMock, patch

from weather_tool.tool import WeatherTool


def _geo_mock(name="London", admin1="England", country="United Kingdom", lat=51.5, lon=-0.12):
    m = MagicMock()
    m.ok = True
    m.json.return_value = {
        "results": [
            {"name": name, "admin1": admin1, "country": country, "latitude": lat, "longitude": lon}
        ]
    }
    return m


def _weather_mock(temp=18.4, feels=17.1, humidity=62, wind=14.2, code=0):
    m = MagicMock()
    m.ok = True
    m.json.return_value = {
        "current": {
            "temperature_2m": temp,
            "apparent_temperature": feels,
            "relative_humidity_2m": humidity,
            "wind_speed_10m": wind,
            "weather_code": code,
        }
    }
    return m


@patch("weather_tool.tool.requests.get")
def test_run_returns_formatted_weather(mock_get):
    mock_get.side_effect = [_geo_mock(), _weather_mock()]
    result = WeatherTool()._run(city="London")
    assert "Weather in London, England, United Kingdom" in result
    assert "Clear sky" in result
    assert "18.4°C" in result
    assert "17.1°C" in result
    assert "62%" in result
    assert "14.2 km/h" in result


@patch("weather_tool.tool.requests.get")
def test_run_omits_admin1_when_absent(mock_get):
    mock_get.side_effect = [
        _geo_mock(name="Tokyo", admin1=None, country="Japan", lat=35.68, lon=139.69),
        _weather_mock(temp=22.0, feels=21.5, humidity=70, wind=10.0, code=1),
    ]
    result = WeatherTool()._run(city="Tokyo")
    assert "Weather in Tokyo, Japan" in result
    assert "Mainly clear" in result
```

- [ ] **Step 2: Run tests to verify the new tests fail**

```bash
uv run pytest tests/test_tool.py::test_run_returns_formatted_weather tests/test_tool.py::test_run_omits_admin1_when_absent -v
```

Expected: both FAIL — `_run` returns `"not implemented"`.

- [ ] **Step 3: Implement `_run` in `tool.py`**

Replace the `_run` method (the stub returning `"not implemented"`) with:

```python
    def _run(self, city: str) -> str:
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

        current = weather_resp.json()["current"]
        condition = WMO_CODES.get(current["weather_code"], "Unknown")

        return (
            f"Weather in {display_name}:\n"
            f"  Condition:    {condition}\n"
            f"  Temperature:  {current['temperature_2m']}°C (feels like {current['apparent_temperature']}°C)\n"
            f"  Humidity:     {current['relative_humidity_2m']}%\n"
            f"  Wind speed:   {current['wind_speed_10m']} km/h"
        )
```

- [ ] **Step 4: Run all tests to verify they pass**

```bash
uv run pytest tests/test_tool.py -v
```

Expected: all 7 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/weather_tool/tool.py tests/test_tool.py
git commit -m "feat: implement WeatherTool _run with Open-Meteo geocoding and forecast"
```

---

### Task 4: Error handling tests

**Files:**
- Modify: `tests/test_tool.py`

- [ ] **Step 1: Append error-handling tests to `tests/test_tool.py`**

Add the following to the bottom of `tests/test_tool.py`:

```python
@patch("weather_tool.tool.requests.get")
def test_run_city_not_found(mock_get):
    m = MagicMock()
    m.ok = True
    m.json.return_value = {"results": []}
    mock_get.return_value = m
    result = WeatherTool()._run(city="Xyzabc123")
    assert "Could not find city: 'Xyzabc123'" in result
    assert "spelling" in result


@patch("weather_tool.tool.requests.get")
def test_run_geocoding_api_error(mock_get):
    m = MagicMock()
    m.ok = False
    m.status_code = 500
    mock_get.return_value = m
    result = WeatherTool()._run(city="London")
    assert "Weather API error (500)" in result


@patch("weather_tool.tool.requests.get")
def test_run_weather_api_error(mock_get):
    weather_err = MagicMock()
    weather_err.ok = False
    weather_err.status_code = 503
    mock_get.side_effect = [_geo_mock(), weather_err]
    result = WeatherTool()._run(city="London")
    assert "Weather API error (503)" in result
```

- [ ] **Step 2: Run the new tests**

```bash
uv run pytest tests/test_tool.py -v
```

Expected: all 10 tests pass. (Error handling was already implemented in Task 3's `_run` — these tests confirm it.)

- [ ] **Step 3: Commit**

```bash
git add tests/test_tool.py
git commit -m "test: add error handling coverage for WeatherTool"
```

- [ ] **Step 4: Push**

```bash
git push origin main
```

---

## Done

The tool is now fully implemented and tested. To use it in a CrewAI crew:

```python
from weather_tool.tool import WeatherTool

tool = WeatherTool()
print(tool._run(city="Berlin"))
```

Output:
```
Weather in Berlin, Berlin, Germany:
  Condition:    Partly cloudy
  Temperature:  14.2°C (feels like 12.8°C)
  Humidity:     74%
  Wind speed:   18.5 km/h
```
