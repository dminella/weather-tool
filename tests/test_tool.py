from unittest.mock import MagicMock, patch

from weather_tool.tool import WeatherInput, WMO_CODES, WeatherTool


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
