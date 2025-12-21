# NYC Rideshare Forecasting - Data Pipeline

This document is a quick look at the data processing pipeline for the NYC rideshare demand forecasting project.

---

## Pipeline Overview

```
00_data_download.ipynb
    │
    ├─→ OUTPUT: data/raw/combined_fhvhv_tripdata.parquet (684M rows, 18GB)
    │
    ↓
01_data_validation.ipynb
    │
    ├─→ OUTPUT: data/validated/fhvhv_valid_data_for_eda.parquet (683M valid rows)
    ├─→ OUTPUT: data/quality_reports/validation_report.csv
    │
    ↓
02_exploratory_analysis.ipynb
    │
    ├─→ OUTPUT: data/processed/zone_daily.parquet (aggregated time series)
    │
    ↓
03_demand_forecasting.ipynb
    │
    ├─→ OUTPUT: data/results/forecast_results.csv
    └─→ OUTPUT: data/results/summary_results.csv
```

### Notebook Descriptions

| Notebook | Purpose | Runtime | Key Outputs |
|----------|---------|---------|-------------|
| **00_data_download** | Download raw trip data from NYC TLC | ~45 min | Combined dataset (18GB) |
| **01_data_validation** | Validate records, flag anomalies | ~70 min | Clean dataset (99.91% pass) |
| **02_exploratory_analysis** | Aggregate and analyze patterns | ~45 min | Zone-daily time series |
| **03_demand_forecasting** | Build and compare models | ~60 min | Forecasts + performance metrics |

---

## Quick Start Guide

### For Recruiters/Reviewers

**Want to see the complete analysis?** Run notebooks in order:
1. `00_data_download.ipynb` - Get the data
2. `01_data_validation.ipynb` - Clean and validate
3. `02_exploratory_analysis.ipynb` - Explore patterns
4. `03_demand_forecasting.ipynb` - Build forecasts

**Want to skip data processing?** Start at notebook 3 or 4 if processed data files exist.

**Just browsing?** All notebooks include:
- Pre-executed outputs (no need to re-run)
- Detailed markdown explanations
- Visualizations and summary statistics

---

## Directory Structure

```
nyc-rideshare-forecasting/
│
├── notebooks/
│   ├── 00_data_download.ipynb          # Step 1: Acquisition
│   ├── 01_data_validation.ipynb        # Step 2: Quality checks
│   ├── 02_exploratory_analysis.ipynb   # Step 3: EDA
│   └── 03_demand_forecasting.ipynb     # Step 4: Modeling
│
├── data/
│   ├── raw/                            # Downloaded monthly files
│   ├── final/                          # Combined dataset
│   ├── validated/                      # Clean validated data
│   ├── processed/                      # Aggregated time series
│   ├── results/                        # Forecasts and metrics
│   └── quality_reports/                # Validation reports
│
├── PIPELINE.md                         # This file
└── README.md                           # Project overview
```

---

## Technical Stack

- **Data Processing:** DuckDB (in-memory SQL for 18GB dataset)
- **Analysis:** pandas, numpy
- **Visualization:** matplotlib, seaborn
- **Forecasting:** Prophet, XGBoost, statsmodels
- **Environment:** Python 3.x, Jupyter notebooks

---

## Data Quality Summary

| Metric | Value |
|--------|-------|
| **Total Records** | 684,376,551 |
| **Valid Records** | 683,780,462 (99.91%) |
| **Time Period** | Jan 2022 - Dec 2024 |
| **Dataset Size** | 18GB (compressed parquet) |
| **Top 100 Zones** | 72% of total trip volume |

---

## Runtime Estimates

| Notebook | Approximate Runtime |
|----------|---------------------|
| 00_data_download | 45 minutes |
| 01_data_validation | 70 minutes |
| 02_exploratory_analysis | 45 minutes |
| 03_demand_forecasting | 60 minutes |
| **Total Pipeline** | **~3.5 hours** |

*Note: Runtimes vary based on system specs and internet speed for downloads.*
