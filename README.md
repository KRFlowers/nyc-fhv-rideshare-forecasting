# NYC Rideshare Demand Forecasting — Time Series Analysis

This project forecasts daily Uber/Lyft demand for NYC using 684M trip records from 2022-2024. Three time series approaches were evaluated—Seasonal Naive, Prophet, and XGBoost. The analysis produces daily demand forecasts by NYC zone.

## Project Overview

**The Problem:** Gig workers face a critical problem: **committing their availability without guaranteed earnings**. Currently, **28 million Americans** work in the rideshare and delivery industries (Flex, 2024), with workers in warehouse and logistics facing the same demand uncertainty. When companies schedule workers based on inaccurate demand forecasts, workers bear the cost:**uncertain income and missed opportunities** to work elsewhere.

**Better demand forecasting enables more accurate scheduling decisions**, reducing income uncertainty for workers while improving operational efficiency for companies.

**The Approach:** This project analyzes 684M FHVHV trip records from NYC spanning 2022-2024. Three forecasting approaches were evaluated: Seasonal Naive (baseline), Prophet (automated seasonality), and XGBoost (lag-based features). This analysis is limited to 1-day-ahead forecasting, with longer operational horizons (7-14 days) to be explored in future iterations.

**The Result:** XGBoost achieved 6.5% MAPE with 35% improvement over the seasonal naive baseline.

## Key Results

**Model Performance:**
- **XGBoost** — 6.5% MAPE (best performance, 35% improvement over baseline)
- **Seasonal Naive** — 9.9% MAPE (baseline)
- **Prophet** — 11.1% MAPE (underperformed baseline)

*Note:  Forecast errors under 10% are generally considered acceptable for demand planning. Model performance is for 1-Day-Ahead Forecasts.*

**Data Insights:**
- Weekend demand averaged 17% higher than weekdays
- Weekly seasonality was the dominant pattern with a slight yearly seasonal component
- Low within-zone variability (CV < 0.3) allowed simple 7-day lag features to capture demand patterns effectively
- 76% of zone pairs showed medium-to-high correlation, indicating a single model approach across all zones may be sufficient
- Strong growth in 2022 that stabilized in 2023-2024 may reflect post-COVID recovery patterns
- Data quality was very high with 99.91% of records passing validation

## Data

- **Source:** [NYC Taxi & Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- **Dataset:** For-Hire Vehicle High Volume (FHVHV) trip records
- **Period:** January 2022 – December 2024 (36 months)
- **Scale:** 684 million trip records
- **Scope:** Top 100 zones capturing ~72% of total demand

## Pipeline

1. **00_data_download.ipynb** — Download and combine monthly Parquet files (~2-3 hrs)
2. **01_data_validation.ipynb** — Validate data quality, flag issues, create a clean dataset (~30 min)
3. **02_exploratory_analysis.ipynb** — Analyze demand patterns, select zones, engineer features (~20 min)
4. **03_demand_forecasting.ipynb** — Compare models and generate zone-level forecasts (~15 min)

## Tech Stack

- **Data Processing:** DuckDB (enables memory-efficient processing of 18GB dataset)
- **Analysis:** pandas, NumPy, SciPy
- **Modeling:** XGBoost, Prophet, scikit-learn
- **Visualization:** Matplotlib, Seaborn

## Limitations

This project analyzes 1-day-ahead predictions and serves as a proof of concept rather than production-grade analysis. Real-world scheduling applications would require 7-14 day forecast horizons to be operationally useful. This was a key lesson learned in demand forecasting, and extending to longer horizons is planned for future iterations.

Analysis was also limited to the top 100 highest-demand zones to keep the project computationally manageable while still capturing 72% of total citywide demand. Lower-demand zones were not modeled but could be included in future iterations. External factors like weather and events were not incorporated at this stage.

## Future Work

- Extend to multi-day predictions (7-day, 14-day) to better reflect real-world operational forcasting requirements.
- Add hyperparameter tuning for XGBoost
- Add weather data and event calendar
- Expand beyond top 100 zones to include all ride-share demand

## How to Run

**Prerequisites:** Python 3.10+, ~40GB disk space

```bash
git clone https://github.com/KRFlowers/nyc-rideshare-forecasting.git
cd nyc-rideshare-forecasting
pip install -r requirements.txt
```

Run notebooks in sequence: 00 > 01 > 02 > 03

**Total runtime:** ~1-2 hours first run, ~30 minutes if data exists

## References

Flex. (2024). *Platform Work in America Report*. Flex Association. https://www.flexassociation.org/

## Author

**Kristi Flowers**  
kristirflowers@gmail.com