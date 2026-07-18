from pyspark.sql import DataFrame

from src.spark.session import get_spark


def read_parquet(path) -> DataFrame:
    spark = get_spark()
    return spark.read.parquet(str(path))

