import os
import time
from functools import wraps

from dotenv import load_dotenv
from sqlalchemy import create_engine, exc as sqlalchemy_exc

from src.utils.logger import logger

# Load environment variables from .env
load_dotenv()


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def retry_on_db_failure(
    max_retries: int = 5,
    base_delay: float = 2.0,
    backoff_factor: float = 2.0,
):
    """Decorator that retries the wrapped function on transient
    database connection errors with exponential backoff.

    Parameters
    ----------
    max_retries : int
        Maximum number of retry attempts.
    base_delay : float
        Initial delay in seconds before the first retry.
    backoff_factor : float
        Multiplier applied to the delay after each retry.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = base_delay

            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except sqlalchemy_exc.OperationalError as error:
                    last_exception = error
                    logger.warning(
                        f"DB connection attempt {attempt}/{max_retries} "
                        f"failed: {error}. Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    delay *= backoff_factor

            # All retries exhausted — raise the last exception
            logger.error(
                f"All {max_retries} DB connection attempts failed. "
                f"Last error: {last_exception}"
            )
            raise last_exception

        return wrapper

    return decorator


@retry_on_db_failure(max_retries=5, base_delay=2.0, backoff_factor=2.0)
def get_database_engine():
    """
    Create and return a SQLAlchemy PostgreSQL database engine.

    Retries up to 5 times with exponential backoff if the database
    host is not immediately reachable (e.g. container still starting).
    """

    if not all([
        DB_HOST,
        DB_PORT,
        DB_NAME,
        DB_USER,
        DB_PASSWORD is not None,
    ]):
        missing = [
            k
            for k, v in [
                ("DB_HOST", DB_HOST),
                ("DB_PORT", DB_PORT),
                ("DB_NAME", DB_NAME),
                ("DB_USER", DB_USER),
                ("DB_PASSWORD", DB_PASSWORD),
            ]
            if not v
        ]
        raise RuntimeError(
            f"Missing required database environment variables: {missing}"
        )

    database_url = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    try:
        # pool_pre_ping ensures connections are verified before use
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )

        # Attempt a lightweight connection to surface DNS/connectivity
        # errors eagerly rather than on the first query.
        with engine.connect() as conn:
            conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )

        logger.info(f"PostgreSQL engine created for database: {DB_NAME}")

        return engine

    except Exception as error:
        logger.error("Failed to create PostgreSQL database engine")
        logger.error(error)
        raise
