/*
02 — FACT ORDER DELIVERY | PostgreSQL
Grain: exactly one row per order_id.
Important: aggregate order_items to order grain BEFORE joining to orders.
*/

DROP TABLE IF EXISTS fact_order_delivery;

CREATE TABLE fact_order_delivery AS
WITH item_agg AS (
    SELECT
        order_id,
        COUNT(*)::integer AS item_count,
        COUNT(DISTINCT seller_id)::integer AS seller_count,
        SUM(price)::numeric(14,2) AS order_item_value_brl,
        SUM(freight_value)::numeric(14,2) AS total_freight_value_brl
    FROM olist_order_items_dataset
    GROUP BY order_id
),
review_agg AS (
    -- Reviews can have more than one row per order in some exports; aggregate first.
    SELECT order_id,
           AVG(review_score)::numeric(4,2) AS avg_review_score,
           COUNT(*)::integer AS review_count
    FROM olist_order_reviews_dataset
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_city,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    DATE_TRUNC('month', o.order_purchase_timestamp)::date AS purchase_month,

    COALESCE(i.item_count, 0) AS item_count,
    COALESCE(i.seller_count, 0) AS seller_count,
    COALESCE(i.order_item_value_brl, 0)::numeric(14,2) AS order_item_value_brl,
    COALESCE(i.total_freight_value_brl, 0)::numeric(14,2) AS total_freight_value_brl,

    CASE WHEN o.order_approved_at IS NOT NULL AND o.order_purchase_timestamp IS NOT NULL
         THEN EXTRACT(EPOCH FROM (o.order_approved_at - o.order_purchase_timestamp)) / 86400.0 END
         AS purchase_to_approval_days,
    CASE WHEN o.order_delivered_carrier_date IS NOT NULL AND o.order_purchase_timestamp IS NOT NULL
         THEN EXTRACT(EPOCH FROM (o.order_delivered_carrier_date - o.order_purchase_timestamp)) / 86400.0 END
         AS purchase_to_carrier_days,
    CASE WHEN o.order_delivered_customer_date IS NOT NULL AND o.order_delivered_carrier_date IS NOT NULL
         THEN EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_delivered_carrier_date)) / 86400.0 END
         AS carrier_to_customer_days,
    CASE WHEN o.order_delivered_customer_date IS NOT NULL AND o.order_purchase_timestamp IS NOT NULL
         THEN EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400.0 END
         AS delivery_cycle_days,

    -- Signed calendar-day variance: positive = late, zero = estimate date, negative = early.
    CASE WHEN o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL AND o.order_estimated_delivery_date IS NOT NULL
         THEN (o.order_delivered_customer_date::date - o.order_estimated_delivery_date::date)::integer END
         AS delivery_variance_days,
    CASE WHEN o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL AND o.order_estimated_delivery_date IS NOT NULL
              AND o.order_delivered_customer_date::date > o.order_estimated_delivery_date::date
         THEN (o.order_delivered_customer_date::date - o.order_estimated_delivery_date::date)::integer END
         AS late_days_if_late,

    CASE
      WHEN o.order_status <> 'delivered' THEN 'not_delivered'
      WHEN o.order_delivered_customer_date IS NULL OR o.order_estimated_delivery_date IS NULL THEN 'missing_delivery_date'
      WHEN o.order_delivered_customer_date::date > o.order_estimated_delivery_date::date THEN 'late'
      ELSE 'on_time'
    END AS delivery_result,
    CASE
      WHEN o.order_status IS DISTINCT FROM 'delivered' OR o.order_delivered_customer_date IS NULL OR o.order_estimated_delivery_date IS NULL THEN NULL
      WHEN o.order_delivered_customer_date::date <= o.order_estimated_delivery_date::date THEN TRUE
      ELSE FALSE
    END AS is_on_time,
    CASE
      WHEN o.order_status IS DISTINCT FROM 'delivered' OR o.order_delivered_customer_date IS NULL OR o.order_estimated_delivery_date IS NULL THEN NULL
      WHEN o.order_delivered_customer_date::date > o.order_estimated_delivery_date::date THEN TRUE
      ELSE FALSE
    END AS is_late,

    r.avg_review_score,
    COALESCE(r.review_count, 0) AS review_count
FROM olist_orders_dataset o
LEFT JOIN olist_customers_dataset c ON c.customer_id = o.customer_id
LEFT JOIN item_agg i ON i.order_id = o.order_id
LEFT JOIN review_agg r ON r.order_id = o.order_id;

ALTER TABLE fact_order_delivery ADD PRIMARY KEY (order_id);
CREATE INDEX idx_fact_delivery_purchase_month ON fact_order_delivery (purchase_month);
CREATE INDEX idx_fact_delivery_customer_state ON fact_order_delivery (customer_state);
CREATE INDEX idx_fact_delivery_result ON fact_order_delivery (delivery_result);

-- Build-time QA: these should return total_orders = distinct_order_ids and duplicate_order_ids = 0.
SELECT COUNT(*) AS total_rows, COUNT(DISTINCT order_id) AS distinct_order_ids,
       COUNT(*) - COUNT(DISTINCT order_id) AS duplicate_order_ids
FROM fact_order_delivery;

SELECT delivery_result, COUNT(*) AS orders
FROM fact_order_delivery
GROUP BY delivery_result ORDER BY orders DESC;
