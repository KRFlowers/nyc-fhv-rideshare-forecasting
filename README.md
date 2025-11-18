# NYC Rideshare Demand Forecasting

Time series forecasting and predictive modeling for NYC High-Volume For-Hire Vehicle (HVFHV) trip data (Uber, Lyft, Via).

## Project Overview

This project builds forecasting models to predict rideshare demand across NYC's 265 taxi zones using 5 years of trip data (2020-2024, 150M+ trips).

**Analysis Goals:**
- Analyze patterns in rideshare demand (hourly, daily, seasonal)
- Build time series forecasting models for zone-level demand
- Predict trip duration and fares using machine learning
- Compare service patterns across Uber, Lyft, and Via
- Seasonal pattern analysis (STL decomposition)

### Dataset

- **Source:** NYC Taxi & Limousine Commission (TLC)
- **Type:** High-Volume For-Hire Vehicle (HVFHV)
- **Companies:** Uber, Lyft, Via
- **Coverage:** 2020-2024 (5 years, 60 months)
- **Size:** ~150 million trips, ~28 GB

### Key Features

- Modular pipeline architecture (separate notebooks for each stage)
- Memory-efficient processing with DuckDB (handles 28 GB on standard laptop)
- Flag-and-filter validation approach (preserves all data for investigation)
- Comprehensive data quality checks

## Project Structure
```
nyc-hvfhv-rideshare-analysis/
├── notebooks/
│   ├── 00_data_download.ipynb      # Stage 0: Data acquisition
│   └── 01_data_validation.ipynb    # Stage 1: Data quality validation
├── data/
│   ├── raw/                        # Downloaded monthly files (not in repo)
│   └── final/                      # Combined dataset (not in repo)
├── docs/
│   └── DATA_SOURCES.md             # Data documentation
├── README.md
├── requirements.txt
└── .gitignore
```

### Pipeline Stages

0. Data Download 
1. Data Validation 
2. Exploratory Analysis 
3. Demand Forecasting 
4. Trip Prediction 

## Getting Started

### Prerequisites

- Python 3.8+
- ~50 GB free disk space (for data)
- 8+ GB RAM recommended

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/nyc-hvfhv-rideshare-analysis.git
cd nyc-hvfhv-rideshare-analysis

# Install dependencies
pip install -r requirements.txt
```

### Download Data
```bash
# Run the download notebook
jupyter notebook notebooks/00_data_download.ipynb
```

**Note:** Download takes 1-2 hours depending on internet speed. Files are large (200-500 MB each).

### Validate Data
```bash
# Run the validation notebook
jupyter notebook notebooks/01_data_validation.ipynb
```

## Data

Data files are not included in this repository due to size (~28 GB combined).

**Download source:** [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

See [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) for complete data documentation including:
- Schema details
- Company identifiers
- Known data quality issues
- Valid value ranges

## Technology Stack

- **Python 3.8+** - Core language
- **DuckDB** - Memory-efficient SQL analytics
- **Pandas** - Data manipulation
- **PyArrow** - Parquet file handling

### Why DuckDB?

DuckDB enables analysis of the 28 GB dataset on a standard laptop:
- Processes data without loading entire file into memory
- 5-10x faster than pandas for large datasets
- SQL interface for complex queries
- Automatic parallel processing

## Analysis Opportunities

This dataset supports multiple forecasting and prediction projects:

1. **Demand Forecasting by Zone** - Predict hourly trips for 265 NYC zones
2. **Trip Duration Prediction** - Estimate trip time from pickup/dropoff
3. **Fare Prediction** - Predict trip cost based on features
4. **Tip Prediction** - Analyze tipping behavior patterns

## Author

[Your Name]

## License

This project is licensed under the MIT License.

## Acknowledgments

- NYC Taxi & Limousine Commission for providing the data
- DuckDB team for excellent analytics database