# 06 — KPI Definition

## 1. Total Orders
Jumlah order yang termasuk dalam scope analisis.

## 2. Delivered Orders
Order dengan status delivered dan memiliki `order_delivered_customer_date`.

## 3. On-Time Delivery Rate
```text
On-Time Delivery Rate
= On-Time Delivered Orders / Delivered Orders × 100%
```

Definisi on-time:
```text
order_delivered_customer_date <= order_estimated_delivery_date
```

## 4. Late Delivery Rate
```text
Late Delivery Rate
= Late Delivered Orders / Delivered Orders × 100%
```

Definisi late:
```text
order_delivered_customer_date > order_estimated_delivery_date
```

## 5. Average Delivery Time
Jumlah hari dari purchase sampai customer menerima order.

## 6. Average Delay
Rata-rata keterlambatan untuk order yang terlambat.

## 7. Carrier Handover Time
Durasi dari purchase sampai order diserahkan ke carrier. Gunakan indikator ini untuk melihat bottleneck sebelum pengiriman.

## 8. Average Freight Value
Rata-rata nilai freight per order/item sesuai grain analisis.

## 9. Average Review Score
Rata-rata review score sebagai indikator pengalaman customer.

## KPI Guardrails
Semua KPI harus menyebutkan **denominator dan grain**. Hindari kalimat seperti “delivery delay = 12%” tanpa menjelaskan 12% dari apa.
