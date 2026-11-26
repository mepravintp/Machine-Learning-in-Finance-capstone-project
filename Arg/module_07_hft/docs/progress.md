# Module 7 — Progress

| Stage | Step | Status | Date | Notes |
| --- | --- | --- | --- | --- |
| Setup | Data loads and passes checks (`helpers/m07_data.py`) | Done | 16 Nov 2026 | 120,000 rows, 20 days, 10 stocks |
| Setup | First look; planning decisions re-tested on the data | Done | 22 Nov 2026 | OBI AUC 0.78: a real signal |
| Decisions | M7-01 to M7-16 agreed one at a time | Done | 22 Nov 2026 | Costs revised (half-spread + 0–1 bp → spread both ways + 3.5 bps Indian charges) |
| Task 1 | Notebook `m07_task1_direction.ipynb`: exploration, 15 inputs, 4 models, test days, DeLong, NO_MOVE | Done | 22 Nov 2026 | Logistic regression 60.6% right vs 42.0%; AUC 0.791 vs OBI alone 0.781 (p < 0.0001) |
| Task 2 | Notebook `m07_task2_signal.ipynb`: Test 1, Test 2, recommendation | Done | 22 Nov 2026 | First build (fixed cut-off 0.70): Test 1 +₹516 per ₹1 crore trade; superseded by the rebuild below after Task 1's review. Test 2 ₹1,315 saved per ₹1 crore of orders |
| Outputs | Final files, workbook `outputs/FINAL_M7_module_output.xlsx` (column guide, Hand-off to Module 9) | Done | 22 Nov 2026 | |
| Reports | `task1_report.md`, `task2_report.md`, `module_7_report.md`; runner; HOW_TO_RUN rows | Done | 22 Nov 2026 | Verified: standalone and runner give identical files; 0 errors |
| Review | Task 1 step 7: what Task 1 means for Task 2 (M7-17); Test 1 rule revised to cost-aware (M7-13) | Done | 22 Nov 2026 | Missed at first: Task 2 was built before this review; fixed and made a fixed step |
| Task 1 | Standard sections added (as Modules 1–6): overfitting check, by stock and day, shuffled-label luck test, model-choice factor table with 95% ranges, what the model relies on, ₹ in the review | Done | 22 Nov 2026 | All pass: gap +0.003; 10/10 stocks, 3/3 days; luck p 0.0099; gain +0.008 to +0.012 |
| Task 2 | Rebuilt end to end on the reviewed decisions: cost-aware Test 1 (M7-13), 95% range and by-stock view added (as other modules); findings, final file, report, workbook, decisions, docs, prep files | Done | 22 Nov 2026 | Test 1 +₹700 a trade, +₹10.3 lakh (range +₹6.4 to +₹14.1), 3/3 days, 8/10 stocks; Test 2 ₹1,315 per ₹1 crore of orders |
| Module 9 inputs | Task 2 step 5b: HFT in the standard fields; `module9_inputs.csv`; workbook 'Module 9 inputs' tab and hand-off row; reports, docs, prep files | Done | 22 Nov 2026 | Order timing on equity money ≈ 0.010% a year |
