/*
04 — DELIVERY KPI & EXPLORATORY QUERIES | PostgreSQL
Read KPI definitions in docs/06_kpi_definition.md before interpreting results.
*/

-- A. Overall KPI. On-time/late denominator = orders with usable actual + estimated delivery dates.
SELECT
  COUNT(*) AS all_orders_in_scope,
  COUNT(*) FILTER (WHERE order_status = 'delivered') AS delivered_status_orders,
  COUNT(*) FILTER (WHERE delivery_result IN ('on_time','late')) AS evaluable_delivered_orders,
  COUNT(*) FILTER (WHERE delivery_result = 'on_time') AS on_time_orders,
  COUNT(*) FILTER (WHERE delivery_result = 'late') AS late_orders,
  ROUND(100.0 * COUNT(*) FILTER (WHERE delivery_result = 'on_time') /
        NULLIF(COUNT(*) FILTER (WHERE delivery_result IN ('on_time','late')), 0), 2) AS on_time_rate_pct,
  ROUND(100.0 * COUNT(*) FILTER (WHERE delivery_result = 'late') /
        NULLIF(COUNT(*) FILTER (WHERE delivery_result IN ('on_time','late')), 0), 2) AS late_rate_pct,
  ROUND(AVG(delivery_cycle_days) FILTER (WHERE delivery_result IN ('on_time','late'))::numeric, 2) AS avg_delivery_cycle_days,
  ROUND(AVG(late_days_if_late)::numeric, 2) AS avg_delay_days_among_late_orders,
  COUNT(*) FILTER (WHERE delivery_result = 'missing_delivery_date') AS delivered_but_dates_missing
FROM fact_order_delivery;

-- B. Monthly delivery performance by purchase month. Small or incomplete final months need context.
SELECT purchase_month,
       COUNT(*) FILTER (WHERE delivery_result IN ('on_time','late')) AS evaluable_delivered_orders,
       COUNT(*) FILTER (WHERE delivery_result = 'on_time') AS on_time_orders,
       COUNT(*) FILTER (WHERE delivery_result = 'late') AS late_orders,
       ROUND(100.0 * COUNT(*) FILTER (WHERE delivery_result = 'late') /
             NULLIF(COUNT(*) FILTER (WHERE delivery_result IN ('on_time','late')), 0), 2) AS late_rate_pct,
       ROUND(AVG(delivery_cycle_days) FILTER (WHERE delivery_result IN ('on_time','late'))::numeric, 2) AS avg_delivery_cycle_days,
       ROUND(AVG(late_days_if_late)::numeric, 2) AS avg_delay_days_among_late_orders
FROM fact_order_delivery
GROUP BY purchase_month
ORDER BY purchase_month;

-- C. Customer state performance. Always show sample size alongside rates.
SELECT customer_state,
       COUNT(*) FILTER (WHERE delivery_result IN ('on_time','late')) AS evaluable_delivered_orders,
       ROUND(100.0 * COUNT(*) FILTER (WHERE delivery_result = 'late') /
             NULLIF(COUNT(*) FILTER (WHERE delivery_result IN ('on_time','late')), 0), 2) AS late_rate_pct,
       ROUND(AVG(delivery_cycle_days) FILTER (WHERE delivery_result IN ('on_time','late'))::numeric, 2) AS avg_delivery_cycle_days
FROM fact_order_delivery
GROUP BY customer_state
HAVING COUNT(*) FILTER (WHERE delivery_result IN ('on_time','late')) >= 100
ORDER BY late_rate_pct DESC NULLS LAST;

-- D. Seller performance. Grain is order-seller pair; require >=50 evaluable order-seller pairs by default.
SELECT seller_id, seller_state,
       COUNT(*) FILTER (WHERE delivery_result IN ('on_time','late')) AS evaluable_order_seller_pairs,
       ROUND(100.0 * COUNT(*) FILTER (WHERE delivery_result = 'late') /
             NULLIF(COUNT(*) FILTER (WHERE delivery_result IN ('on_time','late')), 0), 2) AS late_rate_pct,
       ROUND(AVG(delivery_variance_days) FILTER (WHERE delivery_result IN ('on_time','late'))::numeric, 2) AS avg_signed_variance_days
FROM fact_order_seller_delivery
GROUP BY seller_id, seller_state
HAVING COUNT(*) FILTER (WHERE delivery_result IN ('on_time','late')) >= 50
ORDER BY late_rate_pct DESC NULLS LAST;

-- E. Delivery result versus average review score: association only, not causal evidence.
SELECT delivery_result, COUNT(*) AS orders,
       ROUND(AVG(avg_review_score)::numeric, 2) AS avg_review_score,
       ROUND(100.0 * COUNT(*) FILTER (WHERE avg_review_score IS NOT NULL) / COUNT(*), 2) AS pct_with_review
FROM fact_order_delivery
GROUP BY delivery_result
ORDER BY orders DESC;

-- F. Explore long delivery cycle outliers (review the records before deciding whether to exclude).
SELECT order_id, order_status, customer_state, seller_count,
       delivery_cycle_days, delivery_variance_days, order_purchase_timestamp,
       order_delivered_customer_date, order_estimated_delivery_date
FROM fact_order_delivery
WHERE delivery_cycle_days >= 30
ORDER BY delivery_cycle_days DESC NULLS LAST
LIMIT 100;
