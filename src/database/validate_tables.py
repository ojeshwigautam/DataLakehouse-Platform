from sqlalchemy import inspect, text

from src.database.connection import get_database_engine
from src.utils.logger import logger

EXPECTED_TABLES = [
    "daily_sales",
    "monthly_sales",
    "top_products",
    "top_states",
    "payment_summary",
    "seller_performance",
    "delivery_summary",
]


def validate_postgresql_tables():
    """
    Validate Gold Layer tables loaded into PostgreSQL.
    """

    logger.info("=" * 60)
    logger.info("POSTGRESQL DATABASE VALIDATION")
    logger.info("=" * 60)

    engine = get_database_engine()

    validation_results = {}

    try:
        inspector = inspect(engine)

        existing_tables = inspector.get_table_names()

        logger.info(f"Tables found in PostgreSQL: {len(existing_tables)}")

        with engine.connect() as connection:

            for table_name in EXPECTED_TABLES:

                if table_name not in existing_tables:

                    logger.error(f"[MISSING] {table_name}")

                    validation_results[table_name] = {
                        "exists": False,
                        "rows": 0,
                    }

                    continue

                query = text(f'SELECT COUNT(*) FROM "{table_name}"')

                row_count = connection.execute(query).scalar()

                validation_results[table_name] = {
                    "exists": True,
                    "rows": row_count,
                }

                logger.info(f"[OK] {table_name:<25} " f"Rows: {row_count}")

        missing_tables = [
            table
            for table, result in validation_results.items()
            if not result["exists"]
        ]

        logger.info("=" * 60)

        if missing_tables:

            logger.error(
                f"Database validation failed. " f"Missing tables: {missing_tables}"
            )

            return False

        logger.info("PostgreSQL Database Validation Successful")

        logger.info(f"Validated Tables: {len(EXPECTED_TABLES)}")

        logger.info("=" * 60)

        return True

    except Exception as error:

        logger.error("PostgreSQL database validation failed")

        logger.error(error)

        raise

    finally:

        engine.dispose()


if __name__ == "__main__":
    validate_postgresql_tables()
