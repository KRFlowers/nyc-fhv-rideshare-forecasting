"""Shared utility functions for the SQL Explorer app."""

import time
from datetime import date as dt_date

import duckdb
import pandas as pd
import streamlit as st

from explorer_styles import COMPANY_CODES


def build_where_clause(
    start_date: str,
    end_date: str,
    boroughs: list[str] | None = None,
    companies: list[str] | None = None,
    alias: str = "t",
    zone_alias: str = "pz",
    *,
    all_boroughs: list[str] | None = None,
) -> str:
    """Build a SQL WHERE clause string from active filter values."""
    clauses = [
        f"{alias}.pickup_datetime >= '{start_date}'",
        f"{alias}.pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY",
    ]
    if boroughs and all_boroughs and len(boroughs) < len(all_boroughs):
        quoted = ", ".join(f"'{b}'" for b in boroughs)
        clauses.append(f"{zone_alias}.Borough IN ({quoted})")
    if companies and len(companies) < 3:
        codes = [COMPANY_CODES[c] for c in companies if c in COMPANY_CODES]
        quoted = ", ".join(f"'{c}'" for c in codes)
        clauses.append(f"{alias}.hvfhs_license_num IN ({quoted})")
    return "WHERE " + "\n      AND ".join(clauses)


def execute_query(con, sql: str) -> tuple[pd.DataFrame, float]:
    """Execute SQL via DuckDB. Returns (DataFrame, elapsed_seconds)."""
    t0 = time.perf_counter()
    df = con.execute(sql).fetchdf()
    elapsed = time.perf_counter() - t0
    return df, elapsed


def format_filter_bar(
    start_date,
    end_date,
    boroughs: list[str] | None = None,
    match_count: int | None = None,
    zone_name: str | None = None,
    *,
    all_boroughs: list[str] | None = None,
) -> str:
    """Build the Filtered: caption string from date range and optional context."""
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
        if not boroughs or (all_boroughs and len(boroughs) == len(all_boroughs)):
            parts.append("All boroughs")
        else:
            parts.append(", ".join(boroughs))
    if zone_name:
        parts.append(zone_name)
    if match_count is not None:
        parts.append(f"{match_count:,} matching trips")
    return " \u00b7 ".join(parts)


@st.cache_data(ttl=600)
def get_metric_values(
    start_date: str,
    end_date: str,
    boroughs: tuple,
    companies: tuple,
    _con,
    all_boroughs: tuple,
) -> dict:
    """Query aggregated metric card values for the active filters. Cached for 10 minutes."""
    where = build_where_clause(
        start_date,
        end_date,
        list(boroughs) if boroughs else None,
        list(companies) if companies else None,
        all_boroughs=list(all_boroughs) if all_boroughs else None,
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
        "tips": st.column_config.NumberColumn(format="$%.2f"),
        "tolls": st.column_config.NumberColumn(format="$%.2f"),
        "sales_tax": st.column_config.NumberColumn(format="$%.2f"),
        "congestion_surcharge": st.column_config.NumberColumn(format="$%.2f"),
        "airport_fee": st.column_config.NumberColumn(format="$%.2f"),
        "driver_pay": st.column_config.NumberColumn(format="$%.2f"),
        "month_num": st.column_config.NumberColumn(disabled=True),
        # BCF — format + tooltip explaining the acronym
        "bcf": st.column_config.NumberColumn(
            format="$%.2f", help="Black Car Fund surcharge"
        ),
        # Numeric columns — clean formatting
        "trip_miles": st.column_config.NumberColumn(format="%.1f"),
        "trip_time": st.column_config.NumberColumn(format="%d"),
        # Tooltip for company code column — not obvious without context
        "hvfhs_license_num": st.column_config.TextColumn(
            help="HV0003 = Uber  |  HV0004 = Via  |  HV0005 = Lyft"
        ),
        # Q02 — MoM growth display labels
        "trips": st.column_config.NumberColumn("Current Month Trips"),
        "prev_month": st.column_config.NumberColumn("Prev Month Trips"),
        "trip_diff": st.column_config.NumberColumn("Trip Difference"),
        "growth_pct": st.column_config.NumberColumn("Growth %"),
    }

    # If 'month' is a date/datetime column, format as "MMM YYYY" (Q07);
    # if it's a string (Q11), leave it unformatted.
    if (
        "month" in df.columns
        and hasattr(df["month"].dtype, "kind")
        and df["month"].dtype.kind in ("M", "m")
    ):
        base_config["month"] = st.column_config.DateColumn(format="MMM YYYY")

    # Return only configs for columns present in this dataframe
    return {k: v for k, v in base_config.items() if k in df.columns}


def render_result_bar(df: pd.DataFrame, elapsed: float, total: int | None = None):
    """Render row count, timing caption, and Export CSV link below a dataframe."""
    r1, r2 = st.columns([4, 1])
    with r1:
        if total and total > len(df):
            st.markdown(
                f"""
<p style="font-size:13px; color:#374151; margin-bottom:2px;">
    Returned <strong>{len(df):,}</strong> of <strong>{total:,}</strong> rows
</p>
<p style="font-size:12px; color:#6B7280; margin-top:0;">
    DuckDB queried {total:,} records in <strong>{elapsed:.2f}s</strong>
</p>
""",
                unsafe_allow_html=True,
            )
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
