"""
Reusable decorators for pipeline stage functions.

Decorators:
    - @log_execution  : Log function entry/exit with arguments
    - @measure_time   : Measure and log execution time
    - @handle_exceptions : Catch and log exceptions, re-raise

These decorators avoid repeating logging and timing code in every ETL stage.

Usage::

    from src.utils.decorators import log_execution, measure_time, handle_exceptions

    @handle_exceptions
    @measure_time
    @log_execution
    def run_bronze():
        # stage implementation
        pass
"""

import functools
import traceback
from typing import Any, Callable, Optional, TypeVar

from src.monitoring.execution_timer import ExecutionTimer
from src.monitoring.logger import get_logger

F = TypeVar("F", bound=Callable[..., Any])

pipeline_logger = get_logger("pipeline")


def log_execution(func: F) -> F:
    """Decorator that logs function entry and exit.

    Logs the function name and its arguments on entry,
    and logs completion (with return value) on exit.

    Usage::

        @log_execution
        def run_bronze():
            pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        pipeline_logger.info(f"[{func_name}] START | args={args} kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)
            pipeline_logger.info(f"[{func_name}] COMPLETED | result={result}")
            return result
        except Exception as exc:
            pipeline_logger.error(f"[{func_name}] FAILED | error={exc}")
            raise

    return wrapper  # type: ignore


def measure_time(func: F) -> F:
    """Decorator that measures and logs execution time.

    Uses the ExecutionTimer to capture precise timing information.
    Logs the duration in a structured format.

    Usage::

        @measure_time
        def run_bronze():
            pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__

        timer = ExecutionTimer(func_name)
        timer.start()

        try:
            result = func(*args, **kwargs)
            timer.stop()

            pipeline_logger.info(
                f"[{func_name}] EXECUTION TIME | "
                f"duration={timer.duration:.2f}s | "
                f'summary="{timer.summary()}"'
            )
            return result

        except Exception as exc:
            timer.stop()
            pipeline_logger.error(
                f"[{func_name}] EXECUTION TIME (FAILED) | "
                f"duration={timer.duration:.2f}s | "
                f"error={exc}"
            )
            raise

    return wrapper  # type: ignore


def handle_exceptions(
    func: Optional[F] = None,
    *,
    default_return: Any = None,
    re_raise: bool = True,
    log_traceback: bool = True,
) -> F:
    """Decorator that catches and logs exceptions from pipeline stages.

    Parameters
    ----------
    default_return : Any, optional
        Value to return if the function fails and re_raise is False.
    re_raise : bool, default=True
        Whether to re-raise the exception after logging.
    log_traceback : bool, default=True
        Whether to log the full traceback.

    Usage::

        @handle_exceptions
        def run_bronze():
            pass

        @handle_exceptions(default_return=False, re_raise=False)
        def run_safe():
            pass
    """

    def decorator(f: F) -> F:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            func_name = f.__name__
            try:
                return f(*args, **kwargs)
            except Exception as exc:
                if log_traceback:
                    pipeline_logger.error(
                        f"[{func_name}] EXCEPTION | "
                        f"error={exc}\n{traceback.format_exc()}"
                    )
                else:
                    pipeline_logger.error(f"[{func_name}] EXCEPTION | error={exc}")

                if re_raise:
                    raise
                return default_return

        return wrapper  # type: ignore

    # Allow usage with or without arguments
    if func is not None:
        return decorator(func)
    return decorator  # type: ignore


def log_and_time(func: F = None, *, component: str = "pipeline") -> F:
    """Combined decorator that logs execution and measures time.

    This is a convenience decorator that combines @log_execution
    and @measure_time into a single decorator.

    Parameters
    ----------
    component : str, optional
        Logger component name ('pipeline', 'bronze', 'silver', etc.)

    Usage::

        @log_and_time
        def run_bronze():
            pass

        @log_and_time(component="bronze")
        def run_bronze():
            pass
    """

    def decorator(f: F) -> F:
        @log_execution
        @measure_time
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper  # type: ignore

    if func is not None:
        return decorator(func)
    return decorator  # type: ignore
