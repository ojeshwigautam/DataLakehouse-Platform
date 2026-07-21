"""
SQLAlchemy ORM models for the metadata schema.

Tables:
    - pipeline_runs    : Track every pipeline execution
    - processed_files  : Track all processed files with checksums
    - watermarks       : Store pipeline watermarks (last processed position)
    - pipeline_metrics : Log per-stage execution metrics
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Double,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from src.config.settings import METADATA_SCHEMA

Base = declarative_base()


class PipelineRun(Base):
    """Track every pipeline execution with status and row counts."""

    __tablename__ = "pipeline_runs"
    __table_args__ = {"schema": METADATA_SCHEMA}

    run_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    start_time = Column(DateTime, nullable=False, default=datetime.now)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False, default="RUNNING")
    duration_seconds = Column(Integer, nullable=True)
    files_processed = Column(Integer, nullable=True, default=0)
    rows_processed = Column(BigInteger, nullable=True, default=0)
    error_message = Column(Text, nullable=True)


class ProcessedFile(Base):
    """Track every file that has been processed by the pipeline."""

    __tablename__ = "processed_files"
    __table_args__ = (
        UniqueConstraint("file_name", "checksum", name="_file_checksum_uc"),
        {"schema": METADATA_SCHEMA},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(Text, nullable=False)
    checksum = Column(Text, nullable=False)
    processed_timestamp = Column(DateTime, nullable=False, default=datetime.now)
    run_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(20), nullable=False, default="SUCCESS")


class Watermark(Base):
    """Pipeline watermarks for incremental processing."""

    __tablename__ = "watermarks"
    __table_args__ = {"schema": METADATA_SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_name = Column(String(50), nullable=False, unique=True)
    last_processed_file = Column(Text, nullable=True)
    last_processed_timestamp = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)


class PipelineMetric(Base):
    """Per-stage execution metrics for each pipeline run."""

    __tablename__ = "pipeline_metrics"
    __table_args__ = {"schema": METADATA_SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(UUID(as_uuid=True), nullable=False)
    stage = Column(String(50), nullable=False)
    rows_processed = Column(BigInteger, nullable=True, default=0)
    duration_seconds = Column(Double, nullable=True)
    status = Column(String(20), nullable=False, default="RUNNING")
