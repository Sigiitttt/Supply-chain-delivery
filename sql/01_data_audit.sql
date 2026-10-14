/*
01 — DATA AUDIT | PostgreSQL
Prerequisite: import Olist CSVs into tables using their original basename.
Run the sections independently and document findings before transforming data.
*/

-- A. Row counts: compare volumes across source tables.
SELECT 'olist_orders_dataset' AS table_name, COUNT(*) AS row_count FROM olist_orders_dataset
UNION ALL SELECT 'olist_order_items_dataset', COUNT(*) FROM olist_order_items_dataset
UNION ALL SELECT 'olist_customers_dataset', COUNT(*) FROM olist_customers_dataset
UNION ALL SELECT 'olist_sellers_dataset', COUNT(*) FROM olist_sellers_dataset
UNION ALL SELECT 'olist_products_dataset', COUNT(*) FROM olist_products_dataset
UNION ALL SELECT 'olist_order_payments_dataset', COUNT(*) FROM olist_order_payments_dataset
UNION ALL SELECT 'olist_order_reviews_dataset', COUNT(*) FROM olist_order_reviews_dataset
ORDER BY table_name;

-- B. Duplicate primary/business keys. Expected result: zero rows for true keys.
SELECT order_id, COUNT(*) AS rows_per_key
FROM olist_orders_dataset
GROUP BY order_id HAVING COUNT(*) > 1 ORDER BY rows_per_key DESC;

SELECT customer_id, COUNT(*) AS rows_per_key
FROM olist_customers_dataset
GROUP BY customer_id HAVING COUNT(*) > 1 ORDER BY rows_per_key DESC;

SELECT seller_id, COUNT(*) AS rows_per_key
FROM olist_sellers_dataset
GROUP BY seller_id HAVING COUNT(*) > 1 ORDER BY rows_per_key DESC;

SELECT order_id, order_item_id, COUNT(*) AS rows_per_key
FROM olist_order_items_dataset
GROUP BY order_id, order_item_id HAVING COUNT(*) > 1 ORDER BY rows_per_key DESC;

SELECT order_id, payment_sequential, COUNT(*) AS rows_per_key
FROM olist_order_payments_dataset
GROUP BY order_id, payment_sequential HAVING COUNT(*) > 1 ORDER BY rows_per_key DESC;

-- C. Null checks on delivery-critical columns.
SELECT
  COUNT(*) AS total_orders,
  COUNT(*) FILTER (WHERE order_id IS NULL) AS null_order_id,
  COUNT(*) FILTER (WHERE customer_id IS NULL) AS null_customer_id,
  COUNT(*) FILTER (WHERE order_purchase_timestamp IS NULL) AS null_purchase_ts,
  COUNT(*) FILTER (WHERE order_delivered_carrier_date IS NULL) AS null_carrier_ts,
  COUNT(*) FILTER (WHERE order_delivered_customer_date IS NULL) AS null_actual_delivery_ts,
  COUNT(*) FILTER (WHERE order_estimated_delivery_date IS NULL) AS null_estimated_delivery_ts
FROM olist_orders_dataset;

-- D. Status distribution. Do not assume every order should have a delivery timestamp.
SELECT order_status, COUNT(*) AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_all_orders
FROM olist_orders_dataset
GROUP BY order_status
ORDER BY orders DESC;

-- E. Date range and milestone chronology.
SELECT
  MIN(order_purchase_timestamp) AS first_purchase_ts,
  MAX(order_purchase_timestamp) AS last_purchase_ts,
  MIN(order_delivered_customer_date) AS first_actual_delivery_ts,
  MAX(order_delivered_customer_date) AS last_actual_delivery_ts,
  MIN(order_estimated_delivery_date) AS first_estimated_delivery_date,
  MAX(order_estimated_delivery_date) AS last_estimated_delivery_date
FROM olist_orders_dataset;

SELECT order_id, order_status,
       order_purchase_timestamp, order_approved_at,
       order_delivered_carrier_date, order_delivered_customer_date,
       order_estimated_delivery_date,
       CASE WHEN order_approved_at < order_purchase_timestamp THEN 'approval_before_purchase'
            WHEN order_delivered_carrier_date < order_purchase_timestamp THEN 'carrier_before_purchase'
            WHEN order_delivered_customer_date < order_purchase_timestamp THEN 'delivery_before_purchase'
            WHEN order_delivered_customer_date < order_delivered_carrier_date THEN 'delivery_before_carrier_handover'
            ELSE 'check_other' END AS anomaly_type
FROM olist_orders_dataset
WHERE (order_approved_at < order_purchase_timestamp)
   OR (order_delivered_carrier_date < order_purchase_timestamp)
   OR (order_delivered_customer_date < order_purchase_timestamp)
   OR (order_delivered_customer_date < order_delivered_carrier_date)
ORDER BY order_purchase_timestamp
LIMIT 200;

-- F. Delivered orders with missing milestones and non-delivered orders with delivery dates.
SELECT order_status,
       COUNT(*) AS total_orders,
       COUNT(*) FILTER (WHERE order_delivered_customer_date IS NULL) AS missing_actual_delivery,
       COUNT(*) FILTER (WHERE order_estimated_delivery_date IS NULL) AS missing_estimate,
       COUNT(*) FILTER (WHERE order_delivered_customer_date IS NOT NULL) AS has_actual_delivery
FROM olist_orders_dataset
GROUP BY order_status ORDER BY order_status;

-- G. Referential-integrity checks. Expected orphan counts are ideally zero.
SELECT 'orders -> customers' AS relationship, COUNT(*) AS orphan_rows
FROM olist_orders_dataset o LEFT JOIN olist_customers_dataset c ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL
UNION ALL
SELECT 'items -> orders', COUNT(*)
FROM olist_order_items_dataset i LEFT JOIN olist_orders_dataset o ON o.order_id = i.order_id
WHERE o.order_id IS NULL
UNION ALL
SELECT 'items -> sellers', COUNT(*)
FROM olist_order_items_dataset i LEFT JOIN olist_sellers_dataset s ON s.seller_id = i.seller_id
WHERE s.seller_id IS NULL
UNION ALL
SELECT 'items -> products', COUNT(*)
FROM olist_order_items_dataset i LEFT JOIN olist_products_dataset p ON p.product_id = i.product_id
WHERE p.product_id IS NULL
ORDER BY relationship;

-- H. Item-table grain and basic value checks.
SELECT
  COUNT(*) AS item_rows,
  COUNT(DISTINCT order_id) AS orders_with_items,
  COUNT(*) FILTER (WHERE price IS NULL) AS null_price_rows,
  COUNT(*) FILTER (WHERE freight_value IS NULL) AS null_freight_rows,
  COUNT(*) FILTER (WHERE price < 0) AS negative_price_rows,
  COUNT(*) FILTER (WHERE freight_value < 0) AS negative_freight_rows
FROM olist_order_items_dataset;

-- I. Potential join multiplication check: aggregate items BEFORE joining to order-level rows.
SELECT
  (SELECT COUNT(*) FROM olist_orders_dataset) AS order_source_rows,
  (SELECT COUNT(DISTINCT order_id) FROM olist_orders_dataset) AS distinct_orders,
  (SELECT COUNT(*) FROM olist_order_items_dataset) AS item_source_rows,
  (SELECT COUNT(DISTINCT order_id) FROM olist_order_items_dataset) AS distinct_orders_in_items;
