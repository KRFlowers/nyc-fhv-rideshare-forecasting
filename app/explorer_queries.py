"""
Pre-built query definitions for the SQL Explorer.
16 queries grouped by data scope: Borough, Zone, Overall, Data Quality.


Author: Kristi Flowers
Date: March 2026
"""

from dataclasses import dataclass
from typing import Callable


@dataclass
class QueryDef:
    """Definition for a pre-built query."""
    id: str
    name: str
    category: str
    has_chart: bool
    needs_zone: bool
    build_sql: Callable  # (start_date, end_date, **kwargs) -> str


# ---------------------------------------------------------------------------
# Borough queries
# ---------------------------------------------------------------------------
def build_borough_trip_volume(start_date: str, end_date: str, **kw) -> str:
    return f"""
SELECT pz.Borough,
       COUNT(*) AS total_trips,
       ROUND(AVG(t.base_passenger_fare), 2) AS avg_fare,
       ROUND(AVG(t.trip_miles), 1) AS avg_miles
FROM trips t
JOIN zones pz ON t.PULocationID = pz.zone_id
WHERE t.pickup_datetime >= '{start_date}'
  AND t.pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
GROUP BY pz.Borough
ORDER BY total_trips DESC
""".strip()


def build_borough_mom_growth(start_date: str, end_date: str, **kw) -> str:
    return f"""
WITH monthly AS (
    SELECT pz.Borough,
           DATE_TRUNC('month', t.pickup_datetime) AS month,
           COUNT(*) AS trips
    FROM trips t
    JOIN zones pz ON t.PULocationID = pz.zone_id
    WHERE t.pickup_datetime >= '{start_date}'
      AND t.pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
    GROUP BY pz.Borough, DATE_TRUNC('month', t.pickup_datetime)
)
SELECT Borough, month, trips,
       LAG(trips) OVER (PARTITION BY Borough ORDER BY month) AS prev_month,
       ROUND(100.0 * (trips - LAG(trips) OVER (PARTITION BY Borough ORDER BY month))
             / NULLIF(LAG(trips) OVER (PARTITION BY Borough ORDER BY month), 0), 1
       ) AS growth_pct
FROM monthly
ORDER BY Borough, month
""".strip()


def build_borough_weekday_weekend(start_date: str, end_date: str, **kw) -> str:
    return f"""
WITH classified AS (
    SELECT pz.Borough,
           CAST(t.pickup_datetime AS DATE) AS trip_date,
           CASE WHEN DAYOFWEEK(t.pickup_datetime) IN (0, 6) THEN 'Weekend (Sat–Sun)'
                ELSE 'Weekday (Mon–Fri)' END AS day_type
    FROM trips t
    JOIN zones pz ON t.PULocationID = pz.zone_id
    WHERE t.pickup_datetime >= '{start_date}'
      AND t.pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
),
daily AS (
    SELECT Borough, day_type, trip_date, COUNT(*) AS trips
    FROM classified
    GROUP BY Borough, day_type, trip_date
)
SELECT Borough, day_type,
       ROUND(AVG(trips), 0) AS avg_daily_trips,
       COUNT(DISTINCT trip_date) AS num_days
FROM daily
GROUP BY Borough, day_type
ORDER BY Borough, day_type
""".strip()


def build_borough_peak_hour(start_date: str, end_date: str, **kw) -> str:
    return f"""
WITH hourly AS (
    SELECT pz.Borough,
           EXTRACT(HOUR FROM t.pickup_datetime) AS hour,
           COUNT(*) AS trips
    FROM trips t
    JOIN zones pz ON t.PULocationID = pz.zone_id
    WHERE t.pickup_datetime >= '{start_date}'
      AND t.pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
    GROUP BY pz.Borough, EXTRACT(HOUR FROM t.pickup_datetime)
)
SELECT RANK() OVER (PARTITION BY Borough ORDER BY trips DESC) AS rank,
       Borough, hour, trips
FROM hourly
ORDER BY Borough, rank
""".strip()


# ---------------------------------------------------------------------------
# Zone queries
# ---------------------------------------------------------------------------
def build_zone_busiest(start_date: str, end_date: str, **kw) -> str:
    return f"""
SELECT ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS rank,
       pz.Zone, pz.Borough, COUNT(*) AS total_trips
FROM trips t
JOIN zones pz ON t.PULocationID = pz.zone_id
WHERE t.pickup_datetime >= '{start_date}'
  AND t.pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
GROUP BY pz.Zone, pz.Borough
ORDER BY total_trips DESC
LIMIT 20
""".strip()


def build_zone_rolling_7d(start_date: str, end_date: str, **kw) -> str:
    zone_id = kw.get("zone_id", 79)
    return f"""
WITH daily AS (
    SELECT CAST(t.pickup_datetime AS DATE) AS trip_date,
           COUNT(*) AS trips
    FROM trips t
    WHERE t.PULocationID = {zone_id}
      AND t.pickup_datetime >= '{start_date}'
      AND t.pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
    GROUP BY CAST(t.pickup_datetime AS DATE)
)
SELECT trip_date, trips,
       ROUND(AVG(trips) OVER (
           ORDER BY trip_date
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ), 0) AS rolling_7d_avg
FROM daily
ORDER BY trip_date
""".strip()


def build_zone_rank_monthly(start_date: str, end_date: str, **kw) -> str:
    return f"""
WITH monthly AS (
    SELECT DATE_TRUNC('month', t.pickup_datetime) AS month,
           pz.Zone, pz.Borough,
           COUNT(*) AS trips
    FROM trips t
    JOIN zones pz ON t.PULocationID = pz.zone_id
    WHERE t.pickup_datetime >= '{start_date}'
      AND t.pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
    GROUP BY DATE_TRUNC('month', t.pickup_datetime), pz.Zone, pz.Borough
),
ranked AS (
    SELECT month, Zone, Borough, trips,
           DENSE_RANK() OVER (PARTITION BY month ORDER BY trips DESC) AS rank
    FROM monthly
)
SELECT rank, month, Zone, Borough, trips
FROM ranked
WHERE rank <= 10
ORDER BY month, rank
""".strip()


def build_zone_top_routes(start_date: str, end_date: str, **kw) -> str:
    return f"""
SELECT ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS rank,
       pz.Zone AS pickup_zone, dz.Zone AS dropoff_zone,
       pz.Borough AS pickup_borough, dz.Borough AS dropoff_borough,
       COUNT(*) AS total_trips
FROM trips t
JOIN zones pz ON t.PULocationID = pz.zone_id
JOIN zones dz ON t.DOLocationID = dz.zone_id
WHERE t.pickup_datetime >= '{start_date}'
  AND t.pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
GROUP BY pz.Zone, dz.Zone, pz.Borough, dz.Borough
ORDER BY total_trips DESC
LIMIT 20
""".strip()


# ---------------------------------------------------------------------------
# Overall queries
# ---------------------------------------------------------------------------
def build_overall_market_share(start_date: str, end_date: str, **kw) -> str:
    return f"""
SELECT DATE_TRUNC('month', pickup_datetime) AS month,
       CASE hvfhs_license_num
           WHEN 'HV0003' THEN 'Uber'
           WHEN 'HV0005' THEN 'Lyft'
           WHEN 'HV0004' THEN 'Via'
           ELSE 'Other' END AS company,
       COUNT(*) AS trips,
       ROUND(100.0 * COUNT(*)
             / SUM(COUNT(*)) OVER (PARTITION BY DATE_TRUNC('month', pickup_datetime)),
             1) AS pct
FROM trips
WHERE pickup_datetime >= '{start_date}'
  AND pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
GROUP BY month, company
ORDER BY month, trips DESC
""".strip()


def build_overall_fare_by_distance(start_date: str, end_date: str, **kw) -> str:
    return f"""
SELECT CASE
           WHEN trip_miles < 2 THEN '1. Short (< 2 mi)'
           WHEN trip_miles < 10 THEN '2. Medium (2-10 mi)'
           WHEN trip_miles < 20 THEN '3. Long (10-20 mi)'
           ELSE '4. Very Long (20+ mi)' END AS distance_tier,
       COUNT(*) AS trips,
       ROUND(AVG(base_passenger_fare), 2) AS avg_fare,
       ROUND(AVG(trip_miles), 1) AS avg_miles,
       ROUND(AVG(trip_time / 60.0), 1) AS avg_duration_min
FROM trips
WHERE pickup_datetime >= '{start_date}'
  AND pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
  AND trip_miles > 0
GROUP BY distance_tier
ORDER BY distance_tier
""".strip()


def build_overall_seasonal(start_date: str, end_date: str, **kw) -> str:
    return f"""
SELECT EXTRACT(YEAR FROM pickup_datetime) AS year,
       EXTRACT(MONTH FROM pickup_datetime) AS month_num,
       STRFTIME(DATE_TRUNC('month', pickup_datetime), '%b') AS month,
       COUNT(*) AS total_trips,
       ROUND(COUNT(*) / COUNT(DISTINCT CAST(pickup_datetime AS DATE)), 0) AS avg_daily_trips
FROM trips
WHERE pickup_datetime >= '{start_date}'
  AND pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
GROUP BY year, EXTRACT(MONTH FROM pickup_datetime), DATE_TRUNC('month', pickup_datetime)
ORDER BY year, month_num
""".strip()


def build_overall_holiday(start_date: str, end_date: str, **kw) -> str:
    return f"""
WITH holidays AS (
    SELECT CAST(d AS DATE) AS holiday_date FROM (VALUES
        ('2022-01-01'),('2022-01-17'),('2022-02-21'),('2022-05-30'),
        ('2022-07-04'),('2022-09-05'),('2022-11-24'),('2022-12-25'),
        ('2023-01-01'),('2023-01-16'),('2023-02-20'),('2023-05-29'),
        ('2023-07-04'),('2023-09-04'),('2023-11-23'),('2023-12-25'),
        ('2024-01-01'),('2024-01-15'),('2024-02-19'),('2024-05-27'),
        ('2024-07-04'),('2024-09-02'),('2024-11-28'),('2024-12-25')
    ) AS t(d)
),
daily AS (
    SELECT CAST(pickup_datetime AS DATE) AS trip_date,
           COUNT(*) AS trips
    FROM trips
    WHERE pickup_datetime >= '{start_date}'
      AND pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
    GROUP BY CAST(pickup_datetime AS DATE)
)
SELECT day_type, avg_daily_trips, total_trips, num_days,
       ROUND(100.0 * (avg_daily_trips - non_holiday_avg) / NULLIF(non_holiday_avg, 0), 1) AS pct_difference
FROM (
    SELECT CASE WHEN h.holiday_date IS NOT NULL THEN 'Holiday'
                ELSE 'Non-Holiday' END AS day_type,
           ROUND(AVG(d.trips), 0) AS avg_daily_trips,
           SUM(d.trips) AS total_trips,
           COUNT(*) AS num_days
    FROM daily d
    LEFT JOIN holidays h ON d.trip_date = h.holiday_date
    GROUP BY day_type
) sub
CROSS JOIN (
    SELECT ROUND(AVG(d.trips), 0) AS non_holiday_avg
    FROM daily d
    LEFT JOIN holidays h ON d.trip_date = h.holiday_date
    WHERE h.holiday_date IS NULL
) base
ORDER BY day_type
""".strip()


# ---------------------------------------------------------------------------
# Data Quality queries
# ---------------------------------------------------------------------------
def build_dq_temporal_coverage(start_date: str, end_date: str, **kw) -> str:
    return f"""
SELECT DATE_TRUNC('month', pickup_datetime) AS month,
       COUNT(*) AS records,
       MIN(pickup_datetime) AS earliest,
       MAX(pickup_datetime) AS latest
FROM trips
WHERE pickup_datetime >= '{start_date}'
  AND pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
GROUP BY DATE_TRUNC('month', pickup_datetime)
ORDER BY month
""".strip()


def build_dq_zero_negative(start_date: str, end_date: str, **kw) -> str:
    return f"""
SELECT COUNT(*) AS total_rows,
       SUM(CASE WHEN trip_miles <= 0 THEN 1 ELSE 0 END) AS zero_neg_miles,
       SUM(CASE WHEN trip_time <= 0 THEN 1 ELSE 0 END) AS zero_neg_time,
       SUM(CASE WHEN base_passenger_fare <= 0 THEN 1 ELSE 0 END) AS zero_neg_fare,
       SUM(CASE WHEN driver_pay <= 0 THEN 1 ELSE 0 END) AS zero_neg_driver_pay,
       SUM(CASE WHEN tips < 0 THEN 1 ELSE 0 END) AS negative_tips
FROM trips
WHERE pickup_datetime >= '{start_date}'
  AND pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
""".strip()


def build_dq_null_summary(start_date: str, end_date: str, **kw) -> str:
    return f"""
SELECT COUNT(*) AS total_rows,
       COUNT(*) - COUNT(request_datetime) AS null_request_datetime,
       COUNT(*) - COUNT(pickup_datetime) AS null_pickup_datetime,
       COUNT(*) - COUNT(dropoff_datetime) AS null_dropoff_datetime,
       COUNT(*) - COUNT(trip_miles) AS null_trip_miles,
       COUNT(*) - COUNT(trip_time) AS null_trip_time,
       COUNT(*) - COUNT(base_passenger_fare) AS null_base_fare,
       COUNT(*) - COUNT(tips) AS null_tips,
       COUNT(*) - COUNT(driver_pay) AS null_driver_pay,
       COUNT(*) - COUNT(shared_request_flag) AS null_shared_request,
       COUNT(*) - COUNT(congestion_surcharge) AS null_congestion,
       COUNT(*) - COUNT(airport_fee) AS null_airport_fee
FROM trips
WHERE pickup_datetime >= '{start_date}'
  AND pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
""".strip()


def build_dq_outliers(start_date: str, end_date: str, **kw) -> str:
    return f"""
WITH thresholds AS (
    SELECT PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY trip_miles) AS p99_miles,
           PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY base_passenger_fare) AS p99_fare,
           PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY trip_time / 60.0) AS p99_duration_min
    FROM trips
    WHERE pickup_datetime >= '{start_date}'
      AND pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
      AND trip_miles > 0
      AND base_passenger_fare > 0
)
SELECT t.pickup_datetime, t.trip_miles, t.base_passenger_fare,
       ROUND(t.trip_time / 60.0, 1) AS duration_min,
       ROUND(th.p99_miles, 1) AS p99_miles,
       ROUND(th.p99_fare, 2) AS p99_fare,
       ROUND(th.p99_duration_min, 1) AS p99_duration_min
FROM trips t, thresholds th
WHERE t.pickup_datetime >= '{start_date}'
  AND t.pickup_datetime < '{end_date}'::DATE + INTERVAL 1 DAY
  AND (t.trip_miles > th.p99_miles
       OR t.base_passenger_fare > th.p99_fare
       OR t.trip_time / 60.0 > th.p99_duration_min)
LIMIT 1000
""".strip()


# ---------------------------------------------------------------------------
# Query registry
# ---------------------------------------------------------------------------
QUERY_REGISTRY: list[QueryDef] = [
    # Borough
    QueryDef("borough_volume", "Trip volume by borough", "BOROUGH", True, False, build_borough_trip_volume),
    QueryDef("borough_mom", "Month-over-month growth rate", "BOROUGH", True, False, build_borough_mom_growth),
    QueryDef("borough_weekday", "Weekend vs weekday demand", "BOROUGH", True, False, build_borough_weekday_weekend),
    QueryDef("borough_peak_hour", "Peak hour analysis", "BOROUGH", True, False, build_borough_peak_hour),
    # Zone
    QueryDef("zone_busiest", "Busiest zones — top 20", "ZONE", True, False, build_zone_busiest),
    QueryDef("zone_rolling_7d", "Rolling 7-day average by zone", "ZONE", True, True, build_zone_rolling_7d),
    QueryDef("zone_rank_monthly", "Rank zones by monthly volume", "ZONE", False, False, build_zone_rank_monthly),
    QueryDef("zone_top_routes", "Top pickup-to-dropoff routes", "ZONE", False, False, build_zone_top_routes),
    # Overall
    QueryDef("overall_market", "Company market share by month", "OVERALL", True, False, build_overall_market_share),
    QueryDef("overall_fare_dist", "Trip metrics by distance tier", "OVERALL", False, False, build_overall_fare_by_distance),
    QueryDef("overall_seasonal", "Seasonal patterns across years", "OVERALL", True, False, build_overall_seasonal),
    QueryDef("overall_holiday", "Holiday vs non-holiday demand", "OVERALL", False, False, build_overall_holiday),
    # Data Quality
    QueryDef("dq_temporal", "Temporal coverage — records per month", "DATA QUALITY", True, False, build_dq_temporal_coverage),
    QueryDef("dq_zero_neg", "Zero and negative value scan", "DATA QUALITY", False, False, build_dq_zero_negative),
    QueryDef("dq_nulls", "Null/missing value summary", "DATA QUALITY", False, False, build_dq_null_summary),
    QueryDef("dq_outliers", "Outlier detection — extreme values", "DATA QUALITY", False, False, build_dq_outliers),
]


def get_query_display_options() -> list[str]:
    """Build numbered display strings for the radio list (Q01, Q02, ...)."""
    _cat_labels = {
        "BOROUGH": "Borough",
        "ZONE": "Zone",
        "OVERALL": "Overall",
        "DATA QUALITY": "Data Quality",
    }
    return [
        f"Q{i+1:02d} · {_cat_labels.get(q.category, q.category)} — {q.name}"
        for i, q in enumerate(QUERY_REGISTRY)
    ]
