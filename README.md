# NYC Rideshare Demand Forecasting

Time series forecasting and predictive modeling for NYC High-Volume For-Hire Vehicle (HVFHV) trip data (Uber, Lyft, Via).

## Project Overview

This project builds forecasting models to predict rideshare demand across NYC boroughs using trip data from 2022-2024. The analysis focuses on temporal demand patterns to identify seasonal trends and build predictive models for demand forecasting. The approach combines traditional time series decomposition methods (STL) with modern forecasting techniques (Prophet) and machine learning (XGBoost) to capture both seasonal patterns and complex relationships in rideshare demand.

The analysis examines rideshare demand patterns at multiple temporal scales - daily fluctuations, weekly cycles, and seasonal trends. By aggregating trip data to the borough level, the models can identify distinct demand patterns across Manhattan, Brooklyn, Queens, the Bronx, and Staten Island. This borough-level focus balances analytical depth with computational efficiency while providing actionable insights for understanding rideshare demand dynamics.

## Pipeline Status

This project implements a 4-stage data pipeline:

1. **Stage 0 - Data Download** (Complete): Retrieves and consolidates monthly trip files
2. **Stage 1 - Data Validation** (Complete): Implements quality checks and produces clean dataset
3. **Stage 2 - Exploratory Analysis** (In Progress)
4. **Stage 3 - Modeling** (Planned)

### Dataset

- **Source:** NYC Taxi & Limousine Commission (TLC)
- **Type:** High-Volume For-Hire Vehicle (HVFHV)
- **Companies:** Uber, Lyft, Via
- **Coverage:** January 2022 - December 2024 (3 years)
- **Format:** Parquet files (compressed)

The 2022-2024 timeframe was selected to focus on recent rideshare patterns while providing three full years of history for robust seasonal pattern detection. This period represents normalized rideshare demand and creates a manageable dataset size for analysis on standard hardware. The three-year window captures multiple cycles of seasonal variation, which is essential for time series decomposition and forecasting model training.

### Key Features

The pipeline architecture emphasizes modularity, reproducibility, and memory efficiency. Each stage is implemented as a separate notebook with clear inputs and outputs, creating an auditable data lineage from raw downloads through validated datasets ready for modeling. DuckDB's streaming capabilities enable analysis of large trip datasets on standard laptops without requiring cloud infrastructure or specialized hardware. The validation framework uses a flag-based approach that preserves all records for investigation while creating clean datasets for analysis, and configurable thresholds make the validation logic reusable across different datasets with minimal modification.

## Project Structure

```
nyc-fhv-rideshare-forecasting/
├── notebooks/
│   ├── 00_data_download.ipynb      # Stage 0: Data acquisition and consolidation
│   └── 01_data_validation.ipynb    # Stage 1: Quality validation and flagging
├── data/
│   ├── raw/                        # Downloaded monthly files (not in repo)
│   ├── final/                      # Combined dataset (not in repo)
│   ├── validated/                  # Flagged and clean datasets (not in repo)
│   └── quality_reports/            # Validation metrics (not in repo)
├── docs/
│   └── DATA_SOURCES.md             # Data documentation
├── README.md
├── requirements.txt
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.8+
- ~40-50 GB free disk space
- 16+ GB RAM recommended (8GB minimum)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nyc-fhv-rideshare-forecasting.git
cd nyc-fhv-rideshare-forecasting

# Install dependencies
pip install -r requirements.txt
```

### Running the Pipeline

#### Stage 0: Download Data

```bash
jupyter notebook notebooks/00_data_download.ipynb
```

This stage downloads monthly Parquet files from NYC Open Data and combines them into a single consolidated dataset. The download process automatically skips files that already exist locally to avoid re-downloading, and the consolidation step uses DuckDB to efficiently merge files without loading everything into memory. Runtime varies by network speed and file availability, typically taking 2-3 hours for the full three-year download.

#### Stage 1: Validate Data

```bash
jupyter notebook notebooks/01_data_validation.ipynb
```

The validation stage implements comprehensive quality checks across trip duration, distance, and fare fields. Rather than deleting problematic records, the framework adds quality flags to every record, creating both a flagged dataset (with all records and quality indicators) and a clean dataset (containing only records that pass all validation checks). A detailed validation report documents quality metrics for each validation rule. Processing approximately 70 minutes for large datasets.

## Data

Data files are not included in this repository due to size. The pipeline automatically downloads FHVHV (High Volume For-Hire Vehicle) data for the configured time period from NYC's open data portal.

**Download source:** [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

See [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) for complete data documentation including schema details, company identifiers (Uber=HV0003, Lyft=HV0005), known data quality patterns, and validation threshold rationale.

## Technology Stack

- **Python 3.8+** - Core language
- **DuckDB** - Memory-efficient SQL analytics engine
- **Pandas** - Data manipulation and analysis
- **PyArrow** - Parquet file handling

DuckDB is the key technology enabling this analysis on standard hardware. Unlike pandas which loads entire datasets into memory, DuckDB streams data and processes it in chunks, handling datasets that exceed available RAM. The SQL interface provides a familiar query language for complex aggregations, and automatic parallel processing leverages multiple CPU cores for faster execution. For large-scale data operations like filtering and aggregation, DuckDB typically performs 5-10x faster than pandas while using significantly less memory.

## Validation Framework

The validation pipeline implements a comprehensive quality framework designed for both thoroughness and reusability. The flag-based approach preserves all records rather than deleting problematic data, which enables quality monitoring and investigation of edge cases. Each record receives granular quality flags for specific issues (null values, negative numbers, out-of-bounds data, extreme outliers) plus a master validity indicator for quick filtering.

Validation covers three critical fields for demand forecasting: trip duration (time bounds and extreme value detection), trip distance (distance bounds and negative value checks), and fare amount (fare bounds, negative fare detection, and zero-fare handling). The framework uses configurable thresholds defined at the notebook level, making it easy to adapt the validation logic to different datasets by changing just a few threshold variables.

The pipeline produces two complementary outputs: a flagged dataset containing all records with quality indicators for monitoring and debugging, and a clean dataset containing only valid records ready for exploratory analysis and modeling.

## Author

Kristi [Your Last Name]

## License

This project is licensed under the MIT License.

## Acknowledgments

- NYC Taxi & Limousine Commission for providing public trip data
- DuckDB team for excellent in-process analytics database
- Python data science community for robust open-source tools
