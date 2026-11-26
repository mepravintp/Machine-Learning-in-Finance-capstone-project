# Module 4 — Progress

| Task | Step | Status | Date | Notes |
| --- | --- | --- | --- | --- |
| Setup | Data loads and passes checks (`helpers/m04_data.py`) | Done | 16 Nov 2026 | 5,000 rows, 1.8% churn |
| Setup | First look; 16 Nov plan reviewed against it | Done | 21 Nov 2026 | No column separates churners (every p > 0.09); Estimated_CLV is an exact formula of the financial columns (R² = 1.0); planning decisions M4-01 to M4-05 reopened |
| Setup | Layout (M4-07); `helpers/m04_style.py`; `add_features()` (5 business features) | Done | 21 Nov 2026 | |
| Task 1 | Decisions M4-08 to M4-11 (how predictability is shown, no separate test set, what is delivered, settings with derivations) | Done | 21 Nov 2026 | Settings tested on the data before agreeing; feature engineering (5 business features, 115-input search) and rebalancing tested |
| Task 1 | Notebook: columns, 5 set-ups over 25 rounds, shuffled-label test, business check, broad search, rebalancing evidence, drivers | Done | 21 Nov 2026 | Churn not predictable: 0 of 15 columns (lowest p 0.086); 0 of 5 set-ups beat shuffled labels (p 0.20–0.84); top-1,000 catch 15–22 churners vs 17.8 random; 0 of 10 drivers significant |
| Task 1 | Report `reports/task1_report.md`; runner cell; HOW_TO_RUN row; `FINAL_M4_T1_churn_scores.csv` for Task 3 | Done | 21 Nov 2026 | Standalone and runner runs compared |
| Task 1 | Simple bank rules compared (M4-13, step 6b) | Done | 21 Nov 2026 | 0 of 7 rules beat random (14–22 churners vs 17.8) |
| Task 2 | Decision M4-12: estimate Estimated_CLV from the financial variables; own textbook CLV dropped | Done | 21 Nov 2026 | Recovered rule matches every customer within ₹0.01 (one paisa) |
| Task 2 | Decision M4-14 (models, validation, measures) | Done | 21 Nov 2026 | Tested before agreeing |
| Task 2 | Notebook: five models over 25 rounds; the CLV rule and its weights; finance view | Done | 21 Nov 2026 | Linear regression RMSE ₹36 vs ₹6,739–₹12,057 for trees; rule matches all 5,000 within ₹0.01 (one paisa); complaints cost ₹3.81 crore (12%); top 1,000 hold 42% of CLV |
| Task 2 | Report `reports/task2_report.md`; runner cell; HOW_TO_RUN row; `FINAL_M4_T2_customer_value.csv` for Task 3 | Done | 21 Nov 2026 | Standalone and runner runs compared |
| Task 3 | Decisions M4-16 (churn side), M4-17 (cut-offs), M4-18 (the 1,000 list; break-even, no assumed success rate) | Done | 22 Nov 2026 | Each tested on the data before agreeing; closes M4-04 and M4-05 |
| Task 3 | Notebook: four groups with actual churn, the 1,000 list, back-test, break-even | Done | 22 Nov 2026 | Groups churn alike (p = 0.67); list = 1,000 highest-CLV customers, ₹13.79 crore (42%); reaches ₹18.7 lakh of ₹56.0 lakh value that left vs ₹11.2 lakh random; ₹500 calls must keep ≥ 20% of would-be leavers |
| Task 3 | Report `reports/task3_report.md`; runner cell; HOW_TO_RUN rows; `FINAL_M4_T3_contact_list.csv` | Done | 22 Nov 2026 | Standalone and runner runs compared: all 10 output files identical, 0 errors |
| Module | Decision M4-19 (Module 9 hand-off: rates, break-even floor, 100% ceiling, governance point) | Done | 22 Nov 2026 | Net fee yield 1.77%; retention at most ₹19.5–22.0 lakh on the 1,000 list |
| Module | `reports/module_4_report.md` | Done | 22 Nov 2026 | Answer, chain, cross-task conclusions, decisions, Module 9 hand-off, limitations, glossary |
| Module | Final files renamed `FINAL_M4_…`; final output workbook `outputs/FINAL_M4_module_output.xlsx` (`helpers/m04_final_output.py`, runner's last cell) | Done | 22 Nov 2026 | Project decision P-21; rerun and check to follow |
| Module 9 inputs | Final notebook step: Wealth management's fee income in the standard Module 9 fields; `module9_inputs.csv`; workbook 'Module 9 inputs' tab and hand-off row; reports, docs, prep files | Done | 22 Nov 2026 | Existing outputs unchanged |
