# Module 5 — Progress

| Task | Step | Status | Date | Notes |
| --- | --- | --- | --- | --- |
| Setup | Data loads and passes checks (`helpers/m05_data.py`) | Done | 16 Nov 2026 | 15 stocks × 1,457 days |
| Setup | Target and rebalance decisions (M5-01 to M5-04) | Done | 16 Nov 2026 | Confirmed 22 Nov 2026 after exploration |
| Setup | First look; brief re-read verbatim; macro columns found to be random | Done | 22 Nov 2026 | 15 values per date; day-to-day correlation about 0 |
| Setup | Layout (M5-09); `helpers/m05_style.py`; inputs added to `m05_data.py` | Done | 22 Nov 2026 | |
| Task 1 | Decisions M5-06 (exploration in Task 1), M5-07 (inputs), M5-08 (models, IC, shuffled test), M5-10 (hand-off, kept lean) | Done | 22 Nov 2026 | Each tested on the data before agreeing |
| Task 1 | Notebook: data and macro checks; 22 inputs × 3 horizons; combinations; 5 ways of predicting over 43 months; shuffled test; ₹ value of IC | Done | 22 Nov 2026 | 0 of 66 input tests pass; best of 946 pairs p 0.48; no model beats luck (IC −0.049 to +0.005, p 0.53–0.93) |
| Task 1 | Report `reports/task1_report.md`; runner cell; HOW_TO_RUN rows; `FINAL_M5_T1_return_predictions.csv` for Task 2 | Done | 22 Nov 2026 | Verified: standalone and runner give identical key numbers, predictions, model tests and evidence table; 0 errors, 3 charts each |
| Task 2 | Decisions M5-05 (top 5, confirmed), M5-11 (benchmark all 15 + random picks), M5-12 (equal weight), M5-13 (before costs, turnover shown), M5-14 (output file) | Done | 22 Nov 2026 | Each option tested on Task 1's predictions before agreeing |
| Task 2 | Notebook `m05_task2_ranking.ipynb`: rank, select top 5, equal weight, 43 months; benchmark; 1,000 random picks; top 3/7 check; risk by number held; ₹ | Done | 22 Nov 2026 | No portfolio beats all 15 (15.8% a year): 8.3%–19.1%, p ≥ 0.40; best strategy flips with the number held |
| Task 2 | Report `reports/task2_report.md`; runner cell; HOW_TO_RUN rows | Done | 22 Nov 2026 | Verified: standalone and runner give identical Task 2 files (selections, returns, summary, September portfolio, key numbers); Task 1 outputs unchanged by the runner; 0 errors (runner 5 charts) |
| Task 2 | M5-17: September 2026 portfolio for all strategies; quarterly and weighting checks (steps 9–10) | Done | 22 Nov 2026 | Same answer quarterly and with other weightings; ML models agree on LT and ITC for September |
| Task 2 | M5-15 model for Module 6 (ridge), M5-16 Module 9 figures (replaced by Module 6's final figures, M6-11) | Agreed | 22 Nov 2026 | |
| Module | `reports/module_5_report.md` | Done | 22 Nov 2026 | |
| Module | Final files renamed `FINAL_M5_…`; final output workbook `outputs/FINAL_M5_module_output.xlsx` (`helpers/m05_final_output.py`, runner's last cell) | Done | 22 Nov 2026 | Project decision P-21; rerun and check to follow |
| Module 9 inputs | Final notebook step: ML stock selection in the standard Module 9 fields; `module9_inputs.csv`; workbook 'Module 9 inputs' tab and hand-off row; reports, docs, prep files | Done | 22 Nov 2026 | Existing outputs unchanged |
