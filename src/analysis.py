"""Analisis: perubahan antar tahun, regresi, dan klaster provinsi."""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.outliers_influence import variance_inflation_factor

FITUR_KLASTER = {
    "ln_pend_usaha": "ln pendapatan per usaha",
    "pekerja_per_usaha": "Pekerja per usaha",
    "ln_pend_pekerja": "ln pendapatan per pekerja",
    "margin_pct": "Margin (%)",
    "pct_tdk_dibayar": "Pekerja tidak dibayar (%)",
}


def perubahan_nasional(prov: pd.DataFrame) -> pd.DataFrame:
    kolom = {
        "usaha": "Jumlah usaha",
        "pekerja_total": "Pekerja (total)",
        "pekerja_dibayar": "Pekerja dibayar",
        "pekerja_tdk_dibayar": "Pekerja tidak dibayar",
        "pendapatan_000": "Pendapatan (000 Rp)",
        "pengeluaran_000": "Pengeluaran (000 Rp)",
        "balas_jasa_000": "Balas jasa pekerja (000 Rp)",
    }
    t = prov.groupby("tahun")[list(kolom)].sum().T
    t["perubahan_pct"] = (t[2025] / t[2024] - 1) * 100
    t.index = [kolom[i] for i in t.index]
    return t.rename(columns={2024: "2024", 2025: "2025"})


def perubahan_provinsi(prov: pd.DataFrame, variabel: str) -> pd.DataFrame:
    w = prov.pivot(index="provinsi", columns="tahun", values=variabel)
    w.columns = [str(c) for c in w.columns]
    w["perubahan_pct"] = (w["2025"] / w["2024"] - 1) * 100
    return w.reset_index().sort_values("perubahan_pct")


def regresi(prov: pd.DataFrame):
    """OLS log-log: ln(pendapatan) ~ ln(pekerja dibayar) + ln(pekerja tidak dibayar) + dummy 2025.

    Galat baku robust terhadap korelasi dalam provinsi (cluster), karena provinsi yang sama
    muncul pada dua tahun.
    """
    d = prov.assign(
        ln_pendapatan=np.log(prov["pendapatan_000"]),
        ln_dibayar=np.log(prov["pekerja_dibayar"]),
        ln_tdk_dibayar=np.log(prov["pekerja_tdk_dibayar"]),
        d2025=(prov["tahun"] == 2025).astype(int),
    )
    grup = pd.factorize(d["provinsi"])[0]
    m = smf.ols("ln_pendapatan ~ ln_dibayar + ln_tdk_dibayar + d2025", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": grup}
    )
    ci = m.conf_int()
    tabel = pd.DataFrame(
        {
            "Koefisien": m.params,
            "Galat baku": m.bse,
            "z": m.tvalues,
            "p-value": m.pvalues,
            "CI 95% bawah": ci[0],
            "CI 95% atas": ci[1],
        }
    )
    tabel.index = ["Konstanta", "ln pekerja dibayar", "ln pekerja tidak dibayar", "Dummy tahun 2025"]
    X = m.model.exog
    vif = {
        nama: variance_inflation_factor(X, i)
        for i, nama in enumerate(m.model.exog_names)
        if nama != "Intercept"
    }
    return m, tabel, vif


def klaster(prov_tahun: pd.DataFrame, k: int, seed: int = 42):
    """K-Means pada indikator terstandarisasi. Mengembalikan data berlabel, silhouette per k, dan profil."""
    d = prov_tahun.reset_index(drop=True).copy()
    Z = StandardScaler().fit_transform(d[list(FITUR_KLASTER)])
    silhouette = {
        kk: silhouette_score(Z, KMeans(kk, n_init=20, random_state=seed).fit_predict(Z))
        for kk in range(2, 7)
    }
    km = KMeans(k, n_init=20, random_state=seed).fit(Z)
    urut = pd.Series(km.labels_).value_counts().index.tolist()  # klaster terbesar = Klaster 1
    peta = {lama: baru + 1 for baru, lama in enumerate(urut)}
    d["klaster"] = pd.Series(km.labels_).map(peta).map(lambda n: f"Klaster {n}")
    pc = PCA(2, random_state=seed).fit(Z)
    koord = pc.transform(Z)
    d["PC1"], d["PC2"] = koord[:, 0], koord[:, 1]
    profil = d.groupby("klaster")[list(FITUR_KLASTER)].mean()
    profil.insert(0, "Jumlah provinsi", d.groupby("klaster").size())
    profil = profil.rename(columns=FITUR_KLASTER)
    return d, silhouette, profil, pc.explained_variance_ratio_
