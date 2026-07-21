"""
Reusable execution timer for every pipeline stage.

Captures start time, end time, and computes duration.
Can be used as a context manager or manually.
"""

import time
from contextlib import contextmanager
from datetime import datetime
from typing import Optional


class ExecutionTimer:
    """Timer for measuring execution duration of pipeline stages.

    Usage as context manager::

        with ExecutionTimer("Bronze ETL") as timer:
            # perform stage work
            pass

        print(timer.duration)  # seconds

    Usage manually::

        timer = ExecutionTimer("Bronze ETL")
        timer.start()
        # perform stage work
        timer.stop()
        print(timer.duration)
    """

    def __init__(self, stage_name: str = "pipeline"):
        self.stage_name = stage_name
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None
        self._start_datetime: Optional[datetime] = None
        self._end_datetime: Optional[datetime] = None

    # ── Manual API ────────────────────────────────────────────

    def start(self) -> "ExecutionTimer":
        """Start the timer and record the start timestamp."""
        self._start_time = time.perf_counter()
        self._start_datetime = datetime.now()
        return self

    def stop(self) -> "ExecutionTimer":
        """Stop the timer and record the end timestamp."""
        self._end_time = time.perf_counter()
        self._end_datetime = datetime.now()
        return self

    # ── Properties ────────────────────────────────────────────

    @property
    def duration(self) -> float:
        """Return the elapsed time in seconds.

        Returns 0.0 if the timer hasn't been started/stopped properly.
        """
        if self._start_time is None:
            return 0.0
        end = self._end_time if self._end_time is not None else time.perf_counter()
        return end - self._start_time

    @property
    def duration_formatted(self) -> str:
        """Return duration as a human-readable string."""
        secs = self.duration
        if secs < 60:
            return f"{secs:.2f} sec"
        minutes = int(secs // 60)
        remainder = secs % 60
        return f"{minutes}m {remainder:.1f}s"

    @property
    def start_time(self) -> Optional[str]:
        """Return start time as ISO string."""
        if self._start_datetime:
            return self._start_datetime.strftime("%H:%M:%S")
        return None

    @property
    def end_time(self) -> Optional[str]:
        """Return end time as ISO string."""
        if self._end_datetime:
            return self._end_datetime.strftime("%H:%M:%S")
        return None

    @property
    def start_datetime(self) -> Optional[datetime]:
        return self._start_datetime

    @property
    def end_datetime(self) -> Optional[datetime]:
        return self._end_datetime

    @property
    def elapsed(self) -> float:
        """Alias for duration."""
        return self.duration

    # ── Context Manager ───────────────────────────────────────

    @contextmanager
    def __call__(self):
        """Use as ``with timer():`` after creating an instance."""
        self.start()
        try:
            yield self
        finally:
            self.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    # ── Summary ───────────────────────────────────────────────

    def summary(self) -> str:
        """Return a formatted summary string."""
        return (
            f"{self.stage_name} | "
            f"Start: {self.start_time} | "
            f"End: {self.end_time} | "
            f"Duration: {self.duration_formatted}"
        )

    def get_metrics(self) -> dict:
        """Return timer metrics as a dictionary."""
        return {
            "stage": self.stage_name,
            "start_time": self.start_datetime,
            "end_time": self.end_datetime,
            "duration_seconds": round(self.duration, 2),
            "start_time_str": self.start_time,
            "end_time_str": self.end_time,
        }


def create_timer(stage_name: str = "pipeline") -> ExecutionTimer:
    """Factory function to create an ExecutionTimer."""
    return ExecutionTimer(stage_name)
