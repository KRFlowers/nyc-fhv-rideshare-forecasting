# NYC Rideshare Demand Forecasting — Time Series Analysis

This project forecasts daily Uber/Lyft demand for NYC using 684M trip records from 2022-2024. The analysis focuses on the top 100 highest-volume zones, which capture 72% of total citywide demand. Three time series approaches were evaluated—Seasonal Naive, Prophet, and XGBoost. Results can be used to support more efficient driver allocation and improved service coverage.

**Model Performance:**
- XGBoost achieved 6.5% MAPE with 35% improvement over seasonal naive baseline

**Data Discoveries:**
- Demand follows a consistent weekly pattern with weekends averaging 17% higher than weekdays. This pattern enabled lag-based forecasting.
- Within-zone demand was very stable (CV < 0.3), enabling reliable forecasts with simple lag features
- Data quality was high with 99.91% of records passed validation

## Business Problem

Accurate demand forecasts are important because they create value for both drivers and companies. Optimized scheduling ensures drivers' time is used effectively, while companies can position supply where needed. This project develops zone-level daily forecasts to support both of these goals.

## Key Findings

- Weekend demand is 17% higher than weekdays and weekly seasonality is the dominant pattern
- Low within-zone variability was discovered (CV < 0.3) and influenced model performance (simpler lag-based approaches outperformed flexible seasonality models like Prophet)
- 76% of zone pairs show medium-to-high correlation, which suggested one model could work across all zones
- Strong growth identified in 2022 but stable in 2023-2024. This may reflect post-COVID recovery

## Data

- **Source:** [NYC Taxi & Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- **Dataset:** For-Hire Vehicle High Volume (FHVHV) trip records
- **Period:** January 2022 – December 2024 (36 months)
- **Scale:** 684 million trip records
- **Scope:** Top 100 zones capturing ~72% of total demand

## Pipeline

1. **00_data_download.ipynb** — Download and consolidate monthly Parquet files (~2-3 hrs)
2. **01_data_validation.ipynb** — Quality checks, flagging, clean dataset creation (~30 min)
3. **02_exploratory_analysis.ipynb** — Demand patterns, zone selection, feature engineering (~20 min)
4. **03_demand_forecasting.ipynb** — Model comparison and zone-level forecasts (~15 min)

## Models Evaluated

- **XGBoost** — Lag features (7-day), MAE: 302 trips/day, 6.5% MAPE, **best performance**
- **Seasonal Naive** — Same day last week, MAE: 466 trips/day (baseline)
- **Prophet** — Automated seasonality, MAE: 521 trips/day, underperformed baseline

## Tech Stack

- **Data Processing:** DuckDB (memory-efficient processing of 684M records)
- **Analysis:** pandas, NumPy, SciPy
- **Modeling:** XGBoost, Prophet, scikit-learn
- **Visualization:** Matplotlib, Seaborn

## How to Run

**Prerequisites:** Python 3.10+, ~40GB disk space

```bash
git clone https://github.com/KRFlowers/nyc-rideshare-forecasting.git
cd nyc-rideshare-forecasting
pip install -r requirements.txt
```

Run notebooks in sequence: 00 → 01 → 02 → 03

Total runtime: ~4-5 hours first run, ~45 minutes if data exists

## Limitations

- No external factors (weather, events) included yet
- Top 100 zones only — lower-demand areas not modeled
- 2022-2024 reflects post-COVID patterns

## Future Work

- Hyperparameter tuning for XGBoost
- Add weather and event data
- Expand beyond top 100 zones

## Author

Kristi Flowers
  - kristirflowers@gmail.com