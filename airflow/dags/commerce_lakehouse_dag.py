from datetime import datetime

from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator

from airflow import DAG


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


def _check_for_new_files() -> str:
    """Check the incremental folder for new (unprocessed) files.

    Returns the task ID to branch to:
        - ``incremental_loader`` if new files exist,
        - ``skip_incremental`` if no new files are found.
    """
    import sys

    # Add project root to path so we can import our modules
    sys.path.insert(0, "/opt/airflow/project")

    from src.ingestion.incremental_loader import IncrementalLoader
    from src.utils.logger import logger

    loader = IncrementalLoader()
    new_files = loader.get_new_files()

    logger.info(f"Airflow branch check: {len(new_files)} new file(s) found")

    if new_files:
        return "incremental_loader"
    return "skip_incremental"


default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
}


with DAG(
    dag_id="commerce_lakehouse_etl",
    description=("Orchestrates the Unified Commerce " "Lakehouse ETL Pipeline"),
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

    # ── Discovery & Branching ──────────────────────────────────────

    discover_new_files = BranchPythonOperator(
        task_id="discover_new_files",
        python_callable=_check_for_new_files,
    )

    skip_incremental = DummyOperator(
        task_id="skip_incremental",
    )

    # ── Incremental Loader ─────────────────────────────────────────

    incremental_loader = BashOperator(
        task_id="incremental_loader",
        bash_command=(
            f"{_db_env_exports()} "
            "&& cd /opt/airflow/project "
            '&& python -c "'
            "from src.ingestion.incremental_loader import IncrementalLoader; "
            "IncrementalLoader().run()"
            '"'
        ),
    )

    # ── Bronze / Silver / Gold / Postgres pipeline ─────────────────

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

    # ── Metadata Update ────────────────────────────────────────────

    update_metadata = BashOperator(
        task_id="update_metadata",
        bash_command=(
            f"{_db_env_exports()} "
            "&& cd /opt/airflow/project "
            '&& python -c "'
            "from src.metadata.metadata_manager import MetadataManager; "
            "from datetime import datetime; "
            "mgr = MetadataManager(); "
            "mgr.update_watermark("
            "pipeline_name='airflow_dag', "
            "last_processed_timestamp=datetime.now()"
            ")"
            '"'
        ),
    )

    # ── DAG Flow ───────────────────────────────────────────────────

    # Branch: discover → either incremental_loader or skip
    discover_new_files >> [incremental_loader, skip_incremental]

    # When new files found, process them through the pipeline
    (
        incremental_loader
        >> bronze_etl
        >> bronze_validation
        >> silver_etl
        >> silver_validation
        >> gold_etl
        >> gold_validation
        >> postgres_load
        >> postgres_validation
        >> update_metadata
    )

    # Both branches converge at the end (no downstream join needed
    # since both terminate the DAG).
