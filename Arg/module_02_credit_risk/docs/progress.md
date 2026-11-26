# Module 2 — Progress

| Task | Step | Status | Date | Notes |
| --- | --- | --- | --- | --- |
| Setup | Data loads and passes checks (`helpers/m02_data.py`) | Done | 16 Nov 2026 | 5,000 rows; identifier made Loan_ID at load (M2-01), tested on four cases |
| Setup | Approach agreed task by task (M2-01 to M2-14) | Done | 18 Nov 2026 | Task 3 money rules (M2-05, M2-06, decision rule) settled after Task 2 |
| Setup | Layout: runner, notebooks, outputs, reports (M2-08) | Done | 19 Nov 2026 | `run_module_2.ipynb`, `helpers/m02_style.py` |
| Task 1 | Know the data: checks, default by input, ₹ book view, collateral, term (M2-10) | Done | 19 Nov 2026 | ₹639.7 crore book; 24.5% of ₹ to defaulters; loss at 40% ₹62.7 crore; default flat by term |
| Task 1 | 15 inputs incl. 4 ratios; Interest_Rate as champion (M2-11) | Done | 19 Nov 2026 | Fundamentals explain 72.2% of the rate |
| Task 1 | Split 80/20 + 25-round CV; champion, reference, 5 challengers (M2-07, M2-13) | Done | 19 Nov 2026 | Lasso chosen: CV Brier 0.1411 vs champion 0.1444; ROC-AUC 0.731 vs 0.702 |
| Task 1 | Rebalancing evidence; overfitting check (M2-12) | Done | 19 Nov 2026 | Random forest and LightGBM ruled out (gaps 0.133, 0.109) |
| Task 1 | ₹ case: same approval, same default rate, mispriced loans | Done | 19 Nov 2026 | ₹2.1 crore less loss at 50% approval; +₹60 crore lending at same default rate; 95 overcharged good loans |
| Task 1 | Final test (1,000 loans), bootstrap, DeLong | Done | 19 Nov 2026 | ROC-AUC 0.741 vs 0.719, same direction, not proven at 95% (DeLong p = 0.065) |
| Task 1 | Explainability: weights, odds ratios, SHAP, example loans | Done | 19 Nov 2026 | 7 of 15 inputs kept |
| Task 1 | Report `reports/task1_report.md`; runner cell; HOW_TO_RUN row | Done | 19 Nov 2026 | Standalone and runner runs compared |
| Task 1 | Thresholds reviewed (M2-15): overfitting limit justified and checked; ₹ check turned into a 30–100% sweep; every model vs lasso on unseen loans | Done | 19 Nov 2026 | ₹ turning point about 73% approval, carried to Task 3 |
| Task 2 | Decisions: which PD (M2-16), calibration pass lines (M2-17), band tests and fallback (M2-18) | Done | 19 Nov 2026 | Agreed before building |
| Task 2 | Calibration checks; Platt scaling only if needed (M2-14) | Done | 19 Nov 2026 | All four checks pass on all 5,000 and on 1,000 test loans; Platt not needed |
| Task 2 | Risk bands: four tests (M2-04) | Done | 19 Nov 2026 | All pass, no merges; Low band thin (220 loans); margins +6.0 / +4.1 / +1.1 / −4.3% |
| Task 2 | Loan_ID · Predicted_PD · Risk_Category for every loan | Done | 19 Nov 2026 | `outputs/task2/loan_pd.csv`; hand-off `FINAL_M2_T2_risk_categories.csv` |
| Task 2 | Bands in ₹; scorecard vs bank's bands | Done | 19 Nov 2026 | Very High: 52% of expected loss, −₹8.25 crore a year; 66% same band; bank never signals Low |
| Task 2 | Report `reports/task2_report.md`; runner cell; HOW_TO_RUN row | Done | 19 Nov 2026 | Standalone and runner runs compared |
| Task 3 | Decisions with Task 2 PDs, each tested on the data first: cap re-anchored at 6% (M2-06), cost numbers confirmed (M2-05), which PD (M2-19), the rule (M2-20) | Done | 21 Nov 2026 | Agreed one at a time before building |
| Task 3 | ECL per loan and by band; the rule with reasons and required rate for every loan | Done | 21 Nov 2026 | ECL ₹63.04 vs actual ₹62.72 crore; Approve 2,934 / Review 1,045 / Reject 1,021 |
| Task 3 | Result in ₹; test-loan check; risk-appetite trade-off; cost and LGD sensitivities; scorecard vs champion; concentration; example loans | Done | 21 Nov 2026 | Approve default 11.3% vs 19.9% today; +₹10.45 vs +₹3.07 crore a year; 6% cap does not bind (5.45%) |
| Task 3 | `outputs/task3/FINAL_M2_T3_loan_decisions.csv`; report `reports/task3_report.md`; runner cell; HOW_TO_RUN row | Done | 21 Nov 2026 | Standalone and runner runs compared |
| Task 3 | Decision file upgraded (M2-21): numbers complete incl. Customer_Type and loan amount (for Module 9), every check in words, action for each Review loan, full reason; no blanks, no codes; column guide in Task 3 report §5.1; Retail / Corporate figures for Module 9 in `key_numbers.json` | Done | 21 Nov 2026 | Same layout idea as Module 1's decision file |
| Task 1, 3 | Segment analysis (M2-22): Task 1 step 8b (profiles, sector-risk trend, performance by segment, one vs separate models); Task 3 results by segment with bootstrap; reports and module report §3.7, §5.4, §6.5 | Done | 21 Nov 2026 | One model kept on evidence; ML gain mostly Retail; Corporate earnings gap within chance |
| Module | `reports/module_2_report.md`: Board section (answer, findings, actions, conclusions for the evaluator), the chain, Tasks 1–3, cross-task conclusions, key decisions with agreed vs final numbers, Module 9 hand-off, limitations, glossary | Done | 21 Nov 2026 | Module 9 uses the hand-off (M9-08) |
| Module | Final files renamed `FINAL_M2_…`; final output workbook `outputs/FINAL_M2_module_output.xlsx` (`helpers/m02_final_output.py`, runner's last cell) | Done | 22 Nov 2026 | Project decision P-21; rerun and check to follow |
| Module 9 inputs | Task 3 step 11b: lending return and bad-year results per ₹; `module9_inputs.csv`, `module9_lending_risk.csv`; workbook 'Module 9 inputs' tab and hand-off rows; reports, docs, prep files | Done | 22 Nov 2026 | Approved 3.30% a year; bad year −2.15%; existing outputs unchanged |
