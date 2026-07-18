import os
import sys
import pytest

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from src.spark.session import get_spark


@pytest.fixture(scope="session")
def spark():

    spark = get_spark()
    yield spark
    spark.stop()

