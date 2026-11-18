
from climate_pipeline.ingestion import fetch_historical_weather


def run_pipeline():
    """
    Execute the climate data pipeline.
    """

    print("Starting climate data pipeline...")

    # Ingestion
    print("\nStep 1: Ingesting historical weather data")

    fetch_historical_weather(
        start_date="2025-01-01",
        end_date="2025-12-31",
    )

    print("\nClimate data pipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()
