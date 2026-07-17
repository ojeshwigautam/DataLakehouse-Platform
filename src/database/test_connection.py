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
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

try:
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()

        print("=" * 60)
        print("POSTGRESQL CONNECTION TEST")
        print("=" * 60)
        print("Database connection successful!")
        print(f"Database : {DB_NAME}")
        print(f"Host     : {DB_HOST}")
        print(f"Port     : {DB_PORT}")
        print(f"Version  : {version[0]}")
        print("=" * 60)

except Exception as error:
    print("=" * 60)
    print("DATABASE CONNECTION FAILED")
    print("=" * 60)
    print(error)

