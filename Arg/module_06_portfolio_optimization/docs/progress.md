# Module 6 — Progress

| Stage | Step | Status | Date | Notes |
| --- | --- | --- | --- | --- |
| Setup | Metrics helper `helpers/m06_metrics.py` | Done | 16 Nov 2026; updated 22 Nov 2026 | 261-day year, 6.8% risk-free, Calmar, tracking error, information ratio added; self-test passes |
| Setup | Brief re-read; planning decisions tested on the data (prototype) | Done | 22 Nov 2026 | `Interest_Rate`, `VIX` random; 261 rows a year; minimum-risk = equal weight |
| Setup | Decisions M6-01 to M6-10 | Agreed | 22 Nov 2026 | Cost revised 0.20% → 0.15% |
| Part A | Notebook `m06_partA_backtest.ipynb`: four strategies, 43-month backtest with costs, measures, luck test, checks, ₹ | Done | 22 Nov 2026 | Equal weight best Sharpe (1.06); Markowitz 16.6% CAGR but p 0.79; ML worst (10.6%) |
| Part A | Report `reports/partA_report.md`; runner `run_module_6.ipynb`; HOW_TO_RUN rows | Done | 22 Nov 2026 | Verified: standalone and runner give identical weights, daily returns, comparison, cost checks and key numbers; 0 errors, 2 charts each |
| Part B | Notebook `m06_partB_risk.ipynb`: VaR and CVaR (1 day, 1 month), bell-curve fit, stress tests (a)–(c), ₹ | Done | 22 Nov 2026 | Equal weight lowest on every measure; with real-market correlation its swing ×2.5 (7.8% → 19.4%) |
| Part B | Report `reports/partB_report.md`; runner cell; HOW_TO_RUN rows | Done | 22 Nov 2026 | Verified: standalone and runner give identical Part B files (risk summary, VaR table, stress tests, key numbers); Part A still identical; 0 errors (runner 4 charts) |
| Module | M6-11 (what Module 9 gets), M6-12 (hand-off file); `outputs/FINAL_M6_module_output.xlsx` (Hand-off tab), built by `helpers/m06_final_output.py` | Done | 22 Nov 2026 | Replaces Module 5's before-cost rates (M5-16) |
| Module | `reports/module_6_report.md` | Done | 22 Nov 2026 | |
| Module 9 inputs | Final notebook step: equities in the standard Module 9 fields; `module9_inputs.csv`; workbook 'Module 9 inputs' tab and hand-off row; reports, docs, prep files | Done | 22 Nov 2026 | Existing outputs unchanged |
