import pandas as pd
import pytest

from climate_pipeline.validation import (
    enforce_validation,
    validate_historical_weather,
)


@pytest.fixture
def valid_weather_data():
    """Create a small sample of valid weather data."""

    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2025-01-01", "2025-01-02", "2025-01-03"]
            ),
            "temperature_2m_min": [22.0, 23.0, 21.0],
            "temperature_2m_max": [30.0, 31.0, 29.0],
            "precipitation_sum": [0.0, 2.5, 1.0],
            "month_year": ["2025-01", "2025-01", "2025-01"],
        }
    )


def test_valid_weather_data_passes_validation(valid_weather_data):
    """All validation checks should pass for valid data."""

    results = validate_historical_weather(
        df=valid_weather_data,
        start_date="2025-01-01",
        end_date="2025-01-03",
    )

    assert all(results.values())


def test_invalid_weather_data_fails_validation(valid_weather_data):
    """Invalid temperatures should fail validation."""

    valid_weather_data.loc[0, "temperature_2m_min"] = 35.0

    results = validate_historical_weather(
        df=valid_weather_data,
        start_date="2025-01-01",
        end_date="2025-01-03",
    )

    assert not results["temperature_consistency"]


def test_enforce_validation_raises_error():
    """The pipeline should stop when validation fails."""

    failed_results = {
        "missing_values": True,
        "temperature_consistency": False,
    }

    with pytest.raises(ValueError, match="Data validation failed"):
        enforce_validation(failed_results)
