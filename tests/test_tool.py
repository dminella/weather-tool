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
