"""
Metadata Management Framework for tracking pipeline executions,
processed files, watermarks, and stage metrics.

Provides:
- MetadataManager   — Central orchestrator for all metadata operations
- WatermarkManager  — Read, update, and reset pipeline watermarks
- FileTracker       — Checksum-based duplicate file detection
- PipelineHistory   — Record pipeline execution history
"""

from src.metadata.file_tracker import FileTracker
from src.metadata.metadata_manager import MetadataManager
from src.metadata.pipeline_history import PipelineHistory
from src.metadata.watermark_manager import WatermarkManager

__all__ = [
    "MetadataManager",
    "WatermarkManager",
    "FileTracker",
    "PipelineHistory",
]
