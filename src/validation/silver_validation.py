import pandera.pandas as pa
from pandera import Check

from src.monitoring.logger import get_logger
from src.storage.file_handler import FileHandler
from src.validation.validation_utils import save_validation_report

logger = get_logger("silver")


SilverSchema = pa.DataFrameSchema(
    {
        "order_id": pa.Column(str, nullable=False),
        "order_item_id": pa.Column(int, nullable=False),
        "customer_id": pa.Column(str, nullable=False),
        "product_id": pa.Column(str, nullable=False),
        "seller_id": pa.Column(str, nullable=False),
        "price": pa.Column(float, Check.ge(0), nullable=False),
        "freight_value": pa.Column(float, Check.ge(0), nullable=False),
        "payment_value": pa.Column(float, Check.ge(0), nullable=False),
        "order_purchase_timestamp": pa.Column(str, nullable=False),
        "order_status": pa.Column(str, nullable=False),
    },
    strict=False,
    coerce=True,
)


def validate_silver(file_path):

    df = FileHandler.read(file_path)

    # 1. Empty dataset check
    if df.empty:
        save_validation_report("silver", False, "Dataset is empty.")
        raise ValueError("Silver dataset is empty.")

    # 2. Schema validation
    SilverSchema.validate(df)

    # 3. Row count validation
    if len(df) < 100000:
        save_validation_report("silver", False, f"Unexpected row count: {len(df)}")
        raise ValueError("Silver dataset row count is lower than expected.")

    # 4. order_status validation
    allowed_status = {
        "approved",
        "canceled",
        "created",
        "delivered",
        "invoiced",
        "processing",
        "shipped",
        "unavailable",
    }

    invalid = ~df["order_status"].isin(allowed_status)

    if invalid.any():
        save_validation_report("silver", False, "Invalid order_status values found.")
        raise ValueError("Invalid order_status values detected.")

    # 5. Duplicate rows check
    duplicate_rows = df.duplicated().sum()

    if duplicate_rows > 0:
        save_validation_report(
            "silver", False, f"{duplicate_rows} exact duplicate rows found."
        )
        raise ValueError("Exact duplicate rows detected.")

    save_validation_report("silver", True, "Silver validation passed successfully.")

    logger.info("✅ Silver validation passed.")


if __name__ == "__main__":
    validate_silver("data/silver/silver_orders.csv")
