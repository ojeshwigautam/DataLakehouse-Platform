from sqlalchemy import text

from src.database.connection import get_database_engine
from src.utils.logger import logger


def get_pipeline_metrics():
    """Retrieve pipeline execution metrics from the pipeline_audit table."""

    logger.info("=" * 60)
    logger.info("PIPELINE MONITORING METRICS")
    logger.info("=" * 60)

    engine = get_database_engine()

    query = text(
        """
        SELECT
            COUNT(*) AS total_runs,

            COUNT(*) FILTER (
                WHERE status = 'SUCCESS'
            ) AS successful_runs,

            COUNT(*) FILTER (
                WHERE status = 'FAILED'
            ) AS failed_runs,

            ROUND(
                AVG(execution_time_seconds)::numeric,
                2
            ) AS avg_execution_time_seconds,

            COALESCE(
                SUM(incremental_batches),
                0
            ) AS total_incremental_batches

        FROM pipeline_audit;
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query).mappings().first()

    if result is None:
        logger.warning("No pipeline metrics found")
        return None

    total_runs = result["total_runs"]
    successful_runs = result["successful_runs"]
    failed_runs = result["failed_runs"]

    success_rate = (
        (successful_runs / total_runs) * 100
        if total_runs > 0
        else 0
    )

    logger.info(f"Total Pipeline Runs       : {total_runs}")
    logger.info(f"Successful Runs           : {successful_runs}")
    logger.info(f"Failed Runs               : {failed_runs}")
    logger.info(f"Success Rate              : {success_rate:.2f}%")
    logger.info(
        "Average Execution Time    : "
        f"{result['avg_execution_time_seconds']} seconds"
    )
    logger.info(
        "Incremental Batches       : "
        f"{result['total_incremental_batches']}"
    )

    logger.info("=" * 60)

    return {
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "failed_runs": failed_runs,
        "success_rate": round(success_rate, 2),
        "avg_execution_time_seconds":
            result["avg_execution_time_seconds"],
        "total_incremental_batches":
            result["total_incremental_batches"],
    }


def get_latest_pipeline_run():
    """Retrieve the most recent pipeline execution."""

    engine = get_database_engine()

    query = text(
        """
        SELECT
            run_id,
            pipeline_name,
            start_time,
            end_time,
            status,
            execution_time_seconds,
            incremental_batches,
            error_message
        FROM pipeline_audit
        ORDER BY start_time DESC
        LIMIT 1;
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query).mappings().first()

    if result is None:
        logger.warning("No pipeline runs found")
        return None

    logger.info("LATEST PIPELINE RUN")
    logger.info("-" * 60)
    logger.info(f"Run ID           : {result['run_id']}")
    logger.info(f"Pipeline         : {result['pipeline_name']}")
    logger.info(f"Status           : {result['status']}")
    logger.info(f"Started          : {result['start_time']}")
    logger.info(f"Completed        : {result['end_time']}")
    logger.info(
        f"Execution Time   : "
        f"{result['execution_time_seconds']} seconds"
    )
    logger.info(
        f"Incremental Runs : "
        f"{result['incremental_batches']}"
    )

    if result["error_message"]:
        logger.info(
            f"Error            : "
            f"{result['error_message']}"
        )

    logger.info("=" * 60)

    return dict(result)


if __name__ == "__main__":
    get_pipeline_metrics()
    get_latest_pipeline_run()

