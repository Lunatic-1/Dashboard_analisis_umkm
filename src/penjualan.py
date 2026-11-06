"""Analisis penjualan tingkat usaha: contoh data, pembersihan, ringkasan, pola waktu, dan prakiraan."""
import re
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

# (produk, kategori, harga satuan Rp, bobot popularitas)
PRODUK = [
    ("Kopi Susu Gula Aren", "Minuman", 18000, 0.22),
    ("Americano", "Minuman", 15000, 0.08),
    ("Es Teh Manis", "Minuman", 6000, 0.10),
    ("Matcha Latte", "Minuman", 22000, 0.07),
    ("Coklat Dingin", "Minuman", 20000, 0.06),
    ("Air Mineral", "Minuman", 4000, 0.10),
    ("Roti Bakar Coklat Keju", "Makanan", 15000, 0.09),
    ("Pisang Goreng", "Makanan", 12000, 0.07),
    ("Mie Instan Telur", "Makanan", 14000, 0.06),
    ("Nasi Goreng", "Makanan", 22000, 0.05),
    ("Kentang Goreng", "Makanan", 14000, 0.05),
    ("Cireng", "Makanan", 10000, 0.05),
]


def contoh_data(seed: int = 7) -> pd.DataFrame:
    """Data transaksi SIMULASI sebuah kedai kopi (1 tahun). Bukan data usaha nyata.

    Pola yang ditanam: ramai pada akhir pekan, pertumbuhan bertahap, dua jam puncak.
    """
    rng = np.random.default_rng(seed)
    tanggal = pd.date_range("2025-11-01", "2026-10-31", freq="D")
    bobot = np.array([p[3] for p in PRODUK], dtype=float)
    bobot /= bobot.sum()
    faktor_hari = {0: 0.9, 1: 0.9, 2: 0.95, 3: 1.0, 4: 1.15, 5: 1.4, 6: 1.3}
    jam = np.arange(8, 22)
    bobot_jam = np.array([3, 5, 5, 3, 3, 3, 4, 5, 5, 6, 7, 6, 4, 2], dtype=float)
    bobot_jam /= bobot_jam.sum()

    baris, no = [], 0
    for i, tgl in enumerate(tanggal):
        lam = 34 * (1 + 0.25 * i / len(tanggal)) * faktor_hari[tgl.weekday()] * rng.lognormal(0, 0.12)
        for _ in range(rng.poisson(lam)):
            no += 1
            waktu = tgl + pd.Timedelta(hours=int(rng.choice(jam, p=bobot_jam)), minutes=int(rng.integers(0, 60)))
            k = rng.choice([1, 2, 3, 4], p=[0.45, 0.30, 0.17, 0.08])
            for idx in rng.choice(len(PRODUK), size=k, replace=False, p=bobot):
                nama, kat, harga, _ = PRODUK[idx]
                baris.append((f"T{no:06d}", waktu, nama, kat, int(rng.choice([1, 2], p=[0.85, 0.15])), harga))
    return pd.DataFrame(baris, columns=["id_transaksi", "waktu", "produk", "kategori", "jumlah", "harga_satuan"])


def _angka(seri: pd.Series) -> pd.Series:
    """Ubah teks seperti 'Rp 15.000' menjadi angka; nilai yang tidak terbaca menjadi NaN."""
    if pd.api.types.is_numeric_dtype(seri):
        return seri.astype(float)
    s = seri.astype(str).str.replace(r"(?i)rp\.?", "", regex=True).str.replace(r"\s", "", regex=True)
    s = s.map(lambda v: v.replace(".", "") if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", v) else v)
    s = s.str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def bersihkan(raw, kol_waktu, kol_produk, kol_jumlah, kol_nilai, nilai_adalah="Harga satuan",
              kol_id=None, kol_kategori=None, dayfirst=False):
    """Standarkan kolom dan buang baris tidak valid. Mengembalikan (data bersih, laporan)."""
    d = pd.DataFrame({
        "waktu": pd.to_datetime(raw[kol_waktu], errors="coerce", dayfirst=dayfirst),
        "produk": raw[kol_produk].astype(str).str.strip(),
        "jumlah": _angka(raw[kol_jumlah]),
        "nilai": _angka(raw[kol_nilai]),
    })
    d["id_transaksi"] = raw[kol_id].astype(str) if kol_id else ["B" + str(i) for i in range(len(raw))]
    d["kategori"] = raw[kol_kategori].astype(str).str.strip() if kol_kategori else "Tanpa kategori"

    n0 = len(d)
    alasan = {
        "Tanggal/waktu tidak terbaca": d["waktu"].isna(),
        "Produk kosong": d["produk"].isin(["", "nan", "None"]),
        "Jumlah kosong atau tidak positif": d["jumlah"].isna() | (d["jumlah"] <= 0),
        "Nilai kosong atau negatif": d["nilai"].isna() | (d["nilai"] < 0),
    }
    buang = pd.Series(False, index=d.index)
    laporan = {"Baris awal": n0}
    for nama, mask in alasan.items():
        baru = mask & ~buang
        laporan[nama] = int(baru.sum())
        buang |= mask
    d = d[~buang].copy()
    if nilai_adalah == "Harga satuan":
        d["harga_satuan"] = d["nilai"]
        d["omzet"] = d["jumlah"] * d["nilai"]
    else:
        d["omzet"] = d["nilai"]
        d["harga_satuan"] = d["nilai"] / d["jumlah"]
    d = d.drop(columns="nilai")
    laporan["Baris dipakai"] = len(d)
    return d.reset_index(drop=True), laporan


def ringkasan(d: pd.DataFrame) -> dict:
    trx = d["id_transaksi"].nunique()
    return {
        "omzet": d["omzet"].sum(),
        "transaksi": trx,
        "nilai_per_transaksi": d["omzet"].sum() / trx,
        "unit": d["jumlah"].sum(),
        "awal": d["waktu"].min(),
        "akhir": d["waktu"].max(),
    }


def harian(d: pd.DataFrame) -> pd.Series:
    s = d.groupby(d["waktu"].dt.normalize())["omzet"].sum()
    return s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="D"), fill_value=0.0)


def tren(d: pd.DataFrame, granularitas: str) -> pd.DataFrame:
    kode = {"Harian": "D", "Mingguan": "W", "Bulanan": "M"}[granularitas]
    p = d["waktu"].dt.to_period(kode).dt.start_time
    t = d.groupby(p)["omzet"].sum().rename("omzet").to_frame()
    if granularitas == "Harian":
        t = harian(d).rename("omzet").to_frame()
        t["rata_7_hari"] = t["omzet"].rolling(7, min_periods=4).mean()
    return t.reset_index(names="periode")


def per_produk(d: pd.DataFrame) -> pd.DataFrame:
    t = d.groupby("produk").agg(omzet=("omzet", "sum"), unit=("jumlah", "sum"),
                                transaksi=("id_transaksi", "nunique")).sort_values("omzet", ascending=False)
    t["porsi_pct"] = t["omzet"] / t["omzet"].sum() * 100
    t["kumulatif_pct"] = t["porsi_pct"].cumsum()
    return t.reset_index()


def ada_jam(d: pd.DataFrame) -> bool:
    return d["waktu"].dt.hour.nunique() > 1


def pola_hari_jam(d: pd.DataFrame) -> pd.DataFrame:
    """Jumlah transaksi menurut hari (baris) dan jam (kolom)."""
    t = d.drop_duplicates("id_transaksi")
    m = t.groupby([t["waktu"].dt.weekday, t["waktu"].dt.hour]).size().unstack(fill_value=0)
    m = m.reindex(range(7), fill_value=0)
    m.index = HARI
    return m


def rata_per_hari(d: pd.DataFrame) -> pd.Series:
    s = harian(d)
    r = s.groupby(s.index.weekday).mean()
    r.index = [HARI[i] for i in r.index]
    return r


def _hw(y: pd.Series):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return ExponentialSmoothing(y, trend="add", damped_trend=True, seasonal="add",
                                    seasonal_periods=7, initialization_method="estimated").fit()


def prakiraan(seri: pd.Series, horizon: int = 14, uji: int = 28):
    """Holt-Winters (tren teredam + musiman mingguan) dibandingkan dengan baseline musiman-naif.

    Evaluasi pada `uji` hari terakhir (tidak dipakai untuk melatih). Interval = prakiraan +- 1,96 x simpangan
    baku residual (pendekatan kasar).
    """
    if len(seri) < 8 * 7 + uji:
        return None
    train, test = seri.iloc[:-uji], seri.iloc[-uji:]
    pred = pd.Series(_hw(train).forecast(uji).values, index=test.index).clip(lower=0)
    pola = train.values[-7:]
    naif = pd.Series(np.tile(pola, uji // 7 + 1)[:uji], index=test.index)

    def metrik(p):
        e = test - p
        return {"MAE": float(e.abs().mean()), "WAPE (%)": float(e.abs().sum() / test.abs().sum() * 100)}

    full = _hw(seri)
    fc = full.forecast(horizon).clip(lower=0)
    sigma = float(np.std(full.resid, ddof=1))
    hasil = pd.DataFrame({"prakiraan": fc, "batas_bawah": (fc - 1.96 * sigma).clip(lower=0), "batas_atas": fc + 1.96 * sigma})
    return {"uji": test, "pred_uji": pred, "naif_uji": naif,
            "metrik": pd.DataFrame({"Holt-Winters": metrik(pred), "Baseline musiman-naif": metrik(naif)}).T,
            "prakiraan": hasil}
