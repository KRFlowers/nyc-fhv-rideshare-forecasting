# NYC Rideshare Demand Forecasting

This project uses publicly available New York City Taxi & Limousine Commission For-Hire Vehicle High Volume (FHVHV) trip data to perform time series forecasting on daily demand. The analysis is based on 684 million trip records from 2022 through 2024 and focuses on short-term demand forecasting. Three models are evaluated: a Seasonal Naive baseline, Prophet, and XGBoost.

## Business Context

Demand forecasting is a core part of business operations planning. Accurate forecasts help companies align staffing and resources with expected demand.

What may be less obvious is that forecasting accuracy also affects workers. In demand-driven roles (such as rideshare drivers and warehouse staff), more reliable forecasts help reduce schedule uncertainty and allow them to plan their time more effectively.

## Approach

The project is organized as a notebook-based pipeline, with each step building toward scalable demand forecasting.

- **00_data_download**  
  Downloaded and combined monthly FHVHV files into a single Parquet dataset using DuckDB for memory-efficient processing.

- **01_data_validation**  
  Validated trip records, checked for missing or invalid values, and aggregated data to daily demand by zone.

- **02_exploratory_analysis**  
  Examined demand characteristics globally and by zone, including seasonality, stability, and correlation with citywide patterns.

- **03_demand_forecasting**  
  Evaluated a pilot zone using three models (Seasonal Naive, Prophet, and XGBoost), selected the best-performing model, and scaled it across eligible zones.

## Results

Model performance was evaluated using mean absolute percentage error (MAPE), with an emphasis on short-horizon accuracy and scalability.

- **Pilot zone performance**
  - XGBoost achieved the lowest error and was selected for scaling.
  - Seasonal Naive provided a strong baseline for comparison.
  - Prophet underperformed for one-day-ahead forecasts.

- **Scaled results**
  - XGBoost achieved an average **6.4% MAPE** across 195 zones.
  - **97% of zones** met the <10% MAPE target.
  - High-correlation zones represented **82% of total trips**, supporting the scalability of a shared modeling approach.

- **Key demand patterns**
  - Weekly seasonality dominated demand behavior.
  - Weekend demand averaged higher than weekdays.
  - Demand was stable within zones, supporting additive modeling assumptions.

## Limitations

- One-day-ahead only — keeps initial analysis straightforward; 1-2 week horizons typical of driver scheduling are a natural next step
- Prophet may be worth re-evaluating for longer forecast horizons
- 61 low-correlation zones (airports, entertainment districts) excluded — may need specialized models
- External factors (weather, events) not incorporated

## Next Steps

- Extend to multi-day forecast horizons (7-14 days)
- Add cross-validation and hyperparameter tuning
- Incorporate statistical testing for model comparison
- Develop specialized models for low-correlation zones

## Data

- **Source:** [NYC Taxi & Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- **Dataset:** For-Hire Vehicle High Volume (FHVHV) trip records
- **Period:** January 2022 – December 2024 (36 months)
- **Scale:** 684 million trip records
- **Scope:** 195 high-correlation zones (82% of total demand)

## Notebook Pipeline

| Notebook | Purpose | Runtime |
|----------|---------|---------|
| **00_data_download** | Download and combine monthly Parquet files | ~1 hour |
| **01_data_validation** | Validate data quality, flag issues | ~30 min |
| **02_exploratory_analysis** | Aggregate to daily, analyze patterns | ~15 min |
| **03_demand_forecasting** | Compare models, generate forecasts | ~15 min |

## Tech Stack

- **Data Processing:** DuckDB (memory-efficient processing of 18GB dataset)
- **Analysis:** pandas, NumPy
- **Modeling:** XGBoost, Prophet, scikit-learn
- **Visualization:** Matplotlib

## Author

**K Flowers**
GitHub: [KRFlowers](https://github.com/KRFlowers)
