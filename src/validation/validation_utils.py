import json
from datetime import datetime
from pathlib import Path

REPORT_DIR = Path("reports/data_quality")
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def save_validation_report(layer: str, success: bool, message: str):
    """
    Save validation result as JSON.
    """

    report = {
        "layer": layer,
        "status": "PASSED" if success else "FAILED",
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }

    report_file = REPORT_DIR / f"{layer.lower()}_validation.json"

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)

    return report_file
