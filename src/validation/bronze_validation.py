import pandera.pandas as pa
from pandera import Check

from src.monitoring.logger import get_logger
from src.storage.file_handler import FileHandler
from src.validation.validation_utils import save_validation_report

logger = get_logger("bronze")


BronzeSchema = pa.DataFrameSchema(
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


def validate_bronze(file_path):

    df = FileHandler.read(file_path)

    if df.empty:
        save_validation_report("bronze", False, "Dataset is empty.")
        raise ValueError("Dataset is empty")

    if len(df) < 100000:
        save_validation_report("bronze", False, f"Unexpected row count: {len(df)}")
        raise ValueError("Bronze dataset row count is lower than expected.")

    BronzeSchema.validate(df)

    save_validation_report("bronze", True, "Bronze validation passed.")

    logger.info("✅ Bronze validation passed.")


if __name__ == "__main__":

    validate_bronze("data/bronze/historical/bronze_orders.csv")
