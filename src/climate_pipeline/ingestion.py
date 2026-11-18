
import requests
import pandas as pd


BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

LATITUDE = 5.6037
LONGITUDE = -0.1870

DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
]


def fetch_historical_weather(
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Fetch historical daily weather data from Open-Meteo.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        A DataFrame containing daily weather observations.
    """

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": start_date,
        "end_date": end_date,
        "daily": DAILY_VARIABLES,
        "timezone": "Africa/Accra",
    }

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if "daily" not in data:
        raise ValueError("API response does not contain daily weather data.")

    df = pd.DataFrame(data["daily"])

    return df