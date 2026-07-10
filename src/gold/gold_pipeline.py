import pandas as pd

from src.utils.logger import logger

from src.config.settings import (
    SILVER_DATASET,
    GOLD_DIR,
    GOLD_DAILY_SALES,
    GOLD_MONTHLY_SALES,
    GOLD_TOP_PRODUCTS,
    GOLD_TOP_STATES,
    GOLD_PAYMENT_SUMMARY,
    GOLD_SELLER_PERFORMANCE,
    GOLD_DELIVERY_SUMMARY,
)


def _find_column(df, possible_names):
    """Return the first matching column."""

    for column in possible_names:
        if column in df.columns:
            return column

    return None


def _save(df, output_path, name):
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"{name} created -> {output_path}")


def _prepare_dates(df):
    purchase_column = _find_column(
        df,
        [
            "order_purchase_timestamp",
            "purchase_timestamp",
        ],
    )

    if purchase_column:
        df[purchase_column] = pd.to_datetime(df[purchase_column])
        df["order_date"] = df[purchase_column].dt.date
        df["order_month"] = df[purchase_column].dt.to_period("M").astype(str)

    return df


def _create_daily_sales(df):
    daily = (
        df.groupby("order_date")
        .agg(
            total_orders=("order_id", "nunique"),
            total_revenue=("payment_value", "sum"),
            average_order_value=("payment_value", "mean"),
        )
        .reset_index()
        .sort_values("order_date")
    )

    _save(daily, GOLD_DAILY_SALES, "Daily Sales")


def _create_monthly_sales(df):
    monthly = (
        df.groupby("order_month")
        .agg(
            total_orders=("order_id", "nunique"),
            total_revenue=("payment_value", "sum"),
            average_order_value=("payment_value", "mean"),
        )
        .reset_index()
        .sort_values("order_month")
    )

    _save(monthly, GOLD_MONTHLY_SALES, "Monthly Sales")


def _create_top_products(df):
    product_column = _find_column(
        df,
        [
            "product_category_name",
            "product_category",
        ],
    )

    if product_column is None:
        logger.warning("Product category column not found.")
        return

    top_products = (
        df.groupby(product_column)
        .agg(
            total_orders=("order_id", "count"),
            total_revenue=("payment_value", "sum"),
            average_price=("price", "mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
        .head(10)
    )

    _save(
        top_products,
        GOLD_TOP_PRODUCTS,
        "Top Products",
    )


def _create_top_states(df):
    state_column = _find_column(
        df,
        [
            "customer_state",
        ],
    )

    if state_column is None:
        logger.warning("Customer state column not found.")
        return

    top_states = (
        df.groupby(state_column)
        .agg(
            total_orders=("order_id", "count"),
            total_revenue=("payment_value", "sum"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
    )

    _save(
        top_states,
        GOLD_TOP_STATES,
        "Top States",
    )


def _create_payment_summary(df):
    payment_column = _find_column(
        df,
        [
            "payment_type",
        ],
    )

    if payment_column is None:
        logger.warning("Payment type column not found.")
        return

    payment_summary = (
        df.groupby(payment_column)
        .agg(
            total_transactions=("order_id", "count"),
            total_amount=("payment_value", "sum"),
            average_payment=("payment_value", "mean"),
        )
        .reset_index()
        .sort_values("total_amount", ascending=False)
    )

    _save(
        payment_summary,
        GOLD_PAYMENT_SUMMARY,
        "Payment Summary",
    )


def _create_seller_performance(df):
    seller_column = _find_column(
        df,
        [
            "seller_id",
        ],
    )

    if seller_column is None:
        logger.warning("Seller column not found.")
        return

    seller_performance = (
        df.groupby(seller_column)
        .agg(
            total_orders=("order_id", "count"),
            total_revenue=("payment_value", "sum"),
            average_order_value=("payment_value", "mean"),
        )
        .reset_index()
        .sort_values("total_revenue", ascending=False)
        .head(20)
    )

    _save(
        seller_performance,
        GOLD_SELLER_PERFORMANCE,
        "Seller Performance",
    )


def _create_delivery_summary(df):
    delivered_column = _find_column(
        df,
        [
            "order_delivered_customer_date",
        ],
    )

    purchase_column = _find_column(
        df,
        [
            "order_purchase_timestamp",
        ],
    )

    if delivered_column is None or purchase_column is None:
        logger.warning("Delivery date columns not found.")
        return

    delivery_df = df.copy()

    delivery_df[purchase_column] = pd.to_datetime(
        delivery_df[purchase_column],
        errors="coerce",
    )

    delivery_df[delivered_column] = pd.to_datetime(
        delivery_df[delivered_column],
        errors="coerce",
    )

    delivery_df["delivery_days"] = (
        delivery_df[delivered_column]
        - delivery_df[purchase_column]
    ).dt.days

    summary = pd.DataFrame(
        {
            "average_delivery_days": [
                delivery_df["delivery_days"].mean()
            ],
            "minimum_delivery_days": [
                delivery_df["delivery_days"].min()
            ],
            "maximum_delivery_days": [
                delivery_df["delivery_days"].max()
            ],
        }
    )

    _save(
        summary,
        GOLD_DELIVERY_SUMMARY,
        "Delivery Summary",
    )


def create_gold_layer():
    logger.info("=" * 60)
    logger.info("Creating Gold Layer")
    logger.info("=" * 60)

    df = pd.read_csv(SILVER_DATASET)
    df = _prepare_dates(df)

    _create_daily_sales(df)

    _create_monthly_sales(df)

    _create_top_products(df)

    _create_top_states(df)

    _create_payment_summary(df)

    _create_seller_performance(df)

    _create_delivery_summary(df)

    logger.info("=" * 60)
    logger.info("Gold Layer Completed Successfully")
    logger.info("=" * 60)



if __name__ == "__main__":
    create_gold_layer()

