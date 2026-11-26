# Module 3 — Approach

**The chain:** Data and what drives fraud (Task 1) → **supervised fraud model** (Task 2) → **anomaly detection with Isolation Forest** (Task 3) → **cost-based threshold** (Task 4).

**Business problem (brief):** NovaFin processes thousands of transactions every day. Management wants to identify suspicious transactions while minimizing unnecessary investigation.

**Order of work:** each task is built and its evidence reviewed before the next task's rules are fixed. Each decision is tested on this module's data before it is agreed.

| Task | Decisions | Status |
| --- | --- | --- |
| Task 1 | M3-06 to M3-10 | Agreed; built |
| Task 2 | M3-01, M3-02, M3-11 to M3-14 | Agreed; built |
| Task 3 | M3-15, M3-16, M3-17 (M3-04 closed) | Agreed; built |
| Task 4 | M3-18, M3-19, M3-20 (M3-03 closed) | Agreed; built |

## Data

- `nova_transactions.csv`: 30,000 transactions, 2,500 customers, January 2025 to August 2026. About 49 a day, so the file is a sample of the "thousands every day" in the brief.
- `helpers/m03_data.py`: `load_transactions()` (checks, sorts by time) and `add_features()` (M3-07). None of the derived columns uses Fraud_Flag:

```text
Amount_Ratio     = Amount ÷ Historical_Avg_Transaction      how unusual this amount is for the customer
Hour, Weekday    = from Timestamp
Device_Change    = 1 if the device differs from the customer's previous transaction      (earlier rows only)
Location_Change  = 1 if the city differs from the customer's previous transaction        (earlier rows only)
```

## Task 1 — Exploratory analysis (built)

| Brief item | What is produced |
| --- | --- |
| Fraud rate | Count, %, 95% range, ₹ value, share of money; month by month with a stability test |
| Fraud by transaction type | Rate per type with 95% range, ₹, chi-square, each type against the rest |
| Fraud by amount | Tenths (₹ ranges), distribution, concentration in the largest transactions, ₹ bands for the Board |
| Fraud by location | Rate per city with 95% range, ₹, chi-square |
| Fraud by customer behaviour | Historical_Avg_Transaction, Amount_Ratio, Account_Age_Months, Transaction_Frequency in tenths; two-input logistic check |
| Also tested (in the file) | Merchant category; hour and weekday; device and location change; fraud clustering on devices and customers; earlier fraud on the device or customer |

**Evidence rule (M3-10):** Strong = p below the Bonferroni line and single-column ROC-AUC ≥ 0.60; Weak = significant, ROC-AUC below 0.60; Not informative = not significant. One evidence table ranks every column.

**Output:** `outputs/task1/FINAL_M3_T1_fraud_evidence.csv` and the tables, charts and key numbers behind each item.

## Task 2 — Supervised fraud model (built)

- **Split (M3-01):** train on the first 80% by time (24,000, Jan 2025 – Apr 2026); test once on the last 20% (6,000, May – Aug 2026). Model choice by 25 rounds of stratified 5-fold CV inside training.
- **Measures (M3-02):** PR-AUC decides; catch curves in frauds and ₹ at every investigation budget; ROC-AUC; Brier. Accuracy shown once to explain why it isn't used.
- **Inputs (M3-11):** strong + weak vs all columns; the simpler set wins unless more inputs help beyond chance.
- **Models and rule (M3-12):** amount alone (benchmark), logistic, lasso, decision tree, random forest, LightGBM; no class weights; rule out a gap above 0.10; simplest within chance of the best PR-AUC wins.
- **Calibration (M3-13):** reported, not pass/fail; decided at Task 4.
- **Also (M3-14):** leakage checks; finance case in actual ₹; SHAP and examples; `FINAL_M3_T2_fraud_scores.csv` for Tasks 3 and 4.

## Task 3 — Isolation Forest (built)

- **Inputs (M3-15):** six numeric descriptors on raw ₹, chosen without fraud information; side check on amount + ratio; category encodings tested and shown.
- **Settings (M3-17):** 500 trees of 256 transactions; fitted on training transactions only; flags 2.25% (training fraud rate); SHAP reasons in words.
- **Comparison:** amount alone vs supervised vs Isolation Forest on the 6,000 test transactions; overlap; combining; finance case per 1,000 transactions.
- **Outputs (M3-16):** `unusual_transactions.csv` (deliverable), `FINAL_M3_T3_anomaly_scores.csv` (hand-off), `comparison.csv`.

## Task 4 — Cost-based threshold (built)

- **Costs (M3-18):** brief's ₹10,000 / ₹500 as the base; each missed fraud at its real amount as the finance view.
- **Threshold (M3-19):** investigate when P(fraud) × ₹10,000 > (1 − P(fraud)) × ₹500, i.e. P(fraud) > 4.76%; the sweep (every cut-off on training) as a cross-check; calibration checked above and below the line on training and test.
- **Scope and outputs (M3-20):** one compact sensitivity table under limitations; `FINAL_M3_T4_transaction_decisions.csv`, `threshold_summary.csv`.


## Shared code

- `helpers/m03_data.py`: load, check, `add_features()`, `INPUT_SETS` and `make_inputs()` (model inputs), `data_report()`.
- `helpers/m03_style.py`: chart style shared by all four tasks.
- Results pass between tasks as files in `outputs/taskN/` (P-15).
