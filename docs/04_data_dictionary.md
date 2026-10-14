# 04 — Data Dictionary

Kolom yang paling relevan untuk proyek delivery analytics.

## Orders
| Column | Peran | Keterangan |
|---|---|---|
| `order_id` | Key | ID order |
| `customer_id` | Key | ID customer pada order |
| `order_status` | Dimension | Status order |
| `order_purchase_timestamp` | Date | Waktu order dibuat |
| `order_approved_at` | Date | Waktu pembayaran/order disetujui |
| `order_delivered_carrier_date` | Date | Waktu order diserahkan ke carrier |
| `order_delivered_customer_date` | Date | Waktu order diterima customer |
| `order_estimated_delivery_date` | Date | Estimasi delivery |

## Order Items
| Column | Peran | Keterangan |
|---|---|---|
| `order_id` | Key | Relasi ke orders |
| `product_id` | Key | Relasi ke products |
| `seller_id` | Key | Relasi ke sellers |
| `price` | KPI | Harga item |
| `freight_value` | KPI | Nilai freight/shipping |

## Customers
| Column | Peran | Keterangan |
|---|---|---|
| `customer_id` | Key | ID customer pada order |
| `customer_unique_id` | Business Key | ID customer unik lintas order |
| `customer_city` | Dimension | Kota customer |
| `customer_state` | Dimension | State customer |

## Sellers
| Column | Peran | Keterangan |
|---|---|---|
| `seller_id` | Key | ID seller |
| `seller_city` | Dimension | Kota seller |
| `seller_state` | Dimension | State seller |

## Reviews
| Column | Peran | Keterangan |
|---|---|---|
| `order_id` | Key | Relasi ke orders |
| `review_score` | KPI | Skor review 1–5 |

Definisi akhir dan transformasi kolom akan dicatat kembali setelah data audit dilakukan.
