"""
Dashboard Control Tower — Supply Chain & Delivery Performance (Olist 2016–2018)

Cara menjalankan (dari folder utama proyek):
    python -m streamlit run dashboard/app.py

Struktur:
    Tab 1  Control Tower        : ringkasan KPI, peta wilayah, tren, pesanan paling telat
    Tab 2  Wilayah & Proses     : ranking state, bottleneck tahap pengiriman, ongkir
    Tab 3  Dampak ke Customer   : hubungan keterlambatan dengan skor review
    Tab 4  Seller               : performa seller dan rute asal-tujuan
"""
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ----------------------------------------------------------------------------
# Konfigurasi
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Delivery Control Tower", layout="wide", initial_sidebar_state="expanded")

BASE_DIR = Path(__file__).resolve().parent.parent
FACT_PATH = BASE_DIR / "outputs" / "fact_order_delivery.csv"
COORD_PATH = BASE_DIR / "outputs" / "brazil_states_coordinates.csv"
RAW_DIR = BASE_DIR / "data" / "raw"

# Palet: biru korporat + merah/hijau khusus untuk status
BLUE = "#1F4FBF"
BLUE_DARK = "#0B2A5B"
BLUE_SOFT = "#BFD0F0"
ON_TIME = "#1E8E6A"
LATE = "#D6452F"
AMBER = "#E08A1E"
INK = "#1B2A41"
MUTED = "#6B7A90"
LINE = "#E3E8EF"
BG = "#EEF2F7"

SCALE_LATE = [[0, "#E8EEF8"], [0.5, "#F0A99B"], [1, LATE]]

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp {{ font-family: 'Inter', 'Segoe UI', sans-serif; }}
    .stApp {{ background: {BG}; color: {INK}; }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    .block-container {{ padding-top: 2.2rem; padding-bottom: 2rem; max-width: 1600px; }}

    section[data-testid="stSidebar"] {{ background: #FFFFFF; border-right: 1px solid {LINE}; }}
    section[data-testid="stSidebar"] h2 {{ font-size: 1rem; font-weight: 700; color: {BLUE_DARK}; }}

    /* Header seperti control tower */
    .ct-header {{
        background: linear-gradient(90deg, {BLUE_DARK} 0%, {BLUE} 100%);
        border-radius: 10px; padding: 16px 24px; margin-bottom: 14px;
        display: flex; justify-content: space-between; align-items: center;
    }}
    .ct-title {{ color: #fff; font-size: 1.35rem; font-weight: 700; margin: 0; }}
    .ct-sub {{ color: #C9D8F5; font-size: .82rem; margin: 2px 0 0; }}
    .ct-period {{ color: #fff; font-size: .82rem; text-align: right; line-height: 1.5; }}
    .ct-period b {{ font-weight: 600; }}

    /* Kartu panel: container ber-key "card_*" */
    [class*="st-key-card_"] {{
        background: #FFFFFF; border: 1px solid {LINE} !important; border-radius: 10px;
        padding: 14px 16px 6px !important;
        box-shadow: 0 1px 2px rgba(15, 35, 70, .05);
    }}
    .card-title {{
        font-size: .8rem; font-weight: 700; color: {INK}; text-transform: uppercase;
        letter-spacing: .04em; margin: 0 0 6px; padding-bottom: 8px; border-bottom: 1px solid {LINE};
    }}
    .card-title span {{ color: {MUTED}; font-weight: 500; text-transform: none; letter-spacing: 0; }}

    /* Kartu angka */
    .kpi {{
        background: #fff; border: 1px solid {LINE}; border-radius: 10px; padding: 14px 16px;
        height: 118px; box-sizing: border-box; display: flex; flex-direction: column;
        justify-content: space-between; border-top: 3px solid {BLUE_SOFT};
    }}
    .kpi.good {{ border-top-color: {ON_TIME}; }}
    .kpi.bad {{ border-top-color: {LATE}; }}
    .kpi.warn {{ border-top-color: {AMBER}; }}
    .kpi .label {{ color: {MUTED}; font-size: .72rem; font-weight: 600; text-transform: uppercase;
                   letter-spacing: .05em; min-height: 1.9em; line-height: 1.3; }}
    .kpi .value {{ font-size: 1.65rem; font-weight: 700; line-height: 1.1; color: {BLUE}; }}
    .kpi.good .value {{ color: {ON_TIME}; }}
    .kpi.bad .value {{ color: {LATE}; }}
    .kpi.warn .value {{ color: {AMBER}; }}
    .kpi .sub {{ color: {MUTED}; font-size: .76rem; min-height: 1.3em; }}

    .takeaway {{
        background: #fff; border: 1px solid {LINE}; border-left: 4px solid {BLUE};
        border-radius: 8px; padding: 11px 16px; margin: 4px 0 12px; font-size: .9rem;
    }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {LINE}; }}
    .stTabs [data-baseweb="tab"] {{ background: transparent; padding: 10px 18px; color: {MUTED}; font-weight: 500; }}
    .stTabs [aria-selected="true"] {{ color: {BLUE} !important; font-weight: 700; }}
    .stTabs [data-baseweb="tab-highlight"] {{ background-color: {BLUE}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Helper tampilan
# ----------------------------------------------------------------------------
def theme(fig, height=300, legend=False):
    fig.update_layout(
        template="plotly_white", paper_bgcolor="#fff", plot_bgcolor="#fff",
        font=dict(family="Inter, Segoe UI, sans-serif", size=12, color=INK),
        height=height, margin=dict(l=10, r=10, t=44 if legend else 12, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title_text="",
                    font=dict(size=11, color=MUTED)) if legend else dict(),
        hoverlabel=dict(bgcolor=BLUE_DARK, font_size=12, font_color="#fff", bordercolor=BLUE_DARK),
    )
    fig.update_xaxes(gridcolor=LINE, zeroline=False, linecolor=LINE, tickfont=dict(size=11, color=MUTED))
    fig.update_yaxes(gridcolor=LINE, zeroline=False, linecolor=LINE, tickfont=dict(size=11, color=MUTED))
    return fig


@contextmanager
def card(key, title, note=""):
    """Kartu putih berborder; seluruh isinya (judul + grafik) benar-benar berada di dalam kartu."""
    with st.container(border=True, key=f"card_{key}"):
        note_html = f" <span>· {note}</span>" if note else ""
        st.markdown(f'<div class="card-title">{title}{note_html}</div>', unsafe_allow_html=True)
        yield


def chart(fig, height=300, legend=False):
    st.plotly_chart(theme(fig, height, legend), width="stretch", config={"displayModeBar": False})


def kpi(label, value, sub="", tone=""):
    st.markdown(
        f'<div class="kpi {tone}"><div class="label">{label}</div>'
        f'<div class="value">{value}</div><div class="sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def takeaway(text):
    st.markdown(f'<div class="takeaway">{text}</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
FACT_PARQUET = BASE_DIR / "outputs" / "fact_order_delivery.parquet"
SELLER_PAIRS_PARQUET = BASE_DIR / "outputs" / "order_seller_pairs.parquet"

@st.cache_data(show_spinner="Memuat data...")
def load_fact():
    if FACT_PARQUET.exists():
        df = pd.read_parquet(FACT_PARQUET)
    elif FACT_PATH.exists():
        df = pd.read_csv(
            FACT_PATH,
            parse_dates=["order_purchase_timestamp", "order_delivered_customer_date",
                         "order_estimated_delivery_date", "purchase_month"],
            low_memory=False,
        )
    else:
        return None
    for c in ["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date", "purchase_month"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c])
    df["evaluable"] = df["delivery_result"].isin(["on_time", "late"])
    df["late"] = df["delivery_result"].eq("late")
    return df


@st.cache_data(show_spinner="Menyiapkan data seller...")
def load_seller_pairs():
    if SELLER_PAIRS_PARQUET.exists():
        return pd.read_parquet(SELLER_PAIRS_PARQUET)
    item_csv = RAW_DIR / "olist_order_items_dataset.csv"
    seller_csv = RAW_DIR / "olist_sellers_dataset.csv"
    if item_csv.exists() and seller_csv.exists():
        items = pd.read_csv(item_csv, usecols=["order_id", "seller_id"])
        sellers = pd.read_csv(seller_csv, usecols=["seller_id", "seller_state", "seller_city"])
        return items.drop_duplicates().merge(sellers, on="seller_id", how="left")
    return None


@st.cache_data
def load_coords():
    return pd.read_csv(COORD_PATH) if COORD_PATH.exists() else None


if not FACT_PATH.exists():
    st.error("File `outputs/fact_order_delivery.csv` belum ada. Jalankan dulu notebook `01_data_audit_and_eda.ipynb`.")
    st.stop()

fact = load_fact()
coords = load_coords()
pairs = load_seller_pairs() if (RAW_DIR / "olist_order_items_dataset.csv").exists() else None

# ----------------------------------------------------------------------------
# Filter (sidebar)
# ----------------------------------------------------------------------------
st.sidebar.markdown("## Filter")
min_d = fact["order_purchase_timestamp"].min().date()
max_d = fact["order_purchase_timestamp"].max().date()
date_range = st.sidebar.date_input("Periode pembelian", (min_d, max_d), min_value=min_d, max_value=max_d)
d_from, d_to = date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (min_d, max_d)

all_states = sorted(fact["customer_state"].dropna().unique())
sel_states = st.sidebar.multiselect("State customer", all_states, default=[], placeholder="Semua state")
min_orders_state = st.sidebar.slider("Minimal order per state (untuk ranking)", 10, 1000, 100, 10)
st.sidebar.markdown("---")
st.sidebar.caption("Data historis Olist 2016–2018. Hasil menunjukkan hubungan antar variabel, bukan bukti sebab-akibat.")

mask = (fact["order_purchase_timestamp"].dt.date >= d_from) & (fact["order_purchase_timestamp"].dt.date <= d_to)
if sel_states:
    mask &= fact["customer_state"].isin(sel_states)
df = fact[mask].copy()
ev = df[df["evaluable"]].copy()

if ev.empty:
    st.warning("Tidak ada order yang bisa dievaluasi pada filter ini. Ubah filter di sidebar.")
    st.stop()

# ----------------------------------------------------------------------------
# Angka utama
# ----------------------------------------------------------------------------
n_all, n_ev = len(df), len(ev)
n_late = int(ev["late"].sum())
n_on = n_ev - n_late
on_rate = 100 * n_on / n_ev
late_rate = 100 * n_late / n_ev
avg_days = ev["delivery_cycle_days"].mean()
avg_delay = ev.loc[ev["late"], "late_days_if_late"].mean() if n_late else np.nan
rev_on = ev.loc[~ev["late"], "avg_review_score"].mean()
rev_late = ev.loc[ev["late"], "avg_review_score"].mean() if n_late else np.nan
rev_all = ev["avg_review_score"].mean()

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="ct-header">
      <div>
        <p class="ct-title">Delivery Control Tower</p>
        <p class="ct-sub">Pemantauan ketepatan waktu pengiriman, titik bottleneck, dan dampaknya ke customer</p>
      </div>
      <div class="ct-period">Periode data<br><b>{d_from:%d %b %Y} – {d_to:%d %b %Y}</b></div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(["Control Tower", "Wilayah & Proses", "Dampak ke Customer", "Seller"])

# ============================================================================
# TAB 1 — CONTROL TOWER
# ============================================================================
with tab1:
    k = st.columns(6)
    with k[0]: kpi("Total order", f"{n_all:,}", "semua status")
    with k[1]: kpi("Order dievaluasi", f"{n_ev:,}", "terkirim & tanggal lengkap")
    with k[2]: kpi("Tepat waktu", f"{on_rate:.1f}%", f"{n_on:,} order", "good")
    with k[3]: kpi("Terlambat", f"{late_rate:.1f}%", f"{n_late:,} order", "bad")
    with k[4]: kpi("Rata-rata pengiriman", f"{avg_days:.1f} hari", "dari beli sampai diterima")
    with k[5]: kpi("Rata-rata telat", f"{avg_delay:.1f} hari" if n_late else "-", "hanya order terlambat", "warn")
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    left, mid, right = st.columns([1.05, 1.9, 1.15], gap="medium")

    # ---------- Kolom kiri ----------
    with left:
        with card("rings", "Ringkasan performa", "persentase dari order dievaluasi"):
            fig = make_subplots(rows=1, cols=3, specs=[[{"type": "domain"}] * 3])
            rings = [(on_rate, ON_TIME, f"{on_rate:.0f}%", "Tepat waktu"),
                     (late_rate, LATE, f"{late_rate:.1f}%", "Terlambat"),
                     (100 * rev_all / 5, BLUE, f"{rev_all:.1f}", "Skor review")]
            for i, (val, color, text, _) in enumerate(rings, start=1):
                fig.add_trace(go.Pie(values=[val, 100 - val], hole=.74, sort=False, direction="clockwise",
                                     marker=dict(colors=[color, "#EDF1F6"]), textinfo="none", hoverinfo="skip"),
                              row=1, col=i)
            xs = [0.12, 0.5, 0.88]
            ann = []
            for x, (_, color, text, name) in zip(xs, rings):
                ann.append(dict(text=f"<b>{text}</b>", x=x, y=0.5, showarrow=False, font=dict(size=15, color=color)))
                ann.append(dict(text=name, x=x, y=-0.02, showarrow=False, font=dict(size=11, color=MUTED)))
            fig.update_layout(annotations=ann, showlegend=False)
            chart(fig, 150)

        with card("trend", "Volume order per bulan", "order terkirim yang dievaluasi"):
            monthly = (ev.groupby("purchase_month").agg(order=("order_id", "count"), telat=("late", "sum")).reset_index())
            monthly = monthly[monthly["order"] >= 30]
            monthly["late_rate"] = 100 * monthly["telat"] / monthly["order"]
            fig = go.Figure(go.Scatter(x=monthly["purchase_month"], y=monthly["order"], mode="lines", fill="tozeroy",
                                       line=dict(color=BLUE, width=2.5, shape="spline"),
                                       fillcolor="rgba(31,79,191,.12)",
                                       hovertemplate="%{x|%b %Y}<br>%{y:,} order<extra></extra>"))
            fig.update_xaxes(tickformat="%b %y")
            chart(fig, 210)

        with card("dow", "Order menurut hari pembelian"):
            dow = ev["order_purchase_timestamp"].dt.dayofweek.value_counts().sort_index()
            names = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
            fig = go.Figure(go.Bar(x=[names[i] for i in dow.index], y=dow.values, marker_color=BLUE,
                                   hovertemplate="%{x}: %{y:,} order<extra></extra>"))
            fig.update_layout(bargap=.35)
            chart(fig, 200)

    # ---------- Kolom tengah ----------
    with mid:
        worst_m = monthly.sort_values("late_rate", ascending=False).iloc[0]
        takeaway(f"<b>{on_rate:.1f}%</b> order tiba sesuai estimasi. Bulan paling bermasalah adalah "
                 f"<b>{worst_m['purchase_month']:%B %Y}</b> dengan <b>{worst_m['late_rate']:.1f}%</b> order terlambat.")

        with card("map", "Peta keterlambatan per state", "ukuran lingkaran = jumlah order, warna = late rate"):
            sp_state = (ev.groupby("customer_state")
                        .agg(order=("order_id", "count"), telat=("late", "sum"), hari=("delivery_cycle_days", "mean"))
                        .reset_index())
            sp_state["late_rate"] = 100 * sp_state["telat"] / sp_state["order"]
            if coords is not None:
                mp = sp_state.merge(coords, left_on="customer_state", right_on="geolocation_state", how="left").dropna(
                    subset=["geolocation_lat"])
                fig = px.scatter_geo(
                    mp, lat="geolocation_lat", lon="geolocation_lng", size="order", color="late_rate",
                    hover_name="customer_state", scope="south america", size_max=38,
                    color_continuous_scale=SCALE_LATE,
                    hover_data={"geolocation_lat": False, "geolocation_lng": False,
                                "order": ":,", "late_rate": ":.1f", "hari": ":.1f"},
                    labels={"order": "Order", "late_rate": "Late rate (%)", "hari": "Rata-rata hari"},
                )
                fig.update_traces(marker=dict(line=dict(color="#fff", width=1), opacity=.9))
                fig.update_geos(lonaxis_range=[-75, -33], lataxis_range=[-34, 6], showcountries=True,
                                countrycolor="#C9D3E0", showland=True, landcolor="#F3F6FA",
                                showocean=True, oceancolor="#FFFFFF", showcoastlines=True,
                                coastlinecolor="#C9D3E0", bgcolor="#FFFFFF")
                fig.update_layout(coloraxis_colorbar=dict(title="Late rate (%)", thickness=10, len=.6, x=0.99))
                chart(fig, 520)
            else:
                st.info("File koordinat `outputs/brazil_states_coordinates.csv` belum ada.")

    # ---------- Kolom kanan ----------
    with right:
        with card("feed", "Keterlambatan terparah", "5 order dengan telat terlama"):
            feed = (ev[ev["late"]].sort_values("late_days_if_late", ascending=False).head(5)
                    [["order_id", "customer_city", "customer_state", "late_days_if_late"]].copy())
            feed["Order"] = feed["order_id"].str[:8]
            feed["Tujuan"] = feed["customer_city"].str.title().str[:12] + " (" + feed["customer_state"] + ")"
            feed["Telat (hari)"] = feed["late_days_if_late"].round(0).astype(int)
            st.dataframe(feed[["Order", "Tujuan", "Telat (hari)"]], hide_index=True, width="stretch", height=213)

        with card("crit", "State paling bermasalah", f"min. {min_orders_state} order"):
            crit = sp_state[sp_state["order"] >= min_orders_state].sort_values("late_rate", ascending=False).head(6)
            crit = crit.sort_values("late_rate")
            fig = go.Figure(go.Bar(x=crit["late_rate"], y=crit["customer_state"], orientation="h",
                                   marker_color=[LATE if v > 2 * late_rate else AMBER for v in crit["late_rate"]],
                                   text=crit["late_rate"].map("{:.1f}%".format), textposition="outside",
                                   cliponaxis=False,
                                   hovertemplate="%{y}: %{x:.1f}% terlambat<extra></extra>"))
            fig.update_xaxes(title="Late rate (%)")
            fig.update_layout(margin=dict(r=36))
            chart(fig, 230)

        with card("stage", "Rata-rata durasi tiap tahap", "dalam hari"):
            stage = pd.DataFrame({
                "Tahap": ["Beli → disetujui", "Beli → ke kurir", "Kurir → customer"],
                "Hari": [ev["purchase_to_approval_days"].mean(), ev["purchase_to_carrier_days"].mean(),
                         ev["carrier_to_customer_days"].mean()]})
            fig = go.Figure(go.Bar(x=stage["Hari"], y=stage["Tahap"], orientation="h", marker_color=BLUE,
                                   text=stage["Hari"].map("{:.1f}".format), textposition="outside", cliponaxis=False))
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(margin=dict(r=30))
            chart(fig, 175)

# ============================================================================
# TAB 2 — WILAYAH & PROSES
# ============================================================================
with tab2:
    geo = (ev.groupby("customer_state")
           .agg(order=("order_id", "count"), telat=("late", "sum"), rata_hari=("delivery_cycle_days", "mean"),
                ongkir=("total_freight_value_brl", "mean")).reset_index())
    geo["late_rate"] = 100 * geo["telat"] / geo["order"]
    geo_f = geo[geo["order"] >= min_orders_state]

    if not geo_f.empty:
        w = geo_f.sort_values("late_rate", ascending=False).iloc[0]
        big = geo_f.sort_values("order", ascending=False).iloc[0]
        takeaway(f"Late rate tertinggi ada di <b>{w['customer_state']}</b> ({w['late_rate']:.1f}%, {int(w['order']):,} order). "
                 f"State dengan order terbanyak, <b>{big['customer_state']}</b>, late rate-nya {big['late_rate']:.1f}% "
                 f"({int(big['telat']):,} order terlambat).")

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        with card("t2a", f"12 state dengan late rate tertinggi", f"min. {min_orders_state} order"):
            top = geo_f.sort_values("late_rate", ascending=False).head(12).sort_values("late_rate")
            fig = px.bar(top, x="late_rate", y="customer_state", orientation="h", color="late_rate",
                         color_continuous_scale=SCALE_LATE, text=top["late_rate"].map("{:.1f}%".format),
                         hover_data={"order": ":,", "telat": ":,", "late_rate": ":.2f"})
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_layout(coloraxis_showscale=False, xaxis_title="Late rate (%)", yaxis_title="", margin=dict(r=36))
            chart(fig, 440)
    with c2:
        with card("t2b", "Volume order vs late rate per state"):
            fig = px.scatter(geo_f, x="order", y="late_rate", text="customer_state", log_x=True,
                             labels={"order": "Jumlah order (skala log)", "late_rate": "Late rate (%)"},
                             hover_data={"order": ":,", "late_rate": ":.2f"})
            fig.update_traces(marker=dict(size=11, color=BLUE, opacity=.8, line=dict(color="#fff", width=1)),
                              textposition="top center", textfont=dict(size=10, color=MUTED))
            fig.add_hline(y=late_rate, line_dash="dash", line_color=LATE,
                          annotation_text=f"Rata-rata {late_rate:.1f}%", annotation_position="top left")
            chart(fig, 440)

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        with card("t2c", "Di tahap mana waktu paling lama?", "rata-rata hari"):
            stage2 = pd.DataFrame({
                "Tahap": ["Beli → disetujui", "Beli → diserahkan ke kurir", "Kurir → diterima customer"],
                "Hari": [ev["purchase_to_approval_days"].mean(), ev["purchase_to_carrier_days"].mean(),
                         ev["carrier_to_customer_days"].mean()]})
            fig = px.bar(stage2, x="Hari", y="Tahap", orientation="h", text=stage2["Hari"].map("{:.1f} hari".format))
            fig.update_traces(marker_color=BLUE, textposition="outside", cliponaxis=False)
            fig.update_layout(yaxis=dict(autorange="reversed", title=""), xaxis_title="Hari", margin=dict(r=50))
            chart(fig, 320)
    with c4:
        with card("t2d", "Seberapa lama keterlambatannya?", "hanya order terlambat"):
            fig = px.histogram(ev[ev["late"]], x="late_days_if_late", nbins=40,
                               labels={"late_days_if_late": "Hari terlambat"})
            fig.update_traces(marker_color=LATE, opacity=.9)
            fig.update_layout(yaxis_title="Jumlah order", bargap=.05)
            chart(fig, 320)

    with card("t2e", "Late rate menurut kelompok ongkos kirim", "5 kelompok sama besar"):
        evf = ev.copy()
        evf["band"] = pd.qcut(evf["total_freight_value_brl"].rank(method="first"), 5,
                              labels=["Sangat murah", "Murah", "Sedang", "Mahal", "Sangat mahal"])
        fr = evf.groupby("band", observed=True).agg(order=("order_id", "count"), telat=("late", "sum")).reset_index()
        fr["late_rate"] = 100 * fr["telat"] / fr["order"]
        fig = px.bar(fr, x="band", y="late_rate", text=fr["late_rate"].map("{:.1f}%".format),
                     labels={"band": "Kelompok ongkir", "late_rate": "Late rate (%)"})
        fig.update_traces(marker_color=BLUE, textposition="outside", cliponaxis=False)
        fig.update_layout(yaxis=dict(rangemode="tozero"))
        chart(fig, 300)

    with st.expander("Lihat tabel lengkap per state"):
        show = geo.sort_values("late_rate", ascending=False).rename(columns={
            "customer_state": "State", "order": "Order", "telat": "Terlambat", "rata_hari": "Rata-rata hari",
            "ongkir": "Rata-rata ongkir (BRL)", "late_rate": "Late rate (%)"})
        st.dataframe(show.round(2), width="stretch", hide_index=True)

# ============================================================================
# TAB 3 — DAMPAK KE CUSTOMER
# ============================================================================
with tab3:
    rv = ev.dropna(subset=["avg_review_score"]).copy()
    rv["status"] = np.where(rv["late"], "Terlambat", "Tepat waktu")

    if n_late:
        takeaway(f"Order tepat waktu rata-rata mendapat skor <b>{rev_on:.2f}</b>, sedangkan order terlambat hanya "
                 f"<b>{rev_late:.2f}</b> (selisih {rev_on - rev_late:.2f} poin). Ini hubungan, bukan bukti sebab-akibat.")

    a, b, c = st.columns(3)
    with a: kpi("Skor review — tepat waktu", f"{rev_on:.2f}", "skala 1–5", "good")
    with b: kpi("Skor review — terlambat", f"{rev_late:.2f}" if n_late else "-", "skala 1–5", "bad")
    with c: kpi("Selisih skor", f"{rev_on - rev_late:.2f}" if n_late else "-", "tepat waktu dikurangi terlambat", "warn")
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        with card("t3a", "Sebaran skor review", "% dalam tiap kelompok"):
            dist = (rv.assign(skor=rv["avg_review_score"].round().astype(int))
                    .groupby(["status", "skor"]).size().reset_index(name="order"))
            dist["persen"] = 100 * dist["order"] / dist.groupby("status")["order"].transform("sum")
            fig = px.bar(dist, x="skor", y="persen", color="status", barmode="group",
                         color_discrete_map={"Tepat waktu": ON_TIME, "Terlambat": LATE},
                         labels={"skor": "Skor review", "persen": "% order"})
            fig.update_xaxes(dtick=1)
            chart(fig, 400, legend=True)
    with c2:
        with card("t3b", "Skor review menurut lama keterlambatan", "rata-rata skor"):
            labels = ["Tepat waktu", "Telat 1–3 hari", "Telat 4–7 hari", "Telat 8–14 hari", "Telat >14 hari"]
            rv["kategori"] = pd.cut(rv["delivery_variance_days"], bins=[-1000, 0, 3, 7, 14, 1000], labels=labels)
            cat = (rv.groupby("kategori", observed=True)["avg_review_score"].agg(["mean", "count"])
                   .reindex(labels).dropna().reset_index())
            fig = px.bar(cat, x="kategori", y="mean", text=cat["mean"].map("{:.2f}".format),
                         hover_data={"count": ":,"}, labels={"kategori": "", "mean": "Rata-rata skor"})
            fig.update_traces(marker_color=[ON_TIME] + [LATE] * (len(cat) - 1), textposition="outside", cliponaxis=False)
            fig.update_layout(yaxis_range=[0, 5.3])
            chart(fig, 400, legend=True)

# ============================================================================
# TAB 4 — SELLER
# ============================================================================
with tab4:
    if pairs is None:
        st.info("File data mentah seller tidak ditemukan di `data/raw/`.")
    else:
        sp = pairs.merge(df[["order_id", "customer_state", "evaluable", "late", "delivery_cycle_days"]],
                         on="order_id", how="inner")
        sp = sp[sp["evaluable"]]

        min_seller = st.slider("Minimal order per seller (agar perbandingan adil)", 10, 300, 50, 10)
        sm = (sp.groupby(["seller_id", "seller_state", "seller_city"], dropna=False)
              .agg(order=("order_id", "nunique"), telat=("late", "sum"), rata_hari=("delivery_cycle_days", "mean"))
              .reset_index())
        sm["late_rate"] = 100 * sm["telat"] / sm["order"]
        sm_f = sm[sm["order"] >= min_seller].copy()
        sm_f["seller_label"] = sm_f["seller_id"].str[:8]

        n_bad = int((sm_f["late_rate"] > 15).sum())
        n_good = int((sm_f["late_rate"] < 3).sum())
        takeaway(f"Dari <b>{len(sm_f):,}</b> seller dengan minimal {min_seller} order, "
                 f"<b>{n_bad}</b> seller memiliki late rate di atas 15% dan <b>{n_good}</b> seller di bawah 3%.")

        a, b, c = st.columns(3)
        with a: kpi("Seller dianalisis", f"{len(sm_f):,}", f"minimal {min_seller} order")
        with b: kpi("Late rate di atas 15%", f"{n_bad:,}", "perlu dibina", "bad")
        with c: kpi("Late rate di bawah 3%", f"{n_good:,}", "performa terbaik", "good")
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2, gap="medium")
        with c1:
            with card("t4a", "Volume order vs late rate per seller"):
                fig = px.scatter(sm_f, x="order", y="late_rate",
                                 hover_data={"seller_label": True, "seller_state": True, "order": ":,",
                                             "late_rate": ":.2f", "rata_hari": ":.1f"},
                                 labels={"order": "Jumlah order", "late_rate": "Late rate (%)"})
                fig.update_traces(marker=dict(size=8, color=BLUE, opacity=.6, line=dict(color="#fff", width=1)))
                fig.add_hline(y=15, line_dash="dash", line_color=LATE, annotation_text="Batas 15%",
                              annotation_position="top left")
                chart(fig, 430)
        with c2:
            with card("t4b", "12 seller dengan late rate tertinggi"):
                worst = sm_f.sort_values("late_rate", ascending=False).head(12).sort_values("late_rate")
                fig = px.bar(worst, x="late_rate", y="seller_label", orientation="h",
                             text=worst["late_rate"].map("{:.1f}%".format),
                             hover_data={"seller_state": True, "order": ":,"},
                             labels={"late_rate": "Late rate (%)", "seller_label": "Seller (8 karakter ID)"})
                fig.update_traces(marker_color=LATE, textposition="outside", cliponaxis=False)
                fig.update_layout(margin=dict(r=40))
                chart(fig, 430)

        with card("t4c", "Late rate (%) menurut rute asal → tujuan", "min. 30 order per rute"):
            od = (sp.groupby(["seller_state", "customer_state"])
                  .agg(order=("order_id", "count"), telat=("late", "sum")).reset_index())
            od = od[od["order"] >= 30]
            od["late_rate"] = 100 * od["telat"] / od["order"]
            top_s = sp["seller_state"].value_counts().head(8).index
            top_c = sp["customer_state"].value_counts().head(12).index
            pv = (od[od["seller_state"].isin(top_s) & od["customer_state"].isin(top_c)]
                  .pivot(index="seller_state", columns="customer_state", values="late_rate"))
            fig = px.imshow(pv, aspect="auto", color_continuous_scale=SCALE_LATE, text_auto=".0f",
                            labels=dict(x="State customer (tujuan)", y="State seller (asal)", color="Late rate (%)"))
            chart(fig, 400)

        with st.expander("Lihat tabel seller lengkap"):
            st.dataframe(
                sm_f.sort_values("late_rate", ascending=False)[
                    ["seller_id", "seller_city", "seller_state", "order", "telat", "late_rate", "rata_hari"]
                ].rename(columns={"seller_id": "ID seller", "seller_city": "Kota", "seller_state": "State",
                                  "order": "Order", "telat": "Terlambat", "late_rate": "Late rate (%)",
                                  "rata_hari": "Rata-rata hari"}).round(2),
                width="stretch", hide_index=True)

st.caption("Sumber: Olist Brazilian E-Commerce (2016–2018). Studi kasus historis, bukan kondisi logistik saat ini.")
