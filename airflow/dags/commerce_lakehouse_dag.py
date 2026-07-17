from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


def _db_env_exports() -> str:
    """Export required lakehouse DB env vars from Airflow container env.

    The Airflow container itself should be configured via docker-compose.airflow.yml.
    """

    # Keep this generic: if a variable is unset, export to empty string.
    # The ETL code will fail fast if required values are missing.
    return " ".join(
        [
            "DB_HOST=$DB_HOST",
            "DB_PORT=$DB_PORT",
            "DB_NAME=$DB_NAME",
            "DB_USER=$DB_USER",
            "DB_PASSWORD=$DB_PASSWORD",
        ]
    )


default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
}


with DAG(
    dag_id="commerce_lakehouse_etl",
    description=(
        "Orchestrates the Unified Commerce "
        "Lakehouse ETL Pipeline"
    ),
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=[
        "data-engineering",
        "etl",
        "lakehouse",
    ],
) as dag:

    run_etl_pipeline = BashOperator(
        task_id="run_etl_pipeline",
        bash_command=(
            f"{_db_env_exports()} "
            "&& cd /opt/airflow/project "
            "&& python main.py"
        ),
    )

