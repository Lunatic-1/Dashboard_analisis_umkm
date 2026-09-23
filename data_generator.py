"""
Data Generator - Dataset UMKM Indonesia
========================================
Modul untuk men-generate dataset dummy realistis berdasarkan pola data BPS Indonesia.
Mencakup 34 provinsi, 7 sektor usaha, 3 skala usaha, periode 2019-2024.
"""

import pandas as pd
import numpy as np


def generate_umkm_data(seed: int = 42) -> pd.DataFrame:
    """
    Generate dataset UMKM Indonesia yang realistis.
    
    Returns:
        pd.DataFrame: DataFrame berisi data UMKM dengan kolom:
            - provinsi, sektor, skala, tahun, jumlah_umkm,
              tenaga_kerja, omzet, pertumbuhan
    """
    np.random.seed(seed)

    # 34 Provinsi Indonesia dengan bobot populasi UMKM relatif (berdasarkan pola BPS)
    provinsi_data = {
        "Jawa Barat": 4500,
        "Jawa Tengah": 4200,
        "Jawa Timur": 4800,
        "DKI Jakarta": 3500,
        "DI Yogyakarta": 1200,
        "Banten": 2000,
        "Sumatera Utara": 2500,
        "Sumatera Barat": 1500,
        "Sumatera Selatan": 1400,
        "Riau": 1300,
        "Lampung": 1200,
        "Jambi": 800,
        "Bengkulu": 600,
        "Kepulauan Riau": 700,
        "Kepulauan Bangka Belitung": 500,
        "Aceh": 1100,
        "Kalimantan Barat": 900,
        "Kalimantan Selatan": 850,
        "Kalimantan Timur": 950,
        "Kalimantan Tengah": 600,
        "Kalimantan Utara": 300,
        "Sulawesi Selatan": 1800,
        "Sulawesi Utara": 700,
        "Sulawesi Tengah": 650,
        "Sulawesi Tenggara": 550,
        "Sulawesi Barat": 350,
        "Gorontalo": 400,
        "Bali": 1500,
        "Nusa Tenggara Barat": 1000,
        "Nusa Tenggara Timur": 800,
        "Maluku": 450,
        "Maluku Utara": 350,
        "Papua": 500,
        "Papua Barat": 300,
    }

    sektor_list = [
        "Perdagangan",
        "Kuliner",
        "Fashion",
        "Jasa",
        "Pertanian",
        "Kerajinan",
        "Teknologi",
    ]
    sektor_weights = [0.28, 0.22, 0.15, 0.12, 0.10, 0.08, 0.05]

    skala_list = ["Mikro", "Kecil", "Menengah"]
    skala_weights = [0.65, 0.25, 0.10]

    tahun_list = [2019, 2020, 2021, 2022, 2023, 2024]

    # Faktor pertumbuhan tahunan (dengan penurunan di 2020 karena COVID-19)
    growth_factors = {
        2019: 1.00,
        2020: 0.88,  # Penurunan karena pandemi
        2021: 0.93,  # Pemulihan awal
        2022: 1.02,  # Pemulihan penuh
        2023: 1.08,  # Pertumbuhan positif
        2024: 1.12,  # Pertumbuhan lanjutan
    }

    # Omzet rata-rata per skala (dalam juta Rupiah per tahun)
    omzet_base = {
        "Mikro": 150,      # s.d. 300 juta
        "Kecil": 800,      # 300 juta - 2.5 miliar
        "Menengah": 5000,   # 2.5 miliar - 50 miliar
    }

    # Tenaga kerja rata-rata per skala
    tk_base = {
        "Mikro": 2,
        "Kecil": 8,
        "Menengah": 35,
    }

    records = []

    for provinsi, base_count in provinsi_data.items():
        for tahun in tahun_list:
            for sektor, s_weight in zip(sektor_list, sektor_weights):
                for skala, sk_weight in zip(skala_list, skala_weights):
                    # Hitung jumlah UMKM
                    base = base_count * s_weight * sk_weight * growth_factors[tahun]
                    noise = np.random.normal(1.0, 0.12)
                    jumlah = max(1, int(base * noise))

                    # Hitung tenaga kerja
                    tk_per_unit = tk_base[skala] * np.random.normal(1.0, 0.15)
                    tenaga_kerja = max(1, int(jumlah * tk_per_unit))

                    # Hitung omzet (dalam juta Rupiah)
                    omzet_per_unit = omzet_base[skala] * np.random.normal(1.0, 0.20)
                    omzet = max(10, round(jumlah * omzet_per_unit, 2))

                    # Hitung pertumbuhan (%)
                    if tahun == 2019:
                        pertumbuhan = round(np.random.normal(5.0, 2.0), 2)
                    elif tahun == 2020:
                        pertumbuhan = round(np.random.normal(-12.0, 5.0), 2)
                    elif tahun == 2021:
                        pertumbuhan = round(np.random.normal(-3.0, 4.0), 2)
                    elif tahun == 2022:
                        pertumbuhan = round(np.random.normal(6.0, 3.0), 2)
                    elif tahun == 2023:
                        pertumbuhan = round(np.random.normal(8.0, 2.5), 2)
                    else:
                        pertumbuhan = round(np.random.normal(10.0, 3.0), 2)

                    records.append({
                        "provinsi": provinsi,
                        "sektor": sektor,
                        "skala": skala,
                        "tahun": tahun,
                        "jumlah_umkm": jumlah,
                        "tenaga_kerja": tenaga_kerja,
                        "omzet_juta": omzet,
                        "pertumbuhan_pct": pertumbuhan,
                    })

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    df = generate_umkm_data()
    print(f"Dataset shape: {df.shape}")
    print(f"\nKolom: {list(df.columns)}")
    print(f"\nProvinsi unik: {df['provinsi'].nunique()}")
    print(f"Sektor unik: {df['sektor'].nunique()}")
    print(f"Skala unik: {df['skala'].nunique()}")
    print(f"Tahun: {sorted(df['tahun'].unique())}")
    print(f"\nSample data:")
    print(df.head(10).to_string(index=False))
