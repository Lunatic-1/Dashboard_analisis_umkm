# Data Contoh Penjualan — UCI Online Retail

File: **`penjualan_uci_online_retail_1.csv`, `_2.csv`, `_3.csv`** (total 13,2 MB; 203.181 baris)

Data dibagi menjadi tiga berkas per rentang bulan karena batas ukuran berkas
pada repositori; dashboard menggabungkannya kembali saat dimuat (`app.py`,
fungsi `_contoh()`). Isi ketiga berkas identik strukturnya dengan satu berkas utuh.

## Sumber

- **Dataset:** Online Retail, UCI Machine Learning Repository (dataset 352)
- **Isi:** Transaksi 1 Des 2010 – 31 Mei 2011 dari sebuah toko online di Inggris
  yang menjual hadiah unik; sebagian besar pelanggannya grosir. Ini 6 bulan
  pertama dari 12 bulan data asli (1 Des 2010 – 9 Des 2011, 528.272 baris);
  rentang dibatasi agar berkas muat di repositori. File lengkap 12 bulan
  (36 MB) tidak ikut di-push.
- **Sitasi wajib (untuk laporan):** Chen, D., Sain, S. L., & Guo, K. (2012).
  *Data mining for the online retail industry: A case study of RFM model-based
  customer segmentation using data mining.* Journal of Database Marketing &
  Customer Strategy Management, 19(3).
- **Akses:** Diunduh bebas dari UCI ML Repository untuk keperluan penelitian
  dan pendidikan, tanpa login.
- **Bukan data UMKM Indonesia.** Ini data transaksi ritel Inggris yang nyata,
  dipakai sebagai studi kasus modul penjualan. Sampaikan itu secara jujur di
  presentasi: pola transaksinya nyata, konteks usahanya berbeda.

## Pembersihan yang dilakukan (dari 541.909 baris mentah 12 bulan)

| Langkah | Baris |
|---|---|
| Deskripsi produk kosong | −1.454 |
| Jumlah ≤ 0 (pembatalan/retur, invoice berawalan C) | −9.762 |
| Harga ≤ 0 (penyesuaian stok) | −589 |
| Ongkos kirim, bukan produk ("POSTAGE") | −1.832 |
| Baris bersih 12 bulan | 528.272 |
| **Diambil untuk repo ini (Des 2010 – Mei 2011)** | **203.181** |

- Nama produk distandardisasi ke Title Case.
- **Konversi mata uang:** harga asli dalam pound sterling (£) dikonversi ke rupiah
  dengan kurs **£1 = Rp24.215** (kurs tengah GBP/IDR per 11 Nov 2026, Finnhub).
  Konversi ini hanya untuk penyajian dalam rupiah; bentuk analisis (tren, Pareto,
  WAPE prakiraan) tidak berubah oleh perubahan skala.
- Kolom `harga_satuan_gbp` menyimpan harga asli (£) untuk audit.

## Isi file

| Kolom | Arti |
|---|---|
| `id_transaksi` | Nomor invoice |
| `waktu` | Tanggal + jam (`YYYY-MM-DD HH:MM:SS`) |
| `produk` | Nama produk |
| `jumlah` | Jumlah unit |
| `harga_satuan` | Harga satuan (Rp, hasil konversi) |
| `harga_satuan_gbp` | Harga satuan asli (£) — kolom tambahan |

Tidak ada kolom kategori di sumbernya.

## Ringkasan hasil (terverifikasi dengan `src/penjualan.py`)

- Periode: 1 Des 2010 – 31 Mei 2011 (182 hari kalender, 141 hari berjualan)
- Transaksi: 8.112 invoice; produk: 3.360; unit terjual: 2.111.062
- Omzet: **£3.951.640,48 ≈ Rp95.688.974.133** (rata-rata ±Rp11,8 juta per transaksi)
- Produk terlaris: Regency Cakestand 3 Tier (2,47%), Medium Ceramic Top Storage
  Jar (1,98%), White Hanging Heart T-Light Holder (1,48%). Top-5 hanya 8,0%
  omzet — ekornya sangat panjang (3.360 produk), jadi kurva Pareto-nya landai.
- Toko tutup setiap Sabtu dan libur (mis. Natal–Tahun Baru, 30 Mei 2011),
  sehingga deret harian mengandung angka 0.
- **Prakiraan Holt-Winters jalan, tapi pada 28 hari uji (Mei 2011) kalah dari
  baseline musiman-naif: WAPE 59,4% vs 56,3%.** Periode uji memuat 5 hari tutup.
  Pada data nyata yang berisik, model sederhana tidak kalah — temuan yang layak
  ditulis di laporan, bukan kegagalan modul.

## Batasan yang perlu ditulis di laporan

1. Bukan UMKM Indonesia dan bukan kedai kopi — konteksnya ritel online Inggris.
2. Periode 2010–2011 (sudah lama), harga dalam £ yang dikonversi dengan kurs 2026.
3. Skalanya ritel besar (±Rp95,7 miliar dalam 6 bulan), bukan usaha mikro/kecil.
4. Tidak ada data kategori produk; data pelanggan tidak dipakai.
5. File ini hanya 6 bulan pertama dari 12 bulan data asli.
