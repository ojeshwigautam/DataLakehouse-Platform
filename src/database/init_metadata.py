"""
Initialize the metadata schema and tables in PostgreSQL.

Run from project root:
    python -m src.database.init_metadata

Or inside the Airflow container:
    cd /opt/airflow/project
    python -m src.database.init_metadata
"""

from sqlalchemy import text

from src.database.connection import get_database_engine
from src.metadata.metadata_models import Base
from src.config.settings import METADATA_SCHEMA


def initialize_metadata():
    """Create the metadata schema and all ORM-defined tables."""
    engine = get_database_engine()

    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {METADATA_SCHEMA}"))

    Base.metadata.create_all(bind=engine)

    print(
        f"Schema '{METADATA_SCHEMA}' and all metadata tables "
        f"created successfully."
    )


if __name__ == "__main__":
    initialize_metadata()

