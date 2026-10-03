# Dashboard Analisis Data UMKM Indonesia 🇮🇩

Dashboard web interaktif untuk analisis data **Usaha Mikro, Kecil, dan Menengah (UMKM)** Indonesia. Dibangun menggunakan Python dengan Streamlit, Plotly, Pandas, dan NumPy.

## 🚀 Fitur

- **KPI Cards** — Total UMKM, Tenaga Kerja, Omzet, Pertumbuhan YoY
- **Filter Interaktif** — Tahun, Provinsi, Sektor, Skala Usaha
- **7+ Visualisasi** — Bar, Donut, Line, Scatter, Heatmap, Stacked Bar
- **Tabel Data** — Ringkasan & data lengkap dengan download CSV
- **Dark Theme Premium** — Glassmorphism, gradien, micro-animation

## 📦 Instalasi & Cara Menjalankan

Ikuti langkah-langkah berikut untuk menjalankan dashboard secara lokal:

1. **Clone repository** (opsional jika sudah di-download)
```bash
git clone <repo-url>
cd Dashboard_analisis_umkm
```

2. **Install dependencies**
Pastikan Python sudah terinstall di komputer/laptop Anda, lalu jalankan:
```bash
pip install -r requirements.txt
```

3. **Cara Menjalankan Dashboard (Run)**
Gunakan perintah `streamlit run` untuk menjalankan aplikasi:
```bash
streamlit run app.py
```
*(Alternatif jika perintah di atas error `command not found`, gunakan perintah berikut:)*
```bash
python -m streamlit run app.py
```
Aplikasi akan terbuka secara otomatis di browser (biasanya pada alamat `http://localhost:8501`).

## 🛠️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| Framework | Streamlit |
| Visualisasi | Plotly |
| Data Processing | Pandas + NumPy |
| Styling | Custom CSS |

## 📁 Struktur Proyek

```
Dashboard_analisis_umkm/
├── app.py              # Dashboard utama
├── data_generator.py   # Modul generate data dummy
├── requirements.txt    # Dependencies
└── README.md           # Dokumentasi
```

## 📊 Data

Data yang digunakan adalah **data sampel (dummy)** yang di-generate secara realistis berdasarkan pola data BPS Indonesia, mencakup:

- **34 Provinsi** di Indonesia
- **7 Sektor Usaha**: Perdagangan, Kuliner, Fashion, Jasa, Pertanian, Kerajinan, Teknologi
- **3 Skala Usaha**: Mikro, Kecil, Menengah
- **Periode**: 2019 – 2024
- **Variabel**: Jumlah UMKM, Tenaga Kerja, Omzet, Pertumbuhan
