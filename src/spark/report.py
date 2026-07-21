"""Reconciliation report persistence utilities."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def save_reconciliation_report(
    report: Dict[str, Any],
    *,
    output_dir: str | Path = "reports/reconciliation",
    filename_prefix: Optional[str] = None,
) -> Path:
    """Save reconciliation JSON report to disk.

    Creates `output_dir` if it doesn't exist.

    Returns:
        Full path to saved JSON file.
    """

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if filename_prefix is None:
        pipeline = report.get("pipeline", "pipeline")
        filename_prefix = str(pipeline)

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{ts}.json"

    out_path = out_dir / filename

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return out_path
