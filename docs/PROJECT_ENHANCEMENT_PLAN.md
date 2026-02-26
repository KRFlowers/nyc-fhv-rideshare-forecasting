# NYC Rideshare Forecasting — Next Steps


## Report Expansion Opportunities

These are the 25 enhancements identified in the technical report and future improvements analysis, sorted by recommended implementation order. Value: 1 = highest analytical impact, 10 = nice to have.

| # | Pg | Enhancement | Effort | Rec? | Value | Order |
|---|-----|-------------|--------|------|-------|-------|
| R1 | 8 | Time-series cross-validation (rolling/expanding window with TimeSeriesSplit) | Medium | Yes | 1 | 1 |
| R2 | 20 | Re-evaluate Prophet at longer horizons (7, 14, 30-day) -- test hybrid approach | Medium | Yes | 1 | 2 |
| R3 | 22 | Ljung-Box test on residuals for remaining autocorrelation | Low | Yes | 2 | 3 |
| R4 | 15 | ACF/PACF plots to validate lag feature selection | Low | Yes | 2 | 4 |
| R5 | 22 | Segmented residual analysis by borough or volume tier | Low | Yes | 3 | 5 |
| R6 | 19 | SHAP analysis for zone-level feature interpretation | Medium | Yes | 3 | 6 |
| R7 | 9 | Additional models -- LightGBM, ARIMA/SARIMAX | Medium | Yes | 3 | 7 |
| R8 | 17 | Sensitivity analysis on correlation threshold (0.5 to 0.8) | Low | Yes | 4 | 8 |
| R9 | 15 | Fourier/periodogram analysis to quantify frequency contributions | Low | Yes | 4 | 9 |
| R10 | 19 | External features -- weather, events, subway disruptions | High | Yes | 4 | 10 |
| R11 | 19 | Interaction features (is_weekend x is_holiday, lag_7 x month) | Low | Yes | 4 | 11 |
| R12 | 19 | Recursive feature elimination or SHAP-based feature selection | Medium | Yes | 5 | 12 |
| R13 | 21 | Pooled model comparison (single model with zone_id as feature) | Medium | Yes | 5 | 13 |
| R14 | 17 | Cluster low-correlation zones by demand profile (k-means/hierarchical) | Medium | Yes | 5 | 14 |
| R15 | 21 | Per-zone or group-level hyperparameter tuning (Optuna) | Medium | No | 6 | 15 |
| R16 | 26 | Multi-seed robustness analysis | Low | No | 6 | 16 |
| R17 | 26 | Interactive dashboard (Streamlit or Tableau) | Medium | No | 7 | 17 |
| R18 | 5 | Pipeline orchestrator (DVC, Prefect, or Makefile) | Medium | No | 7 | 18 |
| R19 | 5 | Shared config.yaml to centralize constants across notebooks | Low | No | 8 | 19 |
| R20 | 5 | Automated tests (pytest) on output schemas between notebooks | Medium | No | 8 | 20 |
| R21 | 6 | Profile DuckDB memory usage vs Pandas for cost-benefit analysis | Low | No | 9 | 21 |
| R22 | 11 | Checksum verification and row count validation for downloads | Low | No | 9 | 22 |
| R23 | 13 | Statistical outlier detection (IQR/Z-score by zone) and speed-based validation | Low | No | 10 | 23 |
| R24 | -- | Statistical significance testing (Diebold-Mariano, bootstrap CIs on MAE/MAPE) | Low | Yes | 2 | 24 |
| R25 | -- | Prediction intervals (quantile regression or conformal prediction) | Medium | Yes | 5 | 25 |

## Future Learning Topics

Areas to study for future projects.

- [ ] **F1:** Time-series cross-validation -- understand expanding vs rolling window tradeoffs for demand data
- [ ] **F2:** SHAP for time series -- how to interpret feature contributions when features are lagged versions of the target
- [ ] **F3:** Prophet with regressors -- adding lag features as external regressors to test fair comparison with XGBoost
- [ ] **F4:** Multi-horizon forecasting -- how lag feature reliability degrades at longer horizons and mitigation strategies
- [ ] **F5:** Ljung-Box and residual diagnostics -- formal testing for remaining autocorrelation in forecast errors

---

*Generated: February 2026*
