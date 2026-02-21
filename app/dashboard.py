"""
NYC Rideshare Operations Dashboard
Streamlit dashboard for NYC High-Volume For-Hire Vehicle trip data (2022-2024).
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ---------------------------------------------------------------------------
# Page config & theme
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="NYC Rideshare Operations",
    page_icon="\U0001F695",
    layout="wide",
)

# Color palette
BLUE = "#2563EB"
BLUE_LIGHT = "#93C5FD"
SLATE = "#475569"
EMERALD = "#059669"
AMBER = "#D97706"

# Compact CSS for single-screen fit
st.markdown(
    """<style>
    .block-container {padding:0.8rem 1.5rem 0rem 1.5rem;}
    h1 {margin:0 0 0.1rem 0; font-size:1.5rem; color:#1E293B;}
    h3 {margin:0.3rem 0 0 0; font-size:0.85rem; color:#475569; font-weight:600;}
    .stCaption {margin:0; padding:0;}
    .stCaption p {color:#94A3B8; font-size:0.7rem;}
    [data-testid="stMetric"] {
        background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px;
        padding:0.5rem 0.8rem; text-align:center;
    }
    [data-testid="stMetricValue"] {font-size:1.5rem; color:#1E293B; justify-content:center;}
    [data-testid="stMetricLabel"] {font-size:0.7rem; color:#64748B; justify-content:center; text-transform:uppercase; letter-spacing:0.05em;}
    [data-testid="stVerticalBlock"] > div {gap:0.3rem;}
    [data-testid="stHorizontalBlock"] > div {gap:0.5rem;}
    .element-container {margin-bottom:0 !important;}
    div[data-testid="stPlotlyChart"] {margin-bottom:0 !important;}
    hr {margin:0.2rem 0; border-color:#E2E8F0;}
    /* Subtle sidebar multiselect pills */
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background:#F1F5F9 !important; color:#475569 !important;
        border:1px solid #CBD5E1; border-radius:4px;
    }
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] span[role="presentation"] {
        color:#94A3B8 !important;
    }
    </style>""",
    unsafe_allow_html=True,
)

CHART_MARGIN = dict(l=40, r=15, t=5, b=25)
CHART_FONT = dict(family="Inter, system-ui, sans-serif", size=11, color=SLATE)

# ---------------------------------------------------------------------------
# Data loading (cached)
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "data"


@st.cache_data
def load_data():
    """Load all pipeline outputs."""
    zone_daily = pd.read_parquet(DATA_DIR / "processed" / "zone_daily_full.parquet")
    zone_daily["date"] = pd.to_datetime(zone_daily["date"])

    zone_meta = pd.read_csv(DATA_DIR / "raw" / "zone_metadata.csv")

    forecast = pd.read_csv(DATA_DIR / "results" / "forecast_results.csv")
    forecast["date"] = pd.to_datetime(forecast["date"])

    summary = pd.read_csv(DATA_DIR / "results" / "summary_results.csv")

    return zone_daily, zone_meta, forecast, summary


zone_daily, zone_meta, forecast, summary = load_data()

zone_daily = zone_daily.merge(
    zone_meta[["zone_id", "Borough", "Zone"]], on="zone_id", how="left"
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.title("Filters")

min_date = zone_daily["date"].min().date()
max_date = zone_daily["date"].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

boroughs = sorted(zone_daily["Borough"].dropna().unique())
selected_boroughs = st.sidebar.multiselect(
    "Boroughs", boroughs, default=boroughs
)

zone_options = sorted(forecast["zone_name"].unique())
default_zone = "East Village" if "East Village" in zone_options else zone_options[0]
selected_zone = st.sidebar.selectbox(
    "Forecast Zone", zone_options, index=zone_options.index(default_zone)
)

mask = (
    (zone_daily["date"].dt.date >= start_date)
    & (zone_daily["date"].dt.date <= end_date)
    & (zone_daily["Borough"].isin(selected_boroughs))
)
filtered = zone_daily[mask]

# ---------------------------------------------------------------------------
# Header + KPIs
# ---------------------------------------------------------------------------
st.title("NYC Rideshare Operations Dashboard")
st.caption(f"High-Volume For-Hire Vehicle Trips  \u2022  {start_date:%b %Y} \u2013 {end_date:%b %Y}")

daily_totals = filtered.groupby("date")["daily_trips"].sum()
total_trips = filtered["daily_trips"].sum()
avg_daily = daily_totals.mean()
peak_day_name = filtered.groupby("day_name")["daily_trips"].sum().idxmax()
median_mape = summary["MAPE"].median()

_, k1, k2, k3, k4, _ = st.columns([0.5, 2, 2, 2, 2, 0.5])
k1.metric("Total Trips", f"{total_trips / 1e6:,.1f}M")
k2.metric("Avg Daily Trips", f"{avg_daily:,.0f}")
k3.metric("Peak Day", peak_day_name)
k4.metric("Forecast MAPE", f"{median_mape:.1f}%")

# ---------------------------------------------------------------------------
# Row 1: Daily Demand Trend
# ---------------------------------------------------------------------------
st.subheader("Daily Demand Trend")

daily_ts = daily_totals.reset_index()
daily_ts.columns = ["date", "trips"]

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=daily_ts["date"], y=daily_ts["trips"],
    mode="lines", line=dict(color=BLUE, width=1.2),
    fill="tozeroy", fillcolor="rgba(37,99,235,0.08)",
    hovertemplate="%{x|%b %d, %Y}<br>%{y:,.0f} trips<extra></extra>",
))
fig_trend.update_layout(
    height=170, margin=CHART_MARGIN, font=CHART_FONT,
    hovermode="x unified", showlegend=False,
    xaxis=dict(showgrid=False),
    yaxis=dict(tickformat=",", title="", gridcolor="#F1F5F9"),
    plot_bgcolor="white",
)
st.plotly_chart(fig_trend, use_container_width=True)

# ---------------------------------------------------------------------------
# Row 2: Day of Week | Borough | Monthly Trend
# ---------------------------------------------------------------------------
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.subheader("Demand by Day of Week")

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]
    dow = (
        filtered.groupby("day_name")["daily_trips"]
        .sum().reindex(day_order).reset_index()
    )
    dow.columns = ["day", "trips"]
    dow["pct"] = dow["trips"] / dow["trips"].sum() * 100
    dow["label"] = dow["day"].str[:3]

    fig_dow = go.Figure(go.Bar(
        x=dow["trips"], y=dow["label"], orientation="h",
        text=dow["pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside", textfont=dict(size=10, color=SLATE),
        marker_color=BLUE,
    ))
    fig_dow.update_layout(
        height=210, margin=CHART_MARGIN, font=CHART_FONT,
        xaxis=dict(visible=False),
        yaxis=dict(categoryorder="array", categoryarray=dow["label"].tolist()[::-1],
                   tickfont=dict(size=10)),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig_dow, use_container_width=True)

with col_b:
    st.subheader("Demand by Borough")

    borough_trips = (
        filtered.groupby("Borough")["daily_trips"]
        .sum().sort_values(ascending=True).reset_index()
    )
    borough_trips.columns = ["borough", "trips"]
    borough_trips["pct"] = borough_trips["trips"] / borough_trips["trips"].sum() * 100

    fig_boro = go.Figure(go.Bar(
        x=borough_trips["trips"], y=borough_trips["borough"], orientation="h",
        text=borough_trips["pct"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside", textfont=dict(size=10, color=SLATE),
        marker_color=EMERALD,
    ))
    fig_boro.update_layout(
        height=210, margin=CHART_MARGIN, font=CHART_FONT,
        xaxis=dict(visible=False),
        yaxis=dict(tickfont=dict(size=10)),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig_boro, use_container_width=True)

with col_c:
    st.subheader("Monthly Trend by Year")

    monthly = (
        filtered.groupby(["year", "month"])["daily_trips"]
        .sum().reset_index()
    )
    monthly["year"] = monthly["year"].astype(str)
    year_colors = {"2022": BLUE_LIGHT, "2023": BLUE, "2024": AMBER}

    fig_monthly = go.Figure()
    for yr in sorted(monthly["year"].unique()):
        yr_data = monthly[monthly["year"] == yr]
        fig_monthly.add_trace(go.Scatter(
            x=yr_data["month"], y=yr_data["daily_trips"],
            name=yr, mode="lines+markers",
            line=dict(color=year_colors.get(yr, SLATE), width=2),
            marker=dict(size=4),
        ))
    fig_monthly.update_layout(
        height=210, margin=CHART_MARGIN, font=CHART_FONT,
        xaxis=dict(
            tickmode="array", tickvals=list(range(1, 13)),
            ticktext=["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"],
            showgrid=False,
        ),
        yaxis=dict(tickformat=",.0s", title="", gridcolor="#F1F5F9"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.5,
                    xanchor="center", font=dict(size=10)),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

# ---------------------------------------------------------------------------
# Row 3: Forecast vs Actual
# ---------------------------------------------------------------------------
st.subheader(f"Forecast vs Actual \u2014 {selected_zone}")

zone_fc = forecast[forecast["zone_name"] == selected_zone].sort_values("date")
zone_mape = summary.loc[
    summary["zone_id"] == zone_fc["zone_id"].iloc[0], "MAPE"
].values[0]

fig_fc = go.Figure()
fig_fc.add_trace(go.Scatter(
    x=zone_fc["date"], y=zone_fc["actual"],
    name="Actual", mode="lines",
    line=dict(color=BLUE, width=2),
))
fig_fc.add_trace(go.Scatter(
    x=zone_fc["date"], y=zone_fc["forecast"],
    name="Forecast", mode="lines",
    line=dict(color=AMBER, width=2, dash="dash"),
))
fig_fc.update_layout(
    height=170, margin=CHART_MARGIN, font=CHART_FONT,
    hovermode="x unified",
    xaxis=dict(showgrid=False),
    yaxis=dict(title="", tickformat=",", gridcolor="#F1F5F9"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0.5,
                xanchor="center", font=dict(size=10)),
    annotations=[dict(
        x=1, y=0, xref="paper", yref="paper", xanchor="right",
        text=f"MAPE: {zone_mape:.1f}%", showarrow=False,
        font=dict(size=11, color=SLATE),
    )],
    plot_bgcolor="white",
)
st.plotly_chart(fig_fc, use_container_width=True)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.caption(
    "Data: NYC TLC Trip Record Data (2022\u20132024)  \u2022  "
    "Forecast: XGBoost one-day-ahead model"
)
