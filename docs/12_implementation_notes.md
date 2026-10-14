# 12 — Implementation Notes: SQL Audit and Analytical Tables

## Source tables
Import Olist CSVs into PostgreSQL using the CSV basename without the suffix `.csv`. Use the exact column spellings in the source, including any source-specific spelling such as `product_name_lenght` in the products table. This project does not require renaming source columns to build the delivery fact.

## Why two facts?
- `fact_order_delivery`: one row per order; use it for top-line delivery KPIs and monthly / customer geography performance.
- `fact_order_seller_delivery`: one row per distinct order–seller pair; use it for seller performance. An order containing items from two sellers appears twice in this table, by design, so do not sum order-level totals from it as if it were a one-row-per-order table.

## KPI denominator
The primary on-time/late denominator is **delivered-status orders with both actual and estimated delivery timestamps available**. This can be smaller than `order_status = 'delivered'` counts. Report the evaluable denominator and missing-date count along with rates.

## Delivery date comparison
The on-time rule compares `order_delivered_customer_date::date` to `order_estimated_delivery_date::date`. It treats delivery on the estimated calendar date as on-time; a positive `delivery_variance_days` means late; zero means delivered on estimate date; negative means early. Average late delay uses only late orders.

## Important limitations
1. The dataset is historical (2016–2018), so frame conclusions as a historical case study, not current logistics performance.
2. This is observational data. Associations between delivery delay, geography, seller, and reviews do not prove causality.
3. `order_item_value_brl` sums product price only; freight is stored separately. It is not profit or full company revenue.
4. The order-level `seller_count` and item/freight sums come from pre-aggregated order items; joining raw item rows directly to order rows would inflate order counts.
5. Check each SQL query's result against audit findings before publishing any KPI.

## Run order
See `sql/README.md`. Record actual audit results and unexpected anomalies in a new results log rather than writing unverified values into documentation.
