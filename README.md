# NYC Rideshare Demand Forecasting

## Project Overview

In the demand-driven rideshare industry, unpredictability creates a constant staffing challenge. Inaccurate demand forecasting results in either **excessive costs** from driver surpluses or **degraded service** from driver shortages. This is where high-accuracy forecasting provides a critical advantage, as it allows operators to maximize efficiency while ensuring workers have **predictable schedules**.

This project demonstrates a solution by forecasting rideshare volume across 195 NYC zones using **684 million trip records**. After evaluating Seasonal Naïve, Prophet, and XGBoost, **XGBoost was the strongest performer**, achieving a **6.4% average MAPE** with 97% of zones meeting the 10% error target.

---

## Scope

- **Forecast horizon:** One-day-ahead forecasting is used as an initial benchmark to validate the data and modeling approach before extending to longer horizons
- **Zone selection:** Zones with highly correlated demand patterns were selected so a single model could be applied (195 zones were modeled, 82% of total trip volume)

---

## Approach

The analysis follows a four-stage notebook pipeline.

1. **Data Download** — Download and consolidate monthly trip files into a single Parquet dataset
2. **Data Validation** — Validate trip records against thresholds for duration, distance, and fare
3. **Exploratory Analysis** — Examine demand patterns for seasonality, trend, and cross-zone correlation
4. **Demand Forecasting** — Evaluate three models, select the best performer, scale model across selected zones

An interactive Streamlit dashboard is also included for demand and forecast review (see [below](#streamlit-dashboard)).

---

## Results

Model performance was evaluated using mean absolute percentage error (MAPE) for one-day-ahead forecasts.

### Model Performance

- **XGBoost achieved an average 6.4% MAPE across the zones selected for modeling**
- 97% of zones met the <10% MAPE performance target
- Seasonal Naive model provided a good initial baseline
- Prophet appeared too complex for the short-term horizon forecast

### Demand Patterns

- Day-of-week patterns, indicating weekly seasonality, provided the most consistent demand signal
- Weekend demand was generally higher than weekdays
- Zones highly correlated with global demand accounted for the majority of total trip volume, supporting a shared modeling approach

---

## Streamlit Dashboard

The project also includes an interactive Streamlit dashboard for exploring demand patterns and forecast results.

![Operations Dashboard](images/dashboard_screenshot.png)

- **KPI Summary** — Total trips, average daily demand, peak day, and median forecast MAPE
- **Demand Charts** — Daily trend, day-of-week and borough distributions, and year-over-year monthly comparison
- **Forecast vs Actual** — Zone-level comparison of predicted vs actual demand for a selected zone with MAPE displayed

Run locally:

    streamlit run app/dashboard.py

---

## Limitations

- Forecast horizon was limited to one-day-ahead predictions
- External variables that may affect demand (weather, events, policy changes) were not included
- Low-correlation zones (airports, entertainment districts) were not included in modeling

---

## Next Steps

A detailed analysis report was created that identified the possible enhancements below. These were captured in an enhancement roadmap located in [`docs/`](docs/).

- Incorporate time-series cross-validation (rolling/expanding window)
- Extend forecasting horizon to 7–14 days
- Re-evaluate Prophet at longer horizons where its decomposition approach may be better suited
- Add residual diagnostics (Ljung-Box test, ACF/PACF validation, segmented analysis by borough)
- Apply SHAP analysis for zone-level feature interpretation
- Evaluate additional models (LightGBM, ARIMA/SARIMAX)
- Add statistical significance testing (Diebold-Mariano, bootstrap CIs)
- Explore hyperparameter optimization
- Build additional models for outlier zones that show different demand patterns
- Integrate external demand drivers (weather, events)

---

## Data

- **Source:** NYC Taxi & Limousine Commission
- **Dataset:** For-Hire Vehicle High Volume (FHVHV) trip records
- **Period:** January 2022 – December 2024
- **Scale:** 684 million trip records
- **Scope:** 195 high-correlation zones (82% of total demand)

---

## Tech Stack

- DuckDB (large-scale data processing)
- pandas, NumPy
- XGBoost
- Prophet
- scikit-learn
- Matplotlib
- Streamlit, Plotly

---

## References

- NYC Taxi & Limousine Commission. (n.d.). TLC Trip Record Data. https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

**K Flowers**
GitHub: [KRFlowers](https://github.com/KRFlowers)