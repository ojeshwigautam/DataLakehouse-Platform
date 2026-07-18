from pyspark.sql import SparkSession

from src.spark.config import (
    APP_NAME,
    PARQUET_COMPRESSION,
    SHUFFLE_PARTITIONS,
    SPARK_MASTER,
)


def get_spark() -> SparkSession:
    spark = (
        SparkSession.builder
        .appName(APP_NAME)
        .master(SPARK_MASTER)
        .config("spark.sql.shuffle.partitions", SHUFFLE_PARTITIONS)
        .config("spark.sql.adaptive.enabled", "true")
        .config(
            "spark.sql.parquet.compression.codec",
            PARQUET_COMPRESSION,
        )
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")
    return spark


