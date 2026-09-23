"""

Dashboard Analisis Data UMKM Indonesia
========================================
Dashboard web interaktif menggunakan Streamlit, Plotly, Pandas, dan NumPy.
Menampilkan analisis komprehensif data UMKM Indonesia.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data_generator import generate_umkm_data

# ============================================================
# PAGE CONFIG & CUSTOM CSS
# ============================================================
st.set_page_config(
    page_title="Dashboard UMKM Indonesia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    /* ── Import Google Fonts ────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Root Variables ─────────────────────────────────────── */
    :root {
        --bg-primary: #0a0e1a;
        --bg-secondary: #111827;
        --bg-card: rgba(17, 24, 39, 0.7);
        --border-card: rgba(99, 102, 241, 0.15);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --accent-blue: #6366f1;
        --accent-cyan: #22d3ee;
        --accent-emerald: #10b981;
        --accent-rose: #f43f5e;
        --accent-amber: #f59e0b;
        --accent-violet: #8b5cf6;
        --gradient-1: linear-gradient(135deg, #6366f1, #8b5cf6);
        --gradient-2: linear-gradient(135deg, #22d3ee, #10b981);
        --gradient-3: linear-gradient(135deg, #f43f5e, #f59e0b);
        --gradient-4: linear-gradient(135deg, #10b981, #6366f1);
    }

    /* ── Global Styles ──────────────────────────────────────── */
    .stApp {
        background: var(--bg-primary);
        font-family: 'Inter', sans-serif;
    }

    .stApp > header {
        background: transparent;
    }

    /* ── Sidebar ────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
        border-right: 1px solid var(--border-card);
    }

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown label,
    section[data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif;
    }

    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label {
        color: var(--text-primary) !important;
        font-weight: 500;
    }

    /* ── KPI Metric Cards ───────────────────────────────────── */
    .kpi-container {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        margin-bottom: 24px;
    }

    .kpi-card {
        flex: 1;
        min-width: 200px;
        padding: 24px 20px;
        border-radius: 16px;
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border: 1px solid var(--border-card);
        position: relative;
        overflow: hidden;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
    }

    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
    }

    .kpi-card:nth-child(1)::before { background: var(--gradient-1); }
    .kpi-card:nth-child(2)::before { background: var(--gradient-2); }
    .kpi-card:nth-child(3)::before { background: var(--gradient-3); }
    .kpi-card:nth-child(4)::before { background: var(--gradient-4); }

    .kpi-icon {
        font-size: 28px;
        margin-bottom: 8px;
    }

    .kpi-label {
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: var(--text-secondary);
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.1;
    }

    .kpi-delta {
        font-size: 13px;
        font-weight: 500;
        margin-top: 6px;
    }

    .kpi-delta.positive { color: var(--accent-emerald); }
    .kpi-delta.negative { color: var(--accent-rose); }

    /* ── Section Headers ────────────────────────────────────── */
    .section-header {
        font-family: 'Inter', sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--border-card);
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* ── Chart Container ────────────────────────────────────── */
    .chart-container {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border: 1px solid var(--border-card);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        transition: box-shadow 0.3s ease;
    }

    .chart-container:hover {
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.10);
    }

    .chart-title {
        font-family: 'Inter', sans-serif;
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── Dashboard Title ────────────────────────────────────── */
    .dashboard-title {
        text-align: center;
        padding: 20px 0 12px 0;
    }

    .dashboard-title h1 {
        font-family: 'Inter', sans-serif;
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1, #22d3ee, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 4px;
    }

    .dashboard-title p {
        color: var(--text-secondary);
        font-size: 14px;
        font-weight: 400;
    }

    /* ── Divider ────────────────────────────────────────────── */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-card), transparent);
        margin: 16px 0;
    }

    /* ── Streamlit Overrides ────────────────────────────────── */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    div[data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 12px;
        padding: 16px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 8px;
        color: var(--text-secondary);
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: var(--gradient-1) !important;
        color: white !important;
    }

    /* ── Download Button ────────────────────────────────────── */
    .stDownloadButton > button {
        background: var(--gradient-1) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        padding: 8px 24px !important;
        transition: opacity 0.2s ease !important;
    }

    .stDownloadButton > button:hover {
        opacity: 0.85 !important;
    }

    /* ── Footer ─────────────────────────────────────────────── */
    .footer {
        text-align: center;
        padding: 32px 0 16px 0;
        color: var(--text-secondary);
        font-size: 12px;
        border-top: 1px solid var(--border-card);
        margin-top: 40px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================
# PLOTLY TEMPLATE (Dark Premium)
# ============================================================
_BASE_LEGEND = dict(
    bgcolor="rgba(0,0,0,0)",
    bordercolor="rgba(99,102,241,0.15)",
    borderwidth=1,
    font=dict(size=11, color="#94a3b8"),
)

_BASE_XAXIS = dict(
    gridcolor="rgba(148,163,184,0.08)",
    zerolinecolor="rgba(148,163,184,0.08)",
)

_BASE_YAXIS = dict(
    gridcolor="rgba(148,163,184,0.08)",
    zerolinecolor="rgba(148,163,184,0.08)",
)


def make_layout(*, legend=None, xaxis=None, yaxis=None, **kwargs):
    """Build a Plotly layout dict, deep-merging base defaults with overrides."""
    merged_legend = {**_BASE_LEGEND, **(legend or {})}
    merged_xaxis = {**_BASE_XAXIS, **(xaxis or {})}
    merged_yaxis = {**_BASE_YAXIS, **(yaxis or {})}
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#e2e8f0", size=12),
        margin=dict(l=40, r=20, t=40, b=40),
        legend=merged_legend,
        xaxis=merged_xaxis,
        yaxis=merged_yaxis,
        hoverlabel=dict(
            bgcolor="#1e293b",
            bordercolor="#6366f1",
            font=dict(family="Inter", color="#f1f5f9"),
        ),
        **kwargs,
    )

COLOR_PALETTE = [
    "#6366f1", "#22d3ee", "#10b981", "#f43f5e", "#f59e0b",
    "#8b5cf6", "#ec4899", "#14b8a6", "#f97316", "#3b82f6",
]

SEKTOR_COLORS = {
    "Perdagangan": "#6366f1",
    "Kuliner": "#22d3ee",
    "Fashion": "#f43f5e",
    "Jasa": "#10b981",
    "Pertanian": "#f59e0b",
    "Kerajinan": "#8b5cf6",
    "Teknologi": "#ec4899",
}

SKALA_COLORS = {
    "Mikro": "#6366f1",
    "Kecil": "#22d3ee",
    "Menengah": "#10b981",
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def format_number(n: float, prefix: str = "") -> str:
    """Format angka besar menjadi K, M, B."""
    if abs(n) >= 1_000_000_000:
        return f"{prefix}{n / 1_000_000_000:.1f} B"
    elif abs(n) >= 1_000_000:
        return f"{prefix}{n / 1_000_000:.1f} M"
    elif abs(n) >= 1_000:
        return f"{prefix}{n / 1_000:.1f} K"
    return f"{prefix}{n:,.0f}"


def format_rupiah(n: float) -> str:
    """Format angka ke Rupiah (dalam juta)."""
    if abs(n) >= 1_000_000:
        return f"Rp {n / 1_000_000:.1f} T"
    elif abs(n) >= 1_000:
        return f"Rp {n / 1_000:.1f} M"
    return f"Rp {n:,.0f} Jt"


# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load dan cache dataset UMKM."""
    return generate_umkm_data()


df = load_data()

# ============================================================
# SIDEBAR FILTERS
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 16px 0;">
            <span style="font-size: 42px;">📊</span>
            <h2 style="
                font-family: 'Inter', sans-serif;
                font-size: 20px;
                font-weight: 700;
                background: linear-gradient(135deg, #6366f1, #22d3ee);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin: 8px 0 4px 0;
            ">UMKM Analytics</h2>
            <p style="color: #64748b; font-size: 12px; margin: 0;">Dashboard Analisis Data</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Filter Tahun
    tahun_options = sorted(df["tahun"].unique())
    selected_tahun = st.select_slider(
        "📅 Pilih Rentang Tahun",
        options=tahun_options,
        value=(tahun_options[0], tahun_options[-1]),
    )

    st.markdown("")

    # Filter Provinsi
    all_provinsi = sorted(df["provinsi"].unique())
    selected_provinsi = st.multiselect(
        "🗺️ Pilih Provinsi",
        options=all_provinsi,
        default=[],
        placeholder="Semua Provinsi",
    )

    st.markdown("")

    # Filter Sektor
    all_sektor = sorted(df["sektor"].unique())
    selected_sektor = st.multiselect(
        "🏪 Pilih Sektor Usaha",
        options=all_sektor,
        default=[],
        placeholder="Semua Sektor",
    )

    st.markdown("")

    # Filter Skala
    all_skala = ["Mikro", "Kecil", "Menengah"]
    selected_skala = st.multiselect(
        "📏 Pilih Skala Usaha",
        options=all_skala,
        default=[],
        placeholder="Semua Skala",
    )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div style="text-align:center; padding: 8px 0;">
            <p style="color:#64748b; font-size: 11px; margin: 0;">
                Data sampel berdasarkan pola BPS Indonesia<br>
                Periode 2019 – 2024
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# APPLY FILTERS
# ============================================================
filtered = df[
    (df["tahun"] >= selected_tahun[0]) & (df["tahun"] <= selected_tahun[1])
].copy()

if selected_provinsi:
    filtered = filtered[filtered["provinsi"].isin(selected_provinsi)]

if selected_sektor:
    filtered = filtered[filtered["sektor"].isin(selected_sektor)]

if selected_skala:
    filtered = filtered[filtered["skala"].isin(selected_skala)]

# ============================================================
# DASHBOARD HEADER
# ============================================================
st.markdown(
    """
    <div class="dashboard-title">
        <h1>🇮🇩 Dashboard Analisis UMKM Indonesia</h1>
        <p>Visualisasi data komprehensif Usaha Mikro, Kecil, dan Menengah di Indonesia</p>
    </div>
    <div class="custom-divider"></div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# KPI CARDS
# ============================================================
total_umkm = filtered["jumlah_umkm"].sum()
total_tk = filtered["tenaga_kerja"].sum()
avg_omzet = filtered["omzet_juta"].mean()
avg_growth = filtered["pertumbuhan_pct"].mean()

# Hitung delta dari tahun terakhir vs tahun sebelumnya (jika ada)
latest_year = filtered["tahun"].max()
prev_year = latest_year - 1

df_latest = filtered[filtered["tahun"] == latest_year]
df_prev = filtered[filtered["tahun"] == prev_year]

if not df_prev.empty and not df_latest.empty:
    delta_umkm = (
        (df_latest["jumlah_umkm"].sum() - df_prev["jumlah_umkm"].sum())
        / df_prev["jumlah_umkm"].sum()
        * 100
    )
    delta_tk = (
        (df_latest["tenaga_kerja"].sum() - df_prev["tenaga_kerja"].sum())
        / df_prev["tenaga_kerja"].sum()
        * 100
    )
    delta_omzet = (
        (df_latest["omzet_juta"].mean() - df_prev["omzet_juta"].mean())
        / df_prev["omzet_juta"].mean()
        * 100
    )
else:
    delta_umkm = delta_tk = delta_omzet = 0.0

growth_class_umkm = "positive" if delta_umkm >= 0 else "negative"
growth_class_tk = "positive" if delta_tk >= 0 else "negative"
growth_class_omzet = "positive" if delta_omzet >= 0 else "negative"
growth_class_avg = "positive" if avg_growth >= 0 else "negative"

arrow_umkm = "↑" if delta_umkm >= 0 else "↓"
arrow_tk = "↑" if delta_tk >= 0 else "↓"
arrow_omzet = "↑" if delta_omzet >= 0 else "↓"
arrow_avg = "↑" if avg_growth >= 0 else "↓"

st.markdown(
    f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-icon">🏢</div>
            <div class="kpi-label">Total UMKM</div>
            <div class="kpi-value">{format_number(total_umkm)}</div>
            <div class="kpi-delta {growth_class_umkm}">{arrow_umkm} {abs(delta_umkm):.1f}% vs tahun lalu</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">👥</div>
            <div class="kpi-label">Total Tenaga Kerja</div>
            <div class="kpi-value">{format_number(total_tk)}</div>
            <div class="kpi-delta {growth_class_tk}">{arrow_tk} {abs(delta_tk):.1f}% vs tahun lalu</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Rata-rata Omzet</div>
            <div class="kpi-value">{format_rupiah(avg_omzet)}</div>
            <div class="kpi-delta {growth_class_omzet}">{arrow_omzet} {abs(delta_omzet):.1f}% vs tahun lalu</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon">📈</div>
            <div class="kpi-label">Pertumbuhan Rata-rata</div>
            <div class="kpi-value">{avg_growth:+.1f}%</div>
            <div class="kpi-delta {growth_class_avg}">{arrow_avg} Year-over-Year</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SECTION 1: DISTRIBUSI WILAYAH & SEKTOR
# ============================================================
st.markdown(
    '<div class="section-header">🗺️ Distribusi Wilayah & Sektor Usaha</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown(
        '<div class="chart-container">'
        '<div class="chart-title">📊 Top 10 Provinsi — Jumlah UMKM</div>',
        unsafe_allow_html=True,
    )

    prov_data = (
        filtered.groupby("provinsi", as_index=False)["jumlah_umkm"]
        .sum()
        .sort_values("jumlah_umkm", ascending=True)
        .tail(10)
    )

    fig_bar = px.bar(
        prov_data,
        x="jumlah_umkm",
        y="provinsi",
        orientation="h",
        color="jumlah_umkm",
        color_continuous_scale=["#312e81", "#6366f1", "#22d3ee"],
        labels={"jumlah_umkm": "Jumlah UMKM", "provinsi": ""},
    )
    fig_bar.update_layout(**make_layout(
        height=400,
        showlegend=False,
        coloraxis_showscale=False,
    ))
    fig_bar.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Jumlah: %{x:,.0f}<extra></extra>",
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(
        '<div class="chart-container">'
        '<div class="chart-title">🍩 Distribusi Sektor Usaha</div>',
        unsafe_allow_html=True,
    )

    sektor_data = (
        filtered.groupby("sektor", as_index=False)["jumlah_umkm"].sum()
    )

    fig_donut = px.pie(
        sektor_data,
        values="jumlah_umkm",
        names="sektor",
        hole=0.55,
        color="sektor",
        color_discrete_map=SEKTOR_COLORS,
    )
    fig_donut.update_layout(**make_layout(
        height=400,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(size=11),
        ),
    ))
    fig_donut.update_traces(
        textinfo="percent+label",
        textfont_size=11,
        textfont_color="#e2e8f0",
        hovertemplate="<b>%{label}</b><br>Jumlah: %{value:,.0f}<br>Persentase: %{percent}<extra></extra>",
        marker=dict(line=dict(color="#0a0e1a", width=2)),
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# SECTION 2: TREN & PERTUMBUHAN
# ============================================================
st.markdown(
    '<div class="section-header">📈 Tren & Pertumbuhan Tahunan</div>',
    unsafe_allow_html=True,
)

col3, col4 = st.columns(2)

with col3:
    st.markdown(
        '<div class="chart-container">'
        '<div class="chart-title">📈 Tren Jumlah UMKM per Tahun</div>',
        unsafe_allow_html=True,
    )

    trend_data = (
        filtered.groupby("tahun", as_index=False)
        .agg(total_umkm=("jumlah_umkm", "sum"), total_tk=("tenaga_kerja", "sum"))
    )

    fig_trend = go.Figure()
    fig_trend.add_trace(
        go.Scatter(
            x=trend_data["tahun"],
            y=trend_data["total_umkm"],
            mode="lines+markers",
            name="Jumlah UMKM",
            line=dict(color="#6366f1", width=3, shape="spline"),
            marker=dict(size=10, color="#6366f1", line=dict(width=2, color="#0a0e1a")),
            fill="tozeroy",
            fillcolor="rgba(99, 102, 241, 0.08)",
            hovertemplate="<b>%{x}</b><br>UMKM: %{y:,.0f}<extra></extra>",
        )
    )
    fig_trend.update_layout(**make_layout(
        height=380,
        showlegend=False,
        xaxis=dict(dtick=1, title=""),
        yaxis=dict(title="Jumlah UMKM", title_font=dict(size=12)),
    ))
    st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with col4:
    st.markdown(
        '<div class="chart-container">'
        '<div class="chart-title">📊 Rata-rata Pertumbuhan per Tahun (%)</div>',
        unsafe_allow_html=True,
    )

    growth_data = (
        filtered.groupby("tahun", as_index=False)["pertumbuhan_pct"].mean()
    )

    colors_growth = [
        "#10b981" if v >= 0 else "#f43f5e" for v in growth_data["pertumbuhan_pct"]
    ]

    fig_growth = go.Figure()
    fig_growth.add_trace(
        go.Bar(
            x=growth_data["tahun"],
            y=growth_data["pertumbuhan_pct"],
            marker_color=colors_growth,
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Pertumbuhan: %{y:.1f}%<extra></extra>",
        )
    )
    fig_growth.add_hline(
        y=0,
        line_dash="dot",
        line_color="rgba(148,163,184,0.3)",
        line_width=1,
    )
    fig_growth.update_layout(**make_layout(
        height=380,
        showlegend=False,
        xaxis=dict(dtick=1, title=""),
        yaxis=dict(title="Pertumbuhan (%)", title_font=dict(size=12)),
    ))
    st.plotly_chart(fig_growth, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# SECTION 3: PERBANDINGAN SKALA & SEKTOR
# ============================================================
st.markdown(
    '<div class="section-header">⚖️ Perbandingan Skala & Sektor Usaha</div>',
    unsafe_allow_html=True,
)

col5, col6 = st.columns(2)

with col5:
    st.markdown(
        '<div class="chart-container">'
        '<div class="chart-title">💰 Rata-rata Omzet per Skala Usaha (Juta Rp)</div>',
        unsafe_allow_html=True,
    )

    skala_sektor = (
        filtered.groupby(["skala", "sektor"], as_index=False)["omzet_juta"].mean()
    )

    fig_grouped = px.bar(
        skala_sektor,
        x="skala",
        y="omzet_juta",
        color="sektor",
        barmode="group",
        color_discrete_map=SEKTOR_COLORS,
        labels={"omzet_juta": "Omzet (Juta Rp)", "skala": "Skala Usaha", "sektor": "Sektor"},
        category_orders={"skala": ["Mikro", "Kecil", "Menengah"]},
    )
    fig_grouped.update_layout(**make_layout(
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
    ))
    fig_grouped.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Omzet: Rp %{y:,.0f} Jt<extra></extra>",
    )
    st.plotly_chart(fig_grouped, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with col6:
    st.markdown(
        '<div class="chart-container">'
        '<div class="chart-title">🔥 Tren Sektor Usaha per Tahun</div>',
        unsafe_allow_html=True,
    )

    sektor_trend = (
        filtered.groupby(["tahun", "sektor"], as_index=False)["jumlah_umkm"].sum()
    )

    fig_sektor_line = px.line(
        sektor_trend,
        x="tahun",
        y="jumlah_umkm",
        color="sektor",
        color_discrete_map=SEKTOR_COLORS,
        markers=True,
        labels={"jumlah_umkm": "Jumlah UMKM", "tahun": "", "sektor": "Sektor"},
    )
    fig_sektor_line.update_layout(**make_layout(
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
        xaxis=dict(dtick=1),
    ))
    fig_sektor_line.update_traces(
        line_width=2.5,
        marker_size=7,
        hovertemplate="<b>%{x}</b><br>UMKM: %{y:,.0f}<extra></extra>",
    )
    st.plotly_chart(fig_sektor_line, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# SECTION 4: ANALISIS MENDALAM
# ============================================================
st.markdown(
    '<div class="section-header">🔬 Analisis Mendalam</div>',
    unsafe_allow_html=True,
)

col7, col8 = st.columns(2)

with col7:
    st.markdown(
        '<div class="chart-container">'
        '<div class="chart-title">🔗 Heatmap Korelasi Variabel</div>',
        unsafe_allow_html=True,
    )

    corr_cols = ["jumlah_umkm", "tenaga_kerja", "omzet_juta", "pertumbuhan_pct"]
    corr_labels = ["Jumlah UMKM", "Tenaga Kerja", "Omzet", "Pertumbuhan"]
    corr_matrix = filtered[corr_cols].corr()

    fig_heatmap = go.Figure(
        go.Heatmap(
            z=corr_matrix.values,
            x=corr_labels,
            y=corr_labels,
            colorscale=[
                [0, "#312e81"],
                [0.25, "#4338ca"],
                [0.5, "#6366f1"],
                [0.75, "#22d3ee"],
                [1, "#10b981"],
            ],
            zmin=-1,
            zmax=1,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont=dict(size=14, color="white"),
            hovertemplate="%{x} vs %{y}<br>Korelasi: %{z:.3f}<extra></extra>",
        )
    )
    fig_heatmap.update_layout(**make_layout(
        height=400,
        xaxis=dict(side="bottom"),
    ))
    st.plotly_chart(fig_heatmap, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with col8:
    st.markdown(
        '<div class="chart-container">'
        '<div class="chart-title">🔵 Hubungan Omzet vs Tenaga Kerja</div>',
        unsafe_allow_html=True,
    )

    # Aggregate per provinsi untuk scatter yang lebih bersih
    scatter_data = (
        filtered.groupby(["provinsi", "skala"], as_index=False)
        .agg(
            omzet_juta=("omzet_juta", "mean"),
            tenaga_kerja=("tenaga_kerja", "mean"),
            jumlah_umkm=("jumlah_umkm", "sum"),
        )
    )

    fig_scatter = px.scatter(
        scatter_data,
        x="omzet_juta",
        y="tenaga_kerja",
        size="jumlah_umkm",
        color="skala",
        color_discrete_map=SKALA_COLORS,
        hover_name="provinsi",
        labels={
            "omzet_juta": "Rata-rata Omzet (Juta Rp)",
            "tenaga_kerja": "Rata-rata Tenaga Kerja",
            "jumlah_umkm": "Total UMKM",
            "skala": "Skala",
        },
        size_max=30,
    )
    fig_scatter.update_layout(**make_layout(
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
    ))
    fig_scatter.update_traces(
        marker_line_width=1,
        marker_line_color="#0a0e1a",
        hovertemplate="<b>%{hovertext}</b><br>Omzet: Rp %{x:,.0f} Jt<br>TK: %{y:,.0f}<extra></extra>",
    )
    st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# SECTION 5: DISTRIBUSI SKALA USAHA PER PROVINSI (STACKED)
# ============================================================
st.markdown(
    '<div class="section-header">🏗️ Distribusi Skala Usaha per Provinsi</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="chart-container">'
    '<div class="chart-title">📊 Komposisi Skala Usaha — Top 15 Provinsi</div>',
    unsafe_allow_html=True,
)

stacked_data = (
    filtered.groupby(["provinsi", "skala"], as_index=False)["jumlah_umkm"]
    .sum()
)
top15_prov = (
    stacked_data.groupby("provinsi")["jumlah_umkm"]
    .sum()
    .nlargest(15)
    .index
)
stacked_data = stacked_data[stacked_data["provinsi"].isin(top15_prov)]

fig_stacked = px.bar(
    stacked_data,
    x="provinsi",
    y="jumlah_umkm",
    color="skala",
    barmode="stack",
    color_discrete_map=SKALA_COLORS,
    labels={"jumlah_umkm": "Jumlah UMKM", "provinsi": "", "skala": "Skala"},
    category_orders={
        "skala": ["Mikro", "Kecil", "Menengah"],
        "provinsi": stacked_data.groupby("provinsi")["jumlah_umkm"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist(),
    },
)
fig_stacked.update_layout(**make_layout(
    height=420,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="center",
        x=0.5,
    ),
    xaxis=dict(tickangle=-45),
))
fig_stacked.update_traces(
    marker_line_width=0,
    hovertemplate="<b>%{x}</b><br>UMKM: %{y:,.0f}<extra></extra>",
)
st.plotly_chart(fig_stacked, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# SECTION 6: DATA TABLE
# ============================================================
st.markdown(
    '<div class="section-header">📋 Data Detail</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="chart-container">',
    unsafe_allow_html=True,
)

# Summary stats
tab1, tab2 = st.tabs(["📊 Ringkasan per Provinsi", "📄 Data Lengkap"])

with tab1:
    summary = (
        filtered.groupby("provinsi", as_index=False)
        .agg(
            total_umkm=("jumlah_umkm", "sum"),
            total_tk=("tenaga_kerja", "sum"),
            avg_omzet=("omzet_juta", "mean"),
            avg_pertumbuhan=("pertumbuhan_pct", "mean"),
        )
        .sort_values("total_umkm", ascending=False)
    )
    summary.columns = [
        "Provinsi",
        "Total UMKM",
        "Total Tenaga Kerja",
        "Rata-rata Omzet (Jt Rp)",
        "Rata-rata Pertumbuhan (%)",
    ]
    summary["Rata-rata Omzet (Jt Rp)"] = summary["Rata-rata Omzet (Jt Rp)"].round(1)
    summary["Rata-rata Pertumbuhan (%)"] = summary["Rata-rata Pertumbuhan (%)"].round(2)

    st.dataframe(
        summary,
        use_container_width=True,
        height=400,
        hide_index=True,
    )

    csv_summary = summary.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Ringkasan (CSV)",
        data=csv_summary,
        file_name="ringkasan_umkm_provinsi.csv",
        mime="text/csv",
    )

with tab2:
    display_df = filtered.copy()
    display_df.columns = [
        "Provinsi",
        "Sektor",
        "Skala",
        "Tahun",
        "Jumlah UMKM",
        "Tenaga Kerja",
        "Omzet (Juta Rp)",
        "Pertumbuhan (%)",
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        hide_index=True,
    )

    csv_full = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Data Lengkap (CSV)",
        data=csv_full,
        file_name="data_umkm_lengkap.csv",
        mime="text/csv",
    )

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class="footer">
        <p>📊 <strong>Dashboard Analisis UMKM Indonesia</strong> — Dibuat dengan Streamlit, Plotly, Pandas & NumPy</p>
        <p>Data sampel berdasarkan pola statistik BPS Indonesia | © 2024</p>
    </div>
    """,
    unsafe_allow_html=True,
)
