import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from supabase import Client, create_client


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

TABLE_NAME = "daily_weather"

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

    Credentials are retrieved from environment variables.
    """

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SECRET_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials. Check your project .env file.")

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

    # Convert dates to PostgreSQL-compatible strings
    upload_df["date"] = upload_df["date"].dt.strftime("%Y-%m-%d")

    # Ensure no missing values exist
    if upload_df.isnull().any().any():
        raise ValueError("Data contains missing values. Resolve them before uploading.")

    # Prevent duplicate dates within the upload batch
    if upload_df["date"].duplicated().any():
        raise ValueError("Duplicate dates detected in upload data.")

    # Convert DataFrame to list of dictionaries
    records = upload_df.to_dict(orient="records")

    return records


# --------------------------------------------------
# DATABASE UPLOAD
# --------------------------------------------------


def upload_weather_data(df: pd.DataFrame) -> int:
    """
    Upload validated weather records to Supabase.

    Uses upsert to prevent duplicate daily records.

    Args:
        df: Transformed and validated weather DataFrame.

    Returns:
        Number of records returned by Supabase.
    """

    # Prepare records
    records = prepare_records(df)

    # Create Supabase client
    supabase = get_supabase_client()

    try:
        # Upload using upsert
        response = (
            supabase.table(TABLE_NAME)
            .upsert(
                records,
                on_conflict="date",
            )
            .execute()
        )

        # Count returned records
        uploaded_count = len(response.data)

        print(f"Successfully uploaded {uploaded_count} weather records.")

        return uploaded_count

    except Exception as error:
        raise RuntimeError(f"Failed to upload weather data: {error}") from error
