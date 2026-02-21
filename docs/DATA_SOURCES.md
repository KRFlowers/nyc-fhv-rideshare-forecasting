# Data Sources

## NYC TLC High-Volume For-Hire Vehicle (HVFHV) Trip Data

**Source:** NYC Taxi & Limousine Commission  
**URL:** https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page  
**Format:** Monthly Parquet files  
**License:** Public domain (NYC Open Data)

### What This Project Uses

- **Trip data:** `fhvhv_tripdata_{YYYY}-{MM}.parquet` (Jan 2022 -- Dec 2024, 36 files)
- **Zone metadata:** Taxi Zone Lookup Table (CSV) from the TLC data page

### Company Identifiers

| Code | Company |
|------|---------|
| HV0003 | Uber |
| HV0004 | Via |
| HV0005 | Lyft |

### Citation

> NYC Taxi & Limousine Commission. (2025). TLC Trip Record Data.
> https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
