"""
WatermarkManager — Read, update, and reset pipeline watermarks.

Watermarks track the last processed file and timestamp for each
pipeline, enabling incremental / batch-aware processing.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from src.database.connection import get_database_engine
from src.metadata.metadata_models import Watermark
from src.utils.logger import logger


class WatermarkManager:
    """Manage pipeline watermarks for incremental processing."""

    def __init__(self):
        self.engine = get_database_engine()

    # ----------------------------------------------------------
    # Read
    # ----------------------------------------------------------

    def get_watermark(
        self,
        pipeline_name: str,
    ) -> Optional[dict]:
        """Return the current watermark for the given pipeline.

        Returns a dict with keys:
            - pipeline_name
            - last_processed_file
            - last_processed_timestamp
            - updated_at

        Returns None if no watermark exists.
        """
        with Session(self.engine) as session:
            wm = session.query(Watermark).filter_by(pipeline_name=pipeline_name).first()
            if wm is None:
                logger.info(f"No watermark found for pipeline: {pipeline_name}")
                return None

            result = {
                "pipeline_name": wm.pipeline_name,
                "last_processed_file": wm.last_processed_file,
                "last_processed_timestamp": wm.last_processed_timestamp,
                "updated_at": wm.updated_at,
            }
            logger.info(
                f"Watermark retrieved | pipeline={pipeline_name} | "
                f"file={wm.last_processed_file}"
            )
            return result

    # ----------------------------------------------------------
    # Update
    # ----------------------------------------------------------

    def update_watermark(
        self,
        pipeline_name: str,
        last_processed_file: str,
        last_processed_timestamp: Optional[datetime] = None,
    ):
        """Create or update the watermark for a pipeline.

        If no watermark exists for the pipeline, a new one is
        created.  Otherwise the existing record is updated.
        """
        now = last_processed_timestamp or datetime.now()

        with Session(self.engine) as session:
            wm = session.query(Watermark).filter_by(pipeline_name=pipeline_name).first()

            if wm is None:
                wm = Watermark(
                    pipeline_name=pipeline_name,
                    last_processed_file=last_processed_file,
                    last_processed_timestamp=now,
                    updated_at=datetime.now(),
                )
                session.add(wm)
                logger.info(
                    f"Watermark created | pipeline={pipeline_name} | "
                    f"file={last_processed_file}"
                )
            else:
                wm.last_processed_file = last_processed_file
                wm.last_processed_timestamp = now
                wm.updated_at = datetime.now()
                logger.info(
                    f"Watermark updated | pipeline={pipeline_name} | "
                    f"file={last_processed_file}"
                )

            session.commit()

    # ----------------------------------------------------------
    # Reset
    # ----------------------------------------------------------

    def reset_watermark(self, pipeline_name: str):
        """Reset a pipeline's watermark to its initial (empty) state."""
        with Session(self.engine) as session:
            wm = session.query(Watermark).filter_by(pipeline_name=pipeline_name).first()

            if wm is None:
                logger.warning(
                    f"Cannot reset — no watermark for pipeline: " f"{pipeline_name}"
                )
                return

            wm.last_processed_file = None
            wm.last_processed_timestamp = None
            wm.updated_at = datetime.now()
            session.commit()

            logger.info(f"Watermark reset | pipeline={pipeline_name}")

    # ----------------------------------------------------------
    # Latest Timestamp
    # ----------------------------------------------------------

    def get_last_processed_timestamp(
        self,
        pipeline_name: str,
    ) -> Optional[datetime]:
        """Return the latest processed timestamp for a pipeline.

        This is a convenience method that extracts just the
        timestamp from the watermark record.
        """
        wm = self.get_watermark(pipeline_name)
        if wm is None:
            return None
        return wm["last_processed_timestamp"]
