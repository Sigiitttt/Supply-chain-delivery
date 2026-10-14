# 05 — Data Quality Plan

## Pemeriksaan
Sebelum analisis, lakukan:

1. **Row count & uniqueness** pada setiap tabel.
2. Missing values untuk seluruh timestamp penting.
3. Duplicate key pada tabel utama.
4. Konsistensi relationship antar tabel.
5. Validasi tanggal: purchase <= approval <= carrier delivery <= customer delivery.
6. Validasi bahwa order cancelled/unavailable tidak dipaksa menjadi order delivered.
7. Outlier pada delivery duration dan freight value.
8. Risiko duplicate count ketika join one-to-many tables.

## Prinsip Penting
Jangan mengisi timestamp delivery yang hilang secara sembarang. Missing delivery date dapat berarti order belum selesai atau status tertentu.

## Analytical Dataset
Buat satu tabel turunan, misalnya `fact_order_delivery`, dengan grain:

> **1 row = 1 order**

Kolom turunan utama:
- `delivery_days`
- `estimated_delivery_days`
- `delivery_delay_days`
- `is_late`
- `approval_days`
- `carrier_handover_days`
- `purchase_month`
- `customer_state`
- `seller_state`
- `order_value`
- `freight_value`
- `review_score`

## Data Leakage
Jangan menggunakan informasi yang hanya diketahui setelah customer menerima barang ketika membuat analisis **pre-delivery risk**. Untuk dashboard historical performance, post-delivery fields boleh digunakan.
