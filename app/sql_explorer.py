"""
SQL Explorer V3 

Browse and verify 684M NYC rideshare trip records.
Streamlit app powered by DuckDB, querying Parquet files directly.

Launch:  streamlit run app/v3/sql_explorer_v3.py


Author: Kristi Flowers
Date: March 2026

"""

import base64
import re
import sys
import time
from datetime import date as dt_date
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Import shared modules from parent app/ directory
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from explorer_styles import COMPANY_CODES
from explorer_queries import QUERY_REGISTRY, get_query_display_options


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SQL Explorer — NYC Rideshare",
    page_icon=":material/database:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ACCENT = "#0891B2"
SURFACE = "#F8FAFC"

# ---------------------------------------------------------------------------
# CSS — Global styles (Step 1 of 11) + horizontal layout overrides
# ---------------------------------------------------------------------------
def inject_global_css():
    st.markdown("""
    <style>

    /* ── Hide Streamlit default chrome ── */
    #MainMenu        { visibility: hidden; }
    footer           { visibility: hidden; }
    header           { visibility: hidden; }
    [data-testid="stAppViewContainer"] {
        padding-top: 0 !important;
    }

    /* ── Page background ── */
    body, .stApp {
        background-color: #F9FAFB;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    /* ── Block container padding ── */
    .block-container {
        background-color: #FFFFFF;
        padding-top:    0rem;
        padding-bottom: 1rem;
        padding-left:   2rem;
        padding-right:  2rem;
        max-width:      100%;
    }

    /* ── Tab bar ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 2px solid #E5E7EB;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-size:   13px;
        font-weight: 500;
        padding:     10px 18px;
        color:       #6B7280;
        background:  transparent;
        border:      none;
    }
    .stTabs [aria-selected="true"] {
        color:         __ACCENT__ !important;
        border-bottom: 2px solid __ACCENT__ !important;
        background:    transparent;
    }

    /* ── Expander label ── */
    .streamlit-expanderHeader {
        font-size:      12px;
        color:          #6B7280;
        font-weight:    500;
        letter-spacing: 0.02em;
    }

    /* ── Selectbox input text ── */
    .stSelectbox > div {
        font-size: 13px;
    }

    /* ── Primary button (Run Query, Export CSV) ── */
    .stButton > button {
        background:    __ACCENT__;
        color:         white;
        border:        none;
        border-radius: 6px;
        font-size:     13px;
        font-weight:   500;
        padding:       6px 16px;
    }
    .stButton > button:hover {
        background: #0F766E;
    }
    .stButton > button[kind="secondary"] {
        background:    transparent !important;
        color:         #9CA3AF !important;
        border:        none !important;
        font-size:     11px !important;
        font-weight:   400 !important;
        padding:       4px 8px !important;
    }
    .stButton > button[kind="secondary"]:hover {
        color:         #374151 !important;
        background:    transparent !important;
    }

    /* ── Radio label text ── */

    [data-testid="stRadio"] p {
        font-size: 13px !important;
        color: #374151 !important;
    }

    /* ── Hide sidebar entirely ── */
    section[data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }

    /* ── Section 1: Header bar (dark) ── */
    .v3-header-bar {
        background: __SURFACE__;
        margin: -0.5rem -2rem 0 -2rem;
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }
    .v3-title {
        color: #0891B2 !important;
        font-size: 26px !important;        /* was 22px */
        font-weight: 700 !important;
        margin: 0 !important;
        line-height: 1.5 !important;
    }
    .v3-subtitle {
        color: #1E293B !important;
        font-size: 17px !important;
        font-weight: 400 !important;
        margin: 0 !important;
        line-height: 1.5 !important;
    }
    .v3-info {
        color: #1E293B !important;
        font-size: 11px !important;
        font-weight: 400 !important;
        text-align: left; !important;
        margin: 0; !important;
        line-height: 1.7 !important;
        font-style: italic !important;
    }

    /* ── Section 2: Filter bar (white strip) ── */
    .v3-filter-bar {
        background: #FFFFFF;
        margin: 0 -2rem;
        padding: 16px 2rem 0 2rem;
        border-bottom: none;
    }
    .v3-filter-label {
        font-size: 10px;
        font-weight: 600;
        color: #9CA3AF;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 0;
    }

    /* Style the st.container that holds filter widgets */
    .v3-filter-bar + div > [data-testid="stVerticalBlock"] {
        background: #FFFFFF;
        margin: 0 -2rem;
        padding: 0 2rem 16px 2rem;
        border-bottom: 1px solid #E5E7EB;
    }

    /* ── Section 3: Data area (gray bg, breathing room) ── */
    .v3-data-area {
        padding-top: 1.5rem;
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: __SURFACE__;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 0.3rem 0.5rem;
        text-align: center;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.05rem;
        font-weight: 400;
        color: #1E293B;
        justify-content: center;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.6rem;
        color: #94A3B8;
        justify-content: center;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ── SQL code blocks ── */
    .stCodeBlock {
        border: 1px solid #E5E7EB;
        border-radius: 6px;
    }

    /* ── Compact selectbox height ── */
    .stSelectbox > div[data-baseweb="select"] {
        min-height: 36px;
    }

    /* ── Selectbox font size ── */
    .stSelectbox [data-baseweb="select"] span {
        font-size: 13px;
        color: #374151;
    }

    /* ── Dividers ── */
    hr {
        margin-top:    0.5rem;
        margin-bottom: 0.5rem;
        border-color:  #E5E7EB;
    }
                          

    /* ── Compact label text above each filter ── */
    .stSelectbox label,
    .stDateInput label {
        font-size:      11px;
        font-weight:    600;
        color:          #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* ── Filter dropdowns — light gray fill ── */
    [data-testid="stSelectbox"] > div > div {
        background-color: __SURFACE__ !important;
        border: 1px solid #E2E8F0 !important;
    }

    /* ── Date input — light gray fill ── */
    [data-testid="stDateInput"] input {
        background-color: __SURFACE__ !important;
        border: 1px solid #E2E8F0 !important;
    }


    </style>
    """.replace("__ACCENT__", ACCENT).replace("__SURFACE__", SURFACE), unsafe_allow_html=True)


inject_global_css()


# ---------------------------------------------------------------------------
# Data paths (app/v3/ -> app/ -> project root -> data/raw)
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PARQUET_PATH = DATA_DIR / "combined_fhvhv_tripdata.parquet"
ZONES_PATH = DATA_DIR / "zone_metadata.csv"


# ---------------------------------------------------------------------------
# Startup: file checks
# ---------------------------------------------------------------------------
def check_data_files() -> bool:
    missing = []
    if not PARQUET_PATH.exists():
        missing.append(str(PARQUET_PATH))
    if not ZONES_PATH.exists():
        missing.append(str(ZONES_PATH))
    if missing:
        st.error(
            "**Required data files not found:**\n\n"
            + "\n".join(f"- `{f}`" for f in missing)
            + "\n\nRun `00_data_download.ipynb` to download the data first."
        )
        return False
    return True


if not check_data_files():
    st.stop()


# ---------------------------------------------------------------------------
# DuckDB connection
# ---------------------------------------------------------------------------
@st.cache_resource
def init_duckdb() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("SET threads=6")
    con.execute("SET preserve_insertion_order=false")
    con.execute("SET enable_progress_bar=false")
    con.execute(
        f"CREATE OR REPLACE VIEW trips AS "
        f"SELECT * FROM read_parquet('{PARQUET_PATH.as_posix()}')"
    )
    con.execute(
        f"CREATE OR REPLACE VIEW zones AS "
        f"SELECT * FROM read_csv_auto('{ZONES_PATH.as_posix()}')"
    )
    return con


con = init_duckdb()


# ---------------------------------------------------------------------------
# Dataset info (cached)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def get_dataset_info() -> dict:
    _con = init_duckdb()
    row = _con.execute(
        "SELECT COUNT(*) AS row_count, "
        "MIN(pickup_datetime) AS min_date, "
        "MAX(pickup_datetime) AS max_date "
        "FROM trips"
    ).fetchone()
    zone_count = _con.execute("SELECT COUNT(*) FROM zones").fetchone()[0]
    borough_list = (
        _con.execute(
            "SELECT DISTINCT Borough FROM zones WHERE Borough IS NOT NULL ORDER BY Borough"
        ).fetchdf()["Borough"].tolist()
    )
    file_size_gb = PARQUET_PATH.stat().st_size / (1024**3)
    return {
        "row_count": row[0],
        "min_date": pd.Timestamp(row[1]).date(),
        "max_date": pd.Timestamp(row[2]).date(),
        "zone_count": zone_count,
        "file_size_gb": round(file_size_gb, 1),
        "boroughs": sorted(borough_list),
    }


dataset_info = get_dataset_info()


# ---------------------------------------------------------------------------
# Header (horizontal layout)
# ---------------------------------------------------------------------------
def render_header(info: dict):
    """Render the dark header bar with title and dataset stats."""
    _min = info["min_date"].strftime("%b %Y")
    _max = info["max_date"].strftime("%b %Y")
    st.markdown(
        '<div class="v3-header-bar">'
        '<div>'
        '<p class="v3-title">SQL Explorer</p>'
        '<p class="v3-subtitle">Browse, filter, and query NYC rideshare trip data</p>'        
        f'<p class="v3-info">'
        f'<strong>{info["row_count"] / 1e6:.0f}M rows</strong> &middot; '
        f'{info["zone_count"]} zones &middot; {info["file_size_gb"]:.1f} GB '
        f'&middot; {_min} &ndash; {_max}</p>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _reset_date_range():
    """Callback to reset date range before widget re-renders."""
    st.session_state["date_range_input"] = (
        st.session_state["_date_min"],
        st.session_state["_date_max"],
    )


def render_filters(info: dict) -> dict:
    """Render the filter toolbar and return filter values."""
    # Store min/max in session state for the reset callback
    st.session_state["_date_min"] = info["min_date"]
    st.session_state["_date_max"] = info["max_date"]

    # Initialize date range on first load only
    if "date_range_input" not in st.session_state:
        st.session_state["date_range_input"] = (info["min_date"], info["max_date"])

    # ── White filter bar ──────────────────────────────────────────────
    st.markdown('<div class="v3-filter-bar"><p class="v3-filter-label">Filters</p></div>', unsafe_allow_html=True)

    filter_container = st.container()
    with filter_container:
        col1, col2, col3, col4, col_reset, _ = st.columns([1.8, 1.2, 1.2, 1.2, 0.8, 2.2])

        with col1:
            st.markdown("<p style='font-size:10px; font-weight:600; color:#9CA3AF; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:4px;'>Date Range</p>", unsafe_allow_html=True)
            date_range = st.date_input(
                "Date Range",
                min_value=info["min_date"],
                max_value=info["max_date"],
                label_visibility="collapsed",
                key="date_range_input",
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date = end_date = info["min_date"]

        with col_reset:
            st.markdown("<p style='font-size:10px; margin-bottom:4px;'>&nbsp;</p>", unsafe_allow_html=True)
            st.button("Reset", key="reset_dates", type="secondary", on_click=_reset_date_range)

        with col2:
            st.markdown("<p style='font-size:10px; font-weight:600; color:#9CA3AF; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:4px;'>Borough</p>", unsafe_allow_html=True)
            borough_options = ["All boroughs"] + info["boroughs"]
            selected_borough = st.selectbox(
                "Borough",
                options=borough_options,
                index=0,
                label_visibility="collapsed",
                key="borough_filter",
            )

        with col3:
            st.markdown("<p style='font-size:10px; font-weight:600; color:#9CA3AF; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:4px;'>Company</p>", unsafe_allow_html=True)
            company_options = [
                "All companies", "Uber (HV0003)", "Lyft (HV0005)", "Via (HV0004)",
            ]
            selected_company = st.selectbox(
                "Company",
                options=company_options,
                index=0,
                label_visibility="collapsed",
                key="company_filter",
            )

        with col4:
            st.markdown(f"<p style='font-size:10px; font-weight:600; color:{ACCENT}; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:4px;'>Sort</p>", unsafe_allow_html=True)
            sort_options = [
                "pickup_datetime", "trip_miles", "trip_time",
                "base_passenger_fare", "tips", "driver_pay",
            ]
            selected_sort = st.selectbox(
                "Sort by",
                options=sort_options,
                index=0,
                label_visibility="collapsed",
                key="sort_col",
            )

    # Close filter section with bottom border, open data area with breathing room
    st.markdown('<div class="v3-data-area"></div>', unsafe_allow_html=True)

    # Convert selectbox values to filter lists for query logic
    if selected_borough == "All boroughs":
        boroughs = info["boroughs"]
    else:
        boroughs = [selected_borough]

    _company_map = {
        "All companies": None,
        "Uber (HV0003)": "Uber",
        "Lyft (HV0005)": "Lyft",
        "Via (HV0004)": "Via",
    }
    _company_name = _company_map[selected_company]
    if _company_name:
        companies = [_company_name]
    else:
        companies = ["Uber", "Lyft", "Via"]

    return {
        "start_date": start_date,
        "end_date": end_date,
        "boroughs": boroughs,
        "companies": companies,
        "sort_col": selected_sort,
    }


render_header(dataset_info)


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------
def build_where_clause(
    start_date: str,
    end_date: str,
    boroughs: list[str] | None = None,
    companies: list[str] | None = None,
    alias: str = "t",
    zone_alias: str = "pz",
) -> str:
    clauses = [
        f"{alias}.pickup_datetime >= '{start_date}'",
        f"{alias}.pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY",
    ]
    if boroughs and len(boroughs) < len(dataset_info["boroughs"]):
        quoted = ", ".join(f"'{b}'" for b in boroughs)
        clauses.append(f"{zone_alias}.Borough IN ({quoted})")
    if companies and len(companies) < 3:
        codes = [COMPANY_CODES[c] for c in companies if c in COMPANY_CODES]
        quoted = ", ".join(f"'{c}'" for c in codes)
        clauses.append(f"{alias}.hvfhs_license_num IN ({quoted})")
    return "WHERE " + "\n      AND ".join(clauses)


def execute_query(sql: str) -> tuple[pd.DataFrame, float]:
    """Execute SQL via DuckDB. Returns (DataFrame, elapsed_seconds)."""
    t0 = time.perf_counter()
    df = con.execute(sql).fetchdf()
    elapsed = time.perf_counter() - t0
    return df, elapsed


def format_filter_context(
    start_date,
    end_date,
    boroughs: list[str] | None = None,
    match_count: int | None = None,
    zone_name: str | None = None,
) -> str:
    if isinstance(start_date, dt_date):
        s = start_date.strftime("%b %d, %Y")
    else:
        s = str(start_date)
    if isinstance(end_date, dt_date):
        e = end_date.strftime("%b %d, %Y")
    else:
        e = str(end_date)

    parts = [f"Filtered: {s} \u2013 {e}"]
    if boroughs is not None:
        if not boroughs or len(boroughs) == len(dataset_info["boroughs"]):
            parts.append("All boroughs")
        else:
            parts.append(", ".join(boroughs))
    if zone_name:
        parts.append(zone_name)
    if match_count is not None:
        parts.append(f"{match_count:,} matching trips")
    return " \u00b7 ".join(parts)


# ---------------------------------------------------------------------------
# Browse metrics (cached)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=600)
def get_browse_metrics(
    start_date: str, end_date: str,
    boroughs: tuple, companies: tuple,
) -> dict:
    _con = init_duckdb()
    where = build_where_clause(
        start_date, end_date,
        list(boroughs) if boroughs else None,
        list(companies) if companies else None,
    )
    sql = f"""
    SELECT COUNT(*) AS trip_count,
           ROUND(AVG(t.base_passenger_fare), 2) AS avg_fare,
           ROUND(AVG(t.trip_miles), 1) AS avg_miles,
           ROUND(AVG(t.trip_time / 60.0), 0) AS avg_duration_min,
           ROUND(AVG(t.tips), 2) AS avg_tips,
           COUNT(DISTINCT t.PULocationID) AS zones_active
    FROM trips t
    JOIN zones pz ON t.PULocationID = pz.zone_id
    {where}
    """
    row = _con.execute(sql).fetchone()
    return {
        "trip_count": row[0],
        "avg_fare": row[1],
        "avg_miles": row[2],
        "avg_duration_min": row[3],
        "avg_tips": row[4],
        "zones_active": row[5],
        "sql": sql.strip(),
    }


# ---------------------------------------------------------------------------
# Table formatting helper
# ---------------------------------------------------------------------------
def build_column_config(df) -> dict:
    """
    Build a column_config dict for st.dataframe().
    Applies number formatting only — raw column names are preserved.
    Tooltips added for ambiguous code fields only.
    Only configures columns that are present in the dataframe.
    """
    base_config = {
        # Currency columns — format only, no rename
        "base_passenger_fare": st.column_config.NumberColumn(format="$%.2f"),
        "tips":                st.column_config.NumberColumn(format="$%.2f"),
        "tolls":               st.column_config.NumberColumn(format="$%.2f"),
        "sales_tax":           st.column_config.NumberColumn(format="$%.2f"),
        "congestion_surcharge":st.column_config.NumberColumn(format="$%.2f"),
        "airport_fee":         st.column_config.NumberColumn(format="$%.2f"),
        "driver_pay":          st.column_config.NumberColumn(format="$%.2f"),
        "month_num": st.column_config.NumberColumn(disabled=True),


        # BCF — format + tooltip explaining the acronym
        "bcf": st.column_config.NumberColumn(
            format="$%.2f",
            help="Black Car Fund surcharge"
        ),

        # Numeric columns — clean formatting
        "trip_miles": st.column_config.NumberColumn(format="%.1f"),
        "trip_time":  st.column_config.NumberColumn(format="%d"),

        # Tooltip for company code column — not obvious without context
        "hvfhs_license_num": st.column_config.TextColumn(
            help="HV0003 = Uber  |  HV0004 = Via  |  HV0005 = Lyft"
        ),
    }

    # If 'month' is a date/datetime column, format as "MMM YYYY" (Q07);
    # if it's a string (Q11), leave it unformatted.
    if "month" in df.columns and hasattr(df["month"].dtype, "kind") and df["month"].dtype.kind in ("M", "m"):
        base_config["month"] = st.column_config.DateColumn(format="MMM YYYY")

    # Return only configs for columns present in this dataframe
    return {k: v for k, v in base_config.items() if k in df.columns}


def result_bar(df: pd.DataFrame, elapsed: float, total: int | None = None):
    """Render the result count + timing caption and export button."""
    r1, r2 = st.columns([4, 1])
    with r1:
        if total and total > len(df):
            st.markdown(f"""
<p style="font-size:13px; color:#374151; margin-bottom:2px;">
    Returned <strong>{len(df):,}</strong> of <strong>{total:,}</strong> rows
</p>
<p style="font-size:12px; color:#6B7280; margin-top:0;">
    DuckDB queried {total:,} records in <strong>{elapsed:.2f}s</strong>
</p>
""", unsafe_allow_html=True)
        else:
            st.caption(f"{len(df):,} rows returned in {elapsed:.1f}s")
    with r2:
        st.download_button(
            "Export CSV",
            df.to_csv(index=False),
            file_name="results.csv",
            mime="text/csv",
            key=f"export_{id(df)}",
        )


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_browse, tab_prebuilt, tab_custom = st.tabs(
    ["Browse & Filter", "Pre-Built Queries", "Custom SQL"]
)


# ---- Browse & Filter Tab ----
with tab_browse:
    # Filter toolbar (only on this tab) — outside try so filters is always defined
    filters = render_filters(dataset_info)

    try:
        # Compute summary metrics
        with st.spinner("Computing summary statistics..."):
            metrics = get_browse_metrics(
                str(filters["start_date"]),
                str(filters["end_date"]),
                tuple(sorted(filters["boroughs"])),
                tuple(sorted(filters["companies"])),
            )

        # Filter context line
        st.caption(
            format_filter_context(
                filters["start_date"],
                filters["end_date"],
                filters["boroughs"],
                match_count=metrics["trip_count"],
            )
        )

        # 6 KPI metric cards
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Matching Trips", f"{metrics['trip_count'] / 1e6:,.1f}M")
        k2.metric("Avg Fare", f"${metrics['avg_fare']:,.2f}")
        k3.metric("Avg Miles", f"{metrics['avg_miles']:.1f}")
        k4.metric(
            "Avg Duration",
            f"{int(metrics['avg_duration_min'])} min"
            if metrics["avg_duration_min"]
            else "\u2014",
        )
        k5.metric("Avg Tips", f"${metrics['avg_tips']:,.2f}")
        k6.metric("Zone Count", f"{metrics['zones_active']}")

        sort_col = filters["sort_col"]

        # Build sample records query
        where = build_where_clause(
            str(filters["start_date"]),
            str(filters["end_date"]),
            filters["boroughs"],
            filters["companies"],
        )
        sample_sql = f"""
SELECT t.*, pz.Zone AS pickup_zone, pz.Borough AS pickup_borough
FROM trips t
JOIN zones pz ON t.PULocationID = pz.zone_id
{where}
ORDER BY t.{sort_col} ASC
LIMIT 1000
""".strip()

        with st.spinner(f"Sorting {metrics['trip_count']:,} trips by {sort_col}..."):
            df_browse, elapsed_browse = execute_query(sample_sql)

        # Export CSV inline link + timing
        if not df_browse.empty:
            csv_data = df_browse.to_csv(index=False)
            b64 = base64.b64encode(csv_data.encode()).decode()
            st.markdown(
                f'<a href="data:file/csv;base64,{b64}" download="browse_results.csv" '
                f'style="font-size:13px; color:{ACCENT}; text-decoration:none; '
                f'float:right; margin-top:4px; margin-bottom:8px;">↓ Export CSV</a>',
                unsafe_allow_html=True,
            )

        # Formatted table
        st.dataframe(
            df_browse,
            use_container_width=True,
            hide_index=True,
            height=340,
            column_config=build_column_config(df_browse),
            column_order=[
                "pickup_datetime", "pickup_borough", "pickup_zone",
                "hvfhs_license_num", "trip_miles", "trip_time",
                "base_passenger_fare", "tips", "driver_pay",
            ],
        )

        st.caption(
            f"Showing {len(df_browse):,} of {metrics['trip_count']:,} rows "
            f"· queried in {elapsed_browse:.1f}s"
        )

        # View SQL expanders
        with st.expander("View SQL \u2014 Summary Statistics"):
            st.code(metrics["sql"], language="sql")
        with st.expander("View SQL \u2014 Sample Records"):
            st.code(sample_sql, language="sql")

    except Exception as e:
        st.error(f"Query error: {e}")

# ---- Pre-Built Queries Tab ----
with tab_prebuilt:

    _query_labels = get_query_display_options()
    _label_to_idx = {label: i for i, label in enumerate(_query_labels)}

    col_select, col_results = st.columns([1.0, 3.0])

    with col_select:
        st.markdown("<div style='margin-top:-12px'></div>", unsafe_allow_html=True)
        st.caption(
            format_filter_context(
                filters["start_date"],
                filters["end_date"],
            )
        )
        selected_option = st.radio(
            "query", _query_labels, index=None,
            label_visibility="collapsed", key="q_selected",
        )

    with col_results:
        if selected_option is None:
            st.markdown("""
<div style="
    color:       #9CA3AF;
    font-size:   14px;
    margin-top:  80px;
    text-align:  center;
">
    ← Select a query to view results
</div>
""", unsafe_allow_html=True)
        else:
            qdef = QUERY_REGISTRY[_label_to_idx[selected_option]]

            # Inline zone dropdown for zone-specific queries
            zone_id = None
            zone_name = None
            if qdef.needs_zone:
                zone_df = con.execute(
                    "SELECT zone_id, Zone, Borough FROM zones ORDER BY Zone"
                ).fetchdf()
                zone_options = [
                    f"{row['Zone']} ({row['zone_id']})"
                    for _, row in zone_df.iterrows()
                ]
                zone_selection = st.selectbox(
                    "Zone", zone_options, key="inline_zone"
                )
                zone_id = int(zone_selection.split("(")[-1].rstrip(")"))
                zone_name = zone_selection.split(" (")[0]

            # Q02 date range warning
            if selected_option.startswith("Q02"):
                days_span = (filters["end_date"] - filters["start_date"]).days
                if days_span < 60:
                    st.warning("This query works best with a date range of 60 days or more.")

            # Build and execute query
            try:
                kwargs = {}
                if zone_id is not None:
                    kwargs["zone_id"] = zone_id
                sql = qdef.build_sql(
                    str(filters["start_date"]),
                    str(filters["end_date"]),
                    **kwargs,
                )

                with st.spinner("Running query..."):
                    df_pb, elapsed_pb = execute_query(sql)

                if df_pb.empty:
                    st.info("No results for the current filters.")
                else:
                    # Export CSV — inline link above dataframe
                    csv_data = df_pb.to_csv(index=False)
                    b64 = base64.b64encode(csv_data.encode()).decode()
                    st.markdown(
                        f'<a href="data:file/csv;base64,{b64}" download="query_results.csv" '
                        f'style="font-size:13px; color:#0891B2; text-decoration:none; '
                        f'float:right; margin-right:1in; margin-top:4px; margin-bottom:8px;">↓ Export CSV</a>',
                        unsafe_allow_html=True,
                    )

                    df_kwargs = dict(
                        data=df_pb,
                        use_container_width=True,
                        hide_index=True,
                        height=380,
                        column_config=build_column_config(df_pb),
                    )
                    _column_orders = {
                        "Q04": ["Borough", "rank", "hour", "trips"],
                        "Q05": ["Zone", "Borough", "rank", "total_trips"],
                        "Q07": ["Zone", "Borough", "rank", "month", "trips"],
                        "Q08": ["pickup_zone", "dropoff_zone", "pickup_borough", "dropoff_borough", "rank", "total_trips"],
                    }
                    q_key = selected_option[:3]
                    if q_key in _column_orders:
                        df_kwargs["column_order"] = _column_orders[q_key]
                    elif "month_num" in df_pb.columns:
                        df_kwargs["column_order"] = [c for c in df_pb.columns if c != "month_num"]
                    st.dataframe(**df_kwargs)

                    st.caption(f"{len(df_pb):,} rows returned in {elapsed_pb:.1f}s")

                # View SQL expander
                with st.expander("View SQL"):
                    st.code(sql, language="sql")

            except Exception as e:
                st.error(f"Query error: {e}")

# ---- Custom SQL Tab ----
with tab_custom:
    user_sql = st.text_area(
        "SQL Query",
        height=150,
        placeholder="SELECT * FROM trips LIMIT 100",
        key="custom_sql",
    )

    if st.button("Run Query", type="primary"):
        if not user_sql.strip():
            st.warning("Enter a SQL query to run.")
        else:
            sql_to_run = user_sql.strip().rstrip(";")
            auto_limited = False
            if not re.search(r"\bLIMIT\b", sql_to_run, re.IGNORECASE):
                sql_to_run += "\nLIMIT 10000"
                auto_limited = True

            try:
                placeholder = st.empty()
                placeholder.info("Preparing query...")
                with st.spinner("Running custom query..."):
                    df_custom, elapsed_custom = execute_query(sql_to_run)
                placeholder.empty()

                if auto_limited:
                    st.caption("Auto-applied LIMIT 10,000 for safety.")

                if df_custom.empty:
                    st.info("Query returned no results.")
                else:
                    result_bar(df_custom, elapsed_custom)
                    st.dataframe(
                        df_custom,
                        use_container_width=True,
                        hide_index=True,
                        height=320,
                        column_config=build_column_config(df_custom),
                    )

                # Query Explain pane
                with st.expander("Query Execution Plan"):
                    try:
                        explain_sql = f"EXPLAIN {sql_to_run}"
                        plan_df = con.execute(explain_sql).fetchdf()
                        plan_text = "\n".join(plan_df.iloc[:, 0].tolist())
                        st.code(plan_text, language="text")
                    except Exception as ex:
                        st.warning(f"Could not generate execution plan: {ex}")

            except Exception as e:
                st.error(f"SQL error: {e}")

    with st.expander("Sample Queries"):
        st.markdown("""
**Trip count by borough:**
```sql
SELECT pz.Borough, COUNT(*) AS trips
FROM trips t
JOIN zones pz ON t.PULocationID = pz.zone_id
GROUP BY pz.Borough
ORDER BY trips DESC
```

**Average fare for a specific zone:**
```sql
SELECT pz.Zone, ROUND(AVG(t.base_passenger_fare), 2) AS avg_fare,
       COUNT(*) AS trips
FROM trips t
JOIN zones pz ON t.PULocationID = pz.zone_id
WHERE pz.Zone = 'East Village'
GROUP BY pz.Zone
```

**Trips per hour for a date range:**
```sql
SELECT EXTRACT(HOUR FROM pickup_datetime) AS hour,
       COUNT(*) AS trips
FROM trips
WHERE pickup_datetime >= '2024-01-01'
  AND pickup_datetime < '2024-02-01'
GROUP BY hour
ORDER BY hour
```

**Available tables:** `trips` (684M rows), `zones` (265 rows)
        """)
