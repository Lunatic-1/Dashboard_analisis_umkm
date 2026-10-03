"""

Dashboard Analisis Data UMKM Indonesia
========================================
Dashboard web interaktif menggunakan Streamlit, Plotly, Pandas, dan NumPy.
Menampilkan analisis komprehensif data UMKM Indonesia.
"""

import json
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from io import BytesIO
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

# ============================================================
# THEME INITIALIZATION
# ============================================================
if 'theme' not in st.session_state:
    st.session_state.theme = '🌙 Dark'

is_dark = st.session_state.theme == '🌙 Dark'

THEME = {
    'font_color': '#e2e8f0' if is_dark else '#1e293b',
    'text_secondary': '#94a3b8' if is_dark else '#64748b',
    'hover_bg': '#1e293b' if is_dark else '#ffffff',
    'hover_font': '#f1f5f9' if is_dark else '#0f172a',
    'grid': 'rgba(148,163,184,0.08)' if is_dark else 'rgba(0,0,0,0.06)',
    'marker_line': '#0a0e1a' if is_dark else '#ffffff',
    'heatmap_text': 'white' if is_dark else '#1e293b',
    'map_paper_bg': 'rgba(10,14,26,0)' if is_dark else 'rgba(241,245,249,0)',
    'map_land': '#1e293b' if is_dark else '#e2e8f0',
    'map_ocean': '#0f172a' if is_dark else '#dbeafe',
}

LIGHT_OVERRIDE_CSS = """
<style>
    :root {
        --bg-primary: #f1f5f9 !important;
        --bg-secondary: #e2e8f0 !important;
        --bg-card: rgba(255, 255, 255, 0.9) !important;
        --border-card: rgba(99, 102, 241, 0.15) !important;
        --text-primary: #0f172a !important;
        --text-secondary: #475569 !important;
    }
    .stApp {
        background: linear-gradient(135deg, #f1f5f9 0%, #e8eef7 50%, #f1f5f9 100%) !important;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #eef2ff 0%, #f1f5f9 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.15) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown label,
    section[data-testid="stSidebar"] label {
        color: #475569 !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label {
        color: #0f172a !important;
    }
    .kpi-card {
        background: rgba(255, 255, 255, 0.9) !important;
        border-color: rgba(99, 102, 241, 0.15) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-card:hover {
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.10) !important;
    }
    .kpi-label { color: #475569 !important; }
    .kpi-value { color: #0f172a !important; }
    .chart-container {
        background: rgba(255, 255, 255, 0.9) !important;
        border-color: rgba(99, 102, 241, 0.15) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .chart-container:hover {
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.08) !important;
    }
    .chart-title { color: #0f172a !important; }
    .section-header {
        color: #0f172a !important;
        border-bottom-color: rgba(99, 102, 241, 0.3) !important;
    }
    .dashboard-title h1 {
        background: linear-gradient(135deg, #4338ca, #0891b2, #059669) !important;
        -webkit-background-clip: text !important;
        background-clip: text !important;
    }
    .dashboard-title p { color: #475569 !important; }
    .footer {
        color: #475569 !important;
        border-top-color: rgba(99, 102, 241, 0.15) !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.9) !important;
        border-color: rgba(99, 102, 241, 0.15) !important;
        color: #475569 !important;
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.9) !important;
        border-color: rgba(99, 102, 241, 0.15) !important;
    }
    .custom-divider {
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.2), transparent) !important;
    }
    .filter-badge-bar {
        background: rgba(255, 255, 255, 0.85) !important;
        border-color: rgba(99, 102, 241, 0.15) !important;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.06) !important;
    }
    .filter-badge-label { color: #475569 !important; }
    .insight-box {
        background: rgba(255, 255, 255, 0.85) !important;
        border-color: rgba(99, 102, 241, 0.2) !important;
    }
    .insight-box p { color: #334155 !important; }
    .kpi-progress-bg { background: rgba(99, 102, 241, 0.08) !important; }
    .kpi-card::after { opacity: 0 !important; }
</style>
"""

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
        padding: 24px 20px 20px 20px;
        border-radius: 20px;
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border: 1px solid var(--border-card);
        position: relative;
        overflow: hidden;
        transition: transform 0.35s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.35s ease;
    }

    .kpi-card:hover {
        transform: translateY(-6px) scale(1.01);
        box-shadow: 0 20px 50px rgba(99, 102, 241, 0.18);
    }

    /* Top gradient bar */
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        border-radius: 20px 20px 0 0;
        transition: height 0.3s ease;
    }

    .kpi-card:hover::before { height: 6px; }

    .kpi-card:nth-child(1)::before { background: var(--gradient-1); }
    .kpi-card:nth-child(2)::before { background: var(--gradient-2); }
    .kpi-card:nth-child(3)::before { background: var(--gradient-3); }
    .kpi-card:nth-child(4)::before { background: var(--gradient-4); }

    /* Glow orb */
    .kpi-card::after {
        content: '';
        position: absolute;
        bottom: -30px;
        right: -30px;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        opacity: 0.06;
        transition: opacity 0.3s ease, transform 0.3s ease;
    }
    .kpi-card:hover::after { opacity: 0.14; transform: scale(1.3); }
    .kpi-card:nth-child(1)::after { background: #6366f1; }
    .kpi-card:nth-child(2)::after { background: #22d3ee; }
    .kpi-card:nth-child(3)::after { background: #f43f5e; }
    .kpi-card:nth-child(4)::after { background: #10b981; }

    .kpi-icon {
        font-size: 28px;
        margin-bottom: 8px;
        display: block;
    }

    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: var(--text-secondary);
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 30px;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.1;
        letter-spacing: -0.5px;
    }

    .kpi-delta {
        font-size: 12px;
        font-weight: 600;
        margin-top: 6px;
    }

    .kpi-delta.positive { color: var(--accent-emerald); }
    .kpi-delta.negative { color: var(--accent-rose); }

    /* Progress bar under value */
    .kpi-progress-bg {
        height: 4px;
        border-radius: 999px;
        background: rgba(255,255,255,0.07);
        margin-top: 10px;
        overflow: hidden;
    }
    .kpi-progress-fill {
        height: 100%;
        border-radius: 999px;
        transition: width 1s cubic-bezier(0.4,0,0.2,1);
    }
    .kpi-card:nth-child(1) .kpi-progress-fill { background: var(--gradient-1); }
    .kpi-card:nth-child(2) .kpi-progress-fill { background: var(--gradient-2); }
    .kpi-card:nth-child(3) .kpi-progress-fill { background: var(--gradient-3); }
    .kpi-card:nth-child(4) .kpi-progress-fill { background: var(--gradient-4); }

    /* ── Filter Badge Bar ───────────────────────────────────── */
    .filter-badge-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        padding: 10px 16px;
        border-radius: 12px;
        background: rgba(17, 24, 39, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-card);
        margin-bottom: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.15);
    }
    .filter-badge-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-secondary);
        margin-right: 4px;
    }
    .filter-badge {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    .filter-badge.year   { background: rgba(99,102,241,0.15); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.25); }
    .filter-badge.prov   { background: rgba(34,211,238,0.12); color: #67e8f9; border: 1px solid rgba(34,211,238,0.2); }
    .filter-badge.sector { background: rgba(16,185,129,0.12); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.2); }
    .filter-badge.scale  { background: rgba(245,158,11,0.12); color: #fcd34d; border: 1px solid rgba(245,158,11,0.2); }

    /* ── Insight Box ────────────────────────────────────────── */
    .insight-box {
        padding: 14px 18px;
        border-radius: 12px;
        background: rgba(99,102,241,0.07);
        border: 1px solid rgba(99,102,241,0.18);
        margin-bottom: 20px;
        animation: fadeSlideIn 0.5s ease;
    }
    .insight-box .insight-title {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #a5b4fc;
        margin-bottom: 6px;
    }
    .insight-box p {
        font-size: 13px;
        color: #cbd5e1;
        margin: 0;
        line-height: 1.6;
    }
    .insight-box strong { color: #e2e8f0; }

    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateY(-8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Section Headers ────────────────────────────────────── */
    .section-header {
        font-family: 'Inter', sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 36px 0 16px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(90deg, #6366f1, #22d3ee, transparent) 1;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* ── Chart Container ────────────────────────────────────── */
    .chart-container {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        border: 1px solid var(--border-card);
        border-radius: 20px;
        padding: 22px;
        margin-bottom: 16px;
        transition: box-shadow 0.35s ease, border-color 0.35s ease;
    }

    .chart-container:hover {
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.12);
        border-color: rgba(99, 102, 241, 0.25);
    }

    .chart-title {
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.2px;
    }

    /* ── Dashboard Title ────────────────────────────────────── */
    .dashboard-title {
        text-align: center;
        padding: 24px 0 16px 0;
    }

    .dashboard-title h1 {
        font-family: 'Inter', sans-serif;
        font-size: 38px;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1, #22d3ee, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 6px;
        letter-spacing: -1px;
    }

    .dashboard-title p {
        color: var(--text-secondary);
        font-size: 14px;
        font-weight: 400;
    }

    /* ── Divider ────────────────────────────────────────────── */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(99,102,241,0.25), transparent);
        margin: 16px 0;
    }

    /* ── Streamlit Overrides ────────────────────────────────── */
    .stDataFrame {
        border-radius: 14px;
        overflow: hidden;
    }

    div[data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 14px;
        padding: 16px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 999px;
        color: var(--text-secondary);
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 13px;
        padding: 6px 18px;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        border-color: rgba(99,102,241,0.4);
        color: #a5b4fc;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border-color: transparent !important;
        box-shadow: 0 4px 14px rgba(99,102,241,0.35);
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
        transition: opacity 0.2s ease, transform 0.2s ease !important;
        box-shadow: 0 4px 14px rgba(99,102,241,0.3) !important;
    }

    .stDownloadButton > button:hover {
        opacity: 0.88 !important;
        transform: translateY(-1px) !important;
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

    /* ── Count-up Animation ─────────────────────────────────── */
    @keyframes countUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .kpi-value {
        animation: countUp 0.6s ease both;
    }
    .kpi-card:nth-child(1) .kpi-value { animation-delay: 0.0s; }
    .kpi-card:nth-child(2) .kpi-value { animation-delay: 0.1s; }
    .kpi-card:nth-child(3) .kpi-value { animation-delay: 0.2s; }
    .kpi-card:nth-child(4) .kpi-value { animation-delay: 0.3s; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
if not is_dark:
    st.markdown(LIGHT_OVERRIDE_CSS, unsafe_allow_html=True)

# ============================================================
# PLOTLY TEMPLATE (Dark Premium)
# ============================================================
_BASE_LEGEND = dict(
    bgcolor="rgba(0,0,0,0)",
    bordercolor="rgba(99,102,241,0.15)",
    borderwidth=1,
    font=dict(size=11, color=THEME['text_secondary']),
)

_BASE_XAXIS = dict(
    gridcolor=THEME['grid'],
    zerolinecolor=THEME['grid'],
)

_BASE_YAXIS = dict(
    gridcolor=THEME['grid'],
    zerolinecolor=THEME['grid'],
)


def make_layout(*, legend=None, xaxis=None, yaxis=None, **kwargs):
    """Build a Plotly layout dict, deep-merging base defaults with overrides."""
    merged_legend = {**_BASE_LEGEND, **(legend or {})}
    merged_xaxis = {**_BASE_XAXIS, **(xaxis or {})}
    merged_yaxis = {**_BASE_YAXIS, **(yaxis or {})}
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=THEME['font_color'], size=12),
        margin=dict(l=40, r=20, t=40, b=40),
        legend=merged_legend,
        xaxis=merged_xaxis,
        yaxis=merged_yaxis,
        hoverlabel=dict(
            bgcolor=THEME['hover_bg'],
            bordercolor="#6366f1",
            font=dict(family="Inter", color=THEME['hover_font']),
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


def to_excel(dataframe: pd.DataFrame) -> bytes:
    """Convert DataFrame ke format Excel bytes."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()


def generate_insight(filtered: pd.DataFrame, section: str) -> str:
    """Generate otomatis insight teks berdasarkan data yang difilter."""
    if filtered.empty:
        return "Tidak ada data yang sesuai dengan filter yang dipilih."

    if section == "distribusi":
        top_prov = (
            filtered.groupby("provinsi")["jumlah_umkm"].sum()
            .sort_values(ascending=False)
        )
        if top_prov.empty:
            return "Data tidak tersedia."
        prov1 = top_prov.index[0]
        val1 = format_number(top_prov.iloc[0])
        top_sektor = filtered.groupby("sektor")["jumlah_umkm"].sum().idxmax()
        share_prov = top_prov.iloc[0] / top_prov.sum() * 100
        return (
            f"<strong>{prov1}</strong> menjadi provinsi dengan UMKM terbanyak ({val1} unit, "
            f"kontribusi <strong>{share_prov:.1f}%</strong> dari total). "
            f"Sektor dominan secara nasional adalah <strong>{top_sektor}</strong>."
        )

    elif section == "tren":
        trend = filtered.groupby("tahun")["jumlah_umkm"].sum().sort_index()
        if len(trend) < 2:
            return "Dibutuhkan minimal 2 tahun data untuk analisis tren."
        peak_year = trend.idxmax()
        min_year = trend.idxmin()
        growth_total = (trend.iloc[-1] - trend.iloc[0]) / trend.iloc[0] * 100 if trend.iloc[0] > 0 else 0
        return (
            f"Puncak jumlah UMKM terjadi pada tahun <strong>{peak_year}</strong> "
            f"({format_number(trend[peak_year])} unit). "
            f"Tahun <strong>{min_year}</strong> mencatat angka terendah. "
            f"Pertumbuhan total periode ini: <strong>{growth_total:+.1f}%</strong>."
        )

    elif section == "skala":
        avg_omzet = filtered.groupby("skala")["omzet_juta"].mean().sort_values(ascending=False)
        if avg_omzet.empty:
            return "Data tidak tersedia."
        top_skala = avg_omzet.index[0]
        ratio = avg_omzet.iloc[0] / avg_omzet.iloc[-1] if avg_omzet.iloc[-1] > 0 else 1
        top_sektor_per_skala = (
            filtered[filtered["skala"] == "Menengah"]
            .groupby("sektor")["omzet_juta"].mean()
            .idxmax() if not filtered[filtered["skala"] == "Menengah"].empty else "N/A"
        )
        return (
            f"Skala <strong>{top_skala}</strong> mencatat rata-rata omzet tertinggi, "
            f"sekitar <strong>{ratio:.1f}x</strong> lebih tinggi dari skala terkecil. "
            f"Di skala Menengah, sektor <strong>{top_sektor_per_skala}</strong> mendominasi omzet."
        )

    elif section == "analisis":
        corr_cols = ["jumlah_umkm", "tenaga_kerja", "omzet_juta", "pertumbuhan_pct"]
        if filtered[corr_cols].shape[0] < 5:
            return "Data terlalu sedikit untuk analisis korelasi."
        corr = filtered[corr_cols].corr()
        tk_omzet_corr = corr.loc["tenaga_kerja", "omzet_juta"]
        umkm_tk_corr = corr.loc["jumlah_umkm", "tenaga_kerja"]
        strength = "kuat" if abs(tk_omzet_corr) > 0.7 else "sedang" if abs(tk_omzet_corr) > 0.4 else "lemah"
        direction = "positif" if tk_omzet_corr > 0 else "negatif"
        return (
            f"Terdapat korelasi <strong>{strength} {direction}</strong> "
            f"(r = {tk_omzet_corr:.2f}) antara Tenaga Kerja dan Omzet. "
            f"Korelasi Jumlah UMKM–Tenaga Kerja: <strong>r = {umkm_tk_corr:.2f}</strong>."
        )

    return ""


# ============================================================
# INDONESIA GEOJSON (Simplified bounding boxes for 34 provinsi)
# Uses a lightweight inline approach — fetches from reliable CDN
# ============================================================
@st.cache_data(show_spinner=False)
def load_indonesia_geojson():
    """Load GeoJSON Indonesia dari URL publik (cached)."""
    import urllib.request
    url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia.geojson"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


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

    # Theme Toggle
    st.radio(
        "🎨 Tema Tampilan",
        options=['🌙 Dark', '☀️ Light'],
        horizontal=True,
        key='theme',
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

    st.markdown("")

    # Pencarian Provinsi
    search_query = st.text_input(
        "🔍 Cari Provinsi",
        value="",
        placeholder="Ketik nama provinsi...",
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

# Filter berdasarkan pencarian provinsi
if search_query:
    filtered = filtered[filtered["provinsi"].str.contains(search_query, case=False, na=False)]

# Search feedback
if search_query:
    matched_count = filtered["provinsi"].nunique()
    if matched_count > 0:
        st.success(f"🔍 Ditemukan **{matched_count} provinsi** cocok dengan \"{search_query}\"")
    else:
        st.warning(f"⚠️ Tidak ditemukan provinsi dengan kata kunci \"{search_query}\"")

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
# ACTIVE FILTER BADGE BAR
# ============================================================
tahun_badge = f"📅 {selected_tahun[0]} – {selected_tahun[1]}"

if selected_provinsi:
    if len(selected_provinsi) <= 2:
        prov_badge = "🗺️ " + ", ".join(selected_provinsi)
    else:
        prov_badge = f"🗺️ {len(selected_provinsi)} Provinsi"
else:
    prov_badge = "🗺️ Semua Provinsi"

if selected_sektor:
    sektor_badge = "🏪 " + ", ".join(selected_sektor) if len(selected_sektor) <= 2 else f"🏪 {len(selected_sektor)} Sektor"
else:
    sektor_badge = "🏪 Semua Sektor"

if selected_skala:
    skala_badge = "📏 " + ", ".join(selected_skala)
else:
    skala_badge = "📏 Semua Skala"

total_rows = len(filtered)

st.markdown(
    f"""
    <div class="filter-badge-bar">
        <span class="filter-badge-label">🔎 Filter Aktif:</span>
        <span class="filter-badge year">{tahun_badge}</span>
        <span class="filter-badge prov">{prov_badge}</span>
        <span class="filter-badge sector">{sektor_badge}</span>
        <span class="filter-badge scale">{skala_badge}</span>
        <span style="margin-left:auto; font-size:11px; color:#64748b; font-weight:500;">
            {total_rows:,} baris data
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# KPI CARDS
# ============================================================
total_umkm = filtered["jumlah_umkm"].sum()
total_tk = filtered["tenaga_kerja"].sum()
avg_omzet = filtered["omzet_juta"].mean() if not filtered.empty else 0
avg_growth = filtered["pertumbuhan_pct"].mean() if not filtered.empty else 0

# Hitung delta dari tahun terakhir vs tahun sebelumnya (jika ada)
latest_year = filtered["tahun"].max() if not filtered.empty else 0
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

# Progress bars: relative to max across KPIs
umkm_progress = min(100, int(abs(delta_umkm) * 5)) if delta_umkm else 60
tk_progress = min(100, int(abs(delta_tk) * 5)) if delta_tk else 55
omzet_progress = min(100, int(abs(delta_omzet) * 5)) if delta_omzet else 70
growth_progress = min(100, int(abs(avg_growth) * 5)) if avg_growth else 50

st.markdown(
    f"""
    <div class="kpi-container">
        <div class="kpi-card">
            <span class="kpi-icon">🏢</span>
            <div class="kpi-label">Total UMKM</div>
            <div class="kpi-value">{format_number(total_umkm)}</div>
            <div class="kpi-delta {growth_class_umkm}">{arrow_umkm} {abs(delta_umkm):.1f}% vs tahun lalu</div>
            <div class="kpi-progress-bg"><div class="kpi-progress-fill" style="width:{umkm_progress}%"></div></div>
        </div>
        <div class="kpi-card">
            <span class="kpi-icon">👥</span>
            <div class="kpi-label">Total Tenaga Kerja</div>
            <div class="kpi-value">{format_number(total_tk)}</div>
            <div class="kpi-delta {growth_class_tk}">{arrow_tk} {abs(delta_tk):.1f}% vs tahun lalu</div>
            <div class="kpi-progress-bg"><div class="kpi-progress-fill" style="width:{tk_progress}%"></div></div>
        </div>
        <div class="kpi-card">
            <span class="kpi-icon">💰</span>
            <div class="kpi-label">Rata-rata Omzet</div>
            <div class="kpi-value">{format_rupiah(avg_omzet)}</div>
            <div class="kpi-delta {growth_class_omzet}">{arrow_omzet} {abs(delta_omzet):.1f}% vs tahun lalu</div>
            <div class="kpi-progress-bg"><div class="kpi-progress-fill" style="width:{omzet_progress}%"></div></div>
        </div>
        <div class="kpi-card">
            <span class="kpi-icon">📈</span>
            <div class="kpi-label">Pertumbuhan Rata-rata</div>
            <div class="kpi-value">{avg_growth:+.1f}%</div>
            <div class="kpi-delta {growth_class_avg}">{arrow_avg} Year-over-Year</div>
            <div class="kpi-progress-bg"><div class="kpi-progress-fill" style="width:{growth_progress}%"></div></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SECTION 1: PETA CHOROPLETH INDONESIA
# ============================================================
st.markdown(
    '<div class="section-header">🗺️ Peta Sebaran UMKM per Provinsi</div>',
    unsafe_allow_html=True,
)

map_insight = generate_insight(filtered, "distribusi")
st.markdown(
    f'<div class="insight-box"><div class="insight-title">💡 Insight Otomatis</div>'
    f'<p>{map_insight}</p></div>',
    unsafe_allow_html=True,
)

with st.spinner("Memuat peta Indonesia..."):
    geojson_data = load_indonesia_geojson()

if geojson_data is not None:
    map_data = (
        filtered.groupby("provinsi", as_index=False)["jumlah_umkm"].sum()
    )

    # Mapping nama provinsi agar sesuai dengan GeoJSON
    prov_name_map = {
        "DKI Jakarta": "Jakarta Raya",
        "DI Yogyakarta": "Di Yogyakarta",
        "Kepulauan Bangka Belitung": "Bangka Belitung",
        "Nusa Tenggara Barat": "Nusa Tenggara Barat",
        "Nusa Tenggara Timur": "Nusa Tenggara Timur",
        "Kalimantan Utara": "Kalimantan Utara",
    }
    map_data["provinsi_geo"] = map_data["provinsi"].replace(prov_name_map)

    # Build choropleth
    fig_map = px.choropleth(
        map_data,
        geojson=geojson_data,
        locations="provinsi_geo",
        featureidkey="properties.state",
        color="jumlah_umkm",
        color_continuous_scale=[
            [0.0, "#0f172a"],
            [0.2, "#312e81"],
            [0.5, "#6366f1"],
            [0.8, "#22d3ee"],
            [1.0, "#10b981"],
        ],
        hover_name="provinsi",
        hover_data={"jumlah_umkm": ":,.0f", "provinsi_geo": False},
        labels={"jumlah_umkm": "Jumlah UMKM"},
    )
    fig_map.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(0,0,0,0)",
    )
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=THEME['font_color'], size=12),
        height=480,
        margin=dict(l=0, r=0, t=10, b=0),
        hoverlabel=dict(
            bgcolor=THEME['hover_bg'],
            bordercolor="#6366f1",
            font=dict(family="Inter", color=THEME['hover_font']),
        ),
        coloraxis_colorbar=dict(
            title="Jumlah UMKM",
            thickness=14,
            len=0.6,
            tickfont=dict(size=10, color=THEME['font_color']),
            title_font=dict(size=11, color=THEME['font_color']),
        ),
    )
    fig_map.update_traces(
        marker_line_color="rgba(99,102,241,0.3)",
        marker_line_width=0.8,
    )

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown(
        '<div class="chart-title">🌐 Peta Choropleth — Konsentrasi UMKM per Provinsi</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_map, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("ℹ️ Peta tidak dapat dimuat (periksa koneksi internet). Menampilkan chart alternatif.")

# ============================================================
# SECTION 2: DISTRIBUSI WILAYAH & SEKTOR
# ============================================================
st.markdown(
    '<div class="section-header">📊 Distribusi Wilayah & Sektor Usaha</div>',
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
        marker=dict(line=dict(color=THEME['marker_line'], width=2)),
    )
    st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# SECTION 3: TREN & PERTUMBUHAN
# ============================================================
st.markdown(
    '<div class="section-header">📈 Tren & Pertumbuhan Tahunan</div>',
    unsafe_allow_html=True,
)

tren_insight = generate_insight(filtered, "tren")
st.markdown(
    f'<div class="insight-box"><div class="insight-title">💡 Insight Otomatis</div>'
    f'<p>{tren_insight}</p></div>',
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
            marker=dict(size=10, color="#6366f1", line=dict(width=2, color=THEME['marker_line'])),
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
# SECTION 4: PERBANDINGAN SKALA & SEKTOR
# ============================================================
st.markdown(
    '<div class="section-header">⚖️ Perbandingan Skala & Sektor Usaha</div>',
    unsafe_allow_html=True,
)

skala_insight = generate_insight(filtered, "skala")
st.markdown(
    f'<div class="insight-box"><div class="insight-title">💡 Insight Otomatis</div>'
    f'<p>{skala_insight}</p></div>',
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
# SECTION 5: ANALISIS MENDALAM
# ============================================================
st.markdown(
    '<div class="section-header">🔬 Analisis Mendalam</div>',
    unsafe_allow_html=True,
)

analisis_insight = generate_insight(filtered, "analisis")
st.markdown(
    f'<div class="insight-box"><div class="insight-title">💡 Insight Otomatis</div>'
    f'<p>{analisis_insight}</p></div>',
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
            textfont=dict(size=14, color=THEME['heatmap_text']),
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
        marker_line_color=THEME['marker_line'],
        hovertemplate="<b>%{hovertext}</b><br>Omzet: Rp %{x:,.0f} Jt<br>TK: %{y:,.0f}<extra></extra>",
    )
    st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# SECTION 6: DISTRIBUSI SKALA USAHA PER PROVINSI (STACKED)
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
# SECTION 7: DATA TABLE
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
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            label="📥 Download CSV",
            data=csv_summary,
            file_name="ringkasan_umkm_provinsi.csv",
            mime="text/csv",
        )
    with dl_col2:
        excel_summary = to_excel(summary)
        st.download_button(
            label="📥 Download Excel",
            data=excel_summary,
            file_name="ringkasan_umkm_provinsi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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
    dl_col3, dl_col4 = st.columns(2)
    with dl_col3:
        st.download_button(
            label="📥 Download CSV",
            data=csv_full,
            file_name="data_umkm_lengkap.csv",
            mime="text/csv",
        )
    with dl_col4:
        excel_full = to_excel(display_df)
        st.download_button(
            label="📥 Download Excel",
            data=excel_full,
            file_name="data_umkm_lengkap.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# FOOTER
# ============================================================
st.markdown(
    """
    <div class="footer">
        <p>📊 <strong>Dashboard Analisis UMKM Indonesia</strong> — Dibuat dengan Streamlit, Plotly, Pandas &amp; NumPy</p>
        <p>Data sampel berdasarkan pola statistik BPS Indonesia | © 2024</p>
    </div>
    """,
    unsafe_allow_html=True,
)
