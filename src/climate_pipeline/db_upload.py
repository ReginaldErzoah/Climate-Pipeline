import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import Client, create_client

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

TABLE_NAME = "daily_weather"
PREFECT_SECRET_BLOCK = "supabase-credentials"

REQUIRED_COLUMNS = [
    "date",
    "month_year",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
]


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client.

    Credentials are retrieved from local environment variables
    or from a Prefect Secret block during managed execution.
    """

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SECRET_KEY")

    # Retrieve credentials from Prefect if environment variables are unavailable.
    if not supabase_url or not supabase_key:
        from prefect.blocks.system import Secret

        secret_block = Secret.load(PREFECT_SECRET_BLOCK)
        secret_value = secret_block.get()

        if isinstance(secret_value, str):
            credentials = json.loads(secret_value)

        elif isinstance(secret_value, dict):
            credentials = secret_value

        else:
            raise TypeError(
                "Unexpected data type returned by Prefect Secret block."
            )

        supabase_url = supabase_url or credentials.get("SUPABASE_URL")
        supabase_key = supabase_key or credentials.get("SUPABASE_SECRET_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "Missing Supabase credentials. Check your .env file "
            "or Prefect Secret block."
        )

    return create_client(supabase_url, supabase_key)


def prepare_records(df: pd.DataFrame) -> list[dict]:
    """
    Prepare a validated DataFrame for database upload.

    Selects the required database columns and converts
    the DataFrame into JSON-compatible records.
    """

    if df.empty:
        raise ValueError("Cannot upload an empty DataFrame.")

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    upload_df = df[REQUIRED_COLUMNS].copy()

    upload_df["date"] = pd.to_datetime(
        upload_df["date"],
        errors="raise",
    )

    upload_df["date"] = upload_df["date"].dt.strftime("%Y-%m-%d")

    if upload_df.isnull().any().any():
        raise ValueError("Data contains missing values. Resolve them before uploading.")

    if upload_df["date"].duplicated().any():
        raise ValueError("Duplicate dates detected in upload data.")

    records = upload_df.to_dict(orient="records")

    return records


def upload_weather_data(df: pd.DataFrame) -> int:
    """
    Upload validated weather records to Supabase.

    Uses upsert to prevent duplicate daily records.

    Args:
        df: Transformed and validated weather DataFrame.

    Returns:
        Number of records returned by Supabase.
    """

    records = prepare_records(df)

    supabase = get_supabase_client()

    try:
        response = (
            supabase.table(TABLE_NAME).upsert(records, on_conflict="date").execute()
        )

        uploaded_count = len(response.data)

        print(f"Successfully uploaded {uploaded_count} weather records.")

        return uploaded_count

    except Exception as error:
        raise RuntimeError(f"Failed to upload weather data: {error}") from error
