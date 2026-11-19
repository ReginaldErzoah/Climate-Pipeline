
from prefect import flow


if __name__ == "__main__":
    deployment = flow.from_source(
        source="https://github.com/ReginaldErzoah/Climate-Pipeline.git",
        entrypoint="src/climate_pipeline/main.py:historical_weather_pipeline",
    )

    deployment.deploy(
        name="climate-pipeline-managed",
        work_pool_name="climate-managed-pool",
        cron="0 6 * * *",
        tags=[
            "climate-pipeline",
            "weather",
            "dataops",
        ],
        description=(
            "Automated historical weather ingestion, transformation, "
            "validation and Supabase upload using Prefect Managed execution."
        ),
        job_variables={
            "pip_packages": [
                "git+https://github.com/ReginaldErzoah/Climate-Pipeline.git"
            ]
        },
    )
