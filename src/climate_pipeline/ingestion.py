import json
from pathlib import Path

import requests

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

LATITUDE = 5.6037
LONGITUDE = -0.1870

DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
]

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Raw data directory
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def fetch_historical_weather(
    start_date: str,
    end_date: str,
) -> dict:
    """
    Fetch historical daily weather data from Open-Meteo
    and save the original API response as a JSON file.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        The original API response as a Python dictionary.
    """

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": start_date,
        "end_date": end_date,
        "daily": DAILY_VARIABLES,
        "timezone": "Africa/Accra",
    }

    # Send API request
    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30,
    )

    # Raise an exception if the request fails
    response.raise_for_status()

    # Parse JSON response
    data = response.json()

    if "daily" not in data:
        raise ValueError("API response does not contain daily weather data.")

    # Create raw data directory if it does not exist
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Define output file path
    file_path = RAW_DATA_DIR / f"weather_{start_date}_{end_date}.json"

    # Save original API response as JSON
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print("Historical weather data successfully ingested.")
    print(f"Raw records: {len(data['daily']['time'])}")
    print(f"Raw data saved to: {file_path}")

    return data
