"""Dashboard Analisis Industri Mikro dan Kecil (IMK) Indonesia, 2024-2025.

Sumber data: BPS, Profil Industri Mikro dan Kecil 2024 dan 2025.
Jalankan dengan:  streamlit run app.py
"""
import io
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analysis import (
    FITUR_KLASTER,
    klaster,
    perubahan_nasional,
    perubahan_provinsi,
    regresi,
)
from src import penjualan as pj
from src.data import fmt_id, load_kbli, load_provinsi

st.set_page_config(page_title="Dashboard Analisis UMKM Indonesia", layout="wide")

BIRU = "#1F4E79"
MERAH = "#B5503C"
PALET = ["#1F4E79", "#B5503C", "#4F8A5B", "#7B6A9E", "#C98B2B", "#5B9BD5", "#7F8C99"]
FONT = "Source Sans 3, Segoe UI, Arial, sans-serif"

# ---------------------------------------------------------------- Gaya halaman
# Token desain dari prototype (Dashboard Analisis UMKM, 11 Nov 2026):
# latar #F2F5F8, permukaan putih, tinta #1B2733, redup #5A6B7B, garis #D9E1E9,
# navy #1F4E79, navy-soft #DBE7F1, hijau delta #2E7D46, merah delta #B03A2E,
# emas badge #C98B2B, judul serif Georgia, isi Segoe UI/system.
st.markdown(
    """
<style>
.stApp { font-family: 'Segoe UI', system-ui, -apple-system, Roboto, 'Helvetica Neue', Arial, sans-serif;
    color: #1B2733; background: #F2F5F8; font-variant-numeric: tabular-nums; }
h1, h2, h3 { font-family: Georgia, 'Times New Roman', Times, serif !important; color: #1B2733;
    font-weight: 700; letter-spacing: 0; }
h2 { font-size: 1.35rem !important; margin-top: 34px !important; }
h3 { font-size: 1.05rem !important; margin-top: 1.2rem; }
.block-container { max-width: 1180px; padding-top: 1.5rem; padding-bottom: 3rem; }
[data-testid="stCaptionContainer"] { color: #5A6B7B; }
[data-testid="stMetric"] { background: #FFFFFF; border: 1px solid #D9E1E9; border-left: 4px solid #1F4E79;
    border-radius: 8px; padding: 16px 18px; box-shadow: 0 1px 3px rgba(27,39,51,0.08); }
[data-testid="stMetricLabel"] p { font-size: .8rem; color: #5A6B7B; font-weight: 700;
    letter-spacing: .05em; text-transform: uppercase; }
[data-testid="stMetricValue"] { font-size: 1.65rem; color: #1B2733; font-weight: 700; font-variant-numeric: tabular-nums; }
[data-testid="stMetricDelta"] { font-size: .85rem; }
div[data-testid="stVerticalBlockBorderWrapper"] { border: 1px solid #D9E1E9; border-radius: 10px;
    box-shadow: 0 1px 3px rgba(27,39,51,0.08); background: #FFFFFF; }
[data-testid="stWidgetLabel"] p { font-size: .78rem; color: #5A6B7B; font-weight: 700;
    letter-spacing: .06em; text-transform: uppercase; }
.stTabs [data-baseweb="tab-list"] { gap: 2px; border-bottom: 1px solid #D9E1E9; }
.stTabs [data-baseweb="tab"] { padding: 10px 18px; font-weight: 500; color: #4A5A6A; }
.stTabs [aria-selected="true"] { color: #1F4E79; font-weight: 600; }
[data-testid="stDataFrame"] { border: 1px solid #D9E1E9; border-radius: 10px; }
div[data-testid="stAlert"] { border-radius: 8px; }
#MainMenu, footer { visibility: hidden; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def muat():
    return load_provinsi(), load_kbli()


prov, kbli = muat()

# nama: (kolom, satuan, format label)
METRIK = {
    "Jumlah usaha": ("usaha", "usaha", ",.0f"),
    "Jumlah pekerja": ("pekerja_total", "orang", ",.0f"),
    "Pendapatan (Rp triliun)": ("pendapatan_triliun", "Rp triliun", ",.1f"),
    "Pengeluaran (Rp triliun)": ("pengeluaran_triliun", "Rp triliun", ",.1f"),
}
INDIKATOR = {
    "Pendapatan per usaha (juta Rp)": "pend_per_usaha_juta",
    "Pekerja per usaha (orang)": "pekerja_per_usaha",
    "Pendapatan per pekerja (juta Rp)": "pend_per_pekerja_juta",
    "Margin (%)": "margin_pct",
    "Pekerja tidak dibayar (%)": "pct_tdk_dibayar",
}


def tema(fig, tinggi=420):
    """Gaya grafik seragam: bersih, garis kisi tipis, angka format Indonesia."""
    fig.update_layout(
        template="simple_white",
        height=tinggi,
        separators=",.",
        font=dict(family=FONT, size=13, color="#2B3A4A"),
        title=dict(x=0, xanchor="left", font=dict(size=15, color="#14263B")),
        margin=dict(l=10, r=25, t=55, b=10),
        legend_title_text="",
        paper_bgcolor="white",
        plot_bgcolor="white",
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#EDF0F4", zeroline=False, linecolor="#C5CCD6")
    fig.update_yaxes(showgrid=True, gridcolor="#EDF0F4", zeroline=False, linecolor="#C5CCD6")
    return fig


def tampil(fig, tinggi=420):
    with st.container(border=True):
        st.plotly_chart(tema(fig, tinggi), width="stretch", config={"displayModeBar": False})


def tabel_fmt(df: pd.DataFrame, desimal: int = 2) -> pd.DataFrame:
    """Format seluruh kolom numerik dengan gaya angka Indonesia."""
    return df.apply(lambda kol: kol.map(lambda v: fmt_id(v, desimal) if isinstance(v, (int, float, np.number)) else v))


HIJAU_DELTA = "#2E7D46"
MERAH_DELTA = "#B03A2E"
NAVY_SOFT = "#DBE7F1"


def kartu_kpi(label, nilai, satuan="", delta=None, arah=None):
    """Kartu KPI ala prototype: putih, garis kiri navy 4px, delta ▲/▼/± berwarna."""
    warna = {"naik": HIJAU_DELTA, "turun": MERAH_DELTA, "datar": "#5A6B7B"}.get(arah, "#5A6B7B")
    glyph = {"naik": "▲", "turun": "▼", "datar": "±"}.get(arah, "")
    delta_html = ""
    if delta:
        delta_html = (f'<div style="font-size:0.85rem; color:{warna}; font-weight:700;">{glyph}{delta} '
                      f'<span style="color:#5A6B7B; font-weight:400;">vs 2024</span></div>')
    return (f'<div style="background:#FFFFFF; border:1px solid #D9E1E9; border-left:4px solid #1F4E79; '
            f'border-radius:8px; padding:16px 18px; box-shadow:0 1px 3px rgba(27,39,51,0.08);">'
            f'<div style="font-size:0.8rem; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; '
            f'color:#5A6B7B;">{label}</div>'
            f'<div style="font-size:1.65rem; font-weight:700; color:#1B2733; font-variant-numeric:tabular-nums;">'
            f'{nilai} <span style="font-size:0.9rem; font-weight:400; color:#5A6B7B;">{satuan}</span></div>'
            f'{delta_html}</div>')


def kartu_temuan(judul, isi_html, badge=None):
    """Kartu temuan ala prototype: panel putih dengan angka kunci navy."""
    badge_html = ""
    if badge:
        badge_html = (f' <span style="background:#C98B2B; color:#241A02; font-size:0.72rem; font-weight:700; '
                      f'letter-spacing:0.07em; padding:3px 9px; border-radius:999px;">{badge}</span>')
    return (f'<div style="background:#FFFFFF; border:1px solid #D9E1E9; border-radius:10px; padding:18px; '
            f'box-shadow:0 1px 3px rgba(27,39,51,0.08);">'
            f'<h3 style="font-size:1.02rem; margin:0 0 8px;">{judul}{badge_html}</h3>'
            f'<div style="font-size:0.93rem;">{isi_html}</div></div>')


def angka_kunci(teks):
    return (f'<span style="font-size:1.3rem; font-weight:700; color:#1F4E79; '
            f'font-variant-numeric:tabular-nums;">{teks}</span>')


def lencana(teks):
    """Pill emas ala prototype untuk menandai status data."""
    return (f'<span style="background:#C98B2B; color:#241A02; font-size:0.72rem; font-weight:700; '
            f'letter-spacing:0.07em; padding:3px 9px; border-radius:999px;">{teks}</span>')


def warna_rank(n):
    """Warna batang per peringkat ala prototype: peringkat 1 navy, lalu palet berurutan.
    Daftar diasumsikan terurut menaik (nilai terkecil dulu, seperti grafik horizontal)."""
    return [PALET[(n - 1 - i) % len(PALET)] for i in range(n)]


def callout_navy(teks):
    """Strip callout navy-soft ala prototype."""
    return (f'<div style="background:{NAVY_SOFT}; border-radius:8px; padding:12px 14px; '
            f'font-size:0.92rem; margin-top:16px;">{teks}</div>')


# ---------------------------------------------------------------- Modul penjualan usaha
@st.cache_data
def _contoh():
    """Contoh data nyata: transaksi UCI Online Retail, 1 Des 2010-31 Mei 2011.

    Data dibagi menjadi tiga berkas (data/penjualan_uci_online_retail_1.csv
    s.d. _3.csv) karena batas ukuran berkas; digabung kembali di sini.
    """
    folder = Path(__file__).resolve().parent / "data"
    berkas = sorted(folder.glob("penjualan_uci_online_retail_*.csv"))
    df = pd.concat((pd.read_csv(b) for b in berkas), ignore_index=True)
    return df.sort_values("waktu").reset_index(drop=True)


@st.cache_data
def _baca(nama: str, isi: bytes) -> pd.DataFrame:
    if nama.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(isi))
    return pd.read_csv(io.BytesIO(isi), sep=None, engine="python")


def _tebak(kolom, kunci, opsional=False):
    """Tebak kolom dari nama; untuk kolom opsional indeks digeser satu karena ada '(tidak ada)'."""
    for i, k in enumerate(kolom):
        if any(x in str(k).lower() for x in kunci):
            return i + 1 if opsional else i
    return 0


def render_penjualan():
    st.subheader("Analisis penjualan tingkat usaha")
    st.caption("Tab ini menganalisis data transaksi satu usaha dan tidak dipengaruhi pengaturan Tahun/Wilayah di atas.")
    sumber = st.radio("Sumber data", ["Contoh data nyata (UCI Online Retail)", "Unggah data sendiri"], horizontal=True, key="jual_sumber")

    if sumber == "Contoh data nyata (UCI Online Retail)":
        st.markdown(lencana("DATA NYATA · UCI ONLINE RETAIL"), unsafe_allow_html=True)
        st.info(
            "Data contoh ini adalah data transaksi NYATA dari UCI Online Retail, toko online di Inggris "
            "(1 Des 2010-31 Mei 2011, 203.181 baris). Harga asli dalam pound sterling sudah dikonversi ke rupiah "
            "(£1 = Rp24.215). Ini bukan data UMKM Indonesia — pakai sebagai studi kasus modul penjualan, dan unggah "
            "data transaksi usaha yang sebenarnya untuk analisis yang bermakna."
        )
        raw = _contoh()
        peta = dict(kol_waktu="waktu", kol_produk="produk", kol_jumlah="jumlah", kol_nilai="harga_satuan",
                    nilai_adalah="Harga satuan", kol_id="id_transaksi", kol_kategori=None, dayfirst=False)
    else:
        berkas = st.file_uploader("Berkas transaksi (CSV atau Excel)", type=["csv", "xlsx", "xls"], key="jual_file")
        if berkas is None:
            st.info(
                "Format yang dibutuhkan: satu baris untuk setiap produk yang terjual, dengan kolom tanggal/waktu, "
                "nama produk, jumlah, dan harga (satuan atau total). Kolom ID transaksi dan kategori bersifat "
                "opsional. Contoh format ada di `data/penjualan_uci_online_retail_1.csv` (bagian 1 dari 3)."
            )
            return
        try:
            raw = _baca(berkas.name, berkas.getvalue())
        except Exception as e:  # noqa: BLE001
            st.error(f"Berkas tidak dapat dibaca: {e}")
            return
        kol = list(raw.columns)
        opsi = ["(tidak ada)"] + kol
        with st.expander("Pemetaan kolom", expanded=True):
            c1, c2, c3 = st.columns(3)
            kw = c1.selectbox("Tanggal/waktu", kol, index=_tebak(kol, ["tanggal", "tgl", "date", "waktu", "time"]))
            kp = c2.selectbox("Produk", kol, index=_tebak(kol, ["produk", "item", "barang", "menu", "product"]))
            kj = c3.selectbox("Jumlah", kol, index=_tebak(kol, ["jumlah", "qty", "quantity", "kuantitas"]))
            c4, c5, c6 = st.columns(3)
            kn = c4.selectbox("Kolom harga", kol, index=_tebak(kol, ["harga", "price", "total", "subtotal", "nilai"]))
            na = c5.radio("Kolom harga berisi", ["Harga satuan", "Total nilai per baris"])
            ki = c6.selectbox("ID transaksi (opsional)", opsi, index=_tebak(kol, ["id", "nota", "invoice", "transaksi"], True))
            kk = c6.selectbox("Kategori (opsional)", opsi, index=_tebak(kol, ["kategori", "category", "jenis"], True))
            dayfirst = st.checkbox("Tanggal berformat hari/bulan/tahun (mis. 15/03/2026)", value=True)
        peta = dict(kol_waktu=kw, kol_produk=kp, kol_jumlah=kj, kol_nilai=kn, nilai_adalah=na,
                    kol_id=None if ki == "(tidak ada)" else ki, kol_kategori=None if kk == "(tidak ada)" else kk,
                    dayfirst=dayfirst)

    d, lap = pj.bersihkan(raw, **peta)
    with st.expander("Laporan pembersihan data"):
        st.dataframe(pd.DataFrame.from_dict(lap, orient="index", columns=["Jumlah baris"]), width="stretch")
        st.download_button("Unduh data bersih (CSV)", d.to_csv(index=False).encode("utf-8"),
                           file_name="penjualan_bersih.csv", mime="text/csv")
    if d.empty:
        st.error("Tidak ada baris valid setelah pembersihan. Periksa pemetaan kolom dan format tanggal.")
        return

    r = pj.ringkasan(d)
    pp = pj.per_produk(d)
    rh = pj.rata_per_hari(d)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total omzet", "Rp " + fmt_id(r["omzet"]))
    k2.metric("Jumlah transaksi", fmt_id(r["transaksi"]))
    k3.metric("Rata-rata nilai transaksi", "Rp " + fmt_id(r["nilai_per_transaksi"]))
    k4.metric("Unit terjual", fmt_id(r["unit"]))
    st.caption(f"Periode data: {r['awal']:%d/%m/%Y} sampai {r['akhir']:%d/%m/%Y}.")

    n80 = int((pp["kumulatif_pct"] < 80).sum() + 1)
    if rh.min() > 0:
        banding_hari = (f"Rata-rata omzet harian tertinggi jatuh pada hari {rh.idxmax()} (Rp {fmt_id(rh.max())}), "
                        f"{fmt_id(rh.max() / rh.min(), 2)} kali hari terendah ({rh.idxmin()}).")
    else:
        # Hari terendah tutup (rata-rata omzet Rp 0), sehingga rasio tidak terdefinisi.
        banding_hari = (f"Rata-rata omzet harian tertinggi jatuh pada hari {rh.idxmax()} (Rp {fmt_id(rh.max())}); "
                        f"hari {rh.idxmin()} tutup (rata-rata omzet Rp 0).")
    temuan = [
        f"**{pp.iloc[0]['produk']}** adalah penyumbang omzet terbesar ({fmt_id(pp.iloc[0]['porsi_pct'], 1)}%).",
        f"{n80} dari {len(pp)} produk ({fmt_id(n80 / len(pp) * 100, 0)}%) menghasilkan 80% omzet.",
        banding_hari,
    ]
    if pj.ada_jam(d):
        jam = int(pj.pola_hari_jam(d).sum().idxmax())
        temuan.append(f"Jam tersibuk berdasarkan jumlah transaksi adalah pukul {jam:02d}.00 sampai {jam + 1:02d}.00.")
    st.info("**Ringkasan temuan**\n\n" + "\n".join(f"- {t}" for t in temuan))

    # ---- Tren
    st.subheader("Tren penjualan")
    gran = st.radio("Granularitas", ["Harian", "Mingguan", "Bulanan"], horizontal=True, key="jual_gran")
    t = pj.tren(d, gran)
    if gran == "Harian":
        fig = px.line(t, x="periode", y=["omzet", "rata_7_hari"], title="Omzet harian dan rata-rata bergerak 7 hari")
        fig.data[0].update(name="Omzet harian", line=dict(color="#A9B8C9", width=1))
        fig.data[1].update(name="Rata-rata 7 hari", line=dict(color=BIRU, width=2.4))
    elif gran == "Mingguan":
        fig = px.line(t, x="periode", y="omzet", color_discrete_sequence=[BIRU], title="Omzet mingguan")
    else:
        fig = px.bar(t, x="periode", y="omzet", color_discrete_sequence=[BIRU], title="Omzet bulanan")
        fig.update_traces(marker_line_width=0)
    fig.update_layout(xaxis_title="", yaxis_title="Omzet (Rp)")
    tampil(fig, 400)
    if gran != "Harian":
        st.caption("Periode pertama dan terakhir bisa belum penuh sehingga tampak lebih rendah.")

    # ---- Produk
    st.subheader("Kinerja produk")
    ukuran = st.selectbox("Peringkat produk berdasarkan", ["Omzet", "Unit terjual"], key="jual_ukuran")
    kolom_u = "omzet" if ukuran == "Omzet" else "unit"
    a, b = st.columns([3, 2])
    with a:
        top = pp.nlargest(10, kolom_u).sort_values(kolom_u)
        fig = px.bar(top, x=kolom_u, y="produk", orientation="h",
                     title=f"10 produk teratas menurut {ukuran.lower()}")
        fig.update_traces(texttemplate="%{x:,.0f}", textposition="outside", cliponaxis=False,
                          marker_line_width=0, marker_color=warna_rank(len(top)))
        fig.update_layout(xaxis_title="Rp" if kolom_u == "omzet" else "unit", yaxis_title="", bargap=0.35)
        fig.update_yaxes(showgrid=False)
        tampil(fig, 420)
    with b:
        pareto = pp.assign(peringkat=range(1, len(pp) + 1))
        fig = px.line(pareto, x="peringkat", y="kumulatif_pct", markers=True, color_discrete_sequence=[BIRU],
                      title="Kontribusi kumulatif omzet (Pareto)")
        fig.add_hline(y=80, line_dash="dash", line_color=MERAH, annotation_text="80%")
        fig.update_layout(xaxis_title="Peringkat produk", yaxis_title="Omzet kumulatif (%)", yaxis_range=[0, 102])
        tampil(fig, 420)
    c1, c2 = st.columns([2, 3])
    with c1:
        if d["kategori"].nunique() > 1:
            kat = d.groupby("kategori", as_index=False)["omzet"].sum()
            fig = px.pie(kat, names="kategori", values="omzet", hole=0.55, color_discrete_sequence=PALET,
                         title="Porsi omzet menurut kategori")
            fig.update_traces(textinfo="percent", marker=dict(line=dict(color="white", width=2)))
            tampil(fig, 340)
    with c2:
        tabel = pp.rename(columns={"produk": "Produk", "omzet": "Omzet (Rp)", "unit": "Unit",
                                   "transaksi": "Transaksi", "porsi_pct": "Porsi (%)", "kumulatif_pct": "Kumulatif (%)"})
        st.dataframe(tabel.assign(**{"Omzet (Rp)": tabel["Omzet (Rp)"].map(fmt_id),
                                     "Unit": tabel["Unit"].map(fmt_id), "Transaksi": tabel["Transaksi"].map(fmt_id),
                                     "Porsi (%)": tabel["Porsi (%)"].map(lambda v: fmt_id(v, 1)),
                                     "Kumulatif (%)": tabel["Kumulatif (%)"].map(lambda v: fmt_id(v, 1))}),
                     width="stretch", height=340, hide_index=True)

    # ---- Pola waktu
    st.subheader("Pola waktu")
    a, b = st.columns(2)
    with a:
        rhh = rh.reindex([h for h in pj.HARI if h in rh.index])
        fig = px.bar(x=rhh.index, y=rhh.values, color_discrete_sequence=[BIRU], title="Rata-rata omzet menurut hari")
        fig.update_traces(marker_line_width=0)
        fig.update_layout(xaxis_title="", yaxis_title="Omzet rata-rata per hari (Rp)", bargap=0.35)
        tampil(fig, 400)
    with b:
        if pj.ada_jam(d):
            m = pj.pola_hari_jam(d)
            fig = px.imshow(m, labels=dict(x="Jam", y="Hari", color="Transaksi"), aspect="auto",
                            color_continuous_scale=[[0, "#FFFFFF"], [1, BIRU]], title="Jumlah transaksi menurut hari dan jam")
            fig.update_xaxes(dtick=1, showgrid=False)
            fig.update_yaxes(showgrid=False)
            tampil(fig, 400)
        else:
            st.info("Data tidak memuat informasi jam, sehingga pola per jam tidak ditampilkan.")

    # ---- Prakiraan
    st.subheader("Prakiraan omzet harian")
    horizon = st.slider("Horizon prakiraan (hari)", 7, 60, 14, key="jual_horizon")
    seri = pj.harian(d)
    hasil = pj.prakiraan(seri, horizon)
    if hasil is None:
        st.info("Prakiraan membutuhkan minimal sekitar 12 minggu data harian. Data saat ini belum cukup.")
    else:
        fc = hasil["prakiraan"]
        hist = seri.iloc[-90:]
        fig = go.Figure()
        fig.add_scatter(x=hist.index, y=hist.values, mode="lines", name="Aktual", line=dict(color=BIRU, width=1.6))
        fig.add_scatter(x=fc.index, y=fc["batas_atas"], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip")
        fig.add_scatter(x=fc.index, y=fc["batas_bawah"], mode="lines", line=dict(width=0), fill="tonexty",
                        fillcolor="rgba(181,80,60,0.15)", name="Interval kira-kira 95%", hoverinfo="skip")
        fig.add_scatter(x=fc.index, y=fc["prakiraan"], mode="lines", name="Prakiraan",
                        line=dict(color=MERAH, width=2, dash="dash"))
        fig.update_layout(title=f"Prakiraan {horizon} hari ke depan (90 hari terakhir sebagai latar)",
                          xaxis_title="", yaxis_title="Omzet harian (Rp)")
        tampil(fig, 420)

        mt = hasil["metrik"].copy()
        mt["MAE"] = mt["MAE"].map(lambda v: "Rp " + fmt_id(v))
        mt["WAPE (%)"] = mt["WAPE (%)"].map(lambda v: fmt_id(v, 1))
        st.markdown("**Evaluasi pada 28 hari terakhir** (tidak dipakai untuk melatih model)")
        st.dataframe(mt, width="stretch")
        lebih = hasil["metrik"].loc["Holt-Winters", "WAPE (%)"] < hasil["metrik"].loc["Baseline musiman-naif", "WAPE (%)"]
        st.caption(
            "Model: Holt-Winters (tren teredam dan musiman mingguan). Baseline musiman-naif mengulang pola 7 hari "
            "terakhir. "
            + ("Model lebih akurat daripada baseline pada data uji. " if lebih else
               "Model tidak lebih akurat daripada baseline pada data uji, sehingga prakiraannya perlu dipakai dengan hati-hati. ")
            + "Interval dihitung kasar dari simpangan baku residual."
        )


# ---------------------------------------------------------------- Kesimpulan
def render_kesimpulan():
    def pct(v):
        return f"{'+' if v > 0 else ''}{fmt_id(v, 1)}%"

    nas = perubahan_nasional(prov)
    marg = {}
    for th in (2024, 2025):
        s = prov[prov["tahun"] == th]
        marg[th] = (s["pendapatan_000"].sum() - s["pengeluaran_000"].sum()) / s["pendapatan_000"].sum() * 100
    p25 = prov[prov["tahun"] == 2025]
    jawa = p25[p25["wilayah"] == "Jawa"]
    top3 = kbli[kbli["tahun"] == 2025].nlargest(3, "usaha")
    model, _, _ = regresi(prov)
    b_d, b_t = model.params["ln_dibayar"], model.params["ln_tdk_dibayar"]
    sil = {th: klaster(prov[prov["tahun"] == th], 3)[1][3] for th in (2024, 2025)}

    st.subheader("Temuan utama dari data nasional (BPS)")
    st.markdown(f"""
- **Skala tetap, tenaga kerja menyusut.** Jumlah usaha {pct(nas.loc['Jumlah usaha', 'perubahan_pct'])}, jumlah pekerja
  {pct(nas.loc['Pekerja (total)', 'perubahan_pct'])}, pendapatan {pct(nas.loc['Pendapatan (000 Rp)', 'perubahan_pct'])}, pengeluaran
  {pct(nas.loc['Pengeluaran (000 Rp)', 'perubahan_pct'])} (2024 ke 2025). Margin kasar bergeser dari {fmt_id(marg[2024], 1)}% ke {fmt_id(marg[2025], 1)}%.
- **Terkonsentrasi di Jawa.** Pulau Jawa menyumbang {fmt_id(jawa['usaha'].sum() / p25['usaha'].sum() * 100, 1)}% usaha dan
  {fmt_id(jawa['pendapatan_000'].sum() / p25['pendapatan_000'].sum() * 100, 1)}% pendapatan pada 2025.
- **Didominasi beberapa jenis industri.** {', '.join(top3['sektor'])} mencakup {fmt_id(top3['usaha'].sum() / kbli[kbli['tahun'] == 2025]['usaha'].sum() * 100, 1)}% usaha pada 2025.
""")
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(kartu_temuan(
            "Regresi pekerja–pendapatan",
            f"Elastisitas terhadap pekerja dibayar {angka_kunci(fmt_id(b_d, 2))} dan terhadap pekerja "
            f"tidak dibayar {angka_kunci(fmt_id(b_t, 2))} (jumlah {fmt_id(b_d + b_t, 2)}). "
            f"Ini asosiasi antar provinsi, bukan sebab-akibat."
        ), unsafe_allow_html=True)
    with f2:
        st.markdown(kartu_temuan(
            "Klaster provinsi (K-Means)",
            f"Silhouette k = 3 hanya {angka_kunci(fmt_id(sil[2024], 2))} (2024) dan "
            f"{angka_kunci(fmt_id(sil[2025], 2))} (2025) — struktur lemah dan tidak stabil antar tahun, "
            f"sehingga klaster dibaca sebagai eksplorasi."
        ), unsafe_allow_html=True)
    with f3:
        st.markdown(kartu_temuan(
            "Penjualan tingkat usaha",
            "Holt-Winters pada data transaksi nyata: WAPE "
            f"{angka_kunci('59,4%')} vs baseline musiman-naif {angka_kunci('56,3%')} "
            f"pada 28 hari uji (Mei 2011) — model tidak lebih akurat dari baseline pada data nyata yang berisik.",
            badge="DATA NYATA"
        ), unsafe_allow_html=True)

    st.subheader("Implikasi bagi pelaku UMKM")
    st.markdown("""
- Jenis industri berbeda jauh dalam produktivitas per pekerja dan margin (tab Jenis Industri), sehingga pemilihan jenis usaha
  dan produk berpengaruh pada hasil.
- Pendapatan yang berasosiasi hampir sebanding dengan tenaga kerja menunjukkan bahwa peningkatan skala tanpa perbaikan
  produktivitas tidak otomatis menaikkan pendapatan per pekerja.
- Di tingkat usaha, pemantauan rutin atas produk penyumbang omzet, hari dan jam ramai, serta prakiraan permintaan
  (tab Penjualan Usaha) membantu perencanaan stok dan jadwal kerja.
""")

    st.subheader("Batasan")
    st.markdown("""
- Data BPS hanya mencakup industri pengolahan skala mikro dan kecil, dari survei sampel, dan hanya dua tahun.
- Hasil regresi dan klaster bersifat asosiatif dan eksploratif.
- Modul penjualan usaha memakai contoh data transaksi nyata (UCI Online Retail, bukan UMKM Indonesia) kecuali pengguna mengunggah data transaksi sendiri.
""")

# ---------------------------------------------------------------- Header + filter (ala prototype: tanpa sidebar)
st.markdown(
    """
<div style="background:#1F4E79; color:#FFFFFF; border-radius:10px; padding:28px 24px 24px; margin-bottom:20px;">
<h1 style="font-family:Georgia,'Times New Roman',Times,serif; font-size:2rem; line-height:1.2; margin:0 0 8px; color:#FFFFFF;">Dashboard Analisis UMKM Indonesia</h1>
<p style="font-size:1rem; color:#D7E5F1; max-width:62ch; margin:0 0 8px;">Dua lapisan analisis: (1) konteks nasional UMKM sektor industri pengolahan dari data BPS 2024&ndash;2025, dan (2) analisis penjualan tingkat usaha.</p>
<p style="font-size:0.85rem; color:#A9C4DA; margin:0;">Sumber data: BPS, Profil Industri Mikro dan Kecil 2024 (Vol. 15, 2025) dan 2025 (Vol. 16, 2026), Katalog 6104006. Survei sampel; cakupan industri pengolahan dengan 1 sampai 19 pekerja. Usaha perdagangan dan jasa tidak termasuk.</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.container(border=True):
    f1, f2, f3 = st.columns([1, 2, 1.1])
    with f1:
        tahun = st.segmented_control("Tahun", [2025, 2024], default=2025)
    with f2:
        wilayah_semua = sorted(prov["wilayah"].unique())
        wilayah = st.multiselect("Wilayah", wilayah_semua, default=wilayah_semua)
        if not wilayah:
            st.warning("Pilih minimal satu wilayah. Sementara semua wilayah dipakai.")
            wilayah = wilayah_semua
    with f3:
        st.markdown(
            "<p style='font-size:0.85rem; color:#5A6B7B; margin-top:1.9rem;'>Cakupan: industri pengolahan "
            "mikro dan kecil (1&ndash;19 pekerja), bukan seluruh UMKM.</p>",
            unsafe_allow_html=True,
        )
st.caption(
    "Pengaturan ini berlaku pada tab Ringkasan Nasional dan Eksplorasi Data (tahun juga pada Jenis Industri). "
    "Tab Model dan Klaster memakai seluruh 38 provinsi. Tab Penjualan Usaha tidak terpengaruh."
)

p_tahun = prov[(prov["tahun"] == tahun) & (prov["wilayah"].isin(wilayah))]
k_tahun = kbli[kbli["tahun"] == tahun]

(tab_jual, tab_ringkas, tab_eda, tab_sektor, tab_ubah, tab_model, tab_simpul, tab_data) = st.tabs(
    ["Penjualan Usaha", "Ringkasan Nasional", "Eksplorasi Data", "Jenis Industri", "Perubahan 2024-2025",
     "Model dan Klaster", "Kesimpulan", "Data dan Metodologi"]
)

with tab_jual:
    render_penjualan()

with tab_simpul:
    render_kesimpulan()

# ================================================================ 1. Ringkasan
with tab_ringkas:
    kolom_kpi = ["usaha", "pekerja_total", "pendapatan_triliun", "pengeluaran_triliun"]
    tot = p_tahun[kolom_kpi].sum()
    margin = (tot["pendapatan_triliun"] - tot["pengeluaran_triliun"]) / tot["pendapatan_triliun"] * 100
    pembanding = None
    marg0 = None
    if tahun == 2025:
        p0 = prov[(prov["tahun"] == 2024) & (prov["wilayah"].isin(wilayah))]
        pembanding = p0[kolom_kpi].sum()
        marg0 = (pembanding["pendapatan_triliun"] - pembanding["pengeluaran_triliun"]) / pembanding["pendapatan_triliun"] * 100

    def delta_kpi(kol):
        """(teks delta, arah) ala prototype: ▲/▼/± dengan warna hijau/merah."""
        if pembanding is None:
            return None, None
        v = (tot[kol] / pembanding[kol] - 1) * 100
        arah = "naik" if v > 0 else ("turun" if v < 0 else "datar")
        return f"{fmt_id(abs(v), 1)}%", arah

    def delta_poin():
        if marg0 is None:
            return None, None
        v = margin - marg0
        arah = "naik" if v > 0 else ("turun" if v < 0 else "datar")
        return f"{fmt_id(abs(v), 1)} poin", arah

    d_usaha, a_usaha = delta_kpi("usaha")
    d_pek, a_pek = delta_kpi("pekerja_total")
    d_pend, a_pend = delta_kpi("pendapatan_triliun")
    d_kel, a_kel = delta_kpi("pengeluaran_triliun")
    d_mar, a_mar = delta_poin()
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(kartu_kpi("Jumlah usaha", fmt_id(tot["usaha"]), "usaha", d_usaha, a_usaha), unsafe_allow_html=True)
    with k2:
        st.markdown(kartu_kpi("Total pekerja", fmt_id(tot["pekerja_total"]), "orang", d_pek, a_pek), unsafe_allow_html=True)
    with k3:
        st.markdown(kartu_kpi("Pendapatan", fmt_id(tot["pendapatan_triliun"], 1), "Rp triliun", d_pend, a_pend), unsafe_allow_html=True)
    with k4:
        st.markdown(kartu_kpi("Pengeluaran", fmt_id(tot["pengeluaran_triliun"], 1), "Rp triliun", d_kel, a_kel), unsafe_allow_html=True)
    with k5:
        st.markdown(kartu_kpi("Margin kasar", f"{fmt_id(margin, 1)}%", "", d_mar, a_mar), unsafe_allow_html=True)

    st.write("")
    pilih = st.selectbox("Tampilkan berdasarkan", list(METRIK), key="rank_metrik")
    kol, sat, fmt = METRIK[pilih]

    kiri, kanan = st.columns([3, 2])
    with kiri:
        top = p_tahun.nlargest(8, kol).sort_values(kol)
        fig = px.bar(top, x=kol, y="provinsi", orientation="h",
                     title=f"8 provinsi teratas: {pilih}, {tahun}")
        fig.update_traces(texttemplate="%{x:" + fmt + "}", textposition="outside", cliponaxis=False,
                          marker_line_width=0, marker_color=warna_rank(len(top)))
        fig.update_layout(xaxis_title=sat, yaxis_title="", bargap=0.35)
        fig.update_yaxes(showgrid=False)
        tampil(fig, 440)
    with kanan:
        porsi = p_tahun.groupby("wilayah", as_index=False)[kol].sum().sort_values(kol, ascending=False)
        fig = px.pie(porsi, names="wilayah", values=kol, hole=0.55, color_discrete_sequence=PALET,
                     title=f"Porsi menurut wilayah")
        fig.update_traces(textinfo="percent", sort=False, marker=dict(line=dict(color="white", width=2)))
        tampil(fig, 440)

    if "Jawa" in wilayah:
        jawa = p_tahun[p_tahun["wilayah"] == "Jawa"][kol].sum() / p_tahun[kol].sum() * 100
        st.caption(f"Pada filter yang dipilih, Pulau Jawa menyumbang {fmt_id(jawa, 1)}% dari {pilih.lower()} tahun {tahun}.")

# ================================================================ 2. EDA
with tab_eda:
    st.subheader("Statistik deskriptif antar provinsi")
    ringkas = p_tahun[list(INDIKATOR.values())].describe().T
    ringkas.index = list(INDIKATOR.keys())
    ringkas = ringkas.rename(columns={"count": "n", "mean": "Rata-rata", "std": "Simpangan baku", "min": "Min",
                                      "25%": "Q1", "50%": "Median", "75%": "Q3", "max": "Maks"})
    st.dataframe(tabel_fmt(ringkas), width="stretch")

    a, b = st.columns(2)
    with a:
        ind = st.selectbox("Distribusi indikator", list(INDIKATOR), key="eda_ind")
        fig = px.box(p_tahun, y=INDIKATOR[ind], points="all", hover_name="provinsi",
                     color_discrete_sequence=[BIRU], title=f"Sebaran {ind}, {tahun}")
        fig.update_layout(yaxis_title="", xaxis_title="")
        tampil(fig, 440)
    with b:
        st.write("")
        st.write("")
        fig = px.scatter(p_tahun, x="pekerja_total", y="pendapatan_triliun", color="wilayah",
                         hover_name="provinsi", log_x=True, log_y=True, color_discrete_sequence=PALET,
                         trendline="ols", trendline_scope="overall", trendline_color_override="#444444",
                         trendline_options=dict(log_x=True, log_y=True),
                         title=f"Pekerja dan pendapatan (skala log), {tahun}")
        fig.update_traces(selector=dict(mode="markers"), marker=dict(size=9, opacity=0.85,
                                                                       line=dict(width=0.5, color="white")))
        fig.update_layout(xaxis_title="Jumlah pekerja", yaxis_title="Pendapatan (Rp triliun)")
        tampil(fig, 440)

    st.subheader("Korelasi antar indikator")
    kor_kolom = {"usaha": "Usaha", "pekerja_total": "Pekerja", "pendapatan_triliun": "Pendapatan",
                 "pend_per_usaha_juta": "Pend./usaha", "pend_per_pekerja_juta": "Pend./pekerja",
                 "margin_pct": "Margin", "pct_tdk_dibayar": "% tdk dibayar"}
    kor = p_tahun[list(kor_kolom)].rename(columns=kor_kolom).corr(method="spearman")
    fig = px.imshow(kor, text_auto=".2f", zmin=-1, zmax=1, aspect="auto",
                    color_continuous_scale=[[0, MERAH], [0.5, "#FFFFFF"], [1, BIRU]],
                    title=f"Korelasi peringkat Spearman, {tahun}")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    tampil(fig, 480)
    st.caption("Jumlah usaha, pekerja, dan pendapatan berkorelasi sangat kuat karena sama-sama mengukur ukuran "
               "provinsi. Indikator per usaha dan per pekerja lebih informatif untuk membandingkan produktivitas.")

# ================================================================ 3. Jenis industri
with tab_sektor:
    pil = st.selectbox("Ukuran", list(METRIK), key="sektor_metrik")
    kol, sat, fmt = METRIK[pil]
    s = k_tahun.sort_values(kol)
    fig = px.bar(s, x=kol, y="label", orientation="h",
                 title=f"{pil} menurut jenis industri (KBLI 2 digit), {tahun}")
    fig.update_traces(texttemplate="%{x:" + fmt + "}", textposition="outside", cliponaxis=False,
                      marker_line_width=0, marker_color=warna_rank(len(s)))
    fig.update_layout(xaxis_title=sat, yaxis_title="", bargap=0.3)
    fig.update_yaxes(showgrid=False)
    tampil(fig, 680)

    top3 = k_tahun.nlargest(3, "usaha")
    pangsa = top3["usaha"].sum() / k_tahun["usaha"].sum() * 100
    st.caption(f"Tiga jenis industri dengan usaha terbanyak ({', '.join(top3['sektor'])}) mencakup "
               f"{fmt_id(pangsa, 1)}% dari seluruh usaha pada {tahun}.")

    st.subheader("Produktivitas menurut jenis industri")
    ind = st.selectbox("Indikator", list(INDIKATOR), key="sektor_ind")
    s2 = k_tahun.sort_values(INDIKATOR[ind])
    fig = px.bar(s2, x=INDIKATOR[ind], y="label", orientation="h",
                 title=f"{ind}, {tahun}")
    fig.update_traces(texttemplate="%{x:,.1f}", textposition="outside", cliponaxis=False,
                      marker_line_width=0, marker_color=warna_rank(len(s2)))
    fig.update_layout(xaxis_title="", yaxis_title="", bargap=0.3)
    fig.update_yaxes(showgrid=False)
    tampil(fig, 680)
    st.caption("Industri dengan jumlah usaha sangat kecil (misalnya KBLI 26 dan 29) rentan terhadap variasi sampel, "
               "sehingga rata-ratanya perlu dibaca hati-hati.")

# ================================================================ 4. Perubahan
with tab_ubah:
    st.subheader("Perbandingan 2024–2025")
    st.caption("Batang abu-abu 2024, batang navy 2025 — ala panel perbandingan prototype.")
    nas = perubahan_nasional(prov)
    banding = [
        ("Jumlah usaha", nas.loc["Jumlah usaha", "2024"], nas.loc["Jumlah usaha", "2025"],
         nas.loc["Jumlah usaha", "perubahan_pct"], "juta usaha", 1e6),
        ("Total pekerja", nas.loc["Pekerja (total)", "2024"], nas.loc["Pekerja (total)", "2025"],
         nas.loc["Pekerja (total)", "perubahan_pct"], "juta orang", 1e6),
        ("Pendapatan", nas.loc["Pendapatan (000 Rp)", "2024"] / 1e9, nas.loc["Pendapatan (000 Rp)", "2025"] / 1e9,
         nas.loc["Pendapatan (000 Rp)", "perubahan_pct"], "Rp triliun", 1),
        ("Pengeluaran", nas.loc["Pengeluaran (000 Rp)", "2024"] / 1e9, nas.loc["Pengeluaran (000 Rp)", "2025"] / 1e9,
         nas.loc["Pengeluaran (000 Rp)", "perubahan_pct"], "Rp triliun", 1),
    ]
    b1, b2, b3, b4 = st.columns(4)
    for kolom_c, (judul, v24, v25, pct_v, satuan, skala) in zip((b1, b2, b3, b4), banding):
        with kolom_c:
            fig = go.Figure()
            fig.add_bar(x=["2024", "2025"], y=[v24, v25], marker_color=["#7F8C99", BIRU], width=0.55,
                        text=[fmt_id(v24 / skala, 1) if satuan != "Rp triliun" else fmt_id(v24, 1),
                              fmt_id(v25 / skala, 1) if satuan != "Rp triliun" else fmt_id(v25, 1)],
                        textposition="outside")
            fig.update_layout(title=f"{judul} ({satuan})", height=260, showlegend=False,
                              margin=dict(l=10, r=10, t=45, b=10), template="simple_white",
                              font=dict(family=FONT, size=13, color="#2B3A4A"),
                              paper_bgcolor="white", plot_bgcolor="white")
            fig.update_xaxes(showgrid=False, linecolor="#C5CCD6")
            fig.update_yaxes(showgrid=True, gridcolor="#EDF0F4", zeroline=False)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
            st.markdown(f"Perubahan: **{'+' if pct_v > 0 else ''}{fmt_id(pct_v, 1)}%**")
    p25 = prov[prov["tahun"] == 2025]
    jawa_u = p25[p25["wilayah"] == "Jawa"]["usaha"].sum() / p25["usaha"].sum() * 100
    jawa_p = p25[p25["wilayah"] == "Jawa"]["pendapatan_000"].sum() / p25["pendapatan_000"].sum() * 100
    top3 = kbli[kbli["tahun"] == 2025].nlargest(3, "usaha")
    pangsa3 = top3["usaha"].sum() / kbli[kbli["tahun"] == 2025]["usaha"].sum() * 100
    st.markdown(callout_navy(
        f"Pulau Jawa menyumbang {fmt_id(jawa_u, 1)}% jumlah usaha dan {fmt_id(jawa_p, 1)}% pendapatan nasional "
        f"pada 2025. Tiga divisi KBLI teratas — {', '.join(top3['sektor'])} — mencakup {fmt_id(pangsa3, 1)}% usaha."
    ), unsafe_allow_html=True)

    st.subheader("Perubahan nasional")
    tmp = nas.copy()
    for kolom in ("2024", "2025"):
        tmp[kolom] = tmp[kolom].map(lambda v: fmt_id(v))
    tmp["perubahan_pct"] = tmp["perubahan_pct"].map(lambda v: f"{'+' if v > 0 else ''}{fmt_id(v, 1)}%")
    st.dataframe(tmp.rename(columns={"perubahan_pct": "Perubahan"}), width="stretch")

    st.subheader("Perubahan antar provinsi")
    var_ubah = {"Jumlah usaha": "usaha", "Jumlah pekerja": "pekerja_total", "Pendapatan": "pendapatan_000"}
    pv = st.selectbox("Variabel", list(var_ubah), key="ubah_var")
    ch = perubahan_provinsi(prov, var_ubah[pv])
    ch["arah"] = np.where(ch["perubahan_pct"] >= 0, "Naik", "Turun")
    fig = px.bar(ch, x="perubahan_pct", y="provinsi", orientation="h", color="arah",
                 color_discrete_map={"Naik": BIRU, "Turun": MERAH},
                 title=f"Perubahan {pv.lower()} 2024 ke 2025 (%)",
                 hover_data={"2024": ":,.0f", "2025": ":,.0f", "arah": False})
    fig.update_traces(marker_line_width=0)
    fig.update_layout(xaxis_title="Perubahan (%)", yaxis_title="", bargap=0.3, showlegend=False,
                      yaxis=dict(categoryorder="total ascending", showgrid=False))
    tampil(fig, 900)
    rentang = ch["perubahan_pct"]
    st.warning(
        f"Perubahan antar provinsi sangat lebar (dari {rentang.min():.0f}% sampai +{rentang.max():.0f}%). Data BPS "
        "berasal dari survei sampel, sehingga selisih dua tahun di tingkat provinsi dapat dipengaruhi variasi "
        "sampel dan tidak otomatis mencerminkan perubahan kondisi riil. Hanya dua titik waktu yang tersedia, "
        "sehingga tidak dilakukan peramalan deret waktu."
    )

# ================================================================ 5. Model dan klaster
with tab_model:
    st.subheader("Regresi: hubungan pekerja dengan pendapatan")
    st.markdown(
        "Model log-log pada 76 pengamatan (38 provinsi x 2 tahun):  \n"
        "`ln(pendapatan) = b0 + b1 ln(pekerja dibayar) + b2 ln(pekerja tidak dibayar) + b3 D2025 + e`  \n"
        "Koefisien b1 dan b2 dibaca sebagai elastisitas: kenaikan 1% pekerja berasosiasi dengan kenaikan "
        "pendapatan sebesar b%. Galat baku robust terhadap korelasi dalam provinsi (cluster)."
    )
    model, tabel, vif = regresi(prov)
    tr = tabel.copy()
    tr["p-value"] = tr["p-value"].map(lambda v: "<0,001" if v < 0.001 else fmt_id(v, 3))
    for kolom in ["Koefisien", "Galat baku", "z", "CI 95% bawah", "CI 95% atas"]:
        tr[kolom] = tr[kolom].map(lambda v: fmt_id(v, 3))
    st.dataframe(tr, width="stretch")
    m1, m2, m3 = st.columns(3)
    m1.metric("R-kuadrat", fmt_id(model.rsquared, 3))
    m2.metric("Jumlah pengamatan", int(model.nobs))
    m3.metric("Jumlah elastisitas (b1 + b2)", fmt_id(model.params["ln_dibayar"] + model.params["ln_tdk_dibayar"], 2))
    st.caption("VIF: " + ", ".join(f"{k} = {fmt_id(v, 1)}" for k, v in vif.items() if k != "d2025")
               + ". Nilai di atas 10 menandakan multikolinearitas yang tinggi, sehingga pembagian pengaruh antara "
               "dua jenis pekerja kurang tegas.")
    st.info(
        "Interpretasi hati-hati: model ini menunjukkan asosiasi antar provinsi, bukan hubungan sebab-akibat. "
        "R-kuadrat tinggi sebagian besar mencerminkan perbedaan ukuran provinsi. Dummy 2025 yang tidak signifikan "
        "berarti tidak ada pergeseran tingkat pendapatan yang jelas antar tahun setelah ukuran tenaga kerja dikendalikan."
    )

    st.subheader("Klaster provinsi (K-Means)")
    c1, c2 = st.columns(2)
    thn_k = c1.selectbox("Tahun data klaster", [2025, 2024], key="k_tahun")
    k = c2.slider("Jumlah klaster (k)", 2, 6, 3)
    st.caption("Indikator (distandarisasi): " + "; ".join(FITUR_KLASTER.values()) + ".")
    hasil, sil, profil, var_pc = klaster(prov[prov["tahun"] == thn_k], k)

    a, b = st.columns(2)
    with a:
        sdf = pd.DataFrame({"k": list(sil), "silhouette": list(sil.values())})
        fig = px.line(sdf, x="k", y="silhouette", markers=True, color_discrete_sequence=[BIRU],
                      title="Silhouette score menurut k")
        fig.update_layout(xaxis=dict(dtick=1), yaxis_title="Silhouette", xaxis_title="Jumlah klaster (k)")
        tampil(fig, 380)
    with b:
        fig = px.scatter(hasil, x="PC1", y="PC2", color="klaster", hover_name="provinsi",
                         color_discrete_sequence=PALET,
                         title=f"Proyeksi PCA ({fmt_id(var_pc.sum() * 100, 0)}% varians)")
        fig.update_traces(marker=dict(size=10, opacity=0.9, line=dict(width=0.5, color="white")))
        tampil(fig, 380)

    st.dataframe(tabel_fmt(profil), width="stretch")
    for nama, grup in hasil.groupby("klaster"):
        st.markdown(f"**{nama}** ({len(grup)} provinsi): " + ", ".join(sorted(grup["provinsi"])))
    st.info(
        "Nilai silhouette yang rendah (di bawah sekitar 0,5) menandakan struktur klaster yang lemah, dan hasilnya "
        "berubah antar tahun. Klaster kecil umumnya berisi provinsi dengan karakter menyimpang (misalnya DKI Jakarta "
        "dengan porsi pekerja dibayar tinggi), bukan kelompok yang tegas. Hasil ini bersifat eksploratif."
    )

# ================================================================ 6. Data dan metodologi
with tab_data:
    st.subheader("Data")
    set_data = st.radio("Dataset", ["Per provinsi", "Per jenis industri (KBLI)"], horizontal=True)
    if set_data == "Per provinsi":
        sumber, nama = prov, "imk_provinsi_2024_2025_olahan.csv"
    else:
        sumber, nama = kbli, "imk_kbli_2024_2025_olahan.csv"
    data_tampil = sumber.drop(columns=["ln_pend_usaha", "ln_pend_pekerja"]).round(3)
    st.dataframe(data_tampil, width="stretch", height=380)
    st.download_button("Unduh CSV", data_tampil.to_csv(index=False).encode("utf-8"), file_name=nama,
                       mime="text/csv")

    st.subheader("Metodologi")
    st.markdown("""
**Sumber.** BPS, *Profil Industri Mikro dan Kecil 2024* (Vol. 15, 2025) dan *2025* (Vol. 16, 2026), Tabel 5 (menurut KBLI) dan
Tabel 6 (menurut provinsi). Nilai pendapatan, pengeluaran, dan balas jasa dalam ribu rupiah.

**Cakupan.** Industri pengolahan (manufaktur) dengan 1 sampai 19 pekerja. Data ini **tidak** mencakup seluruh UMKM
(perdagangan dan jasa tidak termasuk), sehingga kesimpulan hanya berlaku untuk industri mikro dan kecil sektor manufaktur.

**Pengolahan.** Tabel diekstrak dari PDF, lalu divalidasi dengan menjumlahkan seluruh baris dan membandingkannya dengan
baris total nasional BPS (selisih maksimum 4 satuan, akibat pembulatan). Sebagian baris yang terpecah oleh watermark PDF
dibaca ulang secara manual dari dokumen.

**Indikator turunan.** Pendapatan per usaha, pekerja per usaha, pendapatan per pekerja, margin ((pendapatan - pengeluaran) /
pendapatan), dan persentase pekerja tidak dibayar. Margin adalah pendekatan kasar karena pengeluaran tidak memuat seluruh
komponen biaya.

**Modul penjualan usaha.** Menganalisis data transaksi satu usaha. Pembersihan: tanggal tidak terbaca, produk kosong,
jumlah tidak positif, dan nilai kosong atau negatif dibuang dan dilaporkan. Prakiraan memakai Holt-Winters (tren teredam dan
musiman mingguan), dievaluasi pada 28 hari terakhir terhadap baseline musiman-naif dengan MAE dan WAPE. Contoh data yang
tersedia adalah **data transaksi nyata** (UCI Online Retail, toko online Inggris, 1 Des 2010-31 Mei 2011;
harga dalam pound sterling dikonversi ke rupiah, £1 = Rp24.215). Data ini bukan data UMKM Indonesia, melainkan
studi kasus modul penjualan. Sitasi: Chen, Sain, & Guo (2012), UCI Machine Learning Repository, dataset 352.

**Keterbatasan.** (1) Data survei sampel, sehingga angka provinsi memiliki galat sampling yang tidak tersedia di tabel.
(2) Hanya dua tahun, sehingga tidak ada peramalan deret waktu. (3) Provinsi baru hasil pemekaran Papua memiliki jumlah
usaha kecil. (4) Hasil regresi dan klaster bersifat asosiatif dan eksploratif.
""")

# ---------------------------------------------------------------- Footer (ala prototype)
st.markdown(
    """
<div style="margin-top:34px; border-top:1px solid #D9E1E9; padding-top:16px; color:#5A6B7B; font-size:0.85rem;">
Sumber: Badan Pusat Statistik (BPS), Profil Industri Mikro dan Kecil 2024 &amp; 2025, Katalog 6104006.
Repo asal: <a href="https://github.com/Lunatic-1/Dashboard_analisis_umkm" style="color:#1F4E79;">github.com/Lunatic-1/Dashboard_analisis_umkm</a>
</div>
""",
    unsafe_allow_html=True,
)

