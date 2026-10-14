# 07 — Analysis Plan

## A. Executive Performance
- Total orders
- Delivered orders
- On-time rate
- Late rate
- Average delivery days
- Average delay days

## B. Time Analysis
Pertanyaan:
- Bulan apa memiliki late rate tertinggi?
- Apakah performa membaik atau memburuk dari waktu ke waktu?
- Apakah terdapat seasonal pattern?

## C. Geography Analysis
Bandingkan:
- customer state
- seller state
- origin-destination pattern

Cari area dengan volume tinggi dan late rate tinggi secara bersamaan.

## D. Seller Performance
Ranking seller berdasarkan:
- jumlah order
- on-time rate
- late rate
- average delivery time

Gunakan minimum order threshold agar seller dengan 1–2 order tidak mendominasi ranking.

## E. Product / Category Analysis
Cari kategori yang memiliki:
- volume besar
- delivery time tinggi
- late rate tinggi
- review rendah

## F. Customer Experience
Uji hubungan antara delivery performance dan review score.

Jangan langsung menyimpulkan bahwa delay menyebabkan review rendah. Gunakan bahasa **association/relationship** kecuali ada desain analisis kausal yang kuat.

## G. Root Cause Exploration
Analisis kombinasi:
- seller
- geography
- delivery duration
- freight value
- order volume

Tujuan akhirnya adalah menemukan **concentrated operational problems**, bukan sekadar membuat ranking.
