/*
03 — SELLER DELIVERY FACT | PostgreSQL
Grain: one row per distinct order_id + seller_id pair.
Do not use item rows as an order count: an order may contain multiple items for the same seller.
*/

DROP TABLE IF EXISTS fact_order_seller_delivery;

CREATE TABLE fact_order_seller_delivery AS
WITH order_seller_items AS (
    SELECT order_id, seller_id,
           COUNT(*)::integer AS seller_item_count,
           SUM(price)::numeric(14,2) AS seller_item_value_brl,
           SUM(freight_value)::numeric(14,2) AS seller_freight_value_brl
    FROM olist_order_items_dataset
    GROUP BY order_id, seller_id
)
SELECT
    oi.order_id,
    oi.seller_id,
    s.seller_city,
    s.seller_state,
    o.customer_id,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    DATE_TRUNC('month', o.order_purchase_timestamp)::date AS purchase_month,
    oi.seller_item_count,
    oi.seller_item_value_brl,
    oi.seller_freight_value_brl,
    CASE WHEN o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL AND o.order_estimated_delivery_date IS NOT NULL
         THEN (o.order_delivered_customer_date::date - o.order_estimated_delivery_date::date)::integer END
         AS delivery_variance_days,
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
    END AS is_late
FROM order_seller_items oi
JOIN olist_orders_dataset o ON o.order_id = oi.order_id
LEFT JOIN olist_sellers_dataset s ON s.seller_id = oi.seller_id
LEFT JOIN olist_customers_dataset c ON c.customer_id = o.customer_id;

ALTER TABLE fact_order_seller_delivery ADD PRIMARY KEY (order_id, seller_id);
CREATE INDEX idx_seller_delivery_seller_id ON fact_order_seller_delivery (seller_id);
CREATE INDEX idx_seller_delivery_purchase_month ON fact_order_seller_delivery (purchase_month);

SELECT COUNT(*) AS total_order_seller_rows,
       COUNT(DISTINCT (order_id, seller_id)) AS distinct_order_seller_pairs
FROM fact_order_seller_delivery;
