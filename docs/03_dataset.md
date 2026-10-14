# 03 — Dataset

## Dataset Utama
**Brazilian E-Commerce Public Dataset by Olist** dari Kaggle.

Kaggle: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Dataset mencakup sekitar 100.000 order pada periode 2016–2018 dan terdiri dari beberapa tabel relasional. Olist menjelaskan bahwa data tersebut merupakan data komersial yang telah dianonimkan. Dataset juga secara eksplisit cocok untuk analisis delivery performance. citeturn233979search6

## Tabel yang Diprioritaskan

### Core Delivery
- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_customers_dataset.csv`
- `olist_sellers_dataset.csv`

### Supporting
- `olist_products_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_geolocation_dataset.csv`
- `product_category_name_translation.csv`

## Core Relationships
```text
customers  ──< orders >── sellers
                 |
                 ├──< order_items >── products
                 ├──< payments
                 └──< reviews
```

Catatan penting: satu order dapat memiliki beberapa item dan item yang sama dapat melibatkan seller yang berbeda. Struktur ini harus diperhitungkan agar agregasi order tidak menjadi double count. citeturn233979search6

## Scope Analisis
Unit analisis utama adalah **order** untuk KPI delivery, dengan analisis tambahan pada level seller, customer, product category, dan geography.

## Catatan Etika & Interpretasi
Dataset berasal dari periode 2016–2018. Insight sebaiknya dipresentasikan sebagai **historical operational case study**, bukan sebagai gambaran kondisi logistics Brazil saat ini.
