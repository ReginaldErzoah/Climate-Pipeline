import pandas as pd
from prefect import flow, task

from climate_pipeline.db_upload import upload_weather_data
from climate_pipeline.ingestion import fetch_historical_weather
from climate_pipeline.transformation import transform_historical_weather
from climate_pipeline.validation import (
    enforce_validation,
    validate_historical_weather,
)


START_DATE = "2025-01-01"
END_DATE = "2025-12-31"


@task(
    name="Ingest Historical Weather",
    description=(
        "Retrieve historical weather data from Open-Meteo and save the raw response."
    ),
)
def ingestion_task(start_date: str, end_date: str) -> dict:
    """Retrieve and save raw historical weather data."""

    return fetch_historical_weather(
        start_date=start_date,
        end_date=end_date,
    )


@task(
    name="Transform Historical Weather",
    description="Transform raw weather JSON into a structured DataFrame.",
)
def transformation_task(
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """Transform raw weather data into a DataFrame."""

    return transform_historical_weather(
        start_date=start_date,
        end_date=end_date,
    )


@task(
    name="Validate Historical Weather",
    description="Evaluate data quality and enforce validation rules.",
)
def validation_task(
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
) -> dict:
    """Validate transformed weather data."""

    results = validate_historical_weather(
        df=df,
        start_date=start_date,
        end_date=end_date,
    )

    enforce_validation(results)

    return results


@task(
    name="Upload Weather Data",
    description="Upload validated weather records to Supabase.",
)
def upload_task(df: pd.DataFrame) -> int:
    """Upload validated weather data to Supabase."""

    return upload_weather_data(df)


@flow(
    name="Historical Weather Data Pipeline",
    description=(
        "Ingest, transform, validate and upload historical weather data to Supabase."
    ),
    log_prints=True,
)
def historical_weather_pipeline(
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> int:
    """
    Orchestrate the complete historical weather pipeline.

    Pipeline stages:
        1. Ingestion
        2. Transformation
        3. Validation
        4. Database upload
    """

    print("\nSTARTING HISTORICAL WEATHER PIPELINE")

    ingestion_task(
        start_date=start_date,
        end_date=end_date,
    )

    df = transformation_task(
        start_date=start_date,
        end_date=end_date,
    )

    print(f"\nTransformed records: {len(df)}")

    validation_results = validation_task(
        df=df,
        start_date=start_date,
        end_date=end_date,
    )

    print(f"Validation checks passed: {sum(validation_results.values())}")

    # Stage 4: Database upload
    uploaded_records = upload_task(df)

    print("\nPIPELINE EXECUTION COMPLETED")
    print(f"Records uploaded: {uploaded_records}")

    return uploaded_records


# ==================================================
# PREFECT CLOUD DEPLOYMENT
# ==================================================

if __name__ == "__main__":
    historical_weather_pipeline.serve(
        name="climate-pipeline-daily-update",
        cron="0 6 * * *",
        tags=[
            "climate-pipeline",
            "weather",
            "dataops",
        ],
        description=(
            "Automated weather data ingestion, "
            "transformation, validation and Supabase upload."
        ),
    )
