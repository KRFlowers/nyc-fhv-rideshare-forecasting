"""Tab rendering functions for the SQL Explorer app."""

import base64
import re

import streamlit as st

from explorer_queries import QUERY_REGISTRY, get_query_display_options
from explorer_styles import ACCENT
from explorer_utils import (
    build_column_config,
    build_where_clause,
    execute_query,
    format_filter_bar,
    get_metric_values,
    render_result_bar,
)


def render_browse_tab(filters, con, dataset_info):
    """Render the Browse & Filter tab content."""
    all_boroughs = dataset_info["boroughs"]

    try:
        # Compute summary metrics
        with st.spinner("Computing summary statistics..."):
            metrics = get_metric_values(
                str(filters["start_date"]),
                str(filters["end_date"]),
                tuple(sorted(filters["boroughs"])),
                tuple(sorted(filters["companies"])),
                con,
                tuple(sorted(all_boroughs)),
            )

        # Filter context line
        st.caption(
            format_filter_bar(
                filters["start_date"],
                filters["end_date"],
                filters["boroughs"],
                match_count=metrics["trip_count"],
                all_boroughs=all_boroughs,
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
            all_boroughs=all_boroughs,
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
            df_browse, elapsed_browse = execute_query(con, sample_sql)

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
                "pickup_datetime",
                "pickup_borough",
                "pickup_zone",
                "hvfhs_license_num",
                "trip_miles",
                "trip_time",
                "base_passenger_fare",
                "tips",
                "driver_pay",
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


def render_prebuilt_tab(filters, con, dataset_info):
    """Render the Pre-Built Queries tab content."""
    all_boroughs = dataset_info["boroughs"]

    _query_labels = get_query_display_options()
    _label_to_idx = {label: i for i, label in enumerate(_query_labels)}

    col_select, col_results = st.columns([1.0, 3.0])

    with col_select:
        st.markdown("<div style='margin-top:-12px'></div>", unsafe_allow_html=True)
        try:
            _pb_metrics = get_metric_values(
                str(filters["start_date"]),
                str(filters["end_date"]),
                tuple(sorted(filters["boroughs"])),
                tuple(sorted(filters["companies"])),
                con,
                tuple(sorted(all_boroughs)),
            )
            _match_count = _pb_metrics["trip_count"]
        except Exception:
            _match_count = None
        st.caption(
            format_filter_bar(
                filters["start_date"],
                filters["end_date"],
                match_count=_match_count,
                all_boroughs=all_boroughs,
            )
        )
        selected_option = st.radio(
            "query",
            _query_labels,
            index=None,
            label_visibility="collapsed",
            key="q_selected",
        )

    with col_results:
        if selected_option is None:
            st.markdown(
                """
<div style="
    color:       #9CA3AF;
    font-size:   14px;
    margin-top:  80px;
    text-align:  center;
">
    ← Select a query to view results
</div>
""",
                unsafe_allow_html=True,
            )
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
                    f"{row['Zone']} ({row['zone_id']})" for _, row in zone_df.iterrows()
                ]
                zone_selection = st.selectbox("Zone", zone_options, key="inline_zone")
                zone_id = int(zone_selection.split("(")[-1].rstrip(")"))
                zone_name = zone_selection.split(" (")[0]

            # Q02 date range warning
            if selected_option.startswith("Q02"):
                days_span = (filters["end_date"] - filters["start_date"]).days
                if days_span < 60:
                    st.warning(
                        "This query works best with a date range of 60 days or more."
                    )

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
                    df_pb, elapsed_pb = execute_query(con, sql)

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

                    df_kwargs = {
                        "data": df_pb,
                        "use_container_width": True,
                        "hide_index": True,
                        "height": 380,
                        "column_config": build_column_config(df_pb),
                    }
                    _column_orders = {
                        "Q04": ["Borough", "rank", "hour", "trips"],
                        "Q05": ["Zone", "Borough", "rank", "total_trips"],
                        "Q07": ["Zone", "Borough", "rank", "month", "trips"],
                        "Q08": [
                            "pickup_zone",
                            "dropoff_zone",
                            "pickup_borough",
                            "dropoff_borough",
                            "rank",
                            "total_trips",
                        ],
                    }
                    q_key = selected_option[:3]
                    if q_key in _column_orders:
                        df_kwargs["column_order"] = _column_orders[q_key]
                    elif "month_num" in df_pb.columns:
                        df_kwargs["column_order"] = [
                            c for c in df_pb.columns if c != "month_num"
                        ]
                    st.dataframe(**df_kwargs)

                    st.caption(f"{len(df_pb):,} rows returned in {elapsed_pb:.1f}s")

                # View SQL expander
                with st.expander("View SQL"):
                    st.code(sql, language="sql")

            except Exception as e:
                st.error(f"Query error: {e}")


def render_custom_tab(con):
    """Render the Custom SQL tab content."""
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
                    df_custom, elapsed_custom = execute_query(con, sql_to_run)
                placeholder.empty()

                if auto_limited:
                    st.caption("Auto-applied LIMIT 10,000 for safety.")

                if df_custom.empty:
                    st.info("Query returned no results.")
                else:
                    render_result_bar(df_custom, elapsed_custom)
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
