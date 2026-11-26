# Vineet's NovaFin workspace

My version of every capstone module, built to the *NovaFin Capstone — Project Blueprint*. Module and folder names
match `novafin_capstone/`, so each module can be compared one-to-one and the best output chosen per module.

## Layout

```
vineet/
  src/novakit/     shared toolkit: every notebook imports it
    config.py      paths, data loading, seed 42, locked assumptions
    splits.py      repeated stratified CV, time split, whole-day blocks, monthly walk-forward with a gap
    evaluate.py    classification and regression metrics, calibration, cost curve, rank IC
    explain.py     coefficients, SHAP top drivers and individual cases
    finance.py     NPV, IRR, eNPV, ECL, CLV, Sharpe, drawdown, VaR, Black-Scholes, Greeks, implied vol, RAROC
    handoff.py     writes and reads each module's Module 9 record
  notebooks/       00_setup_and_data_audit … 10_allocation (run in order, from inside notebooks/)
  results/         results/<Module folder>/handoff.json and tables
  figures/         figures/<Module folder>/*.png
  tests/           toolkit tests
```

## Run

```bash
pip install -r requirements.txt
python -m pytest                 # from vineet/
jupyter lab notebooks/           # run 00 → 10 in order
```

Data is read from `../novafin_capstone/data/` and never copied or edited. To read it from somewhere else
(e.g. Colab), set `NOVAFIN_DATA` to the folder holding the CSVs.

## Conventions

- Seed 42 everywhere; splits follow the blueprint (time split for transactions, whole days for the order book,
  monthly walk-forward with a 21-day gap for market data, repeated stratified CV for the rest).
- Every module ends with `handoff.write_handoff(...)`: business_line, capacity_cr, expected_return_pct,
  expected_loss_pct, capital_charge_pct, raroc_pct (computed, never typed), stress_loss_pct, ml_edge, evidence,
  key_risks. Notebook 10 builds the allocation from these files only.
- XGBoost stands in for LightGBM in Module 5.

## Status

| # | Notebook | Module | Status |
|---|---|---|---|
| 00 | 00_setup_and_data_audit | Data audit | Done: matches the blueprint's audit table, two refinements noted |
| 01 | 01_strategic_initiatives | 1 Strategic initiatives | Skeleton |
| 02 | 02_credit_risk | 2 Credit risk | Skeleton |
| 03 | 03_fraud | 3 Fraud detection | Skeleton |
| 04 | 04_churn_clv | 4 Churn and CLV | Skeleton |
| 05 | 05_equity_returns | 5 Equity returns | Skeleton |
| 06 | 06_portfolio | 6 Portfolio optimisation | Skeleton |
| 07 | 07_hft | 7 High-frequency order book | Skeleton |
| 08 | 08_options | 8 Derivatives | Skeleton |
| 09 | 09_liquidity_stress | Treasury: liquidity reserve | Skeleton |
| 10 | 10_allocation | 9 Integrated allocation | Skeleton |
