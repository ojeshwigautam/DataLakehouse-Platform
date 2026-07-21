from pathlib import Path

from src.config.settings import GOLD_DIR
from src.database.connection import get_database_engine
from src.storage.file_handler import FileHandler
from src.utils.logger import logger

GOLD_TABLES = {
    "daily_sales.parquet": "daily_sales",
    "monthly_sales.parquet": "monthly_sales",
    "top_products.parquet": "top_products",
    "top_states.parquet": "top_states",
    "payment_summary.parquet": "payment_summary",
    "seller_performance.parquet": "seller_performance",
    "delivery_summary.parquet": "delivery_summary",
}


def load_gold_tables():
    """
    Load Gold Layer CSV datasets into PostgreSQL tables.
    """

    logger.info("=" * 60)
    logger.info("Loading Gold Layer into PostgreSQL")
    logger.info("=" * 60)

    engine = get_database_engine()

    loaded_tables = []

    try:
        for file_name, table_name in GOLD_TABLES.items():

            file_path = Path(GOLD_DIR) / file_name

            if not file_path.exists():
                logger.warning(f"Gold dataset not found: {file_path}")
                continue

            logger.info(f"Loading {file_name} -> PostgreSQL table: {table_name}")

            df = FileHandler.read(file_path)

            df.to_sql(
                name=table_name,
                con=engine,
                if_exists="replace",
                index=False,
            )

            loaded_tables.append(table_name)

            logger.info(f"Table loaded successfully: {table_name} " f"({len(df)} rows)")

        logger.info("=" * 60)
        logger.info(
            f"PostgreSQL Loading Completed - " f"{len(loaded_tables)} tables loaded"
        )
        logger.info("=" * 60)

        return loaded_tables

    except Exception as error:
        logger.error("Failed to load Gold Layer into PostgreSQL")
        logger.error(error)
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    load_gold_tables()
