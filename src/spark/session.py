from pyspark.sql import SparkSession

from src.spark.config import (
    SPARK_APP_NAME,
    SPARK_MASTER,
    SPARK_SHUFFLE_PARTITIONS,
    SPARK_PARQUET_COMPRESSION,
)


def get_spark() -> SparkSession:
    spark = (
        SparkSession.builder
        .appName(SPARK_APP_NAME)
        .master(SPARK_MASTER)
        .config(
            "spark.sql.shuffle.partitions",
            SPARK_SHUFFLE_PARTITIONS,
        )
        .config(
            "spark.sql.parquet.compression.codec",
            SPARK_PARQUET_COMPRESSION,
        )
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    return spark

