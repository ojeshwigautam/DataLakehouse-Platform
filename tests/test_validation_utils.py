"""Tests for validation utility functions."""

import json
from pathlib import Path

from src.validation.validation_utils import save_validation_report


class TestSaveValidationReport:
    def test_saves_report_json(self, tmp_path):
        """save_validation_report should create a JSON report file."""
        report_file = save_validation_report("test_layer", True, "All good!")

        assert Path(report_file).exists()

        with open(report_file, "r") as f:
            data = json.load(f)

        assert data["layer"] == "test_layer"
        assert data["status"] == "PASSED"
        assert data["message"] == "All good!"
        assert "timestamp" in data

    def test_saves_failure_report(self, tmp_path):
        """save_validation_report should record failure status correctly."""
        report_file = save_validation_report("test_layer", False, "Something failed")

        with open(report_file, "r") as f:
            data = json.load(f)

        assert data["status"] == "FAILED"
        assert data["message"] == "Something failed"

    def test_creates_report_directory(self):
        """save_validation_report should create the reports/data_quality directory."""
        import shutil

        from src.validation.validation_utils import REPORT_DIR, save_validation_report

        # Clean up first
        if REPORT_DIR.exists():
            shutil.rmtree(REPORT_DIR)

        report_file = save_validation_report("bronze", True, "OK")
        assert REPORT_DIR.exists()
        assert Path(report_file).exists()
