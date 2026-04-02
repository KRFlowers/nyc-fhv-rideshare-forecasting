# Notebook Review Notes -- Responses to Questions

---


---

## 2. Table of Contents and Section 0 for Rationale/Reference

**Table of contents:** Yes, adding one between the intro and the model selection rationale would help navigation. A simple markdown list linking to section headers works in rendered notebooks. Placing it at the end of cell 0 (intro) or as its own cell right after is standard.




## 6. Section 2.5 -- Verify Zone Temporal Coverage

You're right that this was done in EDA, but repeating it in the modeling notebook is good practice. The data file could have been modified or the notebook could be run on a different dataset later. A quick check confirms assumptions still hold.

A simple lambda approach:

```python
# Verify all zones have complete temporal coverage
days_per_zone = full_df.groupby('zone_id')['date'].nunique()
expected_days = full_df['date'].nunique()

all_complete = (days_per_zone == expected_days).all()
incomplete_zones = days_per_zone[days_per_zone < expected_days]

print(f"Temporal Coverage Check")
print(f"  Expected days per zone: {expected_days}")
print(f"  All zones complete: {all_complete}")
if len(incomplete_zones) > 0:
    print(f"  Incomplete zones: {len(incomplete_zones)}")
```

This is cleaner than the average calculation and directly answers the question: does every zone have every day? You could replace the current "days per zone" line with this, or add it as a separate verification step.

---

## 7. Baseline Did Not Use Train/Test Split

Looking at the baseline code (cells 28-30):

```python
# Cell 28: Apply 7-day lag to FULL pilot zone data (before split)
pilot_df['baseline_pred'] = pilot_df['daily_trips'].shift(7)

# Cell 29: Then filter to test period
baseline_test_df = pilot_df[pilot_df['date'] >= TEST_START_DATE].copy()
```

The baseline applies the 7-day lag to the entire `pilot_df` first, then filters to the test period. It does NOT use `pilot_train_df` or `pilot_test_df` directly.

**Why this works correctly:** The Seasonal Naive model doesn't "train" -- it just looks back 7 days. Applying the shift to the full dataset means the first test day (Jul 1, 2024) uses the actual demand from Jun 24, 2024 as its prediction. Since Jun 24 is in the training period, there's no data leakage. The shift naturally respects the temporal boundary.

**The DataFrame Reference is slightly misleading** when it says `pilot_train_df, pilot_test_df` are for Baseline. The baseline uses `pilot_df` (full data), then filters to the test period. The reference should either:
- Change to: `pilot_df` -- Full pilot zone data, used for baseline lag
- Or add a note: Baseline uses `pilot_df` directly; train/test split not applicable

**Recommendation:** Update the DataFrame Reference to clarify the baseline uses `pilot_df`, not the split DataFrames. The split DataFrames are used by Prophet and for calculating `zone_mean` in the baseline results, but not for the actual baseline prediction.

---


