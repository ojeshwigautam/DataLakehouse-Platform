from pyspark.sql import Row

from src.spark.gold_transforms import (
    daily_sales,
    delivery_summary,
    monthly_sales,
    payment_summary,
    seller_performance,
    top_products,
    top_states,
)


def test_daily_sales_aggregates_orders_and_revenue(spark):
    df = spark.createDataFrame(
        [
            Row(
                order_purchase_timestamp="2026-01-01 10:00:00",
                orders="o1",
                revenue=10.0,
                payment_value=10.0,
            ),
            Row(
                order_purchase_timestamp="2026-01-01 12:00:00",
                orders="o2",
                revenue=20.0,
                payment_value=20.0,
            ),
            Row(
                order_purchase_timestamp="2026-01-02 09:00:00",
                orders="o3",
                revenue=5.0,
                payment_value=5.0,
            ),
        ]
    )

    out = daily_sales(df).collect()
    out_map = {r["purchase_date"].isoformat(): r.asDict() for r in out}

    assert out_map["2026-01-01"]["orders"] == 2
    assert out_map["2026-01-01"]["revenue"] == 30.0
    assert out_map["2026-01-02"]["orders"] == 1
    assert out_map["2026-01-02"]["revenue"] == 5.0


def test_monthly_sales_aggregates(spark):
    df = spark.createDataFrame(
        [
            Row(
                order_purchase_timestamp="2026-01-01 10:00:00",
                orders="o1",
                revenue=10.0,
            ),
            Row(
                order_purchase_timestamp="2026-01-15 10:00:00",
                orders="o2",
                revenue=20.0,
            ),
            Row(
                order_purchase_timestamp="2026-02-01 10:00:00", orders="o3", revenue=5.0
            ),
        ]
    )

    out = monthly_sales(df).collect()
    out_map = {r["month"]: r.asDict() for r in out}

    assert out_map["2026-01"]["orders"] == 2
    assert out_map["2026-01"]["revenue"] == 30.0
    assert out_map["2026-02"]["orders"] == 1
    assert out_map["2026-02"]["revenue"] == 5.0


def test_seller_performance_aggregates_and_avg_delivery_days(spark):
    df = spark.createDataFrame(
        [
            Row(
                seller_id="s1",
                order_purchase_timestamp="2026-01-01 00:00:00",
                order_delivered_customer_date="2026-01-11 00:00:00",
                orders="o1",
                payment_value=10.0,
            ),
            Row(
                seller_id="s1",
                order_purchase_timestamp="2026-01-05 00:00:00",
                order_delivered_customer_date="2026-01-08 00:00:00",
                orders="o2",
                payment_value=20.0,
            ),
            Row(
                seller_id="s2",
                order_purchase_timestamp="2026-01-06 00:00:00",
                order_delivered_customer_date=None,
                orders="o3",
                payment_value=5.0,
            ),
        ]
    )

    out = seller_performance(df).collect()
    out_map = {r["seller_id"]: r.asDict() for r in out}

    assert out_map["s1"]["orders"] == 2
    assert out_map["s1"]["revenue"] == 30.0
    # avg_delivery_days: (10 days, 3 days) => 6.5
    assert float(out_map["s1"]["avg_delivery_days"]) == 6.5

    assert out_map["s2"]["orders"] == 1
    assert out_map["s2"]["revenue"] == 5.0


def test_payment_summary_groups_by_payment_type(spark):
    df = spark.createDataFrame(
        [
            Row(payment_type="credit", order_id="o1", payment_value=10.0),
            Row(payment_type="credit", order_id="o2", payment_value=20.0),
            Row(payment_type="cash", order_id="o3", payment_value=5.0),
        ]
    )

    out = payment_summary(df).collect()
    out_map = {r["payment_type"]: r.asDict() for r in out}

    assert out_map["credit"]["orders"] == 2
    assert out_map["credit"]["total_payment"] == 30.0
    assert out_map["cash"]["orders"] == 1
    assert out_map["cash"]["total_payment"] == 5.0


def test_delivery_summary_produces_delivery_status_and_avg_delivery_days(spark):
    df = spark.createDataFrame(
        [
            Row(
                order_purchase_timestamp="2026-01-01 00:00:00",
                order_delivered_customer_date="2026-01-11 00:00:00",
            ),
            Row(
                order_purchase_timestamp="2026-01-05 00:00:00",
                order_delivered_customer_date=None,
            ),
        ]
    )

    out = delivery_summary(df).collect()
    out_map = {r["delivery_status"]: r.asDict() for r in out}

    assert "delivered" in out_map
    assert "not_delivered" in out_map
    assert float(out_map["delivered"]["avg_delivery_days"]) == 10.0


def test_top_products_and_top_states(spark):
    df = spark.createDataFrame(
        [
            Row(
                product_category="cat1", customer_state="CA", orders="o1", revenue=10.0
            ),
            Row(
                product_category="cat1", customer_state="CA", orders="o2", revenue=20.0
            ),
            Row(product_category="cat2", customer_state="NY", orders="o3", revenue=5.0),
        ]
    )

    top_prod = top_products(df).collect()
    assert top_prod[0]["product_category"] == "cat1"
    assert float(top_prod[0]["revenue"]) == 30.0

    top_st = top_states(df).collect()
    assert top_st[0]["customer_state"] == "CA"
    assert float(top_st[0]["revenue"]) == 30.0
