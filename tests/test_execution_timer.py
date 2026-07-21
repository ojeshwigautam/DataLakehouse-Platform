"""
Tests for the ExecutionTimer module.

Test scenarios:
    - Timer records durations correctly.
    - Timer works as context manager.
    - Timer provides formatted output.
    - Timer handles manual start/stop.
"""

import time

from src.monitoring.execution_timer import ExecutionTimer, create_timer


class TestExecutionTimer:
    """Tests for the ExecutionTimer class."""

    def test_timer_records_duration(self):
        """Timer should record a positive duration after start/stop."""
        timer = ExecutionTimer("test_stage")
        timer.start()
        time.sleep(0.01)  # Small delay to ensure measurable duration
        timer.stop()

        assert timer.duration > 0, "Duration should be greater than 0"
        assert timer.duration < 1.0, "Duration should be less than 1 second"

    def test_timer_context_manager(self):
        """Timer should work as a context manager and record duration."""
        with ExecutionTimer("context_test") as timer:
            time.sleep(0.01)

        assert timer.duration > 0, "Context manager timer should record duration"
        assert timer.start_time is not None
        assert timer.end_time is not None

    def test_timer_formatted_duration(self):
        """Timer should provide a human-readable formatted duration."""
        timer = ExecutionTimer("test")
        timer.start()
        time.sleep(0.01)
        timer.stop()

        formatted = timer.duration_formatted
        assert "sec" in formatted or "m" in formatted

    def test_timer_summary(self):
        """Timer should provide a summary string with key info."""
        timer = ExecutionTimer("summary_test")
        timer.start()
        time.sleep(0.01)
        timer.stop()

        summary = timer.summary()
        assert "summary_test" in summary
        assert "Start:" in summary
        assert "End:" in summary
        assert "Duration:" in summary

    def test_timer_get_metrics(self):
        """Timer should return metrics as a dictionary."""
        timer = ExecutionTimer("metrics_test")
        timer.start()
        time.sleep(0.01)
        timer.stop()

        metrics = timer.get_metrics()
        assert metrics["stage"] == "metrics_test"
        assert metrics["duration_seconds"] > 0
        assert metrics["start_time"] is not None
        assert metrics["end_time"] is not None
        assert metrics["start_time_str"] is not None
        assert metrics["end_time_str"] is not None

    def test_timer_zero_duration_before_start(self):
        """Timer should return 0 duration if never started."""
        timer = ExecutionTimer("never_started")
        assert timer.duration == 0.0, "Unstarted timer should have 0 duration"

    def test_timer_elapsed_property(self):
        """Timer should have an elapsed property that matches duration."""
        timer = ExecutionTimer("elapsed_test")
        timer.start()
        time.sleep(0.01)
        timer.stop()

        assert timer.elapsed == timer.duration

    def test_timer_multiple_uses(self):
        """Timer should be reusable with multiple start/stop cycles."""
        timer = ExecutionTimer("multi")

        timer.start()
        time.sleep(0.01)
        timer.stop()
        d1 = timer.duration

        timer.start()
        time.sleep(0.01)
        timer.stop()
        d2 = timer.duration

        assert d1 > 0
        assert d2 > 0

    def test_create_timer_factory(self):
        """create_timer factory function should return an ExecutionTimer."""
        timer = create_timer("factory_test")
        assert isinstance(timer, ExecutionTimer)
        assert timer.stage_name == "factory_test"

    def test_timer_callable_context_manager(self):
        """Timer should be callable as a context manager."""
        timer = ExecutionTimer("callable_test")
        with timer():
            time.sleep(0.01)

        assert timer.duration > 0, "Callable context manager should work"
