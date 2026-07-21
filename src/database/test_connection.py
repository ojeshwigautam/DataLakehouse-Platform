import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}" f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

from src.monitoring.logger import get_logger  # noqa: E402

logger = get_logger("postgres")

try:
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()

        logger.info("=" * 60)
        logger.info("POSTGRESQL CONNECTION TEST")
        logger.info("=" * 60)
        logger.info("Database connection successful!")
        logger.info(f"Database : {DB_NAME}")
        logger.info(f"Host     : {DB_HOST}")
        logger.info(f"Port     : {DB_PORT}")
        logger.info(f"Version  : {version[0]}")
        logger.info("=" * 60)

except Exception as error:
    logger.error("=" * 60)
    logger.error("DATABASE CONNECTION FAILED")
    logger.error("=" * 60)
    logger.error(str(error))
