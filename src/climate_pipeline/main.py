from prefect import flow, task

from climate_pipeline.ingestion import fetch_historical_weather
from climate_pipeline.transformation import transform_historical_weather
from climate_pipeline.validation import (
    validate_historical_weather,
    enforce_validation,
)
from climate_pipeline.db_upload import upload_weather_data


# --------------------------------------------------
# PIPELINE CONFIGURATION
# --------------------------------------------------

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"


# --------------------------------------------------
# PREFECT TASKS
# --------------------------------------------------

@task(name="Ingest Historical Weather")
def ingestion_task(start_date: str, end_date: str) -> dict:
    """Retrieve historical weather data and save the raw response."""

    return fetch_historical_weather(
        start_date=start_date,
        end_date=end_date,
    )


@task(name="Transform Historical Weather")
def transformation_task(start_date: str, end_date: str):
    """Transform raw weather JSON into a pandas DataFrame."""

    return transform_historical_weather(
        start_date=start_date,
        end_date=end_date,
    )


@task(name="Validate Historical Weather")
def validation_task(df, start_date: str, end_date: str) -> dict:
    """Validate weather data and enforce quality checks."""

    results = validate_historical_weather(
        df=df,
        start_date=start_date,
        end_date=end_date,
    )

    enforce_validation(results)

    return results


@task(name="Upload Weather Data")
def upload_task(df) -> int:
    """Upload validated weather records to Supabase."""

    return upload_weather_data(df)


# --------------------------------------------------
# PREFECT FLOW
# --------------------------------------------------

@flow(name="Historical Weather Data Pipeline")
def historical_weather_pipeline(
    start_date: str = START_DATE,
    end_date: str = END_DATE,
) -> int:
    """Orchestrate the complete historical weather pipeline."""

    # Stage 1: Ingestion
    ingestion_task(start_date, end_date)

    # Stage 2: Transformation
    df = transformation_task(start_date, end_date)

    # Stage 3: Validation
    validation_task(df, start_date, end_date)

    # Stage 4: Database Upload
    uploaded_records = upload_task(df)

    print("\nPIPELINE EXECUTION COMPLETED")
    print(f"Records uploaded: {uploaded_records}")

    return uploaded_records


# --------------------------------------------------
# EXECUTION
# --------------------------------------------------

if __name__ == "__main__":
    historical_weather_pipeline()
