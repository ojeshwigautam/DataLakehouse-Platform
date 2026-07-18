from pyspark.sql.functions import (
    trim,
    lower,
    upper,
    col,
    to_timestamp,
)

from src.spark.readers import read_parquet
from src.spark.writers import write_parquet
from src.config.settings import (
    BRONZE_DATASET,
    SILVER_DIR,
)
from src.spark.session import get_spark


def create_spark_silver():

    spark = get_spark()

    df = read_parquet(BRONZE_DATASET)

    # Remove duplicates
    df = df.dropDuplicates(["order_unique_id"])

    # Clean text columns
    string_columns = [
        field.name
        for field in df.schema.fields
        if field.dataType.simpleString() == "string"
    ]

    for column in string_columns:
        df = df.withColumn(column, trim(col(column)))

    # Standardize cities
    if "customer_city" in df.columns:
        df = df.withColumn(
            "customer_city",
            lower(col("customer_city")),
        )

    if "seller_city" in df.columns:
        df = df.withColumn(
            "seller_city",
            lower(col("seller_city")),
        )

    # Standardize states
    if "customer_state" in df.columns:
        df = df.withColumn(
            "customer_state",
            upper(col("customer_state")),
        )

    if "seller_state" in df.columns:
        df = df.withColumn(
            "seller_state",
            upper(col("seller_state")),
        )

    # Convert timestamps

    timestamp_columns = [
        "shipping_limit_date",
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in timestamp_columns:
        if column in df.columns:
            df = df.withColumn(
                column,
                to_timestamp(col(column)),
            )

    # Remove invalid values

    for column in [
        "price",
        "payment_value",
        "freight_value",
    ]:
        if column in df.columns:
            df = df.filter(col(column) >= 0)

    output = SILVER_DIR / "silver_orders_spark.parquet"

    write_parquet(df, output)

    print("=" * 60)
    print("Spark Silver Created")
    print("=" * 60)

    print(df.count())

    spark.stop()


if __name__ == "__main__":
    create_spark_silver()

