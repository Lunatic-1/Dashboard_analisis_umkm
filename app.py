"""Dashboard Analisis Industri Mikro dan Kecil (IMK) Indonesia, 2024-2025.

Sumber data: BPS, Profil Industri Mikro dan Kecil 2024 dan 2025.
Jalankan dengan:  streamlit run app.py
"""
import io

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
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600&family=Source+Serif+4:wght@600;700&display=swap');
.stApp { font-family: 'Source Sans 3', 'Segoe UI', Arial, sans-serif; color: #1F2933; }
h1, h2, h3 { font-family: 'Source Serif 4', Georgia, serif !important; color: #14263B; font-weight: 600; letter-spacing: 0; }
.block-container { max-width: 1240px; padding-top: 2.2rem; padding-bottom: 3rem; }
h1 { font-size: 1.95rem !important; padding-bottom: .45rem; border-bottom: 2px solid #1F4E79; margin-bottom: .4rem; }
h3 { font-size: 1.2rem !important; margin-top: 1.2rem; }
[data-testid="stCaptionContainer"] { color: #5B6B7B; }
[data-testid="stMetric"] { background: #FFFFFF; border: 1px solid #D9DEE5; border-left: 4px solid #1F4E79;
    border-radius: 4px; padding: 14px 16px; }
[data-testid="stMetricLabel"] p { font-size: .82rem; color: #5B6B7B; font-weight: 500; }
[data-testid="stMetricValue"] { font-size: 1.65rem; color: #14263B; font-weight: 600; }
.stTabs [data-baseweb="tab-list"] { gap: 2px; border-bottom: 1px solid #D9DEE5; }
.stTabs [data-baseweb="tab"] { padding: 10px 18px; font-weight: 500; color: #4A5A6A; }
.stTabs [aria-selected="true"] { color: #1F4E79; font-weight: 600; }
section[data-testid="stSidebar"] { border-right: 1px solid #D9DEE5; }
[data-testid="stSidebar"] h2 { font-size: 1.1rem !important; }
[data-testid="stDataFrame"] { border: 1px solid #D9DEE5; border-radius: 4px; }
div[data-testid="stAlert"] { border-radius: 4px; }
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


# ---------------------------------------------------------------- Modul penjualan usaha
@st.cache_data
def _contoh():
    return pj.contoh_data()


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
    st.caption("Tab ini menganalisis data transaksi satu usaha dan tidak dipengaruhi pengaturan di sidebar.")
    sumber = st.radio("Sumber data", ["Contoh data simulasi", "Unggah data sendiri"], horizontal=True, key="jual_sumber")

    if sumber == "Contoh data simulasi":
        st.warning(
            "Data ini adalah SIMULASI sebuah kedai kopi selama satu tahun, dibuat untuk mendemonstrasikan fitur. "
            "Pola seperti ramai di akhir pekan sudah ditanam pada generator, sehingga bukan temuan nyata. "
            "Unggah data transaksi usaha yang sebenarnya untuk analisis yang bermakna."
        )
        raw = _contoh()
        peta = dict(kol_waktu="waktu", kol_produk="produk", kol_jumlah="jumlah", kol_nilai="harga_satuan",
                    nilai_adalah="Harga satuan", kol_id="id_transaksi", kol_kategori="kategori", dayfirst=False)
    else:
        berkas = st.file_uploader("Berkas transaksi (CSV atau Excel)", type=["csv", "xlsx", "xls"], key="jual_file")
        if berkas is None:
            st.info(
                "Format yang dibutuhkan: satu baris untuk setiap produk yang terjual, dengan kolom tanggal/waktu, "
                "nama produk, jumlah, dan harga (satuan atau total). Kolom ID transaksi dan kategori bersifat "
                "opsional. Contoh format ada di `data/contoh_penjualan_simulasi.csv`."
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
    temuan = [
        f"**{pp.iloc[0]['produk']}** adalah penyumbang omzet terbesar ({fmt_id(pp.iloc[0]['porsi_pct'], 1)}%).",
        f"{n80} dari {len(pp)} produk ({fmt_id(n80 / len(pp) * 100, 0)}%) menghasilkan 80% omzet.",
        f"Rata-rata omzet harian tertinggi jatuh pada hari {rh.idxmax()} (Rp {fmt_id(rh.max())}), "
        f"{fmt_id(rh.max() / rh.min(), 2)} kali hari terendah ({rh.idxmin()}).",
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
        fig = px.bar(top, x=kolom_u, y="produk", orientation="h", color_discrete_sequence=[BIRU],
                     title=f"10 produk teratas menurut {ukuran.lower()}")
        fig.update_traces(texttemplate="%{x:,.0f}", textposition="outside", cliponaxis=False, marker_line_width=0)
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
1. **Skala tetap, tenaga kerja menyusut.** Jumlah usaha {pct(nas.loc['Jumlah usaha', 'perubahan_pct'])}, jumlah pekerja
   {pct(nas.loc['Pekerja (total)', 'perubahan_pct'])}, pendapatan {pct(nas.loc['Pendapatan (000 Rp)', 'perubahan_pct'])}, pengeluaran
   {pct(nas.loc['Pengeluaran (000 Rp)', 'perubahan_pct'])} (2024 ke 2025). Margin kasar bergeser dari {fmt_id(marg[2024], 1)}% ke {fmt_id(marg[2025], 1)}%.
2. **Terkonsentrasi di Jawa.** Pulau Jawa menyumbang {fmt_id(jawa['usaha'].sum() / p25['usaha'].sum() * 100, 1)}% usaha dan
   {fmt_id(jawa['pendapatan_000'].sum() / p25['pendapatan_000'].sum() * 100, 1)}% pendapatan pada 2025.
3. **Didominasi beberapa jenis industri.** {', '.join(top3['sektor'])} mencakup {fmt_id(top3['usaha'].sum() / kbli[kbli['tahun'] == 2025]['usaha'].sum() * 100, 1)}% usaha pada 2025.
4. **Pendapatan tumbuh kira-kira sebanding dengan tenaga kerja.** Elastisitas terhadap pekerja dibayar {fmt_id(b_d, 2)} dan terhadap pekerja
   tidak dibayar {fmt_id(b_t, 2)} (jumlah {fmt_id(b_d + b_t, 2)}). Ini asosiasi antar provinsi, bukan sebab-akibat.
5. **Pengelompokan provinsi lemah.** Silhouette K-Means (k = 3) hanya {fmt_id(sil[2024], 2)} (2024) dan {fmt_id(sil[2025], 2)} (2025), sehingga
   klaster dibaca sebagai eksplorasi, bukan kelompok yang tegas.
""")

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
- Modul penjualan usaha memakai data simulasi kecuali pengguna mengunggah data transaksi sendiri.
""")

# ---------------------------------------------------------------- Sidebar
st.sidebar.header("Pengaturan data nasional (BPS)")
tahun = st.sidebar.selectbox("Tahun", [2025, 2024])
wilayah_semua = sorted(prov["wilayah"].unique())
wilayah = st.sidebar.multiselect("Wilayah", wilayah_semua, default=wilayah_semua)
if not wilayah:
    st.sidebar.warning("Pilih minimal satu wilayah. Sementara semua wilayah dipakai.")
    wilayah = wilayah_semua
st.sidebar.caption(
    "Pengaturan ini berlaku pada tab Ringkasan Nasional dan Eksplorasi Data (tahun juga pada Jenis Industri). "
    "Tab Model dan Klaster memakai seluruh 38 provinsi. Tab Penjualan Usaha tidak terpengaruh."
)

p_tahun = prov[(prov["tahun"] == tahun) & (prov["wilayah"].isin(wilayah))]
k_tahun = kbli[kbli["tahun"] == tahun]

# ---------------------------------------------------------------- Judul
st.title("Dashboard Analisis UMKM Indonesia")
st.markdown("**Dua lapisan analisis: (1) konteks nasional UMKM sektor industri pengolahan dari data BPS 2024-2025, dan (2) analisis penjualan tingkat usaha.**")
st.caption(
    "Sumber: BPS, Profil Industri Mikro dan Kecil 2024 dan 2025. Survei sampel; cakupan industri pengolahan "
    "dengan 1 sampai 19 pekerja. Usaha perdagangan dan jasa tidak termasuk."
)

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
    if tahun == 2025:
        p0 = prov[(prov["tahun"] == 2024) & (prov["wilayah"].isin(wilayah))]
        pembanding = p0[kolom_kpi].sum()

    def delta(kol):
        if pembanding is None:
            return None
        return f"{fmt_id((tot[kol] / pembanding[kol] - 1) * 100, 1)}% vs 2024"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jumlah usaha", fmt_id(tot["usaha"]), delta("usaha"))
    c2.metric("Jumlah pekerja", fmt_id(tot["pekerja_total"]), delta("pekerja_total"))
    c3.metric("Pendapatan (Rp triliun)", fmt_id(tot["pendapatan_triliun"], 1), delta("pendapatan_triliun"))
    c4.metric("Margin kasar", f"{fmt_id(margin, 1)}%", help="(Pendapatan - pengeluaran) / pendapatan")

    st.write("")
    pilih = st.selectbox("Tampilkan berdasarkan", list(METRIK), key="rank_metrik")
    kol, sat, fmt = METRIK[pilih]

    kiri, kanan = st.columns([3, 2])
    with kiri:
        top = p_tahun.nlargest(10, kol).sort_values(kol)
        fig = px.bar(top, x=kol, y="provinsi", orientation="h", color_discrete_sequence=[BIRU],
                     title=f"10 provinsi teratas: {pilih}, {tahun}")
        fig.update_traces(texttemplate="%{x:" + fmt + "}", textposition="outside", cliponaxis=False,
                          marker_line_width=0)
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
    fig = px.bar(s, x=kol, y="label", orientation="h", color_discrete_sequence=[BIRU],
                 title=f"{pil} menurut jenis industri (KBLI 2 digit), {tahun}")
    fig.update_traces(texttemplate="%{x:" + fmt + "}", textposition="outside", cliponaxis=False, marker_line_width=0)
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
    fig = px.bar(s2, x=INDIKATOR[ind], y="label", orientation="h", color_discrete_sequence=[BIRU],
                 title=f"{ind}, {tahun}")
    fig.update_traces(texttemplate="%{x:,.1f}", textposition="outside", cliponaxis=False, marker_line_width=0)
    fig.update_layout(xaxis_title="", yaxis_title="", bargap=0.3)
    fig.update_yaxes(showgrid=False)
    tampil(fig, 680)
    st.caption("Industri dengan jumlah usaha sangat kecil (misalnya KBLI 26 dan 29) rentan terhadap variasi sampel, "
               "sehingga rata-ratanya perlu dibaca hati-hati.")

# ================================================================ 4. Perubahan
with tab_ubah:
    st.subheader("Perubahan nasional")
    nas = perubahan_nasional(prov)
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
tersedia adalah **simulasi** untuk demonstrasi, bukan data usaha nyata.

**Keterbatasan.** (1) Data survei sampel, sehingga angka provinsi memiliki galat sampling yang tidak tersedia di tabel.
(2) Hanya dua tahun, sehingga tidak ada peramalan deret waktu. (3) Provinsi baru hasil pemekaran Papua memiliki jumlah
usaha kecil. (4) Hasil regresi dan klaster bersifat asosiatif dan eksploratif.
""")
