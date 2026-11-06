"""Pemuatan data dan perhitungan indikator turunan.

Sumber: BPS, Profil Industri Mikro dan Kecil 2024 dan 2025 (Tabel 5 dan Tabel 6).
Satuan nilai di berkas CSV mengikuti BPS: ribu rupiah (000 Rp).
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Nama singkat divisi KBLI 2-digit (Industri Pengolahan)
KBLI_NAMA = {
    "10": "Makanan",
    "11": "Minuman",
    "12": "Pengolahan Tembakau",
    "13": "Tekstil",
    "14": "Pakaian Jadi",
    "15": "Kulit dan Alas Kaki",
    "16": "Kayu dan Anyaman",
    "17": "Kertas",
    "18": "Percetakan",
    "20": "Bahan Kimia",
    "21": "Farmasi dan Obat Tradisional",
    "22": "Karet dan Plastik",
    "23": "Galian Bukan Logam",
    "24": "Logam Dasar",
    "25": "Barang Logam",
    "26": "Komputer dan Elektronik",
    "27": "Peralatan Listrik",
    "28": "Mesin dan Perlengkapan",
    "29": "Kendaraan Bermotor",
    "30": "Alat Angkutan Lainnya",
    "31": "Furnitur",
    "32": "Pengolahan Lainnya",
    "33": "Reparasi dan Pemasangan",
}

WILAYAH_PREFIX = {
    "1": "Sumatera", "2": "Sumatera", "3": "Jawa", "5": "Bali dan Nusa Tenggara",
    "6": "Kalimantan", "7": "Sulawesi", "8": "Maluku", "9": "Papua",
}


def _wilayah(kode: str) -> str:
    # Kode 21 (Kepulauan Riau) termasuk Sumatera; 51-53 Bali dan Nusa Tenggara
    return WILAYAH_PREFIX[str(kode)[0]]


def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Tambahkan indikator turunan. Pendapatan/pengeluaran asli dalam ribu Rp."""
    d = df.copy()
    d["pendapatan_triliun"] = d["pendapatan_000"] / 1e9
    d["pengeluaran_triliun"] = d["pengeluaran_000"] / 1e9
    d["balas_jasa_triliun"] = d["balas_jasa_000"] / 1e9
    d["pend_per_usaha_juta"] = d["pendapatan_000"] / d["usaha"] / 1e3
    d["pekerja_per_usaha"] = d["pekerja_total"] / d["usaha"]
    d["pend_per_pekerja_juta"] = d["pendapatan_000"] / d["pekerja_total"] / 1e3
    d["margin_pct"] = (d["pendapatan_000"] - d["pengeluaran_000"]) / d["pendapatan_000"] * 100
    d["pct_tdk_dibayar"] = d["pekerja_tdk_dibayar"] / d["pekerja_total"] * 100
    d["balas_jasa_per_dibayar_juta"] = d["balas_jasa_000"] / d["pekerja_dibayar"].replace(0, np.nan) / 1e3
    # bentuk logaritma untuk klaster dan regresi
    d["ln_pend_usaha"] = np.log(d["pend_per_usaha_juta"])
    d["ln_pend_pekerja"] = np.log(d["pend_per_pekerja_juta"])
    return d


def load_provinsi() -> pd.DataFrame:
    d = pd.read_csv(DATA_DIR / "imk_provinsi_2024_2025.csv", dtype={"kode": str})
    d["wilayah"] = d["kode"].map(_wilayah)
    return add_metrics(d)


def load_kbli() -> pd.DataFrame:
    d = pd.read_csv(DATA_DIR / "imk_kbli_2024_2025.csv", dtype={"kbli": str})
    d["sektor"] = d["kbli"].map(KBLI_NAMA)
    d["label"] = d["kbli"] + " " + d["sektor"]
    return add_metrics(d)


def fmt_id(x: float, desimal: int = 0) -> str:
    """Format angka gaya Indonesia: titik ribuan, koma desimal."""
    s = f"{x:,.{desimal}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")
