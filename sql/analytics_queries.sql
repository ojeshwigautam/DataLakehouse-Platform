-- =========================================================
-- Unified Commerce Lakehouse
-- PostgreSQL Analytics Queries
-- =========================================================


-- ---------------------------------------------------------
-- 1. Daily Sales
-- ---------------------------------------------------------

SELECT *
FROM daily_sales
ORDER BY 1 DESC
LIMIT 20;


-- ---------------------------------------------------------
-- 2. Monthly Sales
-- ---------------------------------------------------------

SELECT *
FROM monthly_sales
ORDER BY 1 DESC;


-- ---------------------------------------------------------
-- 3. Top Products
-- ---------------------------------------------------------

SELECT *
FROM top_products
LIMIT 10;


-- ---------------------------------------------------------
-- 4. Top Customer States
-- ---------------------------------------------------------

SELECT *
FROM top_states
LIMIT 10;


-- ---------------------------------------------------------
-- 5. Payment Method Analysis
-- ---------------------------------------------------------

SELECT *
FROM payment_summary
ORDER BY 1;


-- ---------------------------------------------------------
-- 6. Seller Performance
-- ---------------------------------------------------------

SELECT *
FROM seller_performance
LIMIT 20;


-- ---------------------------------------------------------
-- 7. Delivery Performance
-- ---------------------------------------------------------

SELECT *
FROM delivery_summary;


-- ---------------------------------------------------------
-- 8. Database Table Row Counts
-- ---------------------------------------------------------

SELECT 'daily_sales' AS table_name, COUNT(*) AS row_count
FROM daily_sales

UNION ALL

SELECT 'monthly_sales', COUNT(*)
FROM monthly_sales

UNION ALL

SELECT 'top_products', COUNT(*)
FROM top_products

UNION ALL

SELECT 'top_states', COUNT(*)
FROM top_states

UNION ALL

SELECT 'payment_summary', COUNT(*)
FROM payment_summary

UNION ALL

SELECT 'seller_performance', COUNT(*)
FROM seller_performance

UNION ALL

SELECT 'delivery_summary', COUNT(*)
FROM delivery_summary;

