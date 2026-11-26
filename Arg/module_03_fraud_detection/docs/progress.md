# Module 3 — Progress

| Task | Step | Status | Date | Notes |
| --- | --- | --- | --- | --- |
| Setup | Data loads and passes checks (`helpers/m03_data.py`) | Done | 16 Nov 2026 | 30,000 rows, 2.28% fraud |
| Setup | First look at the data; 16 Nov plan reviewed against it | Done | 21 Nov 2026 | Device_ID behaves like a random label; 'customer' columns change per transaction; amount is the one strong signal |
| Setup | Layout (M3-06); `helpers/m03_style.py`; `add_features()` | Done | 21 Nov 2026 | |
| Task 1 | Decisions M3-07 to M3-10 (behaviour columns, presentation, rows used, evidence rule) | Done | 21 Nov 2026 | Evidence rule tested on the data before agreeing |
| Task 1 | Fraud rate, by month; by type, amount, location, merchant, behaviour, time; device and customer history | Done | 21 Nov 2026 | 684 frauds, ₹2.01 crore (6.2% of the money); stable over time (p = 0.65) |
| Task 1 | Evidence table (16 tests) and Board view in ₹ | Done | 21 Nov 2026 | Strong: Amount, Amount_Ratio (ROC-AUC 0.79). Weak: usual amount, type. Not informative: 12 others. ₹25k+ = 9% of transactions, 55% of frauds, 84% of fraud ₹ |
| Task 1 | Report `reports/task1_report.md`; runner cell; HOW_TO_RUN row | Done | 21 Nov 2026 | Standalone and runner runs compared |
| Task 2 | Decisions M3-01 (time split), M3-02 (PR-AUC deciding), M3-11 (two input sets), M3-12 (models, no class weights, overfitting limit 0.10, selection rule), M3-13 (calibration reported), M3-14 (hand-off, explainability, leakage, finance case) | Done | 21 Nov 2026 | Each tested on the data before agreeing |
| Task 2 | 25-round comparison of 11 set-ups; overfitting check; selection rule | Done | 21 Nov 2026 | Chosen: LightGBM (100 trees, 4 leaves) on strong + weak inputs, PR-AUC 0.132 vs amount alone 0.116; random forest ruled out (gap 0.13–0.14) |
| Task 2 | Finance case in ₹; final test; calibration; SHAP and examples | Done | 21 Nov 2026 | Model finds more frauds but fewer fraud ₹ than amount alone at tight budgets; P(fraud) × amount best at 5% (₹4.53 vs ₹4.36 lakh per 1,000); test ROC-AUC +0.028 proven, PR-AUC +0.021 touches 0 |
| Task 2 | Report `reports/task2_report.md`; runner cell; HOW_TO_RUN row; `FINAL_M3_T2_fraud_scores.csv` for Tasks 3 and 4 | Done | 21 Nov 2026 | Standalone and runner runs compared |
| Task 3 | Decisions M3-15 (inputs and comparison), M3-16 (output files, all tasks; Tasks 1–2 trimmed), M3-17 (settings, share flagged, SHAP reasons) | Done | 21 Nov 2026 | Each tested on the data before agreeing |
| Task 3 | Isolation Forest fitted without the label; input tests; three-way comparison on 6,000 test transactions; overlap; combining; finance case | Done | 21 Nov 2026 | Flagged 680 (2.25%), 13.8% fraud; PR-AUC 0.075 vs supervised 0.124 vs amount 0.103 (gaps beyond chance); adds 3–6 frauds; combining doesn't help |
| Task 3 | `unusual_transactions.csv` with reasons; `FINAL_M3_T3_anomaly_scores.csv`; `comparison.csv`; report; runner cell; HOW_TO_RUN row | Done | 21 Nov 2026 | Standalone and runner runs compared |
| Task 4 | Decisions M3-18 (missed-fraud cost: brief's ₹10,000 base, real amount alongside), M3-19 (the 4.76% line, sweep cross-check, calibration check), M3-20 (scope and outputs) | Done | 21 Nov 2026 | Each tested on the data before agreeing (Task 4 tests run on a snapshot of the scores while the Task 1–3 check ran) |
| Task 4 | Line, calibration around it, sweep, test-set cost, finance view, sensitivity | Done | 21 Nov 2026 | Investigate when P(fraud) > 4.76%: 79 checks per 1,000, cost ₹1.48 vs ₹2.40 lakh (−38%); real saving ₹4.98 lakh per 1,000 (75%); all calibration checks pass |
| Task 4 | `FINAL_M3_T4_transaction_decisions.csv`; `threshold_summary.csv`; report; runner cell; HOW_TO_RUN row | Done | 21 Nov 2026 | Standalone and runner runs compared |
| Module | `reports/module_3_report.md`: Board section (answer, findings, actions, conclusions for the evaluator), the chain, Tasks 1–4, cross-task conclusions, key decisions and where evidence changed the plan, Module 9 hand-off, limitations, glossary | Done | 21 Nov 2026 | Module 9 hand-off (fraud cost 1.55% of money moved with screening, 6.1% without), used in Module 9 (M9-08) |
| Module | Final files renamed `FINAL_M3_…`; final output workbook `outputs/FINAL_M3_module_output.xlsx` (`helpers/m03_final_output.py`, runner's last cell) | Done | 22 Nov 2026 | Project decision P-21; rerun and check to follow |
| Module 9 inputs | Final notebook step: Digital banking's cost of fraud risk in the standard Module 9 fields; `module9_inputs.csv`; workbook 'Module 9 inputs' tab and hand-off row; reports, docs, prep files | Done | 22 Nov 2026 | Existing outputs unchanged |
