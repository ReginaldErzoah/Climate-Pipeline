
import json
from pathlib import Path

import pandas as pd


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Raw data directory
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


def transform_historical_weather(
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Load raw weather JSON and transform it into a DataFrame.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        A transformed DataFrame containing daily weather data.
    """

    # Locate the raw JSON file
    file_path = (
        RAW_DATA_DIR
        / f"weather_{start_date}_{end_date}.json"
    )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Raw data file not found: {file_path}"
        )

    # Load the raw JSON data
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Extract daily observations
    if "daily" not in data:
        raise ValueError(
            "Raw data does not contain daily weather observations."
        )

    df = pd.DataFrame(data["daily"])

    # Convert the original time column to datetime
    df["date"] = pd.to_datetime(df["time"])

    # Create month-year column
    df["month_year"] = df["date"].dt.strftime("%Y-%m")

    print(f"Successfully transformed {len(df)} records.")
    print(f"Transformed columns: {list(df.columns)}")

    return df