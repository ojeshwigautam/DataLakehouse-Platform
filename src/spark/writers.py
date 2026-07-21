from pyspark.sql import DataFrame


def write_parquet(df: DataFrame, path):
    (df.write.mode("overwrite").parquet(str(path)))
