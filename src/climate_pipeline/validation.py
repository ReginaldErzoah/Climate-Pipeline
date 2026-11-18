import pandas as pd


def validate_historical_weather(
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
) -> dict:
    """
    Validate transformed historical weather data.

    Returns:
        A dictionary containing validation results.
    """

    results = {}

    # 1. Check for missing values
    results["missing_values"] = df.isnull().sum().sum() == 0

    # 2. Check for duplicate dates
    results["duplicate_dates"] = df["date"].duplicated().sum() == 0

    # 3. Check date completeness
    expected_dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
    )

    actual_dates = pd.DatetimeIndex(df["date"])

    results["date_completeness"] = len(actual_dates) == len(
        expected_dates
    ) and actual_dates.sort_values().equals(expected_dates)

    # 4. Check temperature consistency
    results["temperature_consistency"] = (
        df["temperature_2m_min"] <= df["temperature_2m_max"]
    ).all()

    # 5. Check precipitation validity
    results["precipitation_validity"] = (df["precipitation_sum"] >= 0).all()

    # 6. Check date field consistency
    expected_month_year = df["date"].dt.strftime("%Y-%m")

    results["date_field_consistency"] = df["month_year"].equals(expected_month_year)

    return results


def enforce_validation(results: dict) -> None:
    """
    Generate a validation report and stop the pipeline
    if any validation check fails.
    """

    print("\nDATA VALIDATION REPORT")
    print("-" * 35)

    for check, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{check}: {status}")

    total_checks = len(results)
    passed_checks = sum(results.values())
    failed_checks = total_checks - passed_checks

    print("-" * 35)
    print(f"Total checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {failed_checks}")

    if failed_checks > 0:
        raise ValueError("Data validation failed. Pipeline execution stopped.")

    print("\nAll validation checks passed.")
    print("Data is approved for the next pipeline stage.")
