# Dashboard Analisis UMKM Indonesia: Sektor Industri Pengolahan Mikro dan Kecil, 2024-2025

Dashboard analisis UMKM (usaha mikro dan kecil di sektor industri pengolahan) untuk tugas data science dan visualisasi data, berbasis **data resmi BPS** (Profil Industri Mikro dan Kecil 2024 dan 2025).
Dashboard interaktif dibangun dengan Python, Streamlit, Plotly, statsmodels, dan scikit-learn.

## Tujuan

1. Memetakan kondisi industri pengolahan mikro dan kecil antar provinsi dan antar jenis industri.
2. Menguji hubungan antara tenaga kerja dan pendapatan (regresi).
3. Mengelompokkan provinsi berdasarkan karakteristik usaha (klaster).
4. Membandingkan kondisi 2024 dan 2025.

## Alur data science

| Tahap | Isi | Lokasi |
|---|---|---|
| Pengumpulan | Tabel 5 (menurut KBLI) dan Tabel 6 (menurut provinsi) dari dua PDF BPS | `data/` |
| Pembersihan dan validasi | Ekstraksi tabel dari PDF, perbaikan baris yang terpecah watermark, validasi jumlah baris terhadap total nasional BPS | lihat Metodologi |
| Rekayasa fitur | Pendapatan per usaha, pekerja per usaha, pendapatan per pekerja, margin, persentase pekerja tidak dibayar | `src/data.py` |
| EDA | Statistik deskriptif, sebaran, korelasi Spearman, scatter log-log | tab Eksplorasi Data |
| Pemodelan | Regresi OLS log-log (galat baku cluster per provinsi) dan K-Means dengan evaluasi silhouette | `src/analysis.py` |
| Prakiraan | Holt-Winters (tren teredam, musiman mingguan) dievaluasi terhadap baseline musiman-naif | `src/penjualan.py` |
| Visualisasi | Dashboard Streamlit delapan tab | `app.py` |

## Dua lapisan analisis

1. **Konteks nasional (data BPS):** statistik industri mikro dan kecil per provinsi dan per jenis industri, 2024-2025.
2. **Penjualan tingkat usaha:** analisis data transaksi satu usaha (tren, kinerja produk, Pareto, pola hari dan jam,
   prakiraan omzet). Dapat memakai data simulasi bawaan atau berkas CSV/Excel yang diunggah.

### Format data transaksi untuk diunggah

Satu baris per produk yang terjual. Kolom wajib: tanggal/waktu, nama produk, jumlah, dan harga (satuan atau total).
Kolom opsional: ID transaksi dan kategori. Pemetaan kolom dilakukan di dashboard, jadi nama kolom bebas. Angka seperti
`Rp 18.000` dan pemisah kolom `;` dikenali. Contoh format: `data/contoh_penjualan_simulasi.csv`.

Sumber data yang bisa dipakai: ekspor dari aplikasi kasir (CSV/Excel), catatan penjualan usaha yang Anda kenal (dengan izin),
atau dataset publik transaksi toko roti/kafe di Kaggle. Data bawaan (`contoh_penjualan_simulasi.csv`) adalah **simulasi**.

## Cara menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

Jika `streamlit` tidak dikenali: `python -m streamlit run app.py`.

## Struktur proyek

```
Dashboard_IMK/
├── app.py                      # dashboard utama
├── requirements.txt
├── README.md
├── .streamlit/config.toml      # tema terang
├── data/
│   ├── imk_provinsi_2024_2025.csv   # 38 provinsi x 2 tahun
│   ├── imk_kbli_2024_2025.csv       # 23 divisi KBLI x 2 tahun
│   └── contoh_penjualan_simulasi.csv  # contoh transaksi SIMULASI (kedai kopi)
└── src/
    ├── data.py                 # pemuatan data BPS dan indikator turunan
    ├── analysis.py             # perubahan, regresi, klaster
    └── penjualan.py            # pembersihan, ringkasan, pola waktu, prakiraan penjualan
```

## Temuan utama

- Jumlah usaha nasional relatif stabil (4,41 juta pada 2024 menjadi 4,46 juta pada 2025, +1,1%), sedangkan jumlah pekerja turun 9,4% (10,47 juta menjadi 9,48 juta). Pendapatan nyaris tidak berubah (+0,2%), sementara pengeluaran turun 5,9%, sehingga margin kasar naik dari 44,6% menjadi 48,0%.
- Pulau Jawa menyumbang sekitar 61,5% usaha dan 65,7% pendapatan pada 2025.
- Tiga jenis industri terbanyak (Makanan, Pakaian Jadi, Kayu dan Anyaman) mencakup 70,5% usaha pada 2025.
- Regresi: elastisitas pendapatan terhadap pekerja dibayar sekitar 0,50 dan terhadap pekerja tidak dibayar sekitar 0,42 (keduanya signifikan), dengan jumlah elastisitas 0,92. R-kuadrat 0,94. Dummy 2025 tidak signifikan.
- Klaster: struktur lemah (silhouette 0,30 untuk 2024 dan 0,44 untuk 2025 pada k = 3) dan tidak stabil antar tahun.
- Modul penjualan: pada data simulasi, Holt-Winters menghasilkan WAPE 14,4% pada 28 hari uji, dibandingkan 21,6% untuk baseline. Angka ini hanya menunjukkan modul berfungsi, bukan temuan tentang usaha nyata.

## Metodologi dan keterbatasan

- **Cakupan.** IMK hanya mencakup industri pengolahan dengan 1 sampai 19 pekerja, bukan seluruh UMKM.
- **Survei sampel.** Angka tingkat provinsi memiliki galat sampling. Perubahan antar provinsi 2024-2025 sangat lebar dan tidak boleh langsung ditafsirkan sebagai perubahan kondisi riil.
- **Dua titik waktu.** Peramalan deret waktu tidak dilakukan karena tidak ada dasar statistik dengan dua tahun data.
- **Validasi ekstraksi.** Jumlah seluruh provinsi dan seluruh KBLI dicocokkan dengan baris total BPS; selisih maksimum 4 satuan (pembulatan). Beberapa baris (Jawa Barat, Jawa Tengah, Jawa Timur, Banten, dan beberapa KBLI) terpecah oleh watermark PDF dan dibaca ulang manual dari dokumen.
- **Nama KBLI** pada dashboard adalah nama singkat divisi KBLI 2 digit.
- **Regresi** bersifat asosiatif, bukan kausal. Multikolinearitas antara dua jenis pekerja cukup tinggi (VIF sekitar 10).

## Sumber

Badan Pusat Statistik. *Profil Industri Mikro dan Kecil 2024* (Vol. 15, 2025) dan *Profil Industri Mikro dan Kecil 2025* (Vol. 16, 2026). Katalog 6104006.
