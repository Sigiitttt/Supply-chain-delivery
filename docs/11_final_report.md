# 11 — Laporan Akhir Studi Kasus (Final Report)

## Cerita Singkat Proyek (Executive Summary)
Proyek ini mengupas tuntas pengalaman belanja dan pengiriman barang di marketplace Olist (Brasil), dengan menganalisis sekitar **100 ribu pesanan** sepanjang tahun 2016 sampai 2018.

Kabar baiknya, mayoritas paket (**93,2%**) berhasil sampai tepat waktu. Tapi di balik itu, ada **6.534 pesanan (6,8%)** yang datang terlambat. Dan keterlambatannya bukan cuma sehari dua hari, melainkan rata-rata **10,6 hari lebih lama** dari tanggal perkiraan. Begitu paket terlambat, kepuasan pembeli langsung runtuh: nilai ulasan yang tadinya rata-rata **4,3 bintang** langsung anjlok drastis ke **2,3 bintang**.

Setelah ditelusuri, biang keladi keterlambatan bukan karena penjual lambat membungkus paket, melainkan **waktu perjalanan kurir di jalanan yang memakan 74% dari total waktu pengiriman (rata-rata 9,3 hari)**. Masalah ini paling banyak menumpuk di kota besar **Rio de Janeiro** dan wilayah pelosok seperti **Alagoas**.

---

## 1. Masalah yang Ingin Diselesaikan
Sebagai tempat bertemunya ribuan pedagang dan pembeli, Olist sangat bergantung pada jasa kurir. Kalau paket sering telat:
1. **Pelanggan Kecewa & Kapok Belanja:** Ulasan bintang 1 bermunculan dan merusak reputasi toko.
2. **Tim CS Kewalahan:** Pembeli bolak-balik menanyakan *"Paket saya sudah sampai mana?"*.
3. **Bingung Menentukan Kesalahan:** Perusahaan sulit membedakan apakah masalahnya ada di penjual yang lambat atau kurir yang macet di jalan.

Tujuan analisis ini adalah mencari tahu **di mana titik macetnya, kenapa bisa terjadi, dan apa langkah nyata yang bisa diambil manajemen.**

---

## 2. Cara Kerja & Data yang Digunakan
* **Data yang Dipakai:** Data nyata e-commerce Olist di Brasil (~100 ribu pesanan).
* **Cara Mengolah:** Menggabungkan tabel pesanan, barang, pembeli, penjual, dan ulasan ke dalam satu tabel ringkas bernama `fact_order_delivery` (1 baris mewakili 1 pesanan utuh).
* **Validasi Data:** Dari 99.441 pesanan, ada 96.478 pesanan yang statusnya berhasil terkirim (*delivered*). Setelah diperiksa kelengkapan tanggalnya, ada **96.470 pesanan valid** yang siap kita evaluasi ketepatan waktunya.
* **Alat Bantu:** SQL untuk merapikan data, Python (Pandas) di Jupyter Notebook untuk menghitung angka statistik, serta aplikasi dashboard interaktif berbasis Streamlit & Plotly.

---

## 3. Angka-Angka Kunci (Ringkasan Performa)

| Apa yang Diukur? | Hasil Nyata | Artinya bagi Bisnis |
|---|---:|---|
| **Total Pesanan Dianalisis** | **96.470 pesanan** | Basis data pengiriman yang valid |
| **Pesanan Tepat Waktu** | **93,2%** (89.936) | Mayoritas pengiriman berjalan lancar |
| **Pesanan Terlambat** | **6,8%** (6.534) | Bagian yang perlu dibenahi |
| **Rata-rata Waktu Pengiriman** | **12,6 hari** | Waktu dari pembeli klik beli sampai barang tiba |
| **Rata-rata Hari Terlambat** | **10,6 hari** | Tambahan waktu tunggu bagi pembeli yang apes |
| **Rating Paket Tepat Waktu** | **4,29 ⭐** | Pembeli puas dan senang |
| **Rating Paket Terlambat** | **2,27 ⭐** | Nilai kepuasan anjlok -2,02 poin |

---

## 4. Temuan Penting dari Data

### 1. Masalah Terbesar Ada di Kurir, Bukan di Penjual
Waktu pengiriman kita bedah menjadi 3 tahap:
* **Verifikasi bayar:** rata-rata cuma **12 jam** (0,5 hari).
* **Penjual bungkus & serah paket ke kurir:** rata-rata **3,3 hari**. Ini wajar untuk toko online.
* **Kurir membawa paket ke rumah pembeli:** rata-rata **9,3 hari**.
Sekitar **tiga perempat waktu terbuang saat paket berada di tangan kurir**. Jadi, perbaikan utama harus ditujukan ke kerja sama logistik antar-kota.

### 2. Rio de Janeiro adalah Titik Kritis Terbesar
Secara persentase, daerah pelosok seperti Alagoas (21,4% telat) memang paling tinggi. Tapi secara jumlah nyata, **Rio de Janeiro (RJ)** adalah penyumbang masalah terbesar:
* Ada **1.495 pesanan telat** di Rio de Janeiro saja (late rate 12,1%).
* Angka ini menyumbang **hampir 23% dari seluruh keterlambatan di Brasil**.
* Artinya, jika Olist berhasil memperbaiki rute pengiriman ke Rio de Janeiro, seperempat masalah keterlambatan nasional langsung beres.

### 3. Sistem Kerap Tumbang Saat Musim Belanja
Keterlambatan melonjak tinggi saat ada event belanja besar:
* **November 2017 (Black Friday):** Keterlambatan naik ke **12,4%**.
* **Maret 2018:** Keterlambatan melonjak tajam ke rekor tertingginya di **19,0%** (1.328 paket telat).
Di bulan biasa, keterlambatan cuma 3%–5%. Ini membuktikan bahwa kapasitas truk dan kurir tidak siap menampung lonjakan pesanan saat promo besar.

### 4. Batas Sabar Pembeli Ada di Hari Ke-3 Keterlambatan
Dari data skor ulasan:
* Telat 1 sampai 3 hari: Pembeli masih cukup sabar (rating rata-rata **3,3**).
* Telat 4 sampai 7 hari: Rating langsung anjlok ke **2,1**.
* Telat lebih dari seminggu: Pembeli marah dan langsung memberi rating **1,7 ke bawah**.
Lebih dari separuh pembeli yang paketnya telat langsung memberikan bintang 1.

---

## 5. Saran Tindakan Nyata (Rekomendasi Bisnis)

1. **Bikin Jalur Logistik Khusus São Paulo – Rio de Janeiro (Prioritas #1):**
   Karena penjual kebanyakan di São Paulo dan pembeli banyak di Rio de Janeiro, buat kontrak armada truk khusus untuk jalur ini dengan janji waktu tiba yang lebih ketat. Ini cara tercepat memangkas angka keterlambatan nasional.

2. **Perbaiki Janji Tanggal Estimasi untuk Daerah Pelosok:**
   Tingkat keterlambatan 21% di Alagoas terjadi karena aplikasi menjanjikan tanggal yang terlalu cepat dan tidak realistis. Cukup tambahkan waktu cadangan otomatis (+4 sampai +6 hari) saat pembeli dari daerah pelosok checkout. Pembeli tidak akan kecewa kalau dari awal tahu barangnya butuh waktu lebih lama.

3. **Kunci Kapasitas Armada 6 Minggu Sebelum Promo Besar:**
   Belajar dari lonjakan telat di Black Friday dan Maret 2018, Olist wajib menambah kuota armada logistik minimal sebulan sebelum festival belanja dimulai, plus otomatis menambah estimasi +3 hari di aplikasi selama musim promo.

4. **Bina Penjual yang Lelet Menyerahkan Paket:**
   Data menemukan ada 20 penjual besar yang butuh waktu lebih dari 6 hari hanya untuk menyerahkan paket ke kurir. Beri peringatan dan batasi kuota order harian mereka sampai proses packing mereka bisa di bawah 3 hari. Sebaliknya, beri diskon biaya platform untuk penjual yang selalu gerak cepat.

---

## 6. Dampak yang Diharapkan
Jika saran di atas dijalankan:
* Angka keterlambatan nasional bisa turun dari **6,8% menjadi sekitar 4%** (menyelamatkan lebih dari 2.400 paket dari keterlambatan).
* Mencegah ribuan ulasan bintang 1 dari pembeli yang kesal.
* Beban kerja tim Customer Service berkurang sekitar 30% karena komplain paket telat menurun drastis.

---

## 7. Catatan & Langkah Selanjutnya
* Data ini adalah data historis tahun 2016–2018, sehingga dijadikan studi kasus pembelajaran optimasi operasional.
* **Langkah Berikutnya:** Memantau tren pengiriman secara mingguan lewat *Control Tower Dashboard* (`dashboard/app.py`), serta mengembangkan sistem pengingat otomatis jika sebuah paket sudah terlambat lebih dari 2 hari agar tim CS bisa segera menghubungi pembeli sebelum mereka memberi bintang 1.
