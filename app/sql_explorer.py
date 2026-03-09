"""
SQL Explorer V3

Browse and verify 684M NYC rideshare trip records.
Streamlit app powered by DuckDB, querying Parquet files directly.

Launch:  streamlit run app/v3/sql_explorer_v3.py


Author: Kristi Flowers
Date: March 2026

"""

import sys
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Import shared modules from parent app/ directory
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from explorer_styles import ACCENT, inject_global_css
from explorer_tabs import render_browse_tab, render_prebuilt_tab, render_custom_tab

# ---------------------------------------------------------------------------
# Data paths (app/v3/ -> app/ -> project root -> data/raw)
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
PARQUET_PATH = DATA_DIR / "combined_fhvhv_tripdata.parquet"
ZONES_PATH = DATA_DIR / "zone_metadata.csv"


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SQL Explorer — NYC Rideshare",
    page_icon=":material/database:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_global_css()


# ---------------------------------------------------------------------------
# Startup: file checks
# ---------------------------------------------------------------------------
def check_data_files() -> bool:
    """Check that required Parquet and CSV data files exist on disk."""
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
    """Initialize DuckDB connection, set performance options, and create virtual views."""
    con = duckdb.connect()
    con.execute("SET threads=6")
    con.execute("SET preserve_insertion_order=false")
    con.execute("SET enable_progress_bar=false")
    # Create virtual views — trips and zones are referenced by all queries
    # throughout the app. Data stays in files on disk — DuckDB reads directly.
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
    """Query DuckDB for dataset summary stats. Cached for 1 hour."""
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
        )
        .fetchdf()["Borough"]
        .tolist()
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
        "<div>"
        '<p class="v3-title">SQL Explorer</p>'
        '<p class="v3-subtitle">Browse, filter, and query NYC rideshare trip data</p>'
        f'<p class="v3-info">'
        f"<strong>{info['row_count'] / 1e6:.0f}M rows</strong> &middot; "
        f"{info['zone_count']} zones &middot; {info['file_size_gb']:.1f} GB "
        f"&middot; {_min} &ndash; {_max} &middot; Raw unfiltered data</p>"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def _reset_date_range():
    """Callback to reset date range to dataset min/max before widget re-renders."""
    st.session_state["date_range_input"] = (
        st.session_state["_date_min"],
        st.session_state["_date_max"],
    )


def render_filters(info: dict) -> dict:
    """Render the filter toolbar and return active filter values as a dict."""
    # Store min/max in session state for the reset callback
    st.session_state["_date_min"] = info["min_date"]
    st.session_state["_date_max"] = info["max_date"]

    # Initialize date range on first load only
    if "date_range_input" not in st.session_state:
        st.session_state["date_range_input"] = (info["min_date"], info["max_date"])

    # ── White filter bar ──────────────────────────────────────────────
    st.markdown(
        '<div class="v3-filter-bar"><p class="v3-filter-label">Filters</p></div>',
        unsafe_allow_html=True,
    )

    filter_container = st.container()
    with filter_container:
        col1, col2, col3, col4, col_reset, _ = st.columns(
            [1.8, 1.2, 1.2, 1.2, 0.8, 2.2]
        )

        with col1:
            st.markdown(
                "<p style='font-size:10px; font-weight:600; color:#9CA3AF; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:4px;'>Date Range</p>",
                unsafe_allow_html=True,
            )
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
            st.markdown(
                "<p style='font-size:10px; margin-bottom:4px;'>&nbsp;</p>",
                unsafe_allow_html=True,
            )
            st.button(
                "Reset", key="reset_dates", type="secondary", on_click=_reset_date_range
            )

        with col2:
            st.markdown(
                "<p style='font-size:10px; font-weight:600; color:#9CA3AF; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:4px;'>Borough</p>",
                unsafe_allow_html=True,
            )
            borough_options = ["All boroughs"] + info["boroughs"]
            selected_borough = st.selectbox(
                "Borough",
                options=borough_options,
                index=0,
                label_visibility="collapsed",
                key="borough_filter",
            )

        with col3:
            st.markdown(
                "<p style='font-size:10px; font-weight:600; color:#9CA3AF; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:4px;'>Company</p>",
                unsafe_allow_html=True,
            )
            company_options = [
                "All companies",
                "Uber (HV0003)",
                "Lyft (HV0005)",
                "Via (HV0004)",
            ]
            selected_company = st.selectbox(
                "Company",
                options=company_options,
                index=0,
                label_visibility="collapsed",
                key="company_filter",
            )

        with col4:
            st.markdown(
                f"<p style='font-size:10px; font-weight:600; color:{ACCENT}; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:4px;'>Sort</p>",
                unsafe_allow_html=True,
            )
            sort_options = [
                "pickup_datetime",
                "trip_miles",
                "trip_time",
                "base_passenger_fare",
                "tips",
                "driver_pay",
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
# Main — app entry point
# All functions are defined above. Execution begins here on every page load.
# ---------------------------------------------------------------------------
tab_browse, tab_prebuilt, tab_custom = st.tabs(
    ["Browse & Filter", "Pre-Built Queries", "Custom SQL"]
)


# ---- Browse & Filter Tab ----
with tab_browse:
    filters = render_filters(dataset_info)
    render_browse_tab(filters, con, dataset_info)

# ---- Pre-Built Queries Tab ----
with tab_prebuilt:
    render_prebuilt_tab(filters, con, dataset_info)

# ---- Custom SQL Tab ----
with tab_custom:
    render_custom_tab(con)
