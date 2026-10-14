# SQL — PostgreSQL

File SQL menganggap file CSV Olist sudah diimpor ke PostgreSQL dengan nama tabel sesuai nama file tanpa `.csv`, misalnya `olist_orders_dataset` dan `olist_order_items_dataset`.

## Urutan menjalankan
1. Impor tabel inti dari CSV: `olist_orders_dataset`, `olist_order_items_dataset`, `olist_customers_dataset`, `olist_sellers_dataset`.
2. Impor juga tabel `olist_products_dataset` dan `olist_order_payments_dataset` untuk audit relasi tambahan jika tersedia.
3. Jalankan `01_data_audit.sql`, baca hasilnya, dan catat anomali; jangan menghapus baris otomatis.
4. Jalankan `02_build_fact_order_delivery.sql` untuk membuat tabel dengan satu baris per order.
5. Jalankan `03_build_fact_order_seller_delivery.sql` untuk tabel analisis seller dengan grain satu baris per kombinasi order–seller.
6. Jalankan `04_kpi_analysis.sql` untuk ringkasan KPI dan analisis awal.

**Dialect:** PostgreSQL 14+.

## Definisi penting
- Grain `fact_order_delivery`: satu baris = satu `order_id`.
- Grain `fact_order_seller_delivery`: satu baris = satu pasangan unik `order_id` + `seller_id`.
- Order yang belum terkirim atau memiliki tanggal aktual/estimasi yang tidak tersedia tidak boleh diam-diam diklasifikasikan sebagai on-time maupun late.
- Untuk membandingkan aktual dengan estimasi, perbandingan memakai kalender tanggal (`::date`). Kolom estimasi Olist umumnya merepresentasikan tanggal, bukan janji jam spesifik.
- Script tidak menghapus atau memperbaiki data sumber. Perbaikan harus terdokumentasi setelah audit.
