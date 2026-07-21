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

    bronze_etl = BashOperator(
        task_id="bronze_etl",
        bash_command=(
            f"{_db_env_exports()} "
            "&& cd /opt/airflow/project "
            "&& python -m src.tasks.bronze_task"
        ),
    )

    bronze_validation = BashOperator(
        task_id="bronze_validation",
        bash_command=(
            f"{_db_env_exports()} "
            "&& cd /opt/airflow/project "
            "&& python -m src.tasks.bronze_validation_task"
        ),
    )

    silver_etl = BashOperator(
        task_id="silver_etl",
        bash_command=(
            f"{_db_env_exports()} "
            "&& cd /opt/airflow/project "
            "&& python -m src.tasks.silver_task"
        ),
    )

    silver_validation = BashOperator(
        task_id="silver_validation",
        bash_command=(
            f"{_db_env_exports()} "
            "&& cd /opt/airflow/project "
            "&& python -m src.tasks.silver_validation_task"
        ),
    )

    gold_etl = BashOperator(
        task_id="gold_etl",
        bash_command=(
            f"{_db_env_exports()} "
            "&& cd /opt/airflow/project "
            "&& python -m src.tasks.gold_task"
        ),
    )

    gold_validation = BashOperator(
        task_id="gold_validation",
        bash_command=(
            f"{_db_env_exports()} "
            "&& cd /opt/airflow/project "
            "&& python -m src.tasks.gold_validation_task"
        ),
    )

    postgres_load = BashOperator(
        task_id="postgres_load",
        bash_command=(
            f"{_db_env_exports()} "
            "&& cd /opt/airflow/project "
            "&& python -m src.tasks.postgres_task"
        ),
    )

    postgres_validation = BashOperator(
        task_id="postgres_validation",
        bash_command=(
            f"{_db_env_exports()} "
            "&& cd /opt/airflow/project "
            "&& python -m src.tasks.postgres_validation_task"
        ),
    )

    bronze_etl >> bronze_validation >> \
    silver_etl >> silver_validation >> \
    gold_etl >> gold_validation >> \
    postgres_load >> postgres_validation

