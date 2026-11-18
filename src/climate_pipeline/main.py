
import sys
from pathlib import Path

# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

# Make the src directory importable
sys.path.insert(0, str(SRC_DIR))


# --------------------------------------------------
# IMPORT PIPELINE MODULES
# --------------------------------------------------

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
# PIPELINE ORCHESTRATION
# --------------------------------------------------

def run_pipeline():

    print("\nStarting Climate Data Pipeline...")
    print("=" * 50)

    # ----------------------------------------------
    # STAGE 1: INGESTION
    # ----------------------------------------------

    print("\nSTAGE 1: DATA INGESTION")

    fetch_historical_weather(
        start_date=START_DATE,
        end_date=END_DATE,
    )

    # ----------------------------------------------
    # STAGE 2: TRANSFORMATION
    # ----------------------------------------------

    print("\nSTAGE 2: DATA TRANSFORMATION")

    df = transform_historical_weather(
        start_date=START_DATE,
        end_date=END_DATE,
    )

    # ----------------------------------------------
    # STAGE 3: DATA VALIDATION
    # ----------------------------------------------

    print("\nSTAGE 3: DATA VALIDATION")

    validation_results = validate_historical_weather(
        df=df,
        start_date=START_DATE,
        end_date=END_DATE,
    )

    # Display validation results
    for check, passed in validation_results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{check}: {status}")

    # Stop execution if any validation check fails
    enforce_validation(validation_results)

    print("\nAll data quality checks passed.")

    # ----------------------------------------------
    # STAGE 4: DATABASE UPLOAD
    # ----------------------------------------------

    print("\nSTAGE 4: DATABASE UPLOAD")

    uploaded_count = upload_weather_data(df)

    # ----------------------------------------------
    # PIPELINE SUMMARY
    # ----------------------------------------------

    print("\n" + "=" * 50)
    print("CLIMATE DATA PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 50)

    print(f"Date range: {START_DATE} to {END_DATE}")
    print(f"Records processed: {len(df)}")
    print(f"Records uploaded: {uploaded_count}")


# --------------------------------------------------
# APPLICATION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    run_pipeline()
