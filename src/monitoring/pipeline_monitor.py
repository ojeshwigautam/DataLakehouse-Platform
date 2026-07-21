"""
Pipeline Monitor — Aggregates pipeline metrics for monitoring dashboard.

Provides aggregated views of:
    - Pipeline start/end times
    - Total runtime
    - Rows read/written
    - Files processed
    - Validation runtime
    - PostgreSQL load runtime
    - Failed stages
    - Success rate

Data is read from ``metadata.pipeline_metrics`` and ``pipeline_audit`` tables.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from src.database.connection import get_database_engine
from src.monitoring.logger import get_logger

logger = get_logger("pipeline")


class PipelineMonitor:
    """Aggregate and report pipeline execution metrics."""

    # ── Main aggregation ──────────────────────────────────────

    @staticmethod
    def get_pipeline_summary() -> Dict[str, Any]:
        """Get a comprehensive summary of all pipeline runs.

        Returns
        -------
        dict
            Summary with total runs, success rate, average duration, etc.
        """
        engine = get_database_engine()

        query = text(
            """
            SELECT
                COUNT(*) AS total_runs,
                COUNT(*) FILTER (WHERE status = 'SUCCESS') AS successful_runs,
                COUNT(*) FILTER (WHERE status = 'FAILED') AS failed_runs,
                ROUND(AVG(execution_time_seconds)::numeric, 2) AS avg_duration_seconds,
                COALESCE(SUM(incremental_batches), 0) AS total_incremental_batches
            FROM pipeline_audit
            """
        )

        with engine.connect() as connection:
            result = connection.execute(query).mappings().first()

        if not result or result["total_runs"] == 0:
            logger.warning("No pipeline runs found in pipeline_audit")
            return {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "success_rate": 0.0,
                "avg_duration_seconds": 0.0,
                "total_incremental_batches": 0,
            }

        total = result["total_runs"]
        successful = result["successful_runs"]
        failed = result["failed_runs"]
        success_rate = round((successful / total) * 100, 2) if total > 0 else 0.0

        return {
            "total_runs": total,
            "successful_runs": successful,
            "failed_runs": failed,
            "success_rate": success_rate,
            "avg_duration_seconds": float(result["avg_duration_seconds"] or 0.0),
            "total_incremental_batches": result["total_incremental_batches"],
        }

    @staticmethod
    def get_latest_run() -> Optional[Dict[str, Any]]:
        """Get the most recent pipeline execution details."""
        engine = get_database_engine()

        query = text(
            """
            SELECT
                run_id, pipeline_name, start_time, end_time,
                status, execution_time_seconds, incremental_batches, error_message
            FROM pipeline_audit
            ORDER BY start_time DESC
            LIMIT 1
            """
        )

        with engine.connect() as connection:
            result = connection.execute(query).mappings().first()

        if not result:
            logger.warning("No pipeline runs found")
            return None

        return dict(result)

    @staticmethod
    def get_stage_metrics(run_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get per-stage metrics for a specific run (or the latest run).

        Parameters
        ----------
        run_id : str, optional
            Specific run to query. If None, returns all runs.

        Returns
        -------
        list[dict]
            List of stage metric records.
        """
        engine = get_database_engine()

        if run_id:
            query = text(
                """
                SELECT run_id, stage, duration_seconds, rows_processed, status, timestamp
                FROM metadata.pipeline_metrics
                WHERE run_id = :run_id
                ORDER BY timestamp ASC
                """
            )
            params = {"run_id": run_id}
        else:
            query = text(
                """
                SELECT run_id, stage, duration_seconds, rows_processed, status, timestamp
                FROM metadata.pipeline_metrics
                ORDER BY timestamp DESC
                LIMIT 50
                """
            )
            params = {}

        try:
            with engine.connect() as connection:
                results = connection.execute(query, params).mappings().all()
            return [dict(row) for row in results]
        except Exception as exc:
            logger.warning(f"Could not fetch stage metrics: {exc}")
            return []

    @staticmethod
    def get_monitoring_dashboard_data() -> Dict[str, Any]:
        """Get all data needed for a monitoring dashboard.

        Returns
        -------
        dict
            Complete dashboard data including summary, latest run, and stage metrics.
        """
        summary = PipelineMonitor.get_pipeline_summary()
        latest_run = PipelineMonitor.get_latest_run()
        stage_metrics = []

        if latest_run:
            stage_metrics = PipelineMonitor.get_stage_metrics(latest_run["run_id"])

        return {
            "summary": summary,
            "latest_run": latest_run,
            "stage_metrics": stage_metrics,
            "generated_at": datetime.now().isoformat(),
        }

    @staticmethod
    def print_dashboard():
        """Print a formatted dashboard to the console."""
        data = PipelineMonitor.get_monitoring_dashboard_data()
        summary = data["summary"]
        latest = data["latest_run"]

        logger.info("=" * 70)
        logger.info("PIPELINE MONITORING DASHBOARD")
        logger.info("=" * 70)

        logger.info("")
        logger.info("SUMMARY")
        logger.info("-" * 70)
        logger.info(f"Total Runs               : {summary['total_runs']}")
        logger.info(f"Successful Runs          : {summary['successful_runs']}")
        logger.info(f"Failed Runs              : {summary['failed_runs']}")
        logger.info(f"Success Rate             : {summary['success_rate']}%")
        logger.info(f"Avg Duration             : {summary['avg_duration_seconds']}s")
        logger.info(
            f"Total Incremental Batches: {summary['total_incremental_batches']}"
        )

        if latest:
            logger.info("")
            logger.info("LATEST RUN")
            logger.info("-" * 70)
            logger.info(f"Run ID      : {latest['run_id']}")
            logger.info(f"Pipeline    : {latest['pipeline_name']}")
            logger.info(f"Status      : {latest['status']}")
            logger.info(f"Started     : {latest['start_time']}")
            logger.info(f"Completed   : {latest['end_time']}")
            logger.info(f"Duration    : {latest['execution_time_seconds']}s")

            if latest.get("error_message"):
                logger.error(f"Error       : {latest['error_message']}")

        if data["stage_metrics"]:
            logger.info("")
            logger.info("STAGE METRICS")
            logger.info("-" * 70)
            for metric in data["stage_metrics"]:
                logger.info(
                    f"  {metric['stage']:<25} "
                    f"duration={metric['duration_seconds']:.2f}s | "
                    f"rows={metric['rows_processed']} | "
                    f"status={metric['status']}"
                )

        logger.info("")
        logger.info("=" * 70)


# ── Convenience function ──────────────────────────────────────────


def get_pipeline_monitor() -> PipelineMonitor:
    """Factory function to create a PipelineMonitor instance."""
    return PipelineMonitor()
