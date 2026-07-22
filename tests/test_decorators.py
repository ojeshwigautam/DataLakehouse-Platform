"""Tests for the decorators module."""

import pytest

from src.utils.decorators import (
    handle_exceptions,
    log_and_time,
    log_execution,
    measure_time,
)


class TestLogExecution:
    def test_logs_start_and_complete(self):
        """log_execution should log function entry and exit."""

        @log_execution
        def sample_func():
            return 42

        result = sample_func()
        assert result == 42

    def test_logs_failure(self):
        """log_execution should log failure when exception occurs."""

        @log_execution
        def failing_func():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            failing_func()


class TestMeasureTime:
    def test_records_duration(self):
        """measure_time should record and log duration."""

        @measure_time
        def sample_func():
            return 42

        result = sample_func()
        assert result == 42

    def test_records_duration_on_failure(self):
        """measure_time should log duration even on failure."""

        @measure_time
        def failing_func():
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            failing_func()


class TestHandleExceptions:
    def test_catches_and_re_raises(self):
        """handle_exceptions should catch, log, and re-raise by default."""

        @handle_exceptions
        def failing_func():
            raise RuntimeError("oops")

        with pytest.raises(RuntimeError, match="oops"):
            failing_func()

    def test_returns_default_when_re_raise_false(self):
        """handle_exceptions should return default_return when re_raise=False."""

        @handle_exceptions(default_return=False, re_raise=False)
        def failing_func():
            raise RuntimeError("oops")

        result = failing_func()
        assert result is False

    def test_default_return_value(self):
        """handle_exceptions should return None by default when re_raise=False."""

        @handle_exceptions(re_raise=False)
        def failing_func():
            raise RuntimeError("oops")

        result = failing_func()
        assert result is None

    def test_passes_through_on_success(self):
        """handle_exceptions should pass through return values on success."""

        @handle_exceptions
        def success_func():
            return "hello"

        result = success_func()
        assert result == "hello"

    def test_log_traceback_false(self):
        """handle_exceptions should work with log_traceback=False."""

        @handle_exceptions(log_traceback=False)
        def failing_func():
            raise RuntimeError("quiet error")

        with pytest.raises(RuntimeError, match="quiet error"):
            failing_func()

    def test_used_without_parentheses(self):
        """handle_exceptions should work as @handle_exceptions (no call)."""

        @handle_exceptions
        def my_func():
            return 99

        assert my_func() == 99


class TestLogAndTime:
    def test_combined_decorator(self):
        """log_and_time should combine log_execution and measure_time."""

        @log_and_time
        def sample_func():
            return "done"

        result = sample_func()
        assert result == "done"

    def test_with_component_arg(self):
        """log_and_time should accept a component argument."""

        @log_and_time(component="bronze")
        def sample_func():
            return "done"

        result = sample_func()
        assert result == "done"
