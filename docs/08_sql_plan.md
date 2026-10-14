# 08 — SQL Analysis Plan

## SQL Objectives
SQL digunakan untuk membangun analytical dataset dan menjawab KPI utama.

## Query Modules

### 01 — Data Audit
- row count
- null check
- duplicate check
- distinct key

### 02 — Core Order Table
Gabungkan `orders` dengan customer, seller, dan agregasi order items pada level order.

### 03 — Delivery KPI
Hitung:
- delivered orders
- on-time orders
- late orders
- late rate
- average delivery days
- average delay days

### 04 — Monthly Performance
Group by month untuk melihat trend KPI.

### 05 — Seller Performance
Gunakan threshold, contoh:
```text
seller dengan >= 50 delivered orders
```
Threshold harus dijelaskan dan dapat disesuaikan.

### 06 — Geographic Performance
Bandingkan performance berdasarkan customer state dan seller state.

### 07 — Review Relationship
Join review secara aman agar satu order tidak terhitung berkali-kali.

## SQL Quality Rule
Setiap query final harus jelas:
- grain data,
- filter scope,
- denominator KPI,
- join logic.
