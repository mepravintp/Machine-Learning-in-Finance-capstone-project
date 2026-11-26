# Module 1 — Progress

| Task | Step | Status | Date | Notes |
| --- | --- | --- | --- | --- |
| Setup | Data loads and passes checks (`helpers/m01_data.py`) | Done | 16 Nov 2026 | 180 rows, no missing values |
| Setup | Finance functions (`helpers/m01_finance.py`) | Done | 16 Nov 2026 | NPV, Expected NPV, break-even, hurdle, decision rule; checked on initiative 1002 |
| Setup | Decisions M1-01 to M1-05, M1-07 | Done | 16 Nov 2026 | See decisions.md |
| Task 1 | Investment distribution | Done | 17 Nov 2026 | ₹31–296 lakh, median 155, even spread; total ₹283 crore |
| Task 1 | ROI distribution | Done | 17 Nov 2026 | Median 10.5%; falls with risk (12.0 → 8.3%); 11 rows at 2.00% floor |
| Task 1 | Risk categories | Done | 17 Nov 2026 | Success Low 89%, Medium 69%, High 70% (p = 0.014) |
| Task 1 | Business-unit performance | Done | 17 Nov 2026 | 63–87% success but p = 0.36; Corporate Banking to watch |
| Task 1 | Growth vs ROI | Done | 17 Nov 2026 | Business_Growth r 0.56; GDP 0.12; own revenue growth 0.03 |
| Task 1 | Investment vs success | Done | 17 Nov 2026 | No link (p = 0.90); size drives NPV (r −0.60) |
| Task 1 | Quality checks, notebook, report, decisions M1-08 to M1-12 | Done | 17 Nov 2026 | `notebooks/m01_task1_eda.ipynb`, `outputs/task1/`, `reports/task1_report.md` |
| Task 1 | Detailed code comments; runner entry | Done | 17 Nov 2026 | Project decisions P-09 to P-11 |
| Task 1 | Restructured to notebook-per-task (P-09, P-10); charts embedded in report (P-13) | Done | 17 Nov 2026 | Old `scripts/m01_task1_eda.py` removed; its code now lives in the notebook |
| Setup | `docs/` folder for documentation, approach, decisions, progress; `concepts.md` removed; `run_module_1.py` added | Done | 17 Nov 2026 | Project decisions P-09, P-14 |
| Setup | Runner is now `run_module_1.ipynb` (one `%run` cell per step); `add_features()` moved to shared `helpers/m01_data.py`; tables use `display()` | Done | 17 Nov 2026 | Decisions P-14 to P-17. Task 1 checked standalone and through the runner: identical key numbers; 6 charts and 8 tables shown both ways |
| Setup | `scripts/` renamed `helpers/` (all modules); `Outcome` column removed from shared `add_features()`; derived columns documented in `DERIVED_COLUMNS` | Done | 17 Nov 2026 | Decisions P-18, P-19. Task 1 re-checked standalone and via runner: identical key numbers |
| Setup | Leakage review: M1-13 (revenues are projections), P-20 (when to explore all rows vs training period only) | Done | 17 Nov 2026 | Applied in Task 2: learned steps inside a Pipeline; tuning inside folds or defaults; save out-of-fold P(Success) |
| Task 2 | Inputs: 26 pre-set columns (10 given, 7 derived, 9 one-hot) | Done | 17 Nov 2026 | M1-17 |
| Task 2 | 7 models × 25 rounds (repeated stratified 5-fold); balancing comparison; model choice; shuffled-label check | Done | 17 Nov 2026 | Lasso best: ROC-AUC 0.578, Brier 0.180 (ties baseline 0.179); trees at chance; M1-14 to M1-18 |
| Task 2 | Explainability: odds ratios, lasso inputs kept, SHAP summary + waterfalls; reliability chart | Done | 17 Nov 2026 | Low risk (odds × 2.4), Business_Growth, Expected_ROI, Revenue growth up; Corporate Banking down |
| Task 2 | Out-of-fold P(Success) per initiative saved for Task 3; report; runner cell | Done | 17 Nov 2026 | `outputs/task2/FINAL_M1_T2_success_probability.csv` (0.56–0.90); `reports/task2_report.md`; standalone and runner checked |
| Task 2 | Step 8b ML + finance model scorecard; step 10e ranked drivers of success (with finance meaning); report sections 5.1 and 7.5; M1-19 extended | Done | 17 Nov 2026 | `8b_model_scorecard.csv`, `10e_success_drivers.csv/.png`; standalone run: 0 errors, key numbers unchanged |
| Task 2 | Lasso explained in depth (step 10b-ii: objective, scaling, coordinate descent, lasso path and entry order on our data; no toy examples in the task notebook, at the user's request); rupee replay of each model's flag (step 8c, M1-21); business reasoning per driver (10e); step 13 split into ML case / finance case / decision | Done | 17 Nov 2026 | So a Board fluent in both ML and finance sees a balanced case |
| Task 1 | Board view in ₹ (step 9) and "What the results say" with data finding next to finance meaning (step 10); report section 3.7 | Done | 17 Nov 2026 | Medium/High risk: 65% of capital, 86% of failed capital; Corporate Banking: 22% of capital, 35% of failed capital |
| Task 2 | 3-initiative scoring check removed from the notebook (not part of the task); report sections 1 (ML and finance case), 5.2, 7.1, 7.5 | Done | 17 Nov 2026 | |
| Check | Task 1 alone, Task 2 alone, then `run_module_1.ipynb`: 0 errors; key numbers identical (runner = standalone = previous run); every chart embedded in the reports | Done | 17 Nov 2026 | P-16. p_success differs only in the 4th decimal on a few rows (floating-point); the at-risk flags are identical |
| Task 3 | M1-20 agreed (option 3: lasso P + flat 0.77 sensitivity); the M1-06 rule was then agreed point by point | Done | 17 Nov 2026 | |
| Task 2 | Risk-rating-only benchmark (M1-22): scorecard row, within-risk-level ROC-AUC, rupee replay row, step 13 and report 5.1b | Done | 17 Nov 2026 | Benchmark ties lasso (0.577 vs 0.578); lasso kept (option 1) |
| Task 3 | M1-06 agreed point by point (A–F); decision rule moved from the helper into the notebook (P-15) | Done | 17 Nov 2026 | Fund 2, Review 38, Reject 140 |
| Task 3 | Notebook (steps 0–12), outputs (`FINAL_M1_T3_initiative_decisions.csv` + summaries + 3 charts), report, runner cell, HOW_TO_RUN row | Done | 17 Nov 2026 | Sensitivity: P source (lasso 38 / no model 74 / rating only 31 in Review); cut-off 4/5/6 yrs → Review 21/38/47 |
| Check | Task 2 alone and Task 3 alone after the benchmark and Task 3 build: 0 errors (Task 2: 11 charts; Task 3: 3 charts); Task 2's earlier key numbers unchanged | Done | 17 Nov 2026 | |
| Check | Runner with Tasks 1–3: 0 errors; key numbers identical to the standalone runs for all three tasks | Done | 17 Nov 2026 | P-16. Task 3 now closes charts left open by Task 2 (one chart was shown twice in the runner); the saved runner output refreshes on its next Run all |
| Review | Report review: contradictions, missing items and weak explanations fixed item by item across the three task reports; overfitting check added (Task 2 step 5b); decisions by unit and risk added (Task 3 step 7b) | Done | 17 Nov 2026 | Standalone runs of Tasks 1–3: 0 errors, key numbers unchanged |
| Module | `reports/module_1_report.md`: final report consolidating the three tasks, with cross-task conclusions (Corporate Banking; likely success vs value; what the ML changed), key decisions, hand-off to Module 9, limitations, glossary (P-23) | Done | 17 Nov 2026 | |
| Check | Runner with Tasks 1–3 after the review changes and the new decision file | Done | 18 Nov 2026 | 0 errors; key numbers identical to the standalone runs |
| Task 3 | Board decision file redesigned (step 10b): every check in words (value, risk, payback, hurdle, model, loss tolerance), decision path, funding condition, priority, full reason; no blank cells, no codes; column guide in Task 3 and module reports | Done | 18 Nov 2026 | |
| Module | Final files renamed `FINAL_M1_…`; final output workbook `outputs/FINAL_M1_module_output.xlsx` (`helpers/m01_final_output.py`, runner's last cell) | Done | 22 Nov 2026 | Project decision P-21; rerun and check to follow |
| Fix | Lasso (Task 2) now uses the project seed 42 (solver 'liblinear' shuffles internally; P-06) | Done | 22 Nov 2026 | Found when Task 2 didn't repeat exactly (up to 0.0001 in P(Success), no decision changed). Confirmed 22 Nov 2026: two runs now give identical files; every figure in the Module 1 reports is unchanged (Fund 2 / ₹3.24 crore / +₹56.0 lakh; Review 38 / ₹62.95 crore; Reject 140; ROC-AUC 0.578; 106 at risk; 1075 +₹48.2 lakh, 164%; 1062 36%). Runner check passed (identical files); workbook rebuilt |
| Module 9 inputs | Task 3 step 10c: return and risk per ₹ by business unit; `module9_inputs.csv`; workbook 'Module 9 inputs' tab and hand-off rows; reports, docs, prep files | Done | 22 Nov 2026 | Deployable initiatives ₹66.2 crore at 12.1% a year (bad case 5.9%); existing outputs unchanged |
